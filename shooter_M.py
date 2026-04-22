import pygame
import math
import random

'''
My goal for merit was to add the following features:
- 

'''
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


# ============================
#   ENEMY PROJECTILE CLASS
# ============================

class EnemyProjectile:
    def __init__(self, x, y, vx, vy, speed=250, radius=5, color=(255, 100, 100)):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.radius = radius
        self.color = color
        self.life = 3.0

    def update(self, dt):
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt
        self.life -= dt

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        return self.life > 0


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

        elif gun_type == "drumgun":
            self.fire_rate = 0.15
            self.speed = 750
            self.bullet_damage = 3
            self.bullet_radius = 4
            self.spread = 20
            self.pellets = 4

        elif gun_type == "cluckgun":
            self.fire_rate = 0.15
            self.speed = 750
            self.bullet_damage = 1
            self.bullet_radius = 4
            self.spread = 20
            self.pellets = 10

        elif gun_type == "slugger":
            self.fire_rate = 0.5
            self.speed = 900
            self.bullet_damage = 20
            self.bullet_radius = 8
            self.spread = 0
            self.pellets = 1


    # Gun update and firing logic remains unchanged
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


# ============================
#        ENEMY SYSTEM
# ============================

class BaseEnemy:
    def __init__(self, health, speed, radius, color):
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

        self.health = health
        self.speed = speed
        self.radius = radius
        self.color = color

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


class BasicEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(25, 100, 14, RED)


class FastEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(15, 180, 12, YELLOW)


class TankEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(60, 60, 20, (150, 0, 0))


# ============================
#     RANGED ENEMY
# ============================

class RangedEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(20, 80, 16, (200, 150, 255))
        self.shoot_cooldown = 1.2
        self.shoot_timer = 0

    def update(self, dt, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist > 200:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        self.shoot_timer -= dt

    def try_shoot(self, player):
        if self.shoot_timer > 0:
            return None

        self.shoot_timer = self.shoot_cooldown

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        vx = dx / dist
        vy = dy / dist

        return EnemyProjectile(self.x, self.y, vx, vy)


# ============================
#     ENEMY SPAWN TABLE
# ============================

enemy_types = [
    BasicEnemy,
    FastEnemy,
    TankEnemy,
    RangedEnemy
]


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

        self.is_dashing = False
        self.dash_speed = 700
        self.dash_time = 0.15
        self.dash_timer = 0
        self.dash_cooldown = 1.0
        self.dash_cooldown_timer = 0
        self.dash_dir = (0, 0)

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

    def start_dash(self):
        if self.vx == 0 and self.vy == 0:
            return

        self.is_dashing = True
        self.dash_timer = self.dash_time
        self.dash_cooldown_timer = self.dash_cooldown
        self.dash_dir = (self.vx, self.vy)

    def update(self, dt):
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt

        if self.is_dashing:
            self.x += self.dash_dir[0] * self.dash_speed * dt
            self.y += self.dash_dir[1] * self.dash_speed * dt

            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
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
enemy_projectiles = []
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

    if keys[pygame.K_SPACE] and player.dash_cooldown_timer <= 0 and not player.is_dashing:
        player.start_dash()

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


    player.handle_input(keys)
    player.update(dt)

    mx, my = pygame.mouse.get_pos()

    if shooting and player.gun.can_fire():
        new_bullets = player.gun.fire(player.x, player.y, mx, my)
        bullets.extend(new_bullets)

    for b in bullets:
        b.update(dt)
    bullets = [b for b in bullets if b.alive()]

    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0:
        enemies.append(random.choice(enemy_types)())
        enemy_spawn_timer = max(0.3, 1.5 - len(enemies) * 0.01)

    for e in enemies:
        e.update(dt, player)

        if isinstance(e, RangedEnemy):
            proj = e.try_shoot(player)
            if proj:
                enemy_projectiles.append(proj)

    for e in enemies:
        for b in bullets:
            dx = e.x - b.x
            dy = e.y - b.y
            if dx * dx + dy * dy < (e.radius + b.radius) ** 2:
                e.hit(b.damage)
                b.life = 0

    enemies = [e for e in enemies if e.alive()]

    for p in enemy_projectiles:
        p.update(dt)
    enemy_projectiles = [p for p in enemy_projectiles if p.alive()]

    for p in enemy_projectiles:
        dx = p.x - player.x
        dy = p.y - player.y
        if dx * dx + dy * dy < (player.radius + p.radius) ** 2:
            player.health -= 10 * dt

    screen.fill(BLACK)
    player.draw(screen)

    for b in bullets:
        b.draw(screen)

    for e in enemies:
        e.draw(screen)

    for p in enemy_projectiles:
        p.draw(screen)

    font = pygame.font.Font(None, 26)
    status = font.render(
        f"Health: {int(player.health)} | Bullets: {len(bullets)} | Enemies: {len(enemies)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    pygame.display.flip()

pygame.quit()