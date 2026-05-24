import pygame
import os
import sys
import random

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()

# 1. Setup Widescreen Game Window
is_fullscreen = False
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED, vsync=1)
pygame.display.set_caption("Brick Blasters!")
running = True

# --- FONT LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = resource_path("WorkSans-Regular.ttf")

if os.path.exists(FONT_PATH):
    font_title = pygame.font.Font(FONT_PATH, 64)
    font_sub = pygame.font.Font(FONT_PATH, 24)
    font_body = pygame.font.Font(FONT_PATH, 20)
else:
    # Fallback to system font if for some reason the file wasn't bundled
    font_title = pygame.font.SysFont("Arial", 64, bold=True)
    font_sub = pygame.font.SysFont("Arial", 24, bold=True)
    font_body = pygame.font.SysFont("Arial", 20)

# --- TEXT WRAPPER FUNCTION ---
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] < max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

# --- GAME SETUP ---
STATE_TITLE = 0
STATE_PLAYING = 1
game_state = STATE_TITLE  

show_message_bad = False
show_message_good = False

# Helper function to reset bricks
def reset_bricks():
    bricks = []
    for row in range(5):
        for col in range(12):
            bricks.append(pygame.Rect(col * 100 + 40, row * 40 + 60, 95, 30))
    return bricks

bricks = reset_bricks()
ball_rect = pygame.Rect(640, 450, 24, 24)
speed_x, speed_y = 7, -7
paddle_rect = pygame.Rect(540, 660, 200, 20)
paddle_speed = 12
flash_timer = 0.0          
flash_speed = 0.05         
COLOR_PADDLE_BASE = (255, 255, 255)
COLOR_PADDLE_FLASH = (0, 0, 255)

# --- MAIN LOOP ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # Fullscreen Toggle
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                mode = pygame.SCALED | pygame.FULLSCREEN if is_fullscreen else pygame.SCALED
                screen = pygame.display.set_mode((screen_width, screen_height), mode, vsync=1)
            
            # Start Game
            if game_state == STATE_TITLE and event.key == pygame.K_RETURN:
                game_state = STATE_PLAYING
            
            # --- FIXED: ADDED RESET LOGIC ---
            if game_state == STATE_PLAYING and (show_message_bad or show_message_good):
                if event.key == pygame.K_SPACE:
                    ball_rect.x, ball_rect.y = 640, 450
                    speed_x, speed_y = 7, -7
                    show_message_bad = False
                    show_message_good = False
                    flash_timer = 0.0
                    bricks = reset_bricks()

    # --- PHYSICS ---
    if game_state == STATE_PLAYING and not show_message_bad and not show_message_good:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: paddle_rect.x -= paddle_speed
        if keys[pygame.K_RIGHT]: paddle_rect.x += paddle_speed
        paddle_rect.clamp_ip(screen.get_rect())

        ball_rect.x += speed_x
        ball_rect.y += speed_y
        if ball_rect.left <= 0 or ball_rect.right >= 1280: speed_x *= -1
        if ball_rect.top <= 0: speed_y *= -1
        if ball_rect.bottom >= 720: show_message_bad = True
        
        if ball_rect.colliderect(paddle_rect):
            speed_y *= -1
            speed_x = random.choice([-10, -7, 7, 10])
            flash_timer = 1.0 

        if flash_timer > 0.0:
            flash_timer -= flash_speed
            if flash_timer < 0.0: flash_timer = 0.0
        
        for brick in bricks[:]:
            if ball_rect.colliderect(brick):
                speed_y *= -1
                bricks.remove(brick)
                break
        if not bricks: show_message_good = True

    # --- RENDERING ---
    screen.fill((10, 10, 20))

    if game_state == STATE_TITLE:
        screen.blit(font_title.render("Brick Blasters!", True, (0, 255, 255)), (440, 50))
        box_x, box_y, box_w = 140, 210, 1000
        pygame.draw.rect(screen, (30, 30, 50), (box_x, box_y, box_w, 450), border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255), (box_x, box_y, box_w, 450), width=3, border_radius=15)
        
        y = 240
        for line in wrap_text("How to play (and an extra cool bug I discovered and decided was too fun to keep!)", font_sub, box_w-60):
            screen.blit(font_sub.render(line, True, (255, 255, 255)), (180, y))
            y += 35
        
        y += 20
        controls = ["- Arrow Keys : Move Paddle", "- F11 : Toggle Fullscreen", "- Clear all bricks to win"]
        for c in controls:
            screen.blit(font_body.render(c, True, (200, 200, 200)), (180, y))
            y += 35
            
        y += 30
        screen.blit(font_body.render("Extra Move: 'The Sideswipe'", True, (255, 165, 0)), (180, y))
        y += 35
        desc = "Catch the ball on the sides of the paddle to trigger this cool thing where the ball stays inside the paddle and you can even move the paddle left and right to keep the ball stuck inside!"
        for line in wrap_text(desc, font_body, box_w-60):
            screen.blit(font_body.render(line, True, (255, 255, 255)), (180, y))
            y += 30

    elif game_state == STATE_PLAYING:
        for b in bricks: pygame.draw.rect(screen, (0, 0, 255), b)
        pygame.draw.ellipse(screen, (255, 255, 255), ball_rect)

        # Dynamic Color Math
        r = int((COLOR_PADDLE_FLASH[0] * flash_timer) + (COLOR_PADDLE_BASE[0] * (1.0 - flash_timer)))
        g = int((COLOR_PADDLE_FLASH[1] * flash_timer) + (COLOR_PADDLE_BASE[1] * (1.0 - flash_timer)))
        b = int((COLOR_PADDLE_FLASH[2] * flash_timer) + (COLOR_PADDLE_BASE[2] * (1.0 - flash_timer)))
        pygame.draw.rect(screen, (r, g, b), paddle_rect)

        if show_message_bad: 
            screen.blit(font_sub.render("You lose! Press SPACE to restart", True, (255, 255, 255)), (430, 320))
        elif show_message_good: 
            screen.blit(font_sub.render("Victory! Press SPACE for next round", True, (0, 255, 0)), (410, 320))
            
    pygame.display.update()

pygame.quit()
