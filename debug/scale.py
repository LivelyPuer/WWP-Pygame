import pygame
from pygame.locals import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((200, 200), HWSURFACE | DOUBLEBUF | RESIZABLE)
    fake_screen = screen.copy()
    size = 1
    pic = pygame.surface.Surface((50, 50))
    pic.fill((255, 100, 200))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.display.quit()
            elif event.type == MOUSEWHEEL:
                size += event.y * 0.01
        fake_screen.fill('black')
        fake_screen.blit(pic, (100, 100))
        print(size)
        res = (screen.get_rect().size[0] * size, screen.get_rect().size[1] * size)
        screen.blit(pygame.transform.scale(fake_screen, res), (0, 0))
        pygame.display.flip()


main()
