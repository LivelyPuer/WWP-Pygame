import itertools
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
surface = pygame.Surface((config.map_width, config.map_height))
# Using blit to copy content from one surface to other
is_pressed = [False, False, False, False, False]  # left, right, up, down, space
game_map.draw_map(surface)
worms = pygame.sprite.Group()
o1 = Worm(1124, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
o2 = Worm(1324, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
o3 = Worm(1624, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
team = itertools.cycle([o1, o2, o3])
active_worm = next(team)
active_worm.can_control = True

is_shooting = True

bullet_pool = pygame.sprite.Group()
weapon_pool = pygame.sprite.Group()

cur_weapon = Weapon(100, 100, active_worm, None, weapon_pool, pilot=(0.5, 0.5), sprite="guns/bazooka.png")
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
            if event.key == pygame.K_UP:
                is_pressed[2] = True
            if event.key == pygame.K_DOWN:
                is_pressed[3] = True
            if event.key == pygame.K_TAB:
                active_worm.can_control = False
                cur_weapon.kill()
                active_worm = next(team)
                cur_weapon = Weapon(100, 100, active_worm, None, weapon_pool, pilot=(0.5, 0.5), sprite="guns/bazooka.png")
                active_worm.can_control = True
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
                    weapon_pool.sprites()[0].set_bullet(
                        Bullet(0, 0, bullet_pool, pilot=(0.5, 0.5), sprite="bullet/bazooka.png"))
                    worm.shoot(10)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = False
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = False
            if event.key == pygame.K_UP:
                is_pressed[2] = False
            if event.key == pygame.K_DOWN:
                is_pressed[3] = False
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
            worm.player_move(-0.7, 0)
    if is_pressed[1]:
        for worm in worms.sprites():
            worm.player_move(+0.7, 0)
    if is_pressed[2]:
        for w in worms.sprites():
            w.turn(1)
    if is_pressed[3]:
        for w in worms.sprites():
            w.turn(-1)

    if clicked and time.time() - click_time > 0.2:
        for worm in worms.sprites():
            worm.jump()
        clicked = False
    game_map.draw_map(surface)

    worms.draw(surface)
    worms.update()

    for w in weapon_pool.sprites():
        if w.is_visible:
            weapon_pool.update()
            weapon_pool.draw(surface)
            break

    for bul in bullet_pool.sprites():
        if bul.is_visible:
            bullet_pool.update()
            bullet_pool.draw(surface)
            break

    if camera_pos.x < config.camera_bounds[0]:
        camera_pos.x = config.camera_bounds[0]
    if camera_pos.x > config.camera_bounds[2]:
        camera_pos.x = config.camera_bounds[2]
    if camera_pos.y < config.camera_bounds[1]:
        camera_pos.y = config.camera_bounds[1]
    if camera_pos.y > config.camera_bounds[3]:
        camera_pos.y = config.camera_bounds[3]

    screen.blit(surface, camera_pos)
    clock.tick(config.fps)
    pygame.display.flip()
    pygame.display.update()
