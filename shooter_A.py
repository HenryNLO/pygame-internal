import pygame
import math
import random

# Initialize Pygame and create the game window
pygame.init()

WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter - Enemies Added")
clock = pygame.time.Clock()

# Basic colors used for drawing
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


# -----------------------------
# Bullet class
# -----------------------------
class Bullet:
    def __init__(self, x, y, vx, vy, damage=10, radius=4, life=2.0, color=YELLOW):
        """
        Initialize a bullet projectile.
        Args:
            x, y: Starting position
            vx, vy: Velocity components (pixels/second)
            damage: Damage dealt to enemies (default 10)
            radius: Size of bullet for collision detection (default 4)
            life: Time until bullet disappears (default 2.0 seconds)
            color: RGB color tuple (default YELLOW)
        """
        # Starting position and velocity
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        # Visual + gameplay attributes
        self.radius = radius
        self.color = color
        self.life = life
        self.damage = damage

    def update(self, dt):
        """
        Update bullet position and lifetime.
        Args:
            dt: Delta time since last frame (seconds)
        """
        # Move bullet and reduce lifetime
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        """
        Render the bullet on screen.
        Args:
            surf: Pygame surface to draw on
        """
        # Draw bullet as a small circle
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        """
        Check if bullet should still exist.
        Returns:
            True if bullet is alive and on-screen, False otherwise
        """
        # Bullet is alive if still on screen and has life remaining
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT


# -----------------------------
# Gun class (handles firing logic)
# -----------------------------
class Gun:
    def __init__(self, gun_type="pistol"):
        """
        Initialize the gun system with a selected weapon type.
        Args:
            gun_type: Starting gun type ('pistol', 'shotgun', or 'machinegun')
        """
        self.cooldown = 0
        self.set_gun(gun_type)

    def set_gun(self, gun_type):
        """
        Switch to a different gun type and update all weapon properties.
        Args:
            gun_type: String identifier for gun type ('pistol', 'shotgun', 'machinegun')
        """
        # Configure stats depending on selected gun type
        self.gun_type = gun_type

        if gun_type == "pistol":
            self.fire_rate = 0.25
            self.speed = 700
            self.bullet_damage = 10
            self.bullet_radius = 4
            self.spread = 0
            self.pellets = 1

        elif gun_type == "shotgun":
            self.fire_rate = 0.8
            self.speed = 600
            self.bullet_damage = 6
            self.bullet_radius = 5
            self.spread = 20
            self.pellets = 6

        elif gun_type == "machinegun":
            self.fire_rate = 0.08
            self.speed = 750
            self.bullet_damage = 7
            self.bullet_radius = 3
            self.spread = 5
            self.pellets = 1

    def update(self, dt):
        """
        Update gun cooldown timer.
        Args:
            dt: Delta time since last frame (seconds)
        """
        # Reduce cooldown timer each frame
        self.cooldown = max(0, self.cooldown - dt)

    def can_fire(self):
        """
        Check if the gun is ready to fire.
        Returns:
            True if cooldown is zero, False otherwise
        """
        # Gun can fire only when cooldown is zero
        return self.cooldown <= 0

    def fire(self, x, y, target_x, target_y):
        """
        Fire bullet(s) toward a target location.
        Args:
            x, y: Starting position of bullets
            target_x, target_y: Target position to aim at
        Returns:
            List of Bullet objects created, or empty list if gun is cooling down
        """
        # Prevent firing if still cooling down
        if not self.can_fire():
            return []

        self.cooldown = self.fire_rate
        bullets = []

        # Angle from player to mouse cursor
        base_angle = math.atan2(target_y - y, target_x - x)

        # Create one or more bullets depending on gun type
        for _ in range(self.pellets):
            # Add random spread for shotgun/machinegun
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


# -----------------------------
# Enemy class
# -----------------------------
class Enemy:
    def __init__(self):
        """
        Initialize an enemy that spawns from screen edge and moves toward player.
        """
        # Spawn enemy randomly along one of the four edges
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

        # Enemy attributes
        self.radius = 14
        self.color = RED
        self.speed = 100
        self.health = 25

    def update(self, dt, player):
        """
        Update enemy position to move toward player.
        Args:
            dt: Delta time since last frame (seconds)
            player: Player object to chase
        """
        # Move toward the player's current position
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist != 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, surf):
        """
        Render the enemy on screen.
        Args:
            surf: Pygame surface to draw on
        """
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def hit(self, damage):
        """
        Deal damage to the enemy when hit by a bullet.
        Args:
            damage: Amount of damage to apply
        """
        # Reduce health when hit by a bullet
        self.health -= damage

    def alive(self):
        """
        Check if enemy is still alive.
        Returns:
            True if health is positive, False otherwise
        """
        return self.health > 0


# -----------------------------
# Player class
# -----------------------------
class Player:
    def __init__(self, x, y):
        """
        Initialize the player character.
        Args:
            x, y: Starting position on screen
        """
        # Starting position and movement attributes
        self.x = x
        self.y = y
        self.speed = 250
        self.radius = 16
        self.color = GREEN
        self.health = 100

        # Movement vector
        self.vx = 0
        self.vy = 0

        # Player starts with a pistol
        self.gun = Gun("pistol")

    def handle_input(self, keys):
        """
        Process keyboard input and update movement velocity.
        Args:
            keys: Pygame key states from pygame.key.get_pressed()
        """
        # Reset movement each frame
        self.vx = 0
        self.vy = 0

        # WASD or arrow keys move the player
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 1

        # Normalize diagonal movement
        if self.vx != 0 and self.vy != 0:
            inv = 1 / math.sqrt(2)
            self.vx *= inv
            self.vy *= inv

    def update(self, dt):
        """
        Update player position and gun state.
        Args:
            dt: Delta time since last frame (seconds)
        """
        # Move player based on velocity
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt

        # Keep player inside screen bounds
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Update gun cooldown
        self.gun.update(dt)

    def draw(self, surf):
        """
        Render the player character on screen.
        Args:
            surf: Pygame surface to draw on
        """
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


# -----------------------------
# Game state variables
# -----------------------------
player = Player(WIDTH // 2, HEIGHT // 2)

bullets = []
enemies = []
shooting = False
enemy_spawn_timer = 0

running = True

# -----------------------------
# Main game loop
# -----------------------------
while running:
    dt = clock.tick(60) / 1000.0  # Convert ms to seconds

    # Handle events (quit, mouse clicks, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                shooting = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                shooting = False

    keys = pygame.key.get_pressed()

    # Switch between different gun types
    if keys[pygame.K_1]:
        player.gun.set_gun("pistol")
    if keys[pygame.K_2]:
        player.gun.set_gun("shotgun")
    if keys[pygame.K_3]:
        player.gun.set_gun("machinegun")

    # Update player movement
    player.handle_input(keys)
    player.update(dt)

    # Get mouse position for aiming
    mx, my = pygame.mouse.get_pos()

    # Fire bullets if mouse is held down
    if shooting and player.gun.can_fire():
        new_bullets = player.gun.fire(player.x, player.y, mx, my)
        bullets.extend(new_bullets)

    # Update bullets and remove dead ones
    for b in bullets:
        b.update(dt)
    bullets = [b for b in bullets if b.alive()]

    # Spawn enemies over time
    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0:
        enemies.append(Enemy())
        enemy_spawn_timer = max(0.3, 1.5 - len(enemies) * 0.01)

    # Update enemy movement
    for e in enemies:
        e.update(dt, player)

    # Bullet → Enemy collision detection
    for e in enemies:
        for b in bullets:
            dx = e.x - b.x
            dy = e.y - b.y
            if dx * dx + dy * dy < (e.radius + b.radius) ** 2:
                e.hit(b.damage)
                b.life = 0  # Remove bullet after hit

    # Remove defeated enemies
    enemies = [e for e in enemies if e.alive()]

    # Enemy → Player collision
    for e in enemies:
        dx = e.x - player.x
        dy = e.y - player.y
        if dx * dx + dy * dy < (e.radius + player.radius) ** 2:
            player.health -= 20 * dt

    # -----------------------------
    # Drawing everything
    # -----------------------------
    screen.fill(BLACK)
    player.draw(screen)

    for b in bullets:
        b.draw(screen)

    for e in enemies:
        e.draw(screen)

    # HUD text
    font = pygame.font.Font(None, 26)
    status = font.render(
        f"Health: {int(player.health)} | Bullets: {len(bullets)} | Enemies: {len(enemies)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    pygame.display.flip()

pygame.quit()
