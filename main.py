import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import os
import sys
import random
import urllib.request
import re
from cryptography.fernet import Fernet

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

songid = "574484"

# --- NEWGROUNDS DOWNLOADER SUB-SYSTEM ---
def download_newgrounds_audio(songid):
    """Fetches audio directly from the Newgrounds data delivery distribution server."""
    import re
    import urllib.request
    
    # Extract just the numeric ID if a full URL was given
    song_id = "".join(filter(str.isdigit, str(songid)))
    if not song_id:
        print("Invalid Newgrounds Link or ID format.")
        return False
        
    print(f"Requesting direct track download for ID: {song_id}")
    direct_mp3_url = f"https://www.newgrounds.com/audio/download/{song_id}"
    
    try:
        # Request the raw media stream directly
        req = urllib.request.Request(direct_mp3_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        output_filename = resource_path("background.mp3")
        print("Downloading stream payload...")
        
        with urllib.request.urlopen(req) as response, open(output_filename, 'wb') as out_file:
            out_file.write(response.read())
            
        print("Download Complete! Saved to background.mp3")
        return True
    except Exception as e:
        print(f"Network Downloader Exception: {e}")
        return False

# --- PRE-STARTUP MUSIC CHECK ---
# Check if the file exists before initializing the window. 
DEFAULT_SONG_ID = "574484"
TARGET_MUSIC_PATH = resource_path('background.mp3')

if not os.path.exists(TARGET_MUSIC_PATH):
    print(f"background.mp3 not found! Initiating auto-download for default Newgrounds ID: {DEFAULT_SONG_ID}")
    download_newgrounds_audio(DEFAULT_SONG_ID)

pygame.init()
pygame.mixer.init()

# --- WINDOW SETUP ---
is_fullscreen = False
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED, vsync=1)
pygame.display.set_caption("Brick Blasters!")
icon_path = resource_path("icon.png")
if os.path.exists(icon_path):
    icon_surface = pygame.image.load(icon_path)
    pygame.display.set_icon(icon_surface)
else:
    print("Icon file not found!")
clock = pygame.time.Clock()
running = True

# --- SOUND LOADING ---
canPlay = True
canPlayEffects = True
sound_bounce = pygame.mixer.Sound(resource_path('hit-sound.mp3'))
sound_break = pygame.mixer.Sound(resource_path("break.mp3"))

def load_background_music():
    """ Safely loads background track into the music channel if it exists """
    if os.path.exists(TARGET_MUSIC_PATH):
        try:
            pygame.mixer.music.load(TARGET_MUSIC_PATH)
        except Exception as e:
            print(f"Could not load music file: {e}")

load_background_music()

# --- FONT LOADING ---
FONT_PATH = resource_path("WorkSans-Regular.ttf")
if os.path.exists(FONT_PATH):
    font_title = pygame.font.Font(FONT_PATH, 64)
    font_sub = pygame.font.Font(FONT_PATH, 24)
    font_body = pygame.font.Font(FONT_PATH, 20)
else:
    font_title = pygame.font.SysFont("Arial", 64, bold=True)
    font_sub = pygame.font.SysFont("Arial", 24, bold=True)
    font_body = pygame.font.SysFont("Arial", 20)

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

# --- GAME SETUP STATES ---
STATE_TITLE, STATE_PLAYING, STATE_CHOOSING_DIFF, STATE_MUSIC_MENU = 0, 1, 2, 3
game_state = STATE_TITLE  
show_message_bad = False
show_message_good = False

# --- PURE PYGAME SCROLLING TUTORIAL CONFIG ---
box_x, box_y, box_w, box_h = 140, 210, 1000, 410
scroll_y = 0  
content_w = box_w - 40
content_h = 850  
tutorial_canvas = pygame.Surface((content_w, content_h), pygame.SRCALPHA)

def render_tutorial_text():
    tutorial_canvas.fill((0, 0, 0, 0)) # Clean canvas
    y = 20
    
    # Header Description
    for line in wrap_text("How to play (and an extra cool bug I discovered and decided was too fun to keep!)", font_sub, content_w - 60):
        tutorial_canvas.blit(font_sub.render(line, True, (255, 255, 255)), (20, y))
        y += 35
        
    y += 15
    controls = ["- Arrow Keys : Move Paddle", "- F11 : Toggle Fullscreen", "- Blast all the bricks to win!"]
    for c in controls:
        tutorial_canvas.blit(font_body.render(c, True, (200, 200, 200)), (20, y))
        y += 30
        
    # Audio Toggles documentation 
    y += 20
    tutorial_canvas.blit(font_body.render("Audio Toggle Keys:", True, (0, 255, 150)), (20, y))
    y += 30
    audio_controls = ["- Press N : Toggle Sound Effects ON/OFF", "- Press M : Toggle Background Music ON/OFF"]
    for ac in audio_controls:
        tutorial_canvas.blit(font_body.render(ac, True, (200, 200, 200)), (20, y))
        y += 30

    # Impact update instruction
    y += 20
    tutorial_canvas.blit(font_body.render("Warning: Highly Volatile Gold Bricks!", True, (255, 70, 70)), (20, y))
    y += 30
    hazard_desc = "Golden bricks reward you with an instant 2X score multiplier! However, they are highly unstable. The sudden impact force will aggressively reverse the ball's horizontal direction right on contact!"
    for line in wrap_text(hazard_desc, font_body, content_w - 60):
        tutorial_canvas.blit(font_body.render(line, True, (255, 210, 210)), (20, y))
        y += 25
        
    # Bug exploit details
    y += 25
    tutorial_canvas.blit(font_body.render("Signature Feature: 'The Sideswipe'", True, (255, 165, 0)), (20, y))
    y += 30
    desc = "Catch the ball cleanly on either side of the paddle. This will lock the ball inside the paddle frame, allowing you to carry it left and right as long as you move the paddle with the ball. (If you even can!) Be careful though. The ball has a chance of launching itself under the paddle and falling into its demise while using this!"
    for line in wrap_text(desc, font_body, content_w - 60):
        tutorial_canvas.blit(font_body.render(line, True, (255, 255, 255)), (20, y))
        y += 25

render_tutorial_text()
max_scroll = max(0, content_h - box_h)

# --- WIDGET SETUP (FOR STATE_MUSIC_MENU) ---
music_input_box = TextBox(
    screen, 390, 320, 500, 50, fontSize=20,
    borderColour=(0, 255, 255), textColour=(255, 255, 255),
    backgroundColor=(0, 0, 0), radius=10
)
music_input_box.hide() # Keep hidden until custom menu state is active

def on_submit_music():
    user_input = music_input_box.getText()
    if user_input:
        success = download_newgrounds_audio(user_input)
        if success:
            load_background_music()
            if canPlay:
                pygame.mixer.music.play(-1)
            # Return to title screen
            global game_state
            game_state = STATE_TITLE
            music_input_box.hide()
            submit_btn.hide()

submit_btn = Button(
    screen, 540, 400, 200, 50, text='Apply Track',
    fontSize=20, margin=10, inactiveColour=(0, 200, 200),
    hoverColour=(0, 255, 255), pressedColour=(0, 150, 150),
    radius=10, onClick=on_submit_music
)
submit_btn.hide()

def reset_bricks():
    bricks = []
    for row in range(5):
        for col in range(12):
            is_special = random.randint(1, 15) == 1 
            bricks.append({
                "rect": pygame.Rect(col * 100 + 40, row * 40 + 60, 95, 30),
                "special": is_special
            })
    return bricks

bricks = reset_bricks()
ball_rect = pygame.Rect(640, 450, 24, 24)
speed_x, speed_y = 7, -7
paddle_rect = pygame.Rect(540, 660, 200, 20)
paddle_speed = 18
flash_timer = 0.0
flash_speed = 0.05
COLOR_PADDLE_BASE = (255, 255, 255)
COLOR_PADDLE_FLASH = (66, 66, 255)

difficulty_buttons = [
    {"rect": pygame.Rect(440, 200, 400, 80), "label": "Easy", "speed": 7},
    {"rect": pygame.Rect(440, 320, 400, 80), "label": "Medium", "speed": 9},
    {"rect": pygame.Rect(440, 440, 400, 80), "label": "Hard", "speed": 14},
    {"rect": pygame.Rect(440, 560, 400, 80), "label": "Holy", "speed": 17}
]

# --- CRYPTOGRAPHY ---
keyfile = "score.key"
savefile = "score.dat"

def load_or_create_key():
    if not os.path.exists(keyfile):
        key = Fernet.generate_key()
        with open(keyfile, "wb") as key_file:
            key_file.write(key)
        return key
    else:
        with open(keyfile, "rb") as key_file:
            return key_file.read()

secretkey = load_or_create_key()
cipher = Fernet(secretkey)

def save_score(score_to_save):
    encryptedscore = cipher.encrypt(str(score_to_save).encode())
    with open(savefile, "wb") as f:
        f.write(encryptedscore)

def load_high_score():
    if not os.path.exists(savefile):
        return 0
    try:
        with open(savefile, "rb") as f:
            encrypteddata = f.read()
            decrypteddata = cipher.decrypt(encrypteddata)
            return int(decrypteddata.decode())
    except:
        return 0

score = 0
high_score = load_high_score()
multiplier = 1
multiplier_timer = 0
game_speed = 8

# --- MAIN LOOP ---
while running:
    clock.tick(60)
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        # Title Screen Scrolling Event Tracker
        if game_state == STATE_TITLE:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_y = max(0, scroll_y - 25)
                elif event.button == 5:
                    scroll_y = min(max_scroll, scroll_y + 25)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * 25))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                canPlayEffects = not canPlayEffects
                if not canPlayEffects:
                    sound_bounce.stop()
                    
            if event.key == pygame.K_m:
                canPlay = not canPlay
                if not canPlay:
                    pygame.mixer.music.stop()
                elif os.path.exists(TARGET_MUSIC_PATH):
                    pygame.mixer.music.play(-1)
                    
            if event.key == pygame.K_c and game_state == STATE_TITLE:
                game_state = STATE_MUSIC_MENU
                music_input_box.show()
                submit_btn.show()
                
            if event.key == pygame.K_ESCAPE and game_state == STATE_MUSIC_MENU:
                game_state = STATE_TITLE
                music_input_box.hide()
                submit_btn.hide()

            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                mode = pygame.SCALED | pygame.FULLSCREEN if is_fullscreen else pygame.SCALED
                screen = pygame.display.set_mode((screen_width, screen_height), mode, vsync=1)
            
            if game_state == STATE_TITLE and event.key == pygame.K_RETURN:
                game_state = STATE_CHOOSING_DIFF
                if canPlay and os.path.exists(TARGET_MUSIC_PATH):
                    # Play if not already running
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)

            if event.key == pygame.K_ESCAPE and game_state == STATE_CHOOSING_DIFF:
                game_state = STATE_TITLE
            
            if game_state == STATE_PLAYING and show_message_good:
                if event.key == pygame.K_SPACE:
                    ball_rect.center = (640, 450)
                    speed_x, speed_y = game_speed, -game_speed
                    show_message_bad = show_message_good = False
                    flash_timer = 0.0
                    bricks = reset_bricks()
                    multiplier_timer = 0 
            elif game_state == STATE_PLAYING and show_message_bad:
                if event.key == pygame.K_SPACE:
                    ball_rect.center = (640, 450)
                    speed_x, speed_y = game_speed, -game_speed
                    show_message_bad = show_message_good = False
                    flash_timer = 0.0
                    bricks = reset_bricks()
                    score = multiplier_timer = 0           
                if event.key == pygame.K_ESCAPE and game_state == STATE_PLAYING:
                    game_state = STATE_CHOOSING_DIFF
                    
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == STATE_CHOOSING_DIFF:
            mouse_pos = event.pos
            for btn in difficulty_buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    game_speed = btn["speed"]
                    speed_x, speed_y = game_speed, -game_speed
                    game_state = STATE_PLAYING
                    bricks = reset_bricks()
                    score = multiplier_timer = 0
                    multiplier = 1
                    ball_rect.center = (640, 450)
                    show_message_bad = show_message_good = False

    # --- PHYSICS ---
    if game_state == STATE_PLAYING and not show_message_bad and not show_message_good:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: paddle_rect.x -= paddle_speed
        if keys[pygame.K_RIGHT]: paddle_rect.x += paddle_speed
        paddle_rect.clamp_ip(screen.get_rect())

        ball_rect.x += speed_x
        ball_rect.y += speed_y
        
        if ball_rect.left <= 0:
            ball_rect.left = 0
            speed_x *= -1
        elif ball_rect.right >= 1280:
            ball_rect.right = 1280
            speed_x *= -1
            
        if ball_rect.top <= 0:
            ball_rect.top = 0
            speed_y *= -1
            
        if ball_rect.bottom >= 720:
            show_message_bad = True
            if score > high_score:
                high_score = score
                save_score(high_score)
        
        if ball_rect.colliderect(paddle_rect):
            if speed_y > 0:
                ball_rect.bottom = paddle_rect.top
                speed_x = random.choice([-10, -7, 7, 10])
                speed_y *= -1
                flash_timer = 1.0
                if canPlayEffects:
                    sound_bounce.play()

        for brick in bricks[:]:
            if ball_rect.colliderect(brick["rect"]):
                overlap_left = ball_rect.right - brick["rect"].left
                overlap_right = brick["rect"].right - ball_rect.left
                overlap_top = ball_rect.bottom - brick["rect"].top
                overlap_bottom = brick["rect"].bottom - ball_rect.top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_top or min_overlap == overlap_bottom:
                    speed_y *= -1
                else:
                    speed_x *= -1
                    
                if brick["special"]:
                    multiplier = 2
                    multiplier_timer = 600
                    speed_x *= -1
                
                score += (5 * multiplier)
                bricks.remove(brick)
                sound_break.play()
                break
                
        if not bricks:
            show_message_good = True
            if score > high_score:
                high_score = score
                save_score(high_score)

    if multiplier_timer > 0:
        multiplier_timer -= 1
    else:
        multiplier = 1

    # --- RENDERING ---
    screen.fill((10, 10, 20))

    if game_state == STATE_TITLE:
        screen.blit(font_title.render("Brick Blasters!", True, (0, 255, 255)), (440, 40))
        screen.blit(font_sub.render("V1.3", True, (0, 0, 255)), (610, 150))
        
        # Scrolled Layout Area Viewport
        pygame.draw.rect(screen, (30, 30, 50), (box_x, box_y, box_w, box_h), border_radius=15)
        view_clip_rect = pygame.Rect(box_x + 10, box_y + 10, box_w - 20, box_h - 20)
        screen.set_clip(view_clip_rect)
        screen.blit(tutorial_canvas, (box_x + 10, box_y + 10 - scroll_y))
        screen.set_clip(None)
        
        pygame.draw.rect(screen, (0, 255, 255), (box_x, box_y, box_w, box_h), width=3, border_radius=15)
        if max_scroll > 0:
            track_h = box_h - 40
            bar_h = max(20, int(track_h * (box_h / content_h)))
            bar_y = box_y + 20 + int((track_h - bar_h) * (scroll_y / max_scroll))
            pygame.draw.rect(screen, (0, 255, 255), (box_x + box_w - 18, bar_y, 8, bar_h), border_radius=4)
            
        screen.blit(font_body.render("Press ENTER to Play  |  Press C for Custom Music Downloader", True, (0, 255, 255)), (380, 650))

    elif game_state == STATE_MUSIC_MENU:
        screen.blit(font_title.render("Custom Music Downloader", True, (0, 255, 255)), (280, 100))
        label_txt = "Enter Newgrounds Audio URL or Track ID number:"
        screen.blit(font_sub.render(label_txt, True, (255, 255, 255)), (390, 260))
        screen.blit(font_body.render("Press ESC to return to main menu", True, (150, 150, 150)), (500, 500))
        
        # Let widgets process inputs and render themselves
        pygame_widgets.update(events)

    elif game_state == STATE_PLAYING:
        for b in bricks: 
            color = (255, 215, 0) if b["special"] else (0, 0, 255)
            pygame.draw.rect(screen, color, b["rect"])
            
        pygame.draw.ellipse(screen, (255, 255, 255), ball_rect)

        score_text = font_body.render(f"Score: {score}", True, (255, 255, 255))
        if multiplier > 1:
            mult_text = font_body.render(f"2X MULTIPLIER ACTIVE!", True, (255, 215, 0))
            screen.blit(mult_text, (10, 70))
        high_score_text = font_body.render(f"High Score: {high_score}", True, (255, 255, 0))

        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

        if flash_timer > 0.0:
            flash_timer -= flash_speed
            if flash_timer < 0.0: flash_timer = 0.0

        r = int((COLOR_PADDLE_FLASH[0] * flash_timer) + (COLOR_PADDLE_BASE[0] * (1.0 - flash_timer)))
        g = int((COLOR_PADDLE_FLASH[1] * flash_timer) + (COLOR_PADDLE_BASE[1] * (1.0 - flash_timer)))
        b = int((COLOR_PADDLE_FLASH[2] * flash_timer) + (COLOR_PADDLE_BASE[2] * (1.0 - flash_timer)))
        pygame.draw.rect(screen, (r, g, b), paddle_rect)

        if show_message_bad: 
            screen.blit(font_sub.render("You lose! Press SPACE to restart or press ESCAPE to choose a different difficulty.", True, (255, 0, 0)), (250, 320))
        elif show_message_good: 
            screen.blit(font_sub.render("You win! Press SPACE to start a new round or press ESCAPE to choose a different difficulty.", True, (0, 255, 0)), (250, 320))

    elif game_state == STATE_CHOOSING_DIFF:
        mouse_pos = pygame.mouse.get_pos()
        for btn in difficulty_buttons:
            is_hovered = btn["rect"].collidepoint(mouse_pos)
            color = (100, 100, 100) if is_hovered else (50, 50, 50)
            
            pygame.draw.rect(screen, color, btn["rect"], border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), btn["rect"], width=3, border_radius=15)
            
            text_surf = font_sub.render(btn["label"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            screen.blit(text_surf, text_rect)
            
    pygame.display.update()

pygame.quit()
