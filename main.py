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
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
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
        color = tuple(min(c + 20, 255) for c in self.color) if self.hovered else self.color
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
    def __init__(self, x, y, width, height, placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                if len(self.text) < 30:
                    self.text += event.unicode
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
        
        # Draw text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = TEXT_COLOR if self.text else (120, 120, 120)
        text_surface = font.render(display_text, False, text_color)
        screen.blit(text_surface, (self.rect.x + 12, self.rect.y + 12))
        
        # Draw blinking cursor
        if self.active and self.cursor_visible and self.text:
            cursor_x = self.rect.x + 12 + font.size(self.text)[0] + 4
            cursor_y = self.rect.y + 10
            pygame.draw.rect(screen, TEXT_COLOR, (cursor_x, cursor_y, 3, 20))
        
    def get_text(self):
        return self.text
        
    def clear(self):
        self.text = ''


class TodoApp:
    """Main application class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hakim Todo List")
        self.clock = pygame.time.Clock()
        
        # Load pixel font
        font_path = os.path.join(os.path.dirname(__file__), 'PressStart2P-Regular.ttf')
        try:
            self.title_font = pygame.font.Font(font_path, 24)
            self.font = pygame.font.Font(font_path, 14)
            self.small_font = pygame.font.Font(font_path, 10)
        except:
            print("Pixel font not found, using default...")
            self.title_font = pygame.font.Font(None, 36)
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        
        # App state
        self.current_view = 'categories'  # 'categories' or 'tasks'
        self.selected_category_id = None
        self.selected_category_name = ''
        
        # Input boxes
        self.category_input = InputBox(150, 510, 400, 50, 'New Goal...')
        self.task_input = InputBox(150, 510, 400, 50, 'New Task...')
        
        # Buttons
        self.back_button = Button(20, 20, 140, 50, '<- BACK', BLUE_COLOR, WHITE_COLOR)
        self.add_category_button = Button(570, 510, 180, 50, '+ ADD', GREEN_COLOR, WHITE_COLOR)
        self.add_task_button = Button(570, 510, 180, 50, '+ ADD', GREEN_COLOR, WHITE_COLOR)
        
        # Load data
        self.categories = []
        self.tasks = []
        self.load_categories()
        
    def load_categories(self):
        """Load categories from database"""
        self.categories = list(categories_collection.find().sort('created_at', -1))
        
    def load_tasks(self, category_id):
        """Load tasks for a specific category"""
        self.tasks = list(tasks_collection.find({'category_id': category_id}).sort('created_at', 1))
        
    def add_category(self, name):
        """Add a new category"""
        if name.strip():
            category = {
                'name': name,
                'created_at': datetime.now()
            }
            categories_collection.insert_one(category)
            self.load_categories()
            
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
        # Title box with retro style
        title_box_rect = pygame.Rect(50, 20, 700, 100)
        PixelBox.draw(self.screen, title_box_rect, ACCENT_COLOR, 6)
        
        # Title text
        title = self.title_font.render('POKEMON TODO', False, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render('SELECT A GOAL', False, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw categories
        y_offset = 140
        for i, category in enumerate(self.categories[:6]):  # Show up to 6 categories
            # Category card with thick pixel borders
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            delete_btn_rect = pygame.Rect(card_rect.right - 55, card_rect.y + 10, 45, 35)
            is_hovered = card_rect.collidepoint(mouse_pos) and not delete_btn_rect.collidepoint(mouse_pos)
            
            # Draw card with pixel box
            card_color = (255, 255, 200) if is_hovered else WHITE_COLOR
            PixelBox.draw(self.screen, card_rect, card_color, 4)
            
            # Category name (truncate if too long)
            name_text = category['name'][:25]
            text = self.font.render(name_text, False, TEXT_COLOR)
            self.screen.blit(text, (card_rect.x + 15, card_rect.y + 18))
            
            # Task count with pixelated badge
            task_count = tasks_collection.count_documents({'category_id': category['_id']})
            completed_count = tasks_collection.count_documents({
                'category_id': category['_id'],
                'completed': True
            })
            
            # Progress badge
            badge_rect = pygame.Rect(card_rect.x + 420, card_rect.y + 12, 120, 30)
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
            
            # Delete button with X
            pygame.draw.rect(self.screen, RED_COLOR, delete_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, delete_btn_rect, 3)
            delete_text = self.font.render('X', False, WHITE_COLOR)
            delete_text_rect = delete_text.get_rect(center=delete_btn_rect.center)
            self.screen.blit(delete_text, delete_text_rect)
            
            y_offset += 65
            
        # Input box and button
        self.category_input.draw(self.screen, self.small_font)
        self.add_category_button.draw(self.screen, self.small_font)
        
    def draw_tasks_view(self):
        """Draw the tasks view for a specific category"""
        # Back button
        self.back_button.draw(self.screen, self.small_font)
        
        # Title box with retro style
        title_box_rect = pygame.Rect(180, 20, 440, 100)
        PixelBox.draw(self.screen, title_box_rect, BLUE_COLOR, 6)
        
        # Category name (truncated)
        title_text = self.selected_category_name[:18]
        title = self.title_font.render(title_text, False, WHITE_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.small_font.render('TASK LIST', False, WHITE_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Draw tasks
        y_offset = 140
        for i, task in enumerate(self.tasks[:6]):  # Show up to 6 tasks
            # Task card
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            delete_btn_rect = pygame.Rect(card_rect.right - 55, card_rect.y + 10, 45, 35)
            is_hovered = card_rect.collidepoint(mouse_pos) and not delete_btn_rect.collidepoint(mouse_pos)
            
            # Draw card with pixel box
            if task['completed']:
                card_color = (200, 240, 200) if is_hovered else (180, 230, 180)
            else:
                card_color = (255, 255, 200) if is_hovered else WHITE_COLOR
            
            PixelBox.draw(self.screen, card_rect, card_color, 4)
            
            # Checkbox (thick pixel borders)
            checkbox_rect = pygame.Rect(card_rect.x + 15, card_rect.y + 15, 28, 28)
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
            
            # Task name (truncate if too long)
            task_name = task['name'][:30]
            text_color = (100, 100, 100) if task['completed'] else TEXT_COLOR
            name_text = self.font.render(task_name, False, text_color)
            self.screen.blit(name_text, (card_rect.x + 60, card_rect.y + 18))
            
            # Delete button
            pygame.draw.rect(self.screen, RED_COLOR, delete_btn_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, delete_btn_rect, 3)
            delete_text = self.font.render('X', False, WHITE_COLOR)
            delete_text_rect = delete_text.get_rect(center=delete_btn_rect.center)
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
            
        # Check category cards
        y_offset = 140
        for i, category in enumerate(self.categories[:6]):
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            delete_btn_rect = pygame.Rect(card_rect.right - 55, card_rect.y + 10, 45, 35)
            
            if delete_btn_rect.collidepoint(pos):
                self.delete_category(category['_id'])
                return
                
            if card_rect.collidepoint(pos):
                self.current_view = 'tasks'
                self.selected_category_id = category['_id']
                self.selected_category_name = category['name']
                self.load_tasks(category['_id'])
                return
                
            y_offset += 65
            
    def handle_tasks_click(self, pos):
        """Handle clicks in tasks view"""
        # Check back button
        if self.back_button.is_clicked(pos):
            self.current_view = 'categories'
            self.selected_category_id = None
            self.task_input.clear()
            return
            
        # Check add button
        if self.add_task_button.is_clicked(pos):
            text = self.task_input.get_text()
            if text.strip():
                self.add_task(self.selected_category_id, text)
                self.task_input.clear()
            return
            
        # Check task cards
        y_offset = 140
        for i, task in enumerate(self.tasks[:6]):
            card_rect = pygame.Rect(80, y_offset, 640, 55)
            checkbox_rect = pygame.Rect(card_rect.x + 15, card_rect.y + 15, 28, 28)
            delete_btn_rect = pygame.Rect(card_rect.right - 55, card_rect.y + 10, 45, 35)
            
            if delete_btn_rect.collidepoint(pos):
                self.delete_task(task['_id'])
                return
                
            if checkbox_rect.collidepoint(pos) or card_rect.collidepoint(pos):
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
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_view == 'categories':
                        self.handle_categories_click(event.pos)
                    else:
                        self.handle_tasks_click(event.pos)
                        
                # Handle input boxes
                if self.current_view == 'categories':
                    if self.category_input.handle_event(event):
                        text = self.category_input.get_text()
                        if text.strip():
                            self.add_category(text)
                            self.category_input.clear()
                else:
                    if self.task_input.handle_event(event):
                        text = self.task_input.get_text()
                        if text.strip():
                            self.add_task(self.selected_category_id, text)
                            self.task_input.clear()
            
            # Update input boxes for cursor animation
            if self.current_view == 'categories':
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
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        # Cleanup
        pygame.quit()
        client.close()
        sys.exit()


if __name__ == '__main__':
    app = TodoApp()
    app.run()
