import itertools
import sys
import time

import pygame

import config
from classes.player import Worm
from classes.ui_models import WormMarker, ShootMarker
from classes.weapon import Bullet, weapons
from map import game_map

clock = pygame.time.Clock()
jump_click_time = 0
jump_clicked = False

shoot_press_time = 0
shoot = False
pygame.init()

cweapon = weapons["shotgun"]
cbullet = cweapon["bullet_info"]
camera_pos = pygame.Vector2(-1024, -576 * 2)
start_pos = pygame.Vector2(0, 0)
pressed_mouse = [False, False, False]  # left, middle, right

screen = pygame.display.set_mode((config.width, config.height))
surface = pygame.Surface((config.map_width, config.map_height))
# Using blit to copy content from one surface to other
is_pressed = [False, False, False, False, False]  # left, right, up, down, space
game_map.draw_map(surface)

worms = pygame.sprite.Group()
bullet_pool = pygame.sprite.Group()
weapon_pool = pygame.sprite.Group()
ui_pool = pygame.sprite.Group()

o1 = Worm(1124, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
o2 = Worm(1324, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
o3 = Worm(1624, 1152, worms, pilot=(8, 8), can_control=False, pilot_pixel=True)
team = itertools.cycle([o1, o2, o3])
active_worm = next(team)
active_worm.can_control = True

worm_marker = WormMarker(10, 10, camera_pos, ui_pool, pilot=(0.5, 0.5))
worm_marker.set_worm(active_worm)

shoot_marker = ShootMarker(10, 10, camera_pos, ui_pool, pilot=(0.5, 0.5))
shoot_marker.set_worm(active_worm)
cur_weapon = cweapon["class"](100, 100, active_worm, None, weapon_pool, **cweapon)
# cur_weapon = Weapon(100, 100, active_worm, None, weapon_pool, duration=False, pilot=(0.5, 0.7), sprite="guns/bazooka.png")
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
                cur_weapon = cweapon["class"](100, 100, active_worm, None, weapon_pool, **cweapon)
                active_worm.can_control = True

                worm_marker.set_worm(active_worm)
                shoot_marker.set_worm(active_worm)
            if event.key == pygame.K_RETURN and not is_pressed[4]:
                if time.time() - jump_click_time < 0.2:
                    for worm in worms.sprites():
                        worm.back_jump()
                    jump_clicked = False
                else:
                    jump_clicked = True
                jump_click_time = time.time()
            if event.key == pygame.K_SPACE and (not active_worm.forward_jumping and not active_worm.back_jumping):
                if cur_weapon.duration:
                    is_pressed[4] = True
                    shoot = False
                    shoot_press_time = time.time()
                else:
                    cur_weapon.set_bullet(cbullet["class"](0, 0, bullet_pool, **cbullet))
                    active_worm.shoot(15)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = False
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = False
            if event.key == pygame.K_UP:
                is_pressed[2] = False
            if event.key == pygame.K_DOWN:
                is_pressed[3] = False
            if event.key == pygame.K_SPACE and cur_weapon.duration and (
                    not active_worm.forward_jumping and not active_worm.back_jumping):
                is_pressed[4] = False
                if not shoot:
                    if active_worm.can_control and active_worm.state == "idle":
                        weapon_pool.sprites()[0].set_bullet(
                            Bullet(0, 0, bullet_pool, radius=30, pilot=(0.5, 1), sprite="bullet/bazooka.png"))
                        active_worm.shoot(15 * (time.time() - shoot_press_time))

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
    if is_pressed[4] and cur_weapon.duration and (not active_worm.forward_jumping and not active_worm.back_jumping):
        if time.time() - shoot_press_time >= 1:
            if not shoot and active_worm.can_control and active_worm.state == "idle":
                cur_weapon.set_bullet(cbullet["class"](0, 0, bullet_pool, **cbullet))
                active_worm.shoot(15)
                is_pressed[4] = False
                shoot = True
    else:
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

        if jump_clicked and time.time() - jump_click_time > 0.2:
            for worm in worms.sprites():
                worm.jump()
            jump_clicked = False
    game_map.draw_map(surface)

    worms.update()
    worms.draw(surface)

    for w in weapon_pool.sprites():
        if w.is_visible:
            weapon_pool.update()
            weapon_pool.draw(surface)
            break

    for bul in bullet_pool.sprites():
        if bul.active:
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
    if not shoot and cur_weapon.duration and is_pressed[4] and (
            not active_worm.forward_jumping and not active_worm.back_jumping):
        for i in range(1, int((time.time() - shoot_press_time) * 100), 10):
            if i > 100:
                break
            rot = pygame.Vector2(-10, 0).rotate(180 - active_worm.get_angle())
            pygame.draw.circle(screen, (255, 255 * (100 - i) * 0.01, 0),
                               active_worm.get_pilot() + camera_pos + rot + rot * i // 10, 3 + (i // 10))

    ui_pool.update()
    if active_worm.state == "idle":
        ui_pool.draw(screen)

    clock.tick(config.fps)
    pygame.display.flip()
    # pygame.display.update()
