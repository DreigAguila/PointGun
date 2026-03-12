import pygame
import random
import math
import json
import os
from enum import Enum
import subprocess
import sys
# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Window setup
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("PointGun - Game")

pygame.mouse.set_visible(False)   # hide system cursor

# Load icon
try:
    icon = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/pistol.png")
    pygame.display.set_icon(icon)
except:
    pass

# Load assets
try:
    game_background = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/gameBackground.png")
    game_background = pygame.transform.scale(game_background, (WINDOW_WIDTH, WINDOW_HEIGHT))
except:
    game_background = None

try:
    paused_image = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/paused.png")
    paused_image = pygame.transform.scale(paused_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
except:
    paused_image = None

try:
    crosshair = pygame.image.load("D:/PointGun Game Python/PointGun/assets/pictures/crosshair.png")
    crosshair = pygame.transform.scale(crosshair, (80, 80))
except:
    crosshair = None


# Load sound effects
try:
    gunshot_sound = pygame.mixer.Sound("D:/PointGun Game Python/PointGun/assets/music/gunshot.mp3")
except:
    gunshot_sound = None

try:
    countdown_sound = pygame.mixer.Sound("D:/PointGun Game Python/PointGun/assets/music/gameCounts.mp3")
except:
    countdown_sound = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Fonts
font_large = pygame.font.Font(None, 80)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 30)
font_tiny = pygame.font.Font(None, 24)

# Game states
class GameState(Enum):
    COUNTDOWN = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# High score file
HIGHSCORE_FILE = "D:/PointGun Game Python/PointGun/highscore.json"
SETTINGS_FILE = "D:/PointGun Game Python/PointGun/settings.json"

def load_highscore():
    """Load high score from file"""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('highscore', 0)
        except:
            return 0
    return 0

def load_target_color():
    """Load target color from settings file"""
    color_map = {"GREEN": GREEN, "RED": RED, "YELLOW": YELLOW, "BLUE": BLUE}
    
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                color_name = data.get('target_color', 'YELLOW')
                return color_map.get(color_name, YELLOW)
        except:
            return YELLOW
    return YELLOW

def save_highscore(score):
    """Save high score to file"""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump({'highscore': score}, f)
    except:
        pass

class Target:
    """Target that appears randomly on screen"""
    def __init__(self, color=YELLOW):
        self.size = 55
        self.x = random.randint(100, WINDOW_WIDTH - 100)
        self.y = random.randint(150, WINDOW_HEIGHT - 100)
        self.color = color
        self.hit = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        
        # Draw border
        #pygame.draw.circle(surface, RED, (self.x, self.y), self.size, 3)

    def is_clicked(self, mouse_pos):
        """Check if target is clicked"""
        distance = math.sqrt((mouse_pos[0] - self.x) ** 2 + (mouse_pos[1] - self.y) ** 2)
        return distance <= self.size

class MenuButton:
    """Three-line menu button (hamburger menu)"""
    def __init__(self, x=20, y=20, width=40, height=30):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.line_height = 3

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        gap = (self.height - 3 * self.line_height) // 4
        
        # Draw three horizontal lines
        for i in range(3):
            line_y = y + gap + i * (self.line_height + gap)
            pygame.draw.line(surface, WHITE, (x, line_y), (x + self.width, line_y), self.line_height)

    def is_clicked(self, mouse_pos):
        """Check if menu button is clicked"""
        return self.rect.collidepoint(mouse_pos)

class Game:
    """Main game class"""
    def __init__(self):
        self.state = GameState.COUNTDOWN
        self.countdown_time = 4  # 4 seconds
        self.game_duration = 60  # 60 seconds
        self.time_remaining = self.game_duration
        self.score = 0
        self.consecutive_hits = 0
        self.points_per_target = 5
        self.target = None
        self.menu_button = MenuButton()
        self.clock = pygame.time.Clock()
        self.start_ticks = 0
        self.countdown_ticks = 0
        self.game_ticks = 0
        self.highscore = load_highscore()
        self.target_color = load_target_color()  # Load target color from settings
        self._last_countdown = -1  # Track last countdown number for sound
        
        # Play start sequences
        self.play_countdown_audio()
        
        # Hide default cursor and use custom crosshair
        pygame.mouse.set_visible(False)

    def play_countdown_audio(self):
        """Play countdown audio (simulate with timing)"""
        self.countdown_ticks = pygame.time.get_ticks()

    def play_game_music(self):
        """Play game background music"""
        try:
            pygame.mixer.music.load("D:/PointGun Game Python/PointGun/assets/music/gameMusic.mp3")
            pygame.mixer.music.play(-1)
        except:
            pass

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check menu button
                if self.menu_button.is_clicked(event.pos):
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        self.create_pause_buttons()
                        pygame.mouse.set_visible(True)  # Show cursor during pause
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor when playing
                    return True
                
                # Check target hit
                if self.state == GameState.PLAYING and self.target and not self.target.hit:
                    if self.target.is_clicked(event.pos):
                        self.hit_target()
                        return True
                    else:
                        self.miss_target()
                        return True

                # Check pause buttons
                if self.state == GameState.PAUSED:
                    if self.resume_button.is_clicked(event.pos):
                        self.state = GameState.PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor when playing
                        return True
                    elif self.restart_button.is_clicked(event.pos):
                        return "restart"
                    elif self.pause_quit_button.is_clicked(event.pos):
                        # Get paths relative to script location
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        menu_path = os.path.join(script_dir, "menu.py")
                        
                        # Start menu process
                        subprocess.Popen([sys.executable, menu_path])
                        
                        return "quit"  # Let main loop handle cleanup


                # Check game over buttons
                if self.state == GameState.GAME_OVER:
                    if self.play_again_button.is_clicked(event.pos):
                        return "restart"
                    elif self.quit_button.is_clicked(event.pos):
                        # Get paths relative to script location
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        menu_path = os.path.join(script_dir, "menu.py")
                        
                        # Start menu process
                        subprocess.Popen([sys.executable, menu_path])
                        
                        return "quit"  # Let main loop handle cleanup

        return True

    def hit_target(self):
        """Handle target hit"""
        # Play gunshot sound
        if gunshot_sound:
            gunshot_sound.play()
        
        self.consecutive_hits += 1
        
        # Update points per target based on consecutive hits
        if self.consecutive_hits >= 20:
            self.points_per_target = 20
        elif self.consecutive_hits >= 5:
            self.points_per_target = 10
        else:
            self.points_per_target = 5
        
        self.score += self.points_per_target
        self.target = Target(self.target_color)  # Spawn new target with selected color

    def miss_target(self):
        """Handle miss"""
        # Play gunshot sound
        if gunshot_sound:
            gunshot_sound.play()
        
        self.consecutive_hits = 0
        self.points_per_target = 5
        self.score = max(0, self.score - 3)  # -3 points, but not below 0
        self.target = Target(self.target_color)  # Spawn new target with selected color

    def update(self):
        """Update game state"""
        current_ticks = pygame.time.get_ticks()
        
        if self.state == GameState.COUNTDOWN:
            elapsed = (current_ticks - self.countdown_ticks) / 1000.0
            # Play countdown sound every second
            remaining = int(self.countdown_time - elapsed)
            if remaining > 0 and remaining != getattr(self, '_last_countdown', -1):
                if countdown_sound:
                    countdown_sound.play()
                self._last_countdown = remaining
            
            if elapsed >= self.countdown_time:
                self.state = GameState.PLAYING
                self.game_ticks = current_ticks
                self.target = Target(self.target_color)  # Spawn new target with selected color
                pygame.mouse.set_visible(False)  # Hide cursor when playing
                # self.play_game_music()  # Commented out - background music disabled
        
        elif self.state == GameState.PLAYING:
            elapsed = (current_ticks - self.game_ticks) / 1000.0
            self.time_remaining = max(0, self.game_duration - elapsed)
            
            if self.time_remaining <= 0:
                self.state = GameState.GAME_OVER
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)  # Show cursor during game over
                # Update high score
                if self.score > self.highscore:
                    self.highscore = self.score
                    save_highscore(self.highscore)
                self.create_game_over_buttons()
        
        elif self.state == GameState.PAUSED:
            # Paused state - no time updates
            pass

    def create_pause_buttons(self):
        """Create buttons for pause screen"""
        button_width = 140
        button_height = 50
        button_y = WINDOW_HEIGHT - 235
        
        # Three buttons: Resume, Restart, Quit
        resume_x = WINDOW_WIDTH // 2 - 230
        restart_x = WINDOW_WIDTH // 2 - 70
        quit_x = WINDOW_WIDTH // 2 + 90
        
        self.resume_button = Button("RESUME", resume_x, button_y, button_width, button_height, GREEN, (0, 200, 0))
        self.restart_button = Button("RESTART", restart_x, button_y, button_width, button_height, BLUE, (0, 0, 200))
        self.pause_quit_button = Button("QUIT", quit_x, button_y, button_width, button_height, RED, (200, 0, 0))

    def create_game_over_buttons(self):
        """Create buttons for game over screen"""
        button_width = 150
        button_height = 50
        button_y = WINDOW_HEIGHT - 185
        
        left_button_x = WINDOW_WIDTH // 2 - button_width - 20
        right_button_x = WINDOW_WIDTH // 2 + 20
        
        self.play_again_button = Button("PLAY AGAIN", left_button_x, button_y, button_width, button_height, GREEN, (0, 200, 0))
        self.quit_button = Button("QUIT", right_button_x, button_y, button_width, button_height, RED, (200, 0, 0))

    def draw(self):
        """Draw game scene"""
        # Draw background
        if game_background:
            screen.blit(game_background, (0, 0))
        else:
            screen.fill(DARK_GRAY)
        
        if self.state == GameState.COUNTDOWN:
            self.draw_countdown()
        
        elif self.state == GameState.PLAYING:
            self.draw_game()
        
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()

    def draw_countdown(self):
        """Draw countdown screen"""
        current_ticks = pygame.time.get_ticks()
        elapsed = (current_ticks - self.countdown_ticks) / 1000.0
        
        remaining = int(self.countdown_time - elapsed)
        
        if remaining > 0:
            # Draw countdown number
            countdown_text = str(remaining)
        else:
            countdown_text = "GO!"
        
        text_surface = font_large.render(countdown_text, True, YELLOW)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(text_surface, text_rect)

    def draw_game(self):
        """Draw game scene with HUD"""
        # Draw target
        if self.target:
            self.target.draw(screen)
        
        # Draw menu button (upper-left)
        self.menu_button.draw(screen)
        
        # Draw timer (top-center)
        timer_text = font_medium.render(f"{self.time_remaining:.1f}s", True, WHITE)
        timer_rect = timer_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(timer_text, timer_rect)
        
        # Draw score (upper-right)
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 20, 30))
        screen.blit(score_text, score_rect)
        
        # Draw consecutive hits indicator
        consecutive_text = font_tiny.render(f"Streak: {self.consecutive_hits}", True, YELLOW)
        consecutive_rect = consecutive_text.get_rect(topright=(WINDOW_WIDTH - 20, 80))
        screen.blit(consecutive_text, consecutive_rect)
        
        # Draw points per target indicator
        points_text = font_tiny.render(f"Pts/Hit: {self.points_per_target}", True, GREEN)
        points_rect = points_text.get_rect(topright=(WINDOW_WIDTH - 20, 105))
        screen.blit(points_text, points_rect)
        
        # Draw crosshair at mouse position
        if crosshair:
            mouse_pos = pygame.mouse.get_pos()
            crosshair_rect = crosshair.get_rect(center=mouse_pos)
            screen.blit(crosshair, crosshair_rect)

    def draw_paused(self):
        """Draw paused screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw current game elements (faded)
        if self.target:
            self.target.draw(screen)
        
        # Draw paused image or text
        if paused_image:
            screen.blit(paused_image, (0, 0))
        else:
            paused_text = font_large.render("PAUSED", True, YELLOW)
            paused_rect = paused_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(paused_text, paused_rect)
        
        # Draw score info
        score_text = font_medium.render(f"Score: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(450, 280))
        screen.blit(score_text, score_rect)
        
        # Draw pause menu buttons
        self.resume_button.draw(screen)
        self.restart_button.draw(screen)
        self.pause_quit_button.draw(screen)

    def draw_game_over(self):
        """Draw game over screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw GAME OVER text
        game_over_text = font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score_text = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 240))
        screen.blit(score_text, score_rect)
        
        # Draw high score
        highscore_text = font_medium.render(f"High Score: {self.highscore}", True, GREEN)
        highscore_rect = highscore_text.get_rect(center=(WINDOW_WIDTH // 2, 330))
        screen.blit(highscore_text, highscore_rect)
        
        # Draw new high score message
        if self.score == self.highscore and self.score > 0:
            new_score_text = font_small.render("NEW HIGH SCORE!", True, YELLOW)
            new_score_rect = new_score_text.get_rect(center=(WINDOW_WIDTH // 2, 360))
            screen.blit(new_score_text, new_score_rect)

        # Draw play again and quit buttons
        self.play_again_button.draw(screen)
        self.quit_button.draw(screen)


class Button:
    """Button class for game over screen"""
    def __init__(self, text, x, y, width, height, color, hover_color, border_radius=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.border_radius = border_radius

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=self.border_radius)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=self.border_radius)

        text_surface = font_small.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event_pos):
        return self.rect.collidepoint(event_pos)


def main():
    """Main game loop"""
    running = True
    game = Game()
    
    while running:
        result = game.handle_events()
        if result is False:
            running = False
        elif result == "restart":
            game = Game()
        elif result == "quit":
            running = False
        
        game.update()
        game.draw()
        
        pygame.time.Clock().tick(60)  # 60 FPS
    
    pygame.quit()


if __name__ == "__main__":
    main()
