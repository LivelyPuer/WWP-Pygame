import sys

import pygame

import config
from map import game_map
from player import GravityObject

clock = pygame.time.Clock()

pygame.init()

screen = pygame.display.set_mode((1024, 576))
# Using blit to copy content from one surface to other
is_pressed = [False, False]  # left, right
game_map.draw_map(screen)

worms = pygame.sprite.Group()
o = GravityObject(100, 0, worms, pilot=(0.5, 0.5), can_control=True)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = True
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = False
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = False

        if event.type == pygame.MOUSEBUTTONUP:
            game_map.remove_circle(*pygame.mouse.get_pos(), 25)

    if is_pressed[0]:
        for worm in worms.sprites():
            worm.physics_move(-1, 0)
    if is_pressed[1]:
        for worm in worms.sprites():
            worm.physics_move(+1, 0)

    game_map.draw_map(screen)
    worms.draw(screen)
    worms.update()
    clock.tick(config.fps)
    pygame.display.flip()
    pygame.display.update()
