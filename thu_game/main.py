# main.py
# ============================================================
# 主入口：创建窗口、切换全屏、跑主循环
# ============================================================

import sys
import pygame

from src import settings
from src.hotspots import load_hotspots
from src.map_scene import MapScene


def main():
    pygame.init()

    def create_screen(fullscreen: bool):
        if fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode(settings.WINDOWED_SIZE)
        return screen

    # 初始窗口
    is_fullscreen = settings.START_FULLSCREEN
    screen = create_screen(is_fullscreen)
    hotspots = load_hotspots()
    scene = MapScene(screen, hotspots)
    pygame.display.set_caption("THU Map - Zoom MVP (Modular)")

    # 场景
    shotspots = load_hotspots()
    cene = MapScene(screen, hotspots)

    running = True
    clock = pygame.time.Clock()

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

                elif e.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    screen = create_screen(is_fullscreen)
                    scene.set_screen(screen)  # 告诉场景：窗口变了

            else:
                # 其他事件交给场景（鼠标拖拽/缩放/点击命中）
                scene.handle_event(e)

        scene.update()

        screen.fill((0, 0, 0))
        scene.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)