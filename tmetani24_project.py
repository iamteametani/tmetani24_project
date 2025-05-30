import pygame
import random
import sys

# 1. Initialize Pygame
pygame.init()
pygame.font.init() # Initialize font module

# 2. Screen Dimensions and Colors
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (20, 20, 50) # Dark blue night sky
PLAYER_COLOR = (255, 180, 0)   # Golden basket
STAR_COLORS = [
    (255, 255, 100), # Light Yellow
    (250, 250, 210), # Lemon Chiffon
    (255, 215, 0),   # Gold
    (240, 230, 140)  # Khaki
]
TEXT_COLOR = (255, 255, 255) # White

# 3. Game Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Falling Stars!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36) # You can try "Comic Sans MS" if you have it for extra cuteness
small_font = pygame.font.SysFont("Arial", 24)

# 4. Player (Basket) Properties
player_width = 100
player_height = 20
player_x = (SCREEN_WIDTH - player_width) // 2
player_y = SCREEN_HEIGHT - player_height - 30 # A bit above the bottom
player_speed = 10

# 5. Star Properties
star_size_min = 10
star_size_max = 25
star_speed_min = 2
star_speed_max = 5
stars = [] # List to store star [rect, color, speed, size]

# 6. Game Variables
score = 0
lives = 5
game_over = False
spawn_timer = 0
spawn_interval = 40 # Lower is faster star spawn

def create_star():
    """Creates a new star with random properties."""
    size = random.randint(star_size_min, star_size_max)
    x = random.randint(0, SCREEN_WIDTH - size)
    y = -size # Start just above the screen
    speed = random.randint(star_speed_min, star_speed_max)
    color = random.choice(STAR_COLORS)
    # Use a Rect for easier collision detection and drawing
    star_rect = pygame.Rect(x, y, size, size)
    return {'rect': star_rect, 'color': color, 'speed': speed, 'original_size': size}

def draw_player(x, y):
    """Draws the player's basket."""
    pygame.draw.rect(screen, PLAYER_COLOR, (x, y, player_width, player_height), border_radius=5)
    # Add a little handle for cuteness
    handle_width = 10
    handle_height = 10
    pygame.draw.rect(screen, PLAYER_COLOR, (x + player_width // 2 - handle_width // 2, y - handle_height + 5, handle_width, handle_height), border_radius=3)


def draw_star(star_info):
    """Draws a star as a polygon (more star-like)."""
    rect = star_info['rect']
    color = star_info['color']
    size = star_info['original_size']
    center_x, center_y = rect.centerx, rect.centery

    # Points for a 5-pointed star
    points = []
    for i in range(5):
        angle = (i * 144 + 90) * (3.14159 / 180) # Outer points
        points.append((center_x + size/2 * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                       center_y + size/2 * pygame.math.Vector2(1, 0).rotate_rad(angle).y))
        angle_inner = ((i * 144) + 90 + 72) * (3.14159 / 180) # Inner points
        points.append((center_x + size/4 * pygame.math.Vector2(1, 0).rotate_rad(angle_inner).x,
                       center_y + size/4 * pygame.math.Vector2(1, 0).rotate_rad(angle_inner).y))
    pygame.draw.polygon(screen, color, points)


def reset_game():
    """Resets game variables for a new game."""
    global player_x, score, lives, stars, game_over, spawn_timer
    player_x = (SCREEN_WIDTH - player_width) // 2
    score = 0
    lives = 5
    stars = []
    game_over = False
    spawn_timer = 0

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_SPACE:
                reset_game()

    if not game_over:
        # --- Player Movement ---
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
            player_x -= player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed

        # --- Star Spawning ---
        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            stars.append(create_star())
            spawn_timer = 0
            # Gradually decrease spawn interval to make game harder
            if spawn_interval > 15 and score % 10 == 0 and score > 0: # Every 10 points
                 spawn_interval = max(15, spawn_interval - 2)


        # --- Star Movement & Collision ---
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for star in stars[:]: # Iterate over a copy for safe removal
            star['rect'].y += star['speed']

            # Check for collision with player
            if star['rect'].colliderect(player_rect):
                stars.remove(star)
                score += 1
                # Optional: Play a catch sound here if you add sounds
            # Check if star is off-screen
            elif star['rect'].top > SCREEN_HEIGHT:
                stars.remove(star)
                lives -= 1
                if lives <= 0:
                    game_over = True

    # --- Drawing ---
    screen.fill(BACKGROUND_COLOR)

    if not game_over:
        draw_player(player_x, player_y)
        for star in stars:
            draw_star(star) # Use the polygon star drawing

        # Display Score and Lives
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, 10))
    else:
        # Game Over Screen
        game_over_text = font.render("GAME OVER", True, (255, 60, 60))
        final_score_text = font.render(f"Final Score: {score}", True, TEXT_COLOR)
        restart_text = small_font.render("Press SPACE to Play Again", True, TEXT_COLOR)

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    pygame.display.flip() # Update the full screen
    clock.tick(60) # Cap FPS at 60

# Quit Pygame and Python
pygame.quit()
sys.exit()
