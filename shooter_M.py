import pygame
import math
import random


# ============================
#      PYGAME SETUP
# ============================
# Initialize Pygame and create the game window
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter - Enemies Added")
clock = pygame.time.Clock()

# Color definitions (RGB tuples)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


# ============================
#       BULLET CLASS
# ============================
# Represents projectiles fired by the player's gun
class Bullet:
    def __init__(self, x, y, vx, vy, damage=10, radius=4, life=2.0, color=YELLOW):
        # Initial position and velocity
        self.x = x
        self.y = y
        self.vx = vx  # X velocity (pixels per second)
        self.vy = vy  # Y velocity (pixels per second)
        self.radius = radius  # Size of the bullet for collision detection
        self.color = color
        self.life = life  # Time remaining before bullet disappears (seconds)
        self.damage = damage  # Damage dealt to enemies

    def update(self, dt):
        # Move bullet based on velocity and delta time
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        # Draw bullet as a circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        # Check if bullet is still active and on screen
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT


# ============================
#   ENEMY PROJECTILE CLASS
# ============================
# Projectiles fired by ranged enemies towards the player
class EnemyProjectile:
    def __init__(self, x, y, vx, vy, speed=250, radius=5, color=(255, 100, 100)):
        # Starting position
        self.x = x
        self.y = y
        # Direction vector (normalized)
        self.vx = vx
        self.vy = vy
        self.speed = speed  # Pixels per second
        self.radius = radius  # Size for collision detection
        self.color = color
        self.life = 3.0  # Projectile will disappear after 3 seconds

    def update(self, dt):
        # Update position with velocity, speed, and delta time
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt
        self.life -= dt

    def draw(self, surf):
        # Draw projectile as a circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        # Check if projectile hasn't expired
        return self.life > 0


# ============================
#       GUN CLASS
# ============================
# Handles weapon logic including fire rate, bullet types, and gun switching
class Gun:
    def __init__(self, gun_type="pistol"):
        self.cooldown = 0  # Time until next shot is allowed
        self.set_gun(gun_type)

    def set_gun(self, gun_type):
        """Switch to a different gun type and update all its properties"""
        self.gun_type = gun_type

        # PISTOL: Balanced single-shot weapon
        if gun_type == "pistol":
            self.fire_rate = 0.25
            self.speed = 700
            self.bullet_damage = 10
            self.bullet_radius = 4
            self.spread = 0  # No bullet spread
            self.pellets = 1  # Single bullet per shot

        # SHOTGUN: Slow, close-range, high damage spread
        elif gun_type == "shotgun":
            self.fire_rate = 0.8
            self.speed = 600
            self.bullet_damage = 6
            self.bullet_radius = 5
            self.spread = 20  # Wide spread pattern
            self.pellets = 6  # Multiple pellets

        # MACHINEGUN: Rapid fire, light bullets
        elif gun_type == "machinegun":
            self.fire_rate = 0.08  # Fast fire rate
            self.speed = 750
            self.bullet_damage = 7
            self.bullet_radius = 3
            self.spread = 5  # Slight spread
            self.pellets = 1

        # DRUMGUN: Medium fire rate with burst pattern
        elif gun_type == "drumgun":
            self.fire_rate = 0.15
            self.speed = 750
            self.bullet_damage = 3
            self.bullet_radius = 4
            self.spread = 20  # Medium spread
            self.pellets = 4  # 4 pellets per shot

        # CLUCKGUN: Extreme spread weapon for fun
        elif gun_type == "cluckgun":
            self.fire_rate = 0.15
            self.speed = 750
            self.bullet_damage = 1  # Weak bullets
            self.bullet_radius = 4
            self.spread = 20
            self.pellets = 10  # Many pellets

        # SLUGGER: Heavy, slow, one-hit wonder
        elif gun_type == "slugger":
            self.fire_rate = 0.5
            self.speed = 900  # Fast projectiles
            self.bullet_damage = 20  # High damage
            self.bullet_radius = 8  # Large bullets
            self.spread = 0
            self.pellets = 1


    def update(self, dt):
        # Decrease cooldown over time to allow next shot
        self.cooldown = max(0, self.cooldown - dt)


    def can_fire(self):
        # Check if gun is ready to fire
        return self.cooldown <= 0

    def fire(self, x, y, target_x, target_y):
        """Fire bullets towards target location"""
        if not self.can_fire():
            return []

        # Set cooldown based on fire rate
        self.cooldown = self.fire_rate
        bullets = []

        # Calculate angle to target
        base_angle = math.atan2(target_y - y, target_x - x)

        # Create bullets with potential spread
        for _ in range(self.pellets):
            # Add random spread to bullet angle
            angle = base_angle + math.radians(self.spread) * (random.random() - 0.5)
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed

            bullets.append(
                Bullet(
                    x, y, vx, vy,
                    damage=self.bullet_damage,
                    radius=self.bullet_radius
                )
            )

        return bullets


# ============================
#        ENEMY SYSTEM
# ============================
# Base class for all enemy types with common behavior
class BaseEnemy:
    def __init__(self, health, speed, radius, color):
        # Randomly spawn from edges of screen
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

        # Enemy properties
        self.health = health
        self.speed = speed  # Pixels per second
        self.radius = radius  # Size for collision and drawing
        self.color = color

    def update(self, dt, player):
        # Move enemy towards player position
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist != 0:
            # Normalize direction and move
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, surf):
        # Draw enemy as a circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def hit(self, damage):
        # Reduce health when damaged
        self.health -= damage

    def alive(self):
        # Check if enemy still has health
        return self.health > 0


# Basic enemy - balanced stats
class BasicEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(25, 100, 14, RED)


# Fast enemy - low health, high speed
class FastEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(15, 180, 12, YELLOW)


# Tank enemy - high health, low speed
class TankEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(60, 60, 20, (150, 0, 0))


# ============================
#     RANGED ENEMY
# ============================
# Enemy that shoots projectiles at the player instead of rushing in
class RangedEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(20, 80, 16, (200, 150, 255))
        self.shoot_cooldown = 1.2  # Seconds between shots
        self.shoot_timer = 0  # Time until next shot

    def update(self, dt, player):
        # Only move closer if player is far away (maintain distance)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 200:  # Stay at 200+ pixel distance
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        # Update shooting timer
        self.shoot_timer -= dt

    def try_shoot(self, player):
        """Attempt to shoot projectile at player"""
        if self.shoot_timer > 0:
            return None

        # Reset cooldown for next shot
        self.shoot_timer = self.shoot_cooldown

        # Calculate direction to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # Normalize direction vector
        vx = dx / dist
        vy = dy / dist

        return EnemyProjectile(self.x, self.y, vx, vy)


# ============================
#     ENEMY SPAWN TABLE
# ============================
# List of enemy types that can be randomly spawned
enemy_types = [
    BasicEnemy,
    FastEnemy,
    TankEnemy,
    RangedEnemy
]


# ============================
#       PLAYER CLASS
# ============================
# Main character controlled by player input
class Player:
    def __init__(self, x, y):
        # Position and movement
        self.x = x
        self.y = y
        self.speed = 250  # Pixels per second
        self.radius = 16  # Size for collision and drawing
        self.color = GREEN
        self.health = 100
        self.vx = 0  # Velocity X
        self.vy = 0  # Velocity Y
        self.gun = Gun("pistol")

        # Dash/dodge ability parameters
        self.is_dashing = False
        self.dash_speed = 700  # Fast movement speed while dashing
        self.dash_time = 0.15  # Duration of dash (seconds)
        self.dash_timer = 0
        self.dash_cooldown = 1.0  # Time before dash can be used again
        self.dash_cooldown_timer = 0
        self.dash_dir = (0, 0)  # Direction of current dash

    def handle_input(self, keys):
        """Update velocity based on currently pressed keys"""
        self.vx = 0
        self.vy = 0

        # WASD or arrow keys for movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 1

        # Normalize diagonal movement to prevent faster diagonal speed
        if self.vx != 0 and self.vy != 0:
            inv = 1 / math.sqrt(2)
            self.vx *= inv
            self.vy *= inv

    def start_dash(self):
        """Initiate a dash in the direction player is moving"""
        if self.vx == 0 and self.vy == 0:
            return  # Can't dash without movement input

        self.is_dashing = True
        self.dash_timer = self.dash_time
        self.dash_cooldown_timer = self.dash_cooldown
        self.dash_dir = (self.vx, self.vy)

    def update(self, dt):
        """Update player position, dash state, and gun cooldown"""
        # Decrease dash cooldown
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        # Handle dash movement
        if self.is_dashing:
            self.x += self.dash_dir[0] * self.dash_speed * dt
            self.y += self.dash_dir[1] * self.dash_speed * dt

            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            # Normal movement
            self.x += self.vx * self.speed * dt
            self.y += self.vy * self.speed * dt

        # Keep player on screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Update gun
        self.gun.update(dt)

    def draw(self, surf):
        """Draw player as a circle"""
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


player = Player(WIDTH // 2, HEIGHT // 2)

# Game state variables
bullets = []  # Player bullets in flight
enemies = []  # Active enemies on screen
enemy_projectiles = []  # Projectiles fired by ranged enemies
shooting = False  # Is mouse button held down
enemy_spawn_timer = 0  # Timer for spawning new enemies

# ============================
#      MAIN GAME LOOP
# ============================
running = True
while running:
    # Delta time in seconds (frames run at 60 FPS)
    dt = clock.tick(60) / 1000.0

    # ============ EVENTS ============
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Left mouse button for shooting
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                shooting = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                shooting = False

    # ============ INPUT HANDLING ============
    keys = pygame.key.get_pressed()

    # Space bar to dash/dodge
    if keys[pygame.K_SPACE] and player.dash_cooldown_timer <= 0 and not player.is_dashing:
        player.start_dash()

    # Number keys to switch guns (1-6)
    if keys[pygame.K_1]:
        player.gun.set_gun("pistol")
    if keys[pygame.K_2]:
        player.gun.set_gun("shotgun")
    if keys[pygame.K_3]:
        player.gun.set_gun("machinegun")
    if keys[pygame.K_4]:
        player.gun.set_gun("drumgun")
    if keys[pygame.K_5]:
        player.gun.set_gun("cluckgun")
    if keys[pygame.K_6]:
        player.gun.set_gun("slugger")


    # ============ PLAYER UPDATE ============
    player.handle_input(keys)
    player.update(dt)

    # Get mouse position for aiming
    mx, my = pygame.mouse.get_pos()

    # Fire bullets if shooting and gun is ready
    if shooting and player.gun.can_fire():
        new_bullets = player.gun.fire(player.x, player.y, mx, my)
        bullets.extend(new_bullets)

    # ============ BULLET UPDATE ============
    for b in bullets:
        b.update(dt)
    # Remove bullets that are dead (expired or off-screen)
    bullets = [b for b in bullets if b.alive()]

    # ============ ENEMY SPAWNING ============
    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0:
        # Spawn random enemy type
        enemies.append(random.choice(enemy_types)())
        # Spawn rate increases as more enemies are alive (harder difficulty)
        enemy_spawn_timer = max(0.3, 1.5 - len(enemies) * 0.01)

    # ============ ENEMY UPDATE ============
    for e in enemies:
        e.update(dt, player)

        # Ranged enemies shoot at player
        if isinstance(e, RangedEnemy):
            proj = e.try_shoot(player)
            if proj:
                enemy_projectiles.append(proj)

    # ============ COLLISION: BULLETS vs ENEMIES ============
    for e in enemies:
        for b in bullets:
            dx = e.x - b.x
            dy = e.y - b.y
            # Check circular collision
            if dx * dx + dy * dy < (e.radius + b.radius) ** 2:
                e.hit(b.damage)
                b.life = 0  # Bullet dies on impact

    # Remove dead enemies
    enemies = [e for e in enemies if e.alive()]

    # ============ ENEMY PROJECTILE UPDATE ============
    for p in enemy_projectiles:
        p.update(dt)
    # Remove expired projectiles
    enemy_projectiles = [p for p in enemy_projectiles if p.alive()]

    # ============ COLLISION: ENEMY PROJECTILES vs PLAYER ============
    for p in enemy_projectiles:
        dx = p.x - player.x
        dy = p.y - player.y
        # Check circular collision
        if dx * dx + dy * dy < (player.radius + p.radius) ** 2:
            player.health -= 10 * dt  # Deal damage over time

    # ============ RENDERING ============
    # Clear screen
    screen.fill(BLACK)
    
    # Draw all game objects
    player.draw(screen)

    for b in bullets:
        b.draw(screen)

    for e in enemies:
        e.draw(screen)

    for p in enemy_projectiles:
        p.draw(screen)

    # Draw UI status bar at top-left
    font = pygame.font.Font(None, 26)
    status = font.render(
        f"Health: {int(player.health)} | Bullets: {len(bullets)} | Enemies: {len(enemies)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    # Update display
    pygame.display.flip()

# Clean up and exit
pygame.quit()