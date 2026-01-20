"""
Pokemon-Style Todo List Application
A pixelated task manager with categories and tasks
"""
import pygame
import sys
import os
from pymongo import MongoClient
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (232, 224, 200)  # Pokemon-style cream color
TEXT_COLOR = (48, 48, 48)
ACCENT_COLOR = (255, 203, 5)  # Pokemon yellow
BLUE_COLOR = (88, 112, 152)  # Darker retro blue
GREEN_COLOR = (104, 176, 88)  # Retro green
RED_COLOR = (216, 80, 80)  # Retro red
WHITE_COLOR = (248, 248, 248)
SHADOW_COLOR = (88, 88, 80)
BORDER_COLOR = (48, 48, 48)

# Database connection
try:
    client = MongoClient('mongodb://localhost:27017/',
                         serverSelectionTimeoutMS=5000)
    client.server_info()  # Force connection check
    db = client['hakim_todo']
    categories_collection = db['categories']
    tasks_collection = db['tasks']
    print("✓ Connected to MongoDB successfully!")
except Exception as e:
    print(f"✗ Failed to connect to MongoDB: {e}")
    print("Make sure MongoDB is running on mongodb://localhost:27017/")
    sys.exit(1)


class Button:
    """Pokemon-style pixelated button"""

    def __init__(self, x, y, width, height, text, color, text_color=TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False

    def draw(self, screen, font):
        # Pixel-perfect shadow (offset by 4 pixels)
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect)

        # Main button with thick pixel border
        color = tuple(min(c + 20, 255)
                      for c in self.color) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)

        # Thick 4px pixel border
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, 4)

        # Inner highlight for 3D effect (top-left)
        if not self.hovered:
            pygame.draw.line(screen, WHITE_COLOR,
                             (self.rect.x + 4, self.rect.y + 4),
                             (self.rect.right - 4, self.rect.y + 4), 2)
            pygame.draw.line(screen, WHITE_COLOR,
                             (self.rect.x + 4, self.rect.y + 4),
                             (self.rect.x + 4, self.rect.bottom - 4), 2)

        # Draw text (centered, pixelated)
        text_surface = font.render(self.text, False, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class PixelBox:
    """Retro pixel art dialog box"""
    @staticmethod
    def draw(screen, rect, color=WHITE_COLOR, border_size=4):
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect)

        # Main box
        pygame.draw.rect(screen, color, rect)

        # Thick border
        pygame.draw.rect(screen, BORDER_COLOR, rect, border_size)

        # Inner highlight for depth
        pygame.draw.line(screen, WHITE_COLOR,
                         (rect.x + border_size, rect.y + border_size),
                         (rect.right - border_size, rect.y + border_size), 2)
        pygame.draw.line(screen, WHITE_COLOR,
                         (rect.x + border_size, rect.y + border_size),
                         (rect.x + border_size, rect.bottom - border_size), 2)


class InputBox:
    """Pixelated input box for text entry"""

    def __init__(self, x, y, width, height, placeholder='', max_length=150):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_length = max_length
        self.scroll_offset = 0
        self.cursor_position = 0  # Cursor position in text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                # Reset cursor to end when clicking
                self.cursor_position = len(self.text)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_position > 0:
                    self.text = self.text[:self.cursor_position -
                                          1] + self.text[self.cursor_position:]
                    self.cursor_position -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_position < len(self.text):
                    self.text = self.text[:self.cursor_position] + \
                        self.text[self.cursor_position+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_position = max(0, self.cursor_position - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_position = min(
                    len(self.text), self.cursor_position + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_position = 0
            elif event.key == pygame.K_END:
                self.cursor_position = len(self.text)
            elif event.key == pygame.K_RETURN:
                return True
            else:
                # Insert character at cursor position
                if len(self.text) < self.max_length and len(event.unicode) > 0 and event.unicode.isprintable():
                    self.text = self.text[:self.cursor_position] + \
                        event.unicode + self.text[self.cursor_position:]
                    self.cursor_position += 1
        return False

    def update(self):
        # Blinking cursor
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen, font):
        # Draw input box with pixel style
        if self.active:
            pygame.draw.rect(screen, ACCENT_COLOR, self.rect)
        else:
            pygame.draw.rect(screen, WHITE_COLOR, self.rect)

        # Thick border
        border_color = ACCENT_COLOR if self.active else BORDER_COLOR
        pygame.draw.rect(screen, border_color, self.rect, 4)

        # Inner shadow for inset effect
        pygame.draw.line(screen, SHADOW_COLOR,
                         (self.rect.x + 4, self.rect.y + 4),
                         (self.rect.right - 4, self.rect.y + 4), 2)
        pygame.draw.line(screen, SHADOW_COLOR,
                         (self.rect.x + 4, self.rect.y + 4),
                         (self.rect.x + 4, self.rect.bottom - 4), 2)

        # Draw text or placeholder with scrolling
        display_text = self.text if self.text else self.placeholder
        text_color = TEXT_COLOR if self.text else (120, 120, 120)
        text_surface = font.render(display_text, False, text_color)

        # Calculate cursor position in pixels
        cursor_text = self.text[:self.cursor_position]
        cursor_x_offset = font.render(
            cursor_text, False, text_color).get_width() if cursor_text else 0

        # Calculate scroll offset to keep cursor visible
        text_width = text_surface.get_width()
        max_visible_width = self.rect.width - 24

        # Smart scrolling to keep cursor in view
        if cursor_x_offset - self.scroll_offset > max_visible_width - 20:
            # Cursor is too far right, scroll right
            self.scroll_offset = cursor_x_offset - max_visible_width + 20
        elif cursor_x_offset - self.scroll_offset < 20:
            # Cursor is too far left, scroll left
            self.scroll_offset = max(0, cursor_x_offset - 20)

        # Don't scroll past the beginning
        self.scroll_offset = max(0, self.scroll_offset)

        # Create a clipping rect for the text area
        clip_rect = pygame.Rect(self.rect.x + 12, self.rect.y + 12,
                                self.rect.width - 24, self.rect.height - 24)
        screen.set_clip(clip_rect)

        # Draw text with scroll offset
        screen.blit(text_surface, (self.rect.x + 12 -
                    self.scroll_offset, self.rect.y + 12))

        # Draw blinking cursor at cursor position
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 12 + cursor_x_offset - self.scroll_offset
            cursor_y = self.rect.y + 10
            pygame.draw.rect(screen, TEXT_COLOR, (cursor_x, cursor_y, 3, 20))

        # Reset clipping
        screen.set_clip(None)

    def get_text(self):
        return self.text

    def clear(self):
        self.text = ''
        self.cursor_position = 0
        self.scroll_offset = 0


class TodoApp:
    """Main application class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pokemon Todo List")
        self.clock = pygame.time.Clock()

        # Load pixel font
        font_path = os.path.join(os.path.dirname(
            __file__), 'PressStart2P-Regular.ttf')
        try:
            self.title_font = pygame.font.Font(font_path, 24)
            self.font = pygame.font.Font(font_path, 14)
            self.small_font = pygame.font.Font(font_path, 10)
        except:
            print("Pixel font not found, using default...")
            self.title_font = pygame.font.Font(None, 36)
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)

        # Get base directory for resource loading
        base_dir = os.path.dirname(__file__)
        
        # Set window icon
        try:
            icon_path = os.path.join(base_dir, 'sprites', 'logo.png')
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
            print("✓ Loaded window icon!")
        except Exception as e:
            print(f"⚠ Could not load icon: {e}")

        # Load Pokemon sprites
        try:
            pikachu_path = os.path.join(base_dir, 'sprites', 'pikachu.png')
            pokeball_path = os.path.join(base_dir, 'sprites', 'pokeball.png')
            badge_path = os.path.join(base_dir, 'sprites', 'badge.png')
            
            self.pikachu_sprite = pygame.image.load(pikachu_path)
            self.pokeball_sprite = pygame.image.load(pokeball_path)
            self.badge_sprite = pygame.image.load(badge_path)
            print("✓ Loaded Pokemon sprites!")
        except Exception as e:
            print(f"⚠ Could not load sprites: {e}")
            self.pikachu_sprite = None
            self.pokeball_sprite = None
            self.badge_sprite = None

        # App state
        self.current_view = 'categories'  # 'categories' or 'tasks'
        self.selected_category_id = None
        self.selected_category_name = ''
        # For edit mode: {'type': 'category'/'task', 'id': ...}
        self.editing_item = None
        self.edit_input = InputBox(150, 300, 500, 50, '')
        # For confirmation mode: {'action': 'delete_category'/'delete_task'/'edit_category'/'edit_task'/'toggle_task', 'data': ...}
        self.confirming_action = None

        # Scrolling
        self.category_scroll = 0
        self.task_scroll = 0
        self.items_per_page = 5

        # Input boxes
        self.category_input = InputBox(150, 510, 400, 50, 'New Goal...')
        self.task_input = InputBox(150, 510, 400, 50, 'New Task...')

        # Buttons
        self.back_button = Button(
            20, 20, 140, 50, '<- BACK', BLUE_COLOR, WHITE_COLOR)
        self.add_category_button = Button(
            570, 510, 180, 50, '+ ADD', GREEN_COLOR, WHITE_COLOR)
        self.add_task_button = Button(
            570, 510, 180, 50, '+ ADD', GREEN_COLOR, WHITE_COLOR)

        # Load data
        self.categories = []
        self.tasks = []
        self.load_categories()

    def load_categories(self):
        """Load categories from database"""
        self.categories = list(
            categories_collection.find().sort('created_at', -1))

    def load_tasks(self, category_id):
        """Load tasks for a specific category"""
        self.tasks = list(tasks_collection.find(
            {'category_id': category_id}).sort('created_at', 1))

    def add_category(self, name):
        """Add a new category"""
        if name.strip():
            category = {
                'name': name,
                'created_at': datetime.now()
            }
            categories_collection.insert_one(category)
            self.load_categories()

    def update_category(self, category_id, new_name):
        """Update a category name"""
        if new_name.strip():
            categories_collection.update_one(
                {'_id': category_id},
                {'$set': {'name': new_name}}
            )
            self.load_categories()
            if self.selected_category_id == category_id:
                self.selected_category_name = new_name

    def add_task(self, category_id, name):
        """Add a new task to a category"""
        if name.strip():
            task = {
                'category_id': category_id,
                'name': name,
                'completed': False,
                'created_at': datetime.now()
            }
            tasks_collection.insert_one(task)
            self.load_tasks(category_id)

    def update_task(self, task_id, new_name):
        """Update a task name"""
        if new_name.strip():
            tasks_collection.update_one(
                {'_id': task_id},
                {'$set': {'name': new_name}}
            )
            self.load_tasks(self.selected_category_id)

    def toggle_task(self, task_id):
        """Toggle task completion status"""
        task = tasks_collection.find_one({'_id': task_id})
        if task:
            new_status = not task['completed']
            tasks_collection.update_one(
                {'_id': task_id},
                {'$set': {'completed': new_status}}
            )
            self.load_tasks(self.selected_category_id)

    def delete_category(self, category_id):
        """Delete a category and all its tasks"""
        categories_collection.delete_one({'_id': category_id})
        tasks_collection.delete_many({'category_id': category_id})
        self.load_categories()

    def delete_task(self, task_id):
        """Delete a task"""
        tasks_collection.delete_one({'_id': task_id})
        self.load_tasks(self.selected_category_id)

    def draw_categories_view(self):
        """Draw the categories view"""
        # Pikachu sprite in corner
        if self.pikachu_sprite:
            self.screen.blit(self.pikachu_sprite, (10, 540))

        # Title box with retro style
        title_box_rect = pygame.Rect(50, 20, 700, 100)
        PixelBox.draw(self.screen, title_box_rect, ACCENT_COLOR, 6)

        # Title text
        title = self.title_font.render('POKEMON TODO', False, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Subtitle with count
        total_categories = len(self.categories)
        subtitle_text = f'SELECT A GOAL ({total_categories})'
        subtitle = self.small_font.render(subtitle_text, False, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(subtitle, subtitle_rect)

        # Draw scrollbar if there are more items than can fit
        if total_categories > self.items_per_page:
            scrollbar_x = 748
            scrollbar_y = 155
            scrollbar_width = 10
            scrollbar_height = 315  # Total scrollable area height
            
            # Scrollbar track
            track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
            pygame.draw.rect(self.screen, SHADOW_COLOR, track_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, track_rect, 2)
            
            # Scrollbar thumb
            thumb_height = max(30, int(scrollbar_height * self.items_per_page / total_categories))
            max_scroll = total_categories - self.items_per_page
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * (self.category_scroll / max_scroll)) if max_scroll > 0 else scrollbar_y
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(self.screen, BLUE_COLOR, thumb_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, thumb_rect, 2)

        # Scroll indicators
        if self.category_scroll > 0:
            # Up arrow
            up_text = self.font.render('^', False, TEXT_COLOR)
            self.screen.blit(up_text, (750, 135))

        if self.category_scroll + self.items_per_page < total_categories:
            # Down arrow
            down_text = self.font.render('v', False, TEXT_COLOR)
            self.screen.blit(down_text, (750, 485))

        # Draw categories with scrolling
        y_offset = 140
        start_idx = self.category_scroll
        end_idx = min(start_idx + self.items_per_page, total_categories)

        for i in range(start_idx, end_idx):
            category = self.categories[i]
            # Category card with thick pixel borders
            card_rect = pygame.Rect(80, y_offset, 640, 55)

            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            edit_btn_rect = pygame.Rect(
                card_rect.right - 105, card_rect.y + 10, 45, 35)
            delete_btn_rect = pygame.Rect(
                card_rect.right - 55, card_rect.y + 10, 45, 35)
            is_hovered = card_rect.collidepoint(mouse_pos) and not delete_btn_rect.collidepoint(
                mouse_pos) and not edit_btn_rect.collidepoint(mouse_pos)

            # Draw card with pixel box
            card_color = (255, 255, 200) if is_hovered else WHITE_COLOR
            PixelBox.draw(self.screen, card_rect, card_color, 4)

            # Pokeball icon
            if self.pokeball_sprite:
                self.screen.blit(self.pokeball_sprite,
                                 (card_rect.x + 10, card_rect.y + 12))
                text_x = card_rect.x + 50
            else:
                text_x = card_rect.x + 15

            # Category name with smart truncation
            name_text = category['name']
            max_text_width = 280  # Space before badge

            # Try to fit the full text, if not truncate with ...
            test_surface = self.font.render(name_text, False, TEXT_COLOR)
            if test_surface.get_width() > max_text_width:
                # Truncate and add ...
                while len(name_text) > 0 and self.font.render(name_text + '...', False, TEXT_COLOR).get_width() > max_text_width:
                    name_text = name_text[:-1]
                name_text += '...'

            text = self.font.render(name_text, False, TEXT_COLOR)
            self.screen.blit(text, (text_x, card_rect.y + 18))

            # Task count with pixelated badge
            task_count = tasks_collection.count_documents(
                {'category_id': category['_id']})
            completed_count = tasks_collection.count_documents({
                'category_id': category['_id'],
                'completed': True
            })

            # Progress badge with badge sprite
            badge_rect = pygame.Rect(
                card_rect.x + 370, card_rect.y + 12, 100, 30)
            badge_color = GREEN_COLOR if completed_count == task_count and task_count > 0 else BLUE_COLOR
            pygame.draw.rect(self.screen, badge_color, badge_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, badge_rect, 3)

            count_text = self.small_font.render(
                f'{completed_count}/{task_count}',
                False,
                WHITE_COLOR
            )
            count_rect = count_text.get_rect(center=badge_rect.center)
            self.screen.blit(count_text, count_rect)

            # Edit button
            pygame.draw.rect(self.screen, BLUE_COLOR, edit_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, edit_btn_rect, 3)
            edit_text = self.small_font.render('E', False, WHITE_COLOR)
            edit_text_rect = edit_text.get_rect(center=edit_btn_rect.center)
            self.screen.blit(edit_text, edit_text_rect)

            # Delete button with X
            pygame.draw.rect(self.screen, RED_COLOR, delete_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, delete_btn_rect, 3)
            delete_text = self.font.render('X', False, WHITE_COLOR)
            delete_text_rect = delete_text.get_rect(
                center=delete_btn_rect.center)
            self.screen.blit(delete_text, delete_text_rect)

            y_offset += 65

        # Input box and button
        self.category_input.draw(self.screen, self.small_font)
        self.add_category_button.draw(self.screen, self.small_font)

    def draw_tasks_view(self):
        """Draw the tasks view for a specific category"""
        # Back button
        self.back_button.draw(self.screen, self.small_font)

        # Pikachu sprite in corner
        if self.pikachu_sprite:
            self.screen.blit(self.pikachu_sprite, (10, 540))

        # Title box with retro style
        title_box_rect = pygame.Rect(180, 20, 440, 100)
        PixelBox.draw(self.screen, title_box_rect, BLUE_COLOR, 6)

        # Category name (truncated)
        title_text = self.selected_category_name[:18]
        title = self.title_font.render(title_text, False, WHITE_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Subtitle with count
        total_tasks = len(self.tasks)
        subtitle_text = f'TASKS ({total_tasks})'
        subtitle = self.small_font.render(subtitle_text, False, WHITE_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(subtitle, subtitle_rect)

        # Draw scrollbar if there are more items than can fit
        if total_tasks > self.items_per_page:
            scrollbar_x = 748
            scrollbar_y = 155
            scrollbar_width = 10
            scrollbar_height = 315  # Total scrollable area height
            
            # Scrollbar track
            track_rect = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
            pygame.draw.rect(self.screen, SHADOW_COLOR, track_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, track_rect, 2)
            
            # Scrollbar thumb
            thumb_height = max(30, int(scrollbar_height * self.items_per_page / total_tasks))
            max_scroll = total_tasks - self.items_per_page
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * (self.task_scroll / max_scroll)) if max_scroll > 0 else scrollbar_y
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(self.screen, BLUE_COLOR, thumb_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, thumb_rect, 2)

        # Scroll indicators
        if self.task_scroll > 0:
            # Up arrow
            up_text = self.font.render('^', False, TEXT_COLOR)
            self.screen.blit(up_text, (750, 135))

        if self.task_scroll + self.items_per_page < total_tasks:
            # Down arrow
            down_text = self.font.render('v', False, TEXT_COLOR)
            self.screen.blit(down_text, (750, 485))

        # Draw tasks with scrolling
        y_offset = 140
        start_idx = self.task_scroll
        end_idx = min(start_idx + self.items_per_page, total_tasks)

        for i in range(start_idx, end_idx):
            task = self.tasks[i]
            # Task card
            card_rect = pygame.Rect(80, y_offset, 640, 55)

            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            edit_btn_rect = pygame.Rect(
                card_rect.right - 105, card_rect.y + 10, 45, 35)
            delete_btn_rect = pygame.Rect(
                card_rect.right - 55, card_rect.y + 10, 45, 35)
            is_hovered = card_rect.collidepoint(mouse_pos) and not delete_btn_rect.collidepoint(
                mouse_pos) and not edit_btn_rect.collidepoint(mouse_pos)

            # Draw card with pixel box
            if task['completed']:
                card_color = (200, 240, 200) if is_hovered else (180, 230, 180)
            else:
                card_color = (255, 255, 200) if is_hovered else WHITE_COLOR

            PixelBox.draw(self.screen, card_rect, card_color, 4)

            # Checkbox (thick pixel borders)
            checkbox_rect = pygame.Rect(
                card_rect.x + 15, card_rect.y + 15, 28, 28)
            pygame.draw.rect(self.screen, WHITE_COLOR, checkbox_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, checkbox_rect, 4)

            # Checkmark if completed (pixelated checkmark)
            if task['completed']:
                # Draw thick pixel checkmark
                pygame.draw.line(self.screen, GREEN_COLOR,
                                 (checkbox_rect.x + 6, checkbox_rect.y + 14),
                                 (checkbox_rect.x + 11, checkbox_rect.y + 20), 5)
                pygame.draw.line(self.screen, GREEN_COLOR,
                                 (checkbox_rect.x + 11, checkbox_rect.y + 20),
                                 (checkbox_rect.x + 22, checkbox_rect.y + 6), 5)

            # Task name with smart truncation
            task_name = task['name']
            max_text_width = 460  # Space before buttons
            text_color = (100, 100, 100) if task['completed'] else TEXT_COLOR

            # Try to fit the full text, if not truncate with ...
            test_surface = self.font.render(task_name, False, text_color)
            if test_surface.get_width() > max_text_width:
                # Truncate and add ...
                while len(task_name) > 0 and self.font.render(task_name + '...', False, text_color).get_width() > max_text_width:
                    task_name = task_name[:-1]
                task_name += '...'

            name_text = self.font.render(task_name, False, text_color)
            self.screen.blit(name_text, (card_rect.x + 60, card_rect.y + 18))

            # Edit button
            pygame.draw.rect(self.screen, BLUE_COLOR, edit_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, edit_btn_rect, 3)
            edit_text = self.small_font.render('E', False, WHITE_COLOR)
            edit_text_rect = edit_text.get_rect(center=edit_btn_rect.center)
            self.screen.blit(edit_text, edit_text_rect)

            # Delete button
            pygame.draw.rect(self.screen, RED_COLOR, delete_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, delete_btn_rect, 3)
            delete_text = self.font.render('X', False, WHITE_COLOR)
            delete_text_rect = delete_text.get_rect(
                center=delete_btn_rect.center)
            self.screen.blit(delete_text, delete_text_rect)

            y_offset += 65

        # Input box and button
        self.task_input.draw(self.screen, self.small_font)
        self.add_task_button.draw(self.screen, self.small_font)

    def handle_categories_click(self, pos):
        """Handle clicks in categories view"""
        # Check add button
        if self.add_category_button.is_clicked(pos):
            text = self.category_input.get_text()
            if text.strip():
                self.add_category(text)
                self.category_input.clear()
            return

        # Check category cards with scroll offset
        y_offset = 140
        start_idx = self.category_scroll
        end_idx = min(start_idx + self.items_per_page, len(self.categories))

        for i in range(start_idx, end_idx):
            category = self.categories[i]
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            edit_btn_rect = pygame.Rect(
                card_rect.right - 105, card_rect.y + 10, 45, 35)
            delete_btn_rect = pygame.Rect(
                card_rect.right - 55, card_rect.y + 10, 45, 35)

            if edit_btn_rect.collidepoint(pos):
                # Show confirmation for editing
                self.confirming_action = {
                    'action': 'edit_category',
                    'data': {'id': category['_id'], 'name': category['name']}
                }
                return

            if delete_btn_rect.collidepoint(pos):
                # Show confirmation for deleting
                self.confirming_action = {
                    'action': 'delete_category',
                    'data': {'id': category['_id'], 'name': category['name']}
                }
                return

            if card_rect.collidepoint(pos):
                self.current_view = 'tasks'
                self.selected_category_id = category['_id']
                self.selected_category_name = category['name']
                self.load_tasks(category['_id'])
                self.task_scroll = 0  # Reset task scroll
                return

            y_offset += 65

    def handle_tasks_click(self, pos):
        """Handle clicks in tasks view"""
        # Check back button
        if self.back_button.is_clicked(pos):
            self.current_view = 'categories'
            self.selected_category_id = None
            self.task_input.clear()
            self.category_scroll = 0  # Reset category scroll
            return

        # Check add button
        if self.add_task_button.is_clicked(pos):
            text = self.task_input.get_text()
            if text.strip():
                self.add_task(self.selected_category_id, text)
                self.task_input.clear()
            return

        # Check task cards with scroll offset
        y_offset = 140
        start_idx = self.task_scroll
        end_idx = min(start_idx + self.items_per_page, len(self.tasks))

        for i in range(start_idx, end_idx):
            task = self.tasks[i]
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            checkbox_rect = pygame.Rect(
                card_rect.x + 15, card_rect.y + 15, 28, 28)
            edit_btn_rect = pygame.Rect(
                card_rect.right - 105, card_rect.y + 10, 45, 35)
            delete_btn_rect = pygame.Rect(
                card_rect.right - 55, card_rect.y + 10, 45, 35)

            if edit_btn_rect.collidepoint(pos):
                # Show confirmation for editing
                self.confirming_action = {
                    'action': 'edit_task',
                    'data': {'id': task['_id'], 'name': task['name']}
                }
                return

            if delete_btn_rect.collidepoint(pos):
                # Show confirmation for deleting
                self.confirming_action = {
                    'action': 'delete_task',
                    'data': {'id': task['_id'], 'name': task['name']}
                }
                return

            if checkbox_rect.collidepoint(pos):
                # Toggle task directly without confirmation when clicking checkbox
                self.toggle_task(task['_id'])
                return

            y_offset += 65

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle mouse wheel scrolling
                if event.type == pygame.MOUSEWHEEL and not self.editing_item and not self.confirming_action:
                    if self.current_view == 'categories':
                        max_scroll = max(
                            0, len(self.categories) - self.items_per_page)
                        self.category_scroll = max(
                            0, min(max_scroll, self.category_scroll - event.y))
                    else:
                        max_scroll = max(0, len(self.tasks) -
                                         self.items_per_page)
                        self.task_scroll = max(
                            0, min(max_scroll, self.task_scroll - event.y))

                # Handle confirmation mode
                if self.confirming_action:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Yes button
                        yes_btn_rect = pygame.Rect(250, 340, 120, 50)
                        # No button
                        no_btn_rect = pygame.Rect(430, 340, 120, 50)

                        if yes_btn_rect.collidepoint(event.pos):
                            # Execute the action
                            action = self.confirming_action['action']
                            data = self.confirming_action['data']

                            if action == 'delete_category':
                                self.delete_category(data['id'])
                                # Adjust scroll if needed
                                if self.category_scroll >= len(self.categories):
                                    self.category_scroll = max(
                                        0, len(self.categories) - self.items_per_page)
                            elif action == 'delete_task':
                                self.delete_task(data['id'])
                                # Adjust scroll if needed
                                if self.task_scroll >= len(self.tasks):
                                    self.task_scroll = max(
                                        0, len(self.tasks) - self.items_per_page)
                            elif action == 'edit_category':
                                # Start editing
                                self.editing_item = {
                                    'type': 'category', 'id': data['id'], 'name': data['name']}
                                self.edit_input.text = data['name']
                                self.edit_input.cursor_position = len(
                                    data['name'])
                            elif action == 'edit_task':
                                # Start editing
                                self.editing_item = {
                                    'type': 'task', 'id': data['id'], 'name': data['name']}
                                self.edit_input.text = data['name']
                                self.edit_input.cursor_position = len(
                                    data['name'])
                            elif action == 'toggle_task':
                                self.toggle_task(data['id'])

                            self.confirming_action = None
                        elif no_btn_rect.collidepoint(event.pos) or not pygame.Rect(200, 230, 400, 180).collidepoint(event.pos):
                            # Cancel action
                            self.confirming_action = None
                    continue

                # Handle edit mode
                if self.editing_item:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Cancel edit if clicked outside
                        if not self.edit_input.rect.collidepoint(event.pos):
                            self.editing_item = None

                    # Handle edit input
                    if self.edit_input.handle_event(event):
                        # Enter pressed - save edit
                        new_name = self.edit_input.get_text()
                        if new_name.strip():
                            if self.editing_item['type'] == 'category':
                                self.update_category(
                                    self.editing_item['id'], new_name)
                            else:
                                self.update_task(
                                    self.editing_item['id'], new_name)
                        self.editing_item = None
                        self.edit_input.clear()
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_view == 'categories':
                        self.handle_categories_click(event.pos)
                    else:
                        self.handle_tasks_click(event.pos)

                # Handle input boxes - properly check for Enter key
                if self.current_view == 'categories':
                    if self.category_input.handle_event(event):
                        # Enter was pressed
                        text = self.category_input.get_text()
                        if text.strip():
                            self.add_category(text)
                            self.category_input.clear()
                else:
                    if self.task_input.handle_event(event):
                        # Enter was pressed
                        text = self.task_input.get_text()
                        if text.strip():
                            self.add_task(self.selected_category_id, text)
                            self.task_input.clear()

            # Update input boxes for cursor animation
            if self.editing_item:
                self.edit_input.update()
            elif self.current_view == 'categories':
                self.category_input.update()
            else:
                self.task_input.update()

            # Handle hover effects
            mouse_pos = pygame.mouse.get_pos()
            self.back_button.check_hover(mouse_pos)
            self.add_category_button.check_hover(mouse_pos)
            self.add_task_button.check_hover(mouse_pos)

            # Draw
            self.screen.fill(BG_COLOR)

            if self.current_view == 'categories':
                self.draw_categories_view()
            else:
                self.draw_tasks_view()

            # Draw confirmation dialog if confirming
            if self.confirming_action:
                # Dim background
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                # Confirmation dialog box
                dialog_rect = pygame.Rect(200, 230, 400, 180)
                PixelBox.draw(self.screen, dialog_rect, WHITE_COLOR, 6)

                # Title and message based on action
                action = self.confirming_action['action']
                data = self.confirming_action['data']

                if action == 'delete_category':
                    title_text = 'DELETE GOAL?'
                    msg_text = 'ALL TASKS WILL BE LOST'
                elif action == 'delete_task':
                    title_text = 'DELETE TASK?'
                    msg_text = 'THIS CANNOT BE UNDONE'
                elif action == 'edit_category':
                    title_text = 'EDIT GOAL?'
                    msg_text = 'CHANGE GOAL NAME'
                elif action == 'edit_task':
                    title_text = 'EDIT TASK?'
                    msg_text = 'CHANGE TASK NAME'
                elif action == 'toggle_task':
                    if data['completed']:
                        title_text = 'MARK INCOMPLETE?'
                        msg_text = 'UNDO COMPLETION'
                    else:
                        title_text = 'MARK COMPLETE?'
                        msg_text = 'FINISH THIS TASK'

                # Draw title
                title = self.font.render(title_text, False, TEXT_COLOR)
                title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 260))
                self.screen.blit(title, title_rect)

                # Draw message
                msg = self.small_font.render(msg_text, False, (100, 100, 100))
                msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, 300))
                self.screen.blit(msg, msg_rect)

                # Yes button
                yes_btn = Button(250, 340, 120, 50, 'YES',
                                 GREEN_COLOR, WHITE_COLOR)
                yes_btn.check_hover(pygame.mouse.get_pos())
                yes_btn.draw(self.screen, self.small_font)

                # No button
                no_btn = Button(430, 340, 120, 50, 'NO',
                                RED_COLOR, WHITE_COLOR)
                no_btn.check_hover(pygame.mouse.get_pos())
                no_btn.draw(self.screen, self.small_font)

            # Draw edit dialog if editing
            elif self.editing_item:
                # Dim background
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                # Edit dialog box
                dialog_rect = pygame.Rect(150, 250, 500, 150)
                PixelBox.draw(self.screen, dialog_rect, WHITE_COLOR, 6)

                # Title
                title_text = 'EDIT ' + self.editing_item['type'].upper()
                title = self.font.render(title_text, False, TEXT_COLOR)
                title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 280))
                self.screen.blit(title, title_rect)

                # Input box
                self.edit_input.draw(self.screen, self.small_font)

                # Instructions
                hint = self.small_font.render(
                    'PRESS ENTER TO SAVE', False, (100, 100, 100))
                hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 370))
                self.screen.blit(hint, hint_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        # Cleanup
        pygame.quit()
        client.close()
        sys.exit()


if __name__ == '__main__':
    app = TodoApp()
    app.run()
