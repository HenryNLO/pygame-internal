import pygame
import math
import random

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter - Enemies Added")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)


class Bullet:
    def __init__(self, x, y, vx, vy, damage=10, radius=4, life=2.0, color=YELLOW):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = life
        self.damage = damage

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT


class Gun:
    def __init__(self, gun_type="pistol"):
        self.cooldown = 0
        self.set_gun(gun_type)

    def set_gun(self, gun_type):
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
        self.cooldown = max(0, self.cooldown - dt)

    def can_fire(self):
        return self.cooldown <= 0

    def fire(self, x, y, target_x, target_y):
        if not self.can_fire():
            return []

        self.cooldown = self.fire_rate
        bullets = []

        base_angle = math.atan2(target_y - y, target_x - x)

        for _ in range(self.pellets):
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


class Enemy:
    def __init__(self):
        # Spawn at edges
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

        self.radius = 14
        self.color = RED
        self.speed = 100
        self.health = 25

    def update(self, dt, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def hit(self, damage):
        self.health -= damage

    def alive(self):
        return self.health > 0


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 250
        self.radius = 16
        self.color = GREEN
        self.health = 100
        self.vx = 0
        self.vy = 0
        self.gun = Gun("pistol")

    def handle_input(self, keys):
        self.vx = 0
        self.vy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 1

        if self.vx != 0 and self.vy != 0:
            inv = 1 / math.sqrt(2)
            self.vx *= inv
            self.vy *= inv

    def update(self, dt):
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        self.gun.update(dt)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)


player = Player(WIDTH // 2, HEIGHT // 2)

bullets = []
enemies = []
shooting = False
enemy_spawn_timer = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0

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

    # This is where I added my custom gun functionality
    # Gun switching
    if keys[pygame.K_1]:
        player.gun.set_gun("pistol")
    if keys[pygame.K_2]:
        player.gun.set_gun("shotgun")
    if keys[pygame.K_3]:
        player.gun.set_gun("machinegun")

    player.handle_input(keys)
    player.update(dt)

    mx, my = pygame.mouse.get_pos()

    if shooting and player.gun.can_fire():
        new_bullets = player.gun.fire(player.x, player.y, mx, my)
        bullets.extend(new_bullets)

    # Update bullets
    for b in bullets:
        b.update(dt)
    bullets = [b for b in bullets if b.alive()]

    # Spawn enemies
    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0:
        enemies.append(Enemy())
        enemy_spawn_timer = max(0.3, 1.5 - len(enemies) * 0.01)

    # Update enemies
    for e in enemies:
        e.update(dt, player)

    # Bullet → Enemy collision
    for e in enemies:
        for b in bullets:
            dx = e.x - b.x
            dy = e.y - b.y
            if dx * dx + dy * dy < (e.radius + b.radius) ** 2:
                e.hit(b.damage)
                b.life = 0

    enemies = [e for e in enemies if e.alive()]

    # Enemy → Player collision
    for e in enemies:
        dx = e.x - player.x
        dy = e.y - player.y
        if dx * dx + dy * dy < (e.radius + player.radius) ** 2:
            player.health -= 20 * dt

    screen.fill(BLACK)
    player.draw(screen)

    for b in bullets:
        b.draw(screen)

    for e in enemies:
        e.draw(screen)

    font = pygame.font.Font(None, 26)
    status = font.render(
        f"Health: {int(player.health)} | Bullets: {len(bullets)} | Enemies: {len(enemies)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    pygame.display.flip()

pygame.quit()