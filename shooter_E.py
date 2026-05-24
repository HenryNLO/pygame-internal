import pygame
import math
import random

# Initialize Pygame and create the main game window
pygame.init()

WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space invaders 2")
clock = pygame.time.Clock()

# Basic colors used throughout the game
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Title screen state variables
game_started = False
player_name = ""

'''
    SHOOTER GAME (GAMEPLAY CONTROLS)

    - WASD to move the player
    - Mouse to aim and shoot
    - Space to dash)
    - Keys 1 to 8 to switch between different guns types
'''


# ---------------------------------------------------------
# BULLET CLASS — Handles player projectiles
# ---------------------------------------------------------
class Bullet:
    def __init__(self, x, y, vx, vy, damage=10, radius=4, life=2.0, color=YELLOW):
        # Position
        self.x = x
        self.y = y

        # Velocity components
        self.vx = vx
        self.vy = vy

        # Visual + gameplay attributes
        self.radius = radius
        self.color = color
        self.life = life
        self.damage = damage

    def update(self, dt):
        # Move bullet based on velocity and reduce lifetime
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        # Draw bullet as a small circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        # Bullet is alive if it still has life and is inside the screen
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT


# ---------------------------------------------------------
# ENEMY PARTICLE — Used for enemy death explosion effects
# ---------------------------------------------------------
class EnemyParticle:
    def __init__(self, x, y, color, size, vx, vy, life):
        # Starting position
        self.x = x
        self.y = y

        # Visual attributes
        self.color = color
        self.size = size

        # Movement
        self.vx = vx
        self.vy = vy

        # Lifetime
        self.life = life

    def update(self, dt):
        # Move particle outward and shrink over time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

        # Gradually shrink particle size
        self.size = max(0, self.size - dt * 10)

    def draw(self, surf):
        # Draw only if still alive
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size))

    def alive(self):
        return self.life > 0


# ---------------------------------------------------------
# ENEMY PROJECTILE — Projectiles fired by ranged enemies
# ---------------------------------------------------------
class EnemyProjectile:
    def __init__(self, x, y, vx, vy, speed=250, radius=5, color=(255, 100, 100)):
        # Position
        self.x = x
        self.y = y

        # Direction (normalized)
        self.vx = vx
        self.vy = vy

        # Projectile attributes
        self.speed = speed
        self.radius = radius
        self.color = color
        self.life = 3.0  # Time before projectile disappears

    def update(self, dt):
        # Move projectile forward and reduce lifetime
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt
        self.life -= dt

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        return self.life > 0


# ---------------------------------------------------------
# GUN CLASS — Handles all player gun types + firing logic
# ---------------------------------------------------------
class Gun:
    def __init__(self, gun_type="pistol"):
        # Time until the next shot can be fired
        self.cooldown = 0

        # Load stats for the selected gun type
        self.set_gun(gun_type)

    def set_gun(self, gun_type):
        # Store the current gun type
        self.gun_type = gun_type

        # Each gun has its own stats:
        # fire_rate = delay between shots
        # speed = projectile speed
        # bullet_damage = damage per projectile
        # bullet_radius = size of projectile
        # spread = randomness in firing angle
        # pellets = number of projectiles fired at once

        if gun_type == "pistol":
            #basic gun
            self.fire_rate = 0.25
            self.speed = 700
            self.bullet_damage = 10
            self.bullet_radius = 4
            self.spread = 0
            self.pellets = 1

        elif gun_type == "shotgun":
            # buzzsaw
            self.fire_rate = 0.8
            self.speed = 600
            self.bullet_damage = 6
            self.bullet_radius = 5
            self.spread = 20
            self.pellets = 6

        elif gun_type == "machinegun":
            #brrr brrr
            self.fire_rate = 0.08
            self.speed = 750
            self.bullet_damage = 7
            self.bullet_radius = 3
            self.spread = 5
            self.pellets = 1

        elif gun_type == "drumgun":
            #Drum roll please
            self.fire_rate = 0.15
            self.speed = 750
            self.bullet_damage = 3
            self.bullet_radius = 4
            self.spread = 20
            self.pellets = 4

        elif gun_type == "The Jerry":
            # Show me the money
            self.fire_rate = 0.1
            self.speed = 1000
            self.bullet_damage = 3
            self.bullet_radius = 3
            self.spread = 10
            self.pellets = 3

        elif gun_type == "slugger":
            # 
            self.fire_rate = 0.5
            self.speed = 900
            self.bullet_damage = 20
            self.bullet_radius = 8
            self.spread = 0
            self.pellets = 1

        elif gun_type == "zero":
            # Cheese
            self.fire_rate = 0.5
            self.speed = 800
            self.bullet_damage = 20
            self.bullet_radius = 5
            self.spread = 15
            self.pellets = 2

        elif gun_type == "Shivel":
            # shiving shuvel
            self.fire_rate = 0.25
            self.speed = 400
            self.bullet_damage = 10
            self.bullet_radius = 7
            self.spread = 45
            self.pellets = 3

    def update(self, dt):
        # Reduce cooldown timer each frame
        self.cooldown = max(0, self.cooldown - dt)

    def can_fire(self):
        # gun can fire only when cooldown reaches zero
        return self.cooldown <= 0

    def fire(self, x, y, target_x, target_y):
        # Prevent firing if still cooling down
        if not self.can_fire():
            return []

        # Reset cooldown
        self.cooldown = self.fire_rate

        bullets = []

        # Angle from player to mouse cursor
        base_angle = math.atan2(target_y - y, target_x - x)

        # Create one or more projectiles depending on gun type
        for _ in range(self.pellets):

            # Add random spread for more chaotic blasters
            angle = base_angle + math.radians(self.spread) * (random.random() - 0.5)

            # Convert angle to velocity components
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed

            # Create projectile
            bullets.append(
                Bullet(
                    x, y, vx, vy,
                    damage=self.bullet_damage,
                    radius=self.bullet_radius
                )
            )

        return bullets


# ---------------------------------------------------------
# BASE ENEMY CLASS — Shared logic for all enemy types
# ---------------------------------------------------------
class BaseEnemy:
    def __init__(self, health, speed, radius, color, contact_damage):
        # Damage dealt to the player when touching the enemy
        self.contact_damage = contact_damage

        # Spawn enemy randomly along one of the four screen edges
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            self.x = random.randint(0, WIDTH)
            self.y = -20
        elif side == "bottom":
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + 20
        elif side == "left":
            self.x = -20
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = WIDTH + 20
            self.y = random.randint(0, HEIGHT)

        # Enemy stats
        self.health = health
        self.speed = speed
        self.radius = radius
        self.color = color

    def update(self, dt, player):
        # Move toward the player's current position
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # Normalize movement so enemies move at consistent speed
        if dist != 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, surf):
        # Draw enemy as a colored circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def hit(self, damage):
        # Reduce enemy health when hit by a projectile
        self.health -= damage

    def alive(self):
        # Enemy is alive if health is above zero
        return self.health > 0


# ---------------------------------------------------------
# BASIC ENEMY — Standard slow-moving enemy
# ---------------------------------------------------------
class BasicEnemy(BaseEnemy):
    def __init__(self):
        # health, speed, radius, color, contact_damage
        super().__init__(25, 100, 14, RED, contact_damage=10)


# ---------------------------------------------------------
# FAST ENEMY — Moves quickly but has low health
# ---------------------------------------------------------
class FastEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(15, 180, 12, YELLOW, contact_damage=7)


# ---------------------------------------------------------
# TANK ENEMY — Slow but high health and heavy contact damage
# ---------------------------------------------------------
class TankEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(60, 90, 20, (150, 0, 0), contact_damage=20)


# ---------------------------------------------------------
# RANGED ENEMY — Keeps distance and fires projectiles at player
# ---------------------------------------------------------
class RangedEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(20, 80, 16, (200, 150, 255), contact_damage=5)

        # Shooting cooldown timer
        self.shoot_cooldown = 1.2
        self.shoot_timer = 0

    def update(self, dt, player):
        # Move only if too far from player (keeps distance)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # If far away, move closer
        if dist > 200:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        # Reduce shooting cooldown
        self.shoot_timer -= dt

    def try_shoot(self, player):
        # Only shoot when cooldown reaches zero
        if self.shoot_timer > 0:
            return None

        # Reset cooldown
        self.shoot_timer = self.shoot_cooldown

        # Calculate direction toward player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # Normalize direction
        vx = dx / dist
        vy = dy / dist

        # Create a projectile aimed at the player
        return EnemyProjectile(self.x, self.y, vx, vy)


# ---------------------------------------------------------
# LIST OF ENEMY TYPES — Used for random spawning
# ---------------------------------------------------------
enemy_types = [
    BasicEnemy,
    FastEnemy,
    TankEnemy,
    RangedEnemy
]
# ---------------------------------------------------------
# PLAYER CLASS — Handles movement, dashing, health, and gun use
# ---------------------------------------------------------
class Player:
    def __init__(self, x, y):
        # Starting position
        self.x = x
        self.y = y

        # Movement speed and hitbox size
        self.speed = 250
        self.radius = 16
        self.color = GREEN

        # Player health
        self.health = 100

        # Movement vector
        self.vx = 0
        self.vy = 0

        # Player starts with the pistol gun
        self.gun = Gun("pistol")

        # -----------------------------
        # DASH MECHANIC VARIABLES
        # -----------------------------
        self.is_dashing = False          # Whether the player is currently dashing
        self.dash_speed = 700            # Speed during dash
        self.dash_time = 0.15            # Duration of dash
        self.dash_timer = 0              # Timer counting down dash duration

        self.dash_cooldown = 1         # Time before dash can be used again
        self.dash_cooldown_timer = 0     # Timer counting down cooldown

        self.dash_dir = (0, 0)           # Direction of dash (based on movement input)

    # ---------------------------------------------------------
    # HANDLE MOVEMENT INPUT (WASD / Arrow Keys)
    # ---------------------------------------------------------
    def handle_input(self, keys):
        # Reset movement vector each frame
        self.vx = 0
        self.vy = 0

        # Vertical movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = 1

        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 1

        # Normalize diagonal movement so speed stays consistent
        if self.vx != 0 and self.vy != 0:
            inv = 1 / math.sqrt(2)
            self.vx *= inv
            self.vy *= inv

    # ---------------------------------------------------------
    # START DASH — triggered when player presses SPACE
    # ---------------------------------------------------------
    def start_dash(self):
        # Can't dash if not moving
        if self.vx == 0 and self.vy == 0:
            return

        # Activate dash
        self.is_dashing = True
        self.dash_timer = self.dash_time
        self.dash_cooldown_timer = self.dash_cooldown

        # Dash direction is based on current movement input
        self.dash_dir = (self.vx, self.vy)

    # ---------------------------------------------------------
    # UPDATE PLAYER — movement, dash logic, boundaries, gun cooldown
    # ---------------------------------------------------------
    def update(self, dt):
        # Reduce dash cooldown timer
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # If currently dashing, move fast in dash direction
        if self.is_dashing:
            self.x += self.dash_dir[0] * self.dash_speed * dt
            self.y += self.dash_dir[1] * self.dash_speed * dt

            # Count down dash duration
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False

        else:
            # Normal movement
            self.x += self.vx * self.speed * dt
            self.y += self.vy * self.speed * dt

        # Keep player inside screen boundaries
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Update gun cooldown
        self.gun.update(dt)

    # ---------------------------------------------------------
    # DRAW PLAYER — simple circle representation
    # ---------------------------------------------------------
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


# ============================
#       TITLE SCREEN
# ============================

# Fonts used for the title and input text
font_big = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 36)

# Loop runs until the player enters a name and presses ENTER
while not game_started:
    screen.fill(BLACK)

    # Render title + input prompt + current typed name
    title = font_big.render("Space Invaders 2", True, WHITE)
    prompt = font_small.render("Enter your name:", True, WHITE)
    name_text = font_small.render(player_name, True, GREEN)

    # Center all text on the screen
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 250))
    screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, 300))

    # Handle keyboard input for name entry
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:

            # Press ENTER to start the game (only if name is not empty)
            if event.key == pygame.K_RETURN:
                if len(player_name) > 0:
                    game_started = True

            # Backspace removes last character
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]

            else:
                # Add typed character (limit name length)
                if len(player_name) < 12:
                    player_name += event.unicode

    pygame.display.flip()
    clock.tick(60)


# ============================
#   CONTROLS SCREEN
# ============================

# Display controls explanation before game starts
controls_shown = False

while not controls_shown:
    screen.fill(BLACK)

    # Title
    controls_title = font_big.render("CONTROLS", True, YELLOW)
    screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, 30))

    # Control instructions
    font_controls = pygame.font.Font(None, 28)
    controls_text = [
        "WASD or Arrow Keys - Move",
        "Mouse - Aim and Shoot",
        "Space - Dash (dodge enemies)",
        "Keys 1-8 - Switch Weapons",
        "",
        "Press SPACE to start the game!"
    ]

    y_pos = 120
    for line in controls_text:
        if line == "":
            y_pos += 20
        else:
            text_surf = font_controls.render(line, True, WHITE)
            screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
        y_pos += 40

    # Handle input to continue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                controls_shown = True

    pygame.display.flip()
    clock.tick(60)


# ============================
#   MAIN GAME LOOP SETUP
# ============================

# Create the player at the center of the screen
player = Player(WIDTH // 2, HEIGHT // 2)

# Lists that store active game objects
enemy_particles = []       # Visual effects when enemies die
bullets = []               # Player projectiles
enemies = []               # Active enemies
enemy_projectiles = []     # Projectiles fired by ranged enemies

# Shooting state
shooting = False

# Timer controlling how often enemies spawn
enemy_spawn_timer = 0

# Main loop control
running = True
game_over = False

# Tracks how long the player has survived
game_time = 0

# Controls reminder system
reminder_timer = 0
reminder_duration = 3.0  # Show reminder for 3 seconds


# ============================
#        MAIN GAME LOOP
# ============================

# Valid keys during gameplay
VALID_KEYS = {
    pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,  # WASD
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,  # Arrow keys
    pygame.K_SPACE,  # Dash
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,  # Weapon switches
    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8
}
while running:
    # dt = time since last frame (used for smooth movement)
    dt = clock.tick(60) / 1000.0

    # -----------------------------------------
    # EVENT HANDLING (keyboard, mouse, quit)
    # -----------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # If player is dead, only allow restart or quit
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset everything to restart the game
                    player = Player(WIDTH // 2, HEIGHT // 2)
                    bullets = []
                    enemies = []
                    enemy_projectiles = []
                    enemy_particles = []
                    game_time = 0
                    game_over = False

                if event.key == pygame.K_ESCAPE:
                    running = False

        # Shooting input (only when alive)
        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooting = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shooting = False
            
            # Check for invalid key presses
            elif event.type == pygame.KEYDOWN:
                if event.key not in VALID_KEYS:
                    reminder_timer = reminder_duration

    # Track how long the player has survived
    game_time += dt
    
    # Update reminder timer
    if reminder_timer > 0:
        reminder_timer -= dt

    # -----------------------------------------
    # GAME LOGIC (only runs if player is alive)
    # -----------------------------------------
    if not game_over:

        keys = pygame.key.get_pressed()

        # DASH INPUT — Spacebar triggers dash if cooldown is ready
        if keys[pygame.K_SPACE] and player.dash_cooldown_timer <= 0 and not player.is_dashing:
            player.start_dash()

        # GUN SWITCHING — Keys 1–8 select different fictional guns
        if keys[pygame.K_1]: player.gun.set_gun("pistol")
        if keys[pygame.K_2]: player.gun.set_gun("shotgun")
        if keys[pygame.K_3]: player.gun.set_gun("machinegun")
        if keys[pygame.K_4]: player.gun.set_gun("drumgun")
        if keys[pygame.K_5]: player.gun.set_gun("The Jerry")
        if keys[pygame.K_6]: player.gun.set_gun("slugger")
        if keys[pygame.K_7]: player.gun.set_gun("zero")
        if keys[pygame.K_8]: player.gun.set_gun("Shivel")

        # Update player movement
        player.handle_input(keys)
        player.update(dt)

        # Mouse position for aiming
        mx, my = pygame.mouse.get_pos()

        # Fire projectiles if mouse is held down
        if shooting and player.gun.can_fire():
            bullets.extend(player.gun.fire(player.x, player.y, mx, my))

        # -----------------------------------------
        # UPDATE BULLETS
        # -----------------------------------------
        for b in bullets:
            b.update(dt)
        bullets = [b for b in bullets if b.alive()]

        # -----------------------------------------
        # SPAWN ENEMIES OVER TIME
        # -----------------------------------------
        enemy_spawn_timer -= dt
        if enemy_spawn_timer <= 0:
            enemies.append(random.choice(enemy_types)())
            enemy_spawn_timer = max(0.3, 1.5 - len(enemies) * 0.01)

        # -----------------------------------------
        # UPDATE ENEMIES + RANGED ENEMY SHOOTING
        # -----------------------------------------
        for e in enemies:
            e.update(dt, player)

            # Ranged enemies fire projectiles
            if isinstance(e, RangedEnemy):
                proj = e.try_shoot(player)
                if proj:
                    enemy_projectiles.append(proj)

        # -----------------------------------------
        # BULLET → ENEMY COLLISIONS
        # -----------------------------------------
        for e in enemies:
            for b in bullets:
                dx = e.x - b.x
                dy = e.y - b.y

                # Simple circle collision check
                if dx * dx + dy * dy < (e.radius + b.radius) ** 2:
                    e.hit(b.damage)
                    b.life = 0  # Remove bullet

        # -----------------------------------------
        # REMOVE DEAD ENEMIES + SPAWN PARTICLES
        # -----------------------------------------
        new_enemies = []
        for e in enemies:
            if e.alive():
                new_enemies.append(e)
            else:
                # Create particle explosion when enemy dies
                for _ in range(20):
                    angle = random.random() * math.tau
                    speed = random.uniform(50, 200)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed

                    enemy_particles.append(
                        EnemyParticle(e.x, e.y, e.color, e.radius, vx, vy, 1.2)
                    )

        enemies = new_enemies

        # -----------------------------------------
        # UPDATE PARTICLES
        # -----------------------------------------
        for p in enemy_particles:
            p.update(dt)
        enemy_particles = [p for p in enemy_particles if p.alive()]

        # -----------------------------------------
        # UPDATE ENEMY PROJECTILES
        # -----------------------------------------
        for p in enemy_projectiles:
            p.update(dt)
        enemy_projectiles = [p for p in enemy_projectiles if p.alive()]

        # -----------------------------------------
        # ENEMY PROJECTILE → PLAYER COLLISION
        # -----------------------------------------
        for p in enemy_projectiles:
            dx = p.x - player.x
            dy = p.y - player.y

            if dx * dx + dy * dy < (player.radius + p.radius) ** 2:
                player.health -= 10 * dt

        # -----------------------------------------
        # ENEMY CONTACT DAMAGE
        # -----------------------------------------
        for e in enemies:
            dx = e.x - player.x
            dy = e.y - player.y

            if dx * dx + dy * dy < (e.radius + player.radius) ** 2:
                player.health -= e.contact_damage * dt

        # -----------------------------------------
        # CHECK PLAYER DEATH
        # -----------------------------------------
        if player.health <= 0:
            game_over = True

    # -----------------------------------------
    # DRAW EVERYTHING
    # -----------------------------------------
    screen.fill(BLACK)

    # Draw player
    player.draw(screen)

    # Draw bullets
    for b in bullets:
        b.draw(screen)

    # Draw enemies
    for e in enemies:
        e.draw(screen)

    # Draw enemy projectiles
    for p in enemy_projectiles:
        p.draw(screen)

    # Draw particles
    for p in enemy_particles:
        p.draw(screen)

    # HUD (player name, time survived, health, current Gun)
    font = pygame.font.Font(None, 26)
    status = font.render(
        f"{player_name} | Time: {int(game_time)}s | Health: {int(player.health)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    # -----------------------------------------
    # CONTROLS REMINDER (when invalid key is pressed)
    # -----------------------------------------
    if reminder_timer > 0:
        # Fade effect based on remaining time
        alpha = int(255 * (reminder_timer / reminder_duration))
        
        # Semi-transparent background
        reminder_surface = pygame.Surface((WIDTH, 180))
        reminder_surface.set_alpha(200)
        reminder_surface.fill((30, 30, 30))
        screen.blit(reminder_surface, (0, HEIGHT - 180))
        
        # Reminder text
        font_reminder = pygame.font.Font(None, 24)
        reminder_title = pygame.font.Font(None, 32)
        
        title_text = reminder_title.render("INVALID KEY! Valid Controls:", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT - 170))
        
        controls_reminder = [
            "WASD or Arrows - Move  |  Mouse - Shoot  |  Space - Dash  |  1-8 - Weapons"
        ]
        
        y_offset = HEIGHT - 130
        for line in controls_reminder:
            text_surf = font_reminder.render(line, True, WHITE)
            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y_offset))
            y_offset += 35

    # -----------------------------------------
    # DEATH SCREEN
    # -----------------------------------------
    if game_over:
        death_big = pygame.font.Font(None, 72)
        death_small = pygame.font.Font(None, 36)

        text1 = death_big.render("YOU DIED", True, RED)
        text2 = death_small.render(f"{player_name}", True, WHITE)
        text3 = death_small.render("Press R to Restart or ESC to Quit", True, WHITE)

        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 180))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 260))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, 330))

    pygame.display.flip()

# Quit game when loop ends
pygame.quit()