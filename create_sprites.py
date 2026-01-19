"""
Create pixelated Pokemon-style character sprites
"""
import pygame
import os

pygame.init()

def create_pikachu_sprite():
    """Create a simple Pikachu sprite"""
    size = 48
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Colors
    yellow = (255, 220, 0)
    dark_yellow = (230, 180, 0)
    black = (48, 48, 48)
    red = (255, 80, 80)
    white = (255, 255, 255)
    
    # Body (simplified pixel art)
    # Head circle
    for x in range(16, 32):
        for y in range(8, 28):
            if (x - 24) ** 2 + (y - 18) ** 2 < 100:
                sprite.set_at((x, y), yellow)
    
    # Ears
    pygame.draw.polygon(sprite, yellow, [(18, 8), (22, 8), (20, 2)])
    pygame.draw.polygon(sprite, yellow, [(26, 8), (30, 8), (28, 2)])
    pygame.draw.polygon(sprite, black, [(19, 2), (21, 2), (20, 0)])
    pygame.draw.polygon(sprite, black, [(27, 2), (29, 2), (28, 0)])
    
    # Eyes
    pygame.draw.circle(sprite, black, (20, 16), 2)
    pygame.draw.circle(sprite, black, (28, 16), 2)
    
    # Cheeks
    pygame.draw.circle(sprite, red, (16, 20), 3)
    pygame.draw.circle(sprite, red, (32, 20), 3)
    
    # Body
    for x in range(18, 30):
        for y in range(26, 40):
            sprite.set_at((x, y), yellow)
    
    # Arms
    for y in range(28, 34):
        sprite.set_at((15, y), yellow)
        sprite.set_at((32, y), yellow)
    
    # Tail (simplified)
    pygame.draw.line(sprite, dark_yellow, (30, 28), (36, 22), 3)
    pygame.draw.line(sprite, dark_yellow, (36, 22), (42, 18), 3)
    
    return sprite

def create_pokeball_sprite():
    """Create a pokeball sprite"""
    size = 32
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Colors
    red = (216, 80, 80)
    white = (248, 248, 248)
    black = (48, 48, 48)
    gray = (120, 120, 120)
    
    # Draw pokeball
    center_x, center_y = 16, 16
    
    # Top half (red)
    for x in range(6, 26):
        for y in range(6, 16):
            if (x - center_x) ** 2 + (y - center_y) ** 2 < 100:
                sprite.set_at((x, y), red)
    
    # Bottom half (white)
    for x in range(6, 26):
        for y in range(16, 26):
            if (x - center_x) ** 2 + (y - center_y) ** 2 < 100:
                sprite.set_at((x, y), white)
    
    # Middle line (black)
    pygame.draw.line(sprite, black, (6, 16), (26, 16), 2)
    
    # Center button
    pygame.draw.circle(sprite, white, (16, 16), 5)
    pygame.draw.circle(sprite, black, (16, 16), 5, 2)
    pygame.draw.circle(sprite, gray, (16, 16), 3)
    
    # Outer circle
    pygame.draw.circle(sprite, black, (16, 16), 10, 2)
    
    return sprite

def create_badge_sprite():
    """Create a Pokemon badge sprite"""
    size = 32
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Colors
    gold = (255, 203, 5)
    orange = (255, 140, 0)
    black = (48, 48, 48)
    
    # Star shape (simplified)
    points = [
        (16, 4),
        (19, 13),
        (28, 13),
        (21, 19),
        (24, 28),
        (16, 22),
        (8, 28),
        (11, 19),
        (4, 13),
        (13, 13)
    ]
    
    pygame.draw.polygon(sprite, gold, points)
    pygame.draw.polygon(sprite, black, points, 2)
    
    # Center circle
    pygame.draw.circle(sprite, orange, (16, 16), 4)
    pygame.draw.circle(sprite, black, (16, 16), 4, 1)
    
    return sprite

def create_checkbox_sprite():
    """Create a pixelated checkbox"""
    size = 28
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    white = (248, 248, 248)
    black = (48, 48, 48)
    
    # Draw box
    pygame.draw.rect(sprite, white, (0, 0, size, size))
    pygame.draw.rect(sprite, black, (0, 0, size, size), 4)
    
    return sprite

def create_checked_sprite():
    """Create a pixelated checked checkbox"""
    size = 28
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    white = (248, 248, 248)
    black = (48, 48, 48)
    green = (104, 176, 88)
    
    # Draw box
    pygame.draw.rect(sprite, white, (0, 0, size, size))
    pygame.draw.rect(sprite, black, (0, 0, size, size), 4)
    
    # Draw checkmark
    pygame.draw.line(sprite, green, (6, 14), (11, 20), 5)
    pygame.draw.line(sprite, green, (11, 20), (22, 6), 5)
    
    return sprite

# Create sprites directory
if not os.path.exists('sprites'):
    os.makedirs('sprites')

# Save sprites
pikachu = create_pikachu_sprite()
pygame.image.save(pikachu, 'sprites/pikachu.png')

pokeball = create_pokeball_sprite()
pygame.image.save(pokeball, 'sprites/pokeball.png')

badge = create_badge_sprite()
pygame.image.save(badge, 'sprites/badge.png')

checkbox = create_checkbox_sprite()
pygame.image.save(checkbox, 'sprites/checkbox.png')

checked = create_checked_sprite()
pygame.image.save(checked, 'sprites/checked.png')

print("✓ Created Pokemon sprites!")
print("  - pikachu.png")
print("  - pokeball.png")
print("  - badge.png")
print("  - checkbox.png")
print("  - checked.png")

pygame.quit()
