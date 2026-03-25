import pygame
from pygame.locals import *
import math
from player import Player

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Top-Down Shooter")
clock = pygame.time.Clock()

# Create player
player = Player(WIDTH // 2, HEIGHT // 2)

# Game loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_w:
                player.moving_up = True
            elif event.key == K_s:
                player.moving_down = True
            elif event.key == K_a:
                player.moving_left = True
            elif event.key == K_d:
                player.moving_right = True
        elif event.type == KEYUP:
            if event.key == K_w:
                player.moving_up = False
            elif event.key == K_s:
                player.moving_down = False
            elif event.key == K_a:
                player.moving_left = False
            elif event.key == K_d:
                player.moving_right = False

    # Update mouse position for aiming
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player.set_aim_direction(mouse_x, mouse_y)

    # Update player
    player.update(dt)

    # Clear screen
    screen.fill(BLACK)

    # Draw player
    player.draw(screen)

    # Draw UI
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(health_text, (10, 10))

    controls_text = font.render("WASD: Move | Mouse: Aim", True, WHITE)
    screen.blit(controls_text, (10, HEIGHT - 40))

    # Update display
    pygame.display.flip()

pygame.quit()