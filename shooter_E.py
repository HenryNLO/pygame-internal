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

# Title screen state
game_started = False
player_name = ""

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

        elif gun_type == "zero":
            self.fire_rate = 0.5
            self.speed = 800
            self.bullet_damage = 20
            self.bullet_radius = 5
            self.spread = 25
            self.pellets = 2

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


class BaseEnemy:
    def __init__(self, health, speed, radius, color, contact_damage):
        self.contact_damage = contact_damage

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
        super().__init__(25, 100, 14, RED, contact_damage=10)

class FastEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(15, 180, 12, YELLOW, contact_damage=7)

class TankEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(60, 90, 20, (150, 0, 0), contact_damage=20)

class RangedEnemy(BaseEnemy):
    def __init__(self):
        super().__init__(20, 80, 16, (200, 150, 255), contact_damage=5)
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


# ============================
#       TITLE SCREEN
# ============================

font_big = pygame.font.Font(None, 72)
font_small = pygame.font.Font(None, 36)

while not game_started:
    screen.fill(BLACK)

    title = font_big.render("SHOOTER GAME", True, WHITE)
    prompt = font_small.render("Enter your name:", True, WHITE)
    name_text = font_small.render(player_name, True, GREEN)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 250))
    screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, 300))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(player_name) > 0:
                    game_started = True

            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]

            else:
                if len(player_name) < 12:
                    player_name += event.unicode

    pygame.display.flip()
    clock.tick(60)


# MAIN GAME LOOP


player = Player(WIDTH // 2, HEIGHT // 2)

bullets = []
enemies = []
enemy_projectiles = []
shooting = False
enemy_spawn_timer = 0

# MAIN GAME LOOP

player = Player(WIDTH // 2, HEIGHT // 2)

bullets = []
enemies = []
enemy_projectiles = []
shooting = False
enemy_spawn_timer = 0

running = True
game_over = False

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Restart / Quit when dead
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset everything
                    player = Player(WIDTH // 2, HEIGHT // 2)
                    bullets = []
                    enemies = []
                    enemy_projectiles = []
                    game_over = False

                if event.key == pygame.K_ESCAPE:
                    running = False

        # Shooting input
        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    shooting = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    shooting = False

    keys = pygame.key.get_pressed()

    # GAMEPLAY ONLY IF NOT DEAD
    if not game_over:

        if keys[pygame.K_SPACE] and player.dash_cooldown_timer <= 0 and not player.is_dashing:
            player.start_dash()

        if keys[pygame.K_1]: player.gun.set_gun("pistol")
        if keys[pygame.K_2]: player.gun.set_gun("shotgun")
        if keys[pygame.K_3]: player.gun.set_gun("machinegun")
        if keys[pygame.K_4]: player.gun.set_gun("drumgun")
        if keys[pygame.K_5]: player.gun.set_gun("cluckgun")
        if keys[pygame.K_6]: player.gun.set_gun("slugger")
        if keys[pygame.K_7]: player.gun.set_gun("zero")

        player.handle_input(keys)
        player.update(dt)

        mx, my = pygame.mouse.get_pos()

        if shooting and player.gun.can_fire():
            bullets.extend(player.gun.fire(player.x, player.y, mx, my))

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

        # Bullet hits
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

        # Projectile hits player
        for p in enemy_projectiles:
            dx = p.x - player.x
            dy = p.y - player.y
            if dx * dx + dy * dy < (player.radius + p.radius) ** 2:
                player.health -= 10 * dt

        # Contact damage
        for e in enemies:
            dx = e.x - player.x
            dy = e.y - player.y
            if dx * dx + dy * dy < (e.radius + player.radius) ** 2:
                player.health -= e.contact_damage * dt

        # Check death
        if player.health <= 0:
            game_over = True

    # DRAWING
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
        f"{player_name} | Health: {int(player.health)} | Bullets: {len(bullets)} | Enemies: {len(enemies)} | Gun: {player.gun.gun_type}",
        True,
        WHITE
    )
    screen.blit(status, (10, 10))

    # DEATH SCREEN
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

pygame.quit()