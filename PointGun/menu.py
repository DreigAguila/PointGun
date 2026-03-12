import subprocess
import time
import pygame
import sys
import json
import os
# Initialize Pygame
pygame.init()
pygame.mixer.init()  # for music

# Window size
window_width = 900
window_height = 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("PointGun")

# Load icon
icon = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/pistol.png")
pygame.display.set_icon(icon)

# Load background image
backgroundImage = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/pointGunMainMenu.png")
backgroundImage = pygame.transform.scale(backgroundImage, (window_width, window_height))

# Load settings background image
settingsBackgroundImage = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/settingsBackground.png")
settingsBackgroundImage = pygame.transform.scale(settingsBackgroundImage, (window_width, window_height))

# Load background music
pygame.mixer.music.load("D:/PointGun Game Python/PointGun/assets/music/gameMusic.mp3")
pygame.mixer.music.play(-1)  # loop indefinitely
# Start volume at 0 (silent)
pygame.mixer.music.set_volume(0.0)

# Gradually increase volume to 0.5 over 5 seconds
target_volume = 0.5
fade_duration = 5  # seconds
fade_steps = fade_duration * 60  # assuming 60 FPS
volume_increment = target_volume / fade_steps
current_volume = 0.0

# ------------------- Colors -------------------
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)


# ------------------- Fonts -------------------
font = pygame.font.Font(None, 30)

# ------------------- Button class -------------------
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, border_radius=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.border_radius = border_radius

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=self.border_radius)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=self.border_radius)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# ------------------- Slider class -------------------
class Slider:
    def __init__(self, x, y, width, min_val=0, max_val=100, initial_val=50):
        self.rect = pygame.Rect(x, y, width, 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.knob_radius = 10

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        knob_x = self.rect.x + int((self.value - self.min_val)/(self.max_val - self.min_val) * self.rect.width)
        pygame.draw.circle(surface, LIGHT_GRAY, (knob_x, self.rect.y + self.rect.height//2), self.knob_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.value = int(self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val))
            


# ------------------- Main Menu Buttons -------------------
start_button = Button("Start", (window_width-250)//2, 270, 250, 50, DARK_GRAY, LIGHT_GRAY)
settings_button = Button("Settings", (window_width-250)//2, 350, 250, 50, DARK_GRAY, LIGHT_GRAY)

# -------------------- label for settings page --------------------
musicLabel = font.render("Music:", True, BLACK)
volumeLabel = font.render("Volume:", True, BLACK)
colorLabel = font.render("Target Color:", True, BLACK)

# ------------------- Settings Page Elements -------------------
return_button = Button("Return", 95, 140, 100, 40, DARK_GRAY, LIGHT_GRAY)
music_on = True
music_button = Button("ON", 300, 220, 200, 40, DARK_GRAY, LIGHT_GRAY)
volume_slider = Slider(300, 305, 300, 0, 100, 50)
target_colors = [GREEN, RED, YELLOW, BLUE]
color_names = {"GREEN": GREEN, "RED": RED, "YELLOW": YELLOW, "BLUE": BLUE}
color_to_name = {GREEN: "GREEN", RED: "RED", YELLOW: "YELLOW", BLUE: "BLUE"}
# High score file
SETTINGS_FILE = "D:/PointGun Game Python/PointGun/settings.json"

def load_settings():
    """Load settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return data
        except:
            return {"target_color": "YELLOW"}
    return {"target_color": "YELLOW"}

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except:
        pass

color_buttons = [Button(" ", 300 + i*110, 370, 50, 30, color, LIGHT_GRAY) for i, color in enumerate(target_colors)]
settings = load_settings()
selected_color = color_names.get(settings.get("target_color", "YELLOW"), YELLOW)

# Clock to control FPS
clock = pygame.time.Clock()

# Initialize page
page = "menu"

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000  # delta time in seconds (frame time)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # -------------- Page-specific events --------------
        if page == "menu":
            if start_button.is_clicked(event):
                subprocess.Popen(["D:/PointGun Game Python/.venv/Scripts/python.exe", "D:/PointGun Game Python/PointGun/start_game.py"])
                print("Start game!")  # replace with actual game start
                
                pygame.quit()   # close pygame window
                sys.exit()      # terminate menu program
            if settings_button.is_clicked(event):
                page = "settings"

        elif page == "settings":
            if return_button.is_clicked(event):
                page = "menu"
            if music_button.is_clicked(event):
                music_on = not music_on
                music_button.text = "ON" if music_on else "OFF"
                if music_on:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            volume_slider.handle_event(event)
            for i, btn in enumerate(color_buttons):
                if btn.is_clicked(event):
                    selected_color = target_colors[i]
                    # Save selected color to settings
                    settings["target_color"] = color_to_name[selected_color]
                    save_settings(settings)

    # ------------------- Volume fade -------------------
    if current_volume < target_volume:
        current_volume += volume_increment
        if current_volume > target_volume:
            current_volume = target_volume
        pygame.mixer.music.set_volume(current_volume)
    else:
        pygame.mixer.music.set_volume(volume_slider.value/100)

    # ------------------- Draw -------------------
    if page == "menu":
        screen.blit(backgroundImage, (0, 0))
        start_button.draw(screen)
        settings_button.draw(screen)
    elif page == "settings":
        screen.blit(settingsBackgroundImage, (0, 0))
        return_button.draw(screen)
        music_button.draw(screen)
        volume_slider.draw(screen)
        
        # Draw labels
        screen.blit(musicLabel, (150, 230))
        screen.blit(volumeLabel, (150, 300))
        screen.blit(colorLabel, (150, 375))
        
        for btn in color_buttons:
            btn.draw(screen)
        # highlight selected color
        sel_index = target_colors.index(selected_color)
        pygame.draw.rect(screen, WHITE, color_buttons[sel_index].rect, 3, border_radius=10)

    pygame.display.flip()

pygame.quit()