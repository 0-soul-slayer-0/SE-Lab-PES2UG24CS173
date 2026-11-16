import pygame
from game.game_engine import GameEngine

pygame.init()

WIDTH, HEIGHT = 600, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Time Tester - Pygame Version")

clock = pygame.time.Clock()
FPS = 60

engine = GameEngine(WIDTH, HEIGHT)

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            engine.handle_event(event)
            if engine.exit_requested:
                running = False
                break

        if not running:
            break

        engine.handle_input()
        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        engine.on_frame_presented()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
