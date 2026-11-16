"""main.py — Main executable entry point for Smart Racing Championship.
Run: python main.py
"""

import sys
import pygame
from src.gui.screen_manager import ScreenManager


def main():
    pygame.init()
    pygame.display.set_caption("Smart Racing Championship — DAA Semester 5")
    
    # 1280x720 Widescreen Display
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    manager = ScreenManager()
    manager.switch_to("main_menu")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Cap at 60 FPS, dt in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
