import sys
import time

import pygame

import config
from map import game_map
from player import Worm, Weapon, Bullet

clock = pygame.time.Clock()
click_time = 0
clicked = False

pygame.init()

camera_pos = pygame.Vector2(-1024, -576 * 2)
start_pos = pygame.Vector2(0, 0)

pressed_mouse = [False, False, False]  # left, middle, right

screen = pygame.display.set_mode((config.width, config.height))
surface = pygame.Surface((config.map_width, config.map_width))

# Using blit to copy content from one surface to other
is_pressed = [False, False]  # left, right
game_map.draw_map(surface)
worms = pygame.sprite.Group()
o = Worm(1124, 1152, worms, pilot=(0.5, 0.5), can_control=True)

is_shooting = True

bullet_pool = pygame.sprite.Group()
weapon_pool = pygame.sprite.Group()

cur_weapon = Weapon(100, 100, o, None, weapon_pool)
# bullet.is_visible = False

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
            if event.key == pygame.K_RETURN:
                if time.time() - click_time < 0.2:
                    for worm in worms.sprites():
                        worm.back_jump()
                    clicked = False
                else:
                    clicked = True
                click_time = time.time()
            if event.key == pygame.K_SPACE:
                for worm in worms.sprites():
                    weapon_pool.sprites()[0].set_bullet(Bullet(0, 0, bullet_pool, pilot=(0.5, 0.5)))
                    print(bullet_pool)
                    worm.shoot(15)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = False
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                start_pos = pygame.Vector2(pygame.mouse.get_pos())
                pressed_mouse[0] = True
        if event.type == pygame.MOUSEMOTION:
            if pressed_mouse[0]:
                camera_pos += (pygame.Vector2(pygame.mouse.get_pos()) - start_pos) * 0.05
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pressed_mouse[0] = False
    # game_map.remove_circle(*pygame.mouse.get_pos(), 25)

    if is_pressed[0]:
        for worm in worms.sprites():
            worm.physics_move(-0.7, 0)
    if is_pressed[1]:
        for worm in worms.sprites():
            print("move")
            worm.physics_move(+0.7, 0)

    if clicked and time.time() - click_time > 0.2:
        for worm in worms.sprites():
            worm.jump()
        clicked = False
    game_map.draw_map(surface)

    worms.draw(surface)
    worms.update()

    weapon_pool.draw(surface)
    weapon_pool.update()
    for bul in bullet_pool.sprites():
        if bul.is_visible:
            bullet_pool.draw(surface)
            bullet_pool.update()
            break
    if camera_pos.x < config.camera_bounds[0]:
        camera_pos.x = config.camera_bounds[0]
    if camera_pos.x > config.camera_bounds[2]:
        camera_pos.x = config.camera_bounds[2]
    if camera_pos.y < config.camera_bounds[1]:
        camera_pos.y = config.camera_bounds[1]
    if camera_pos.y > config.camera_bounds[3]:
        camera_pos.y = config.camera_bounds[3]
    print(camera_pos)
    # if camera_pos.x < camera_bounds
    screen.blit(surface, camera_pos)
    clock.tick(config.fps)
    pygame.display.flip()
    pygame.display.update()
