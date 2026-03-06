# src/map_scene.py
# ============================================================
# MapScene：负责“地图界面”这一整块逻辑
# - 加载地图
# - 缩放缓存（scale 改变时重建）
# - 相机（cam_x/cam_y）
# - 拖拽平移
# - 滚轮缩放（以鼠标为中心）
# - 绘制地图与热点框
# - 点击打印坐标 + 热点命中提示
# ============================================================

import pygame
from .utils import clamp
from . import settings


class MapScene:
    def __init__(self, screen: pygame.Surface, hotspots: list[dict]):
        self.screen = screen
        self.hotspots = hotspots

        self.window_w, self.window_h = self.screen.get_size()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # ---- 加载原图 ----
        self.map_raw = pygame.image.load(settings.MAP_IMAGE_PATH).convert()
        self.raw_w = self.map_raw.get_width()
        self.raw_h = self.map_raw.get_height()

        # ---- 缩放缓存 ----
        self.scale = self.fit_scale()
        self.scaled_map = self.map_raw
        self.scaled_w = self.raw_w
        self.scaled_h = self.raw_h
        self.rebuild_scaled_map()

        # ---- 相机（使用缩放后像素坐标）----
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.apply_camera_constraints()

        # ---- 拖拽 ----
        self.dragging = False
        self.last_mouse = (0, 0)

        # ---- toast ----
        self.toast_text = ""
        self.toast_timer = 0

    # ----------------------------
    # 窗口变化（比如 F11 切换后）
    # ----------------------------
    def set_screen(self, screen: pygame.Surface):
        self.screen = screen
        self.window_w, self.window_h = self.screen.get_size()

        # 保持当前 scale（也可改成重新 fit）
        self.scale = clamp(self.scale, settings.SCALE_MIN, settings.SCALE_MAX)
        self.rebuild_scaled_map()
        self.apply_camera_constraints()

    # ----------------------------
    # 计算“适配窗口”的初始 scale
    # ----------------------------
    def fit_scale(self) -> float:
        s_w = self.window_w / self.raw_w
        s_h = self.window_h / self.raw_h
        s = min(s_w, s_h)
        return clamp(s, settings.SCALE_MIN, settings.SCALE_MAX)

    # ----------------------------
    # 缩放图重建（只在 scale 变化时做）
    # ----------------------------
    def rebuild_scaled_map(self):
        self.scaled_w = max(1, int(self.raw_w * self.scale))
        self.scaled_h = max(1, int(self.raw_h * self.scale))
        self.scaled_map = pygame.transform.smoothscale(self.map_raw, (self.scaled_w, self.scaled_h))

    # ----------------------------
    # 相机约束：大图 clamp，小图居中
    # ----------------------------
    def apply_camera_constraints(self):
        if self.scaled_w <= self.window_w:
            self.cam_x = -(self.window_w - self.scaled_w) / 2
        else:
            self.cam_x = clamp(self.cam_x, 0.0, self.scaled_w - self.window_w)

        if self.scaled_h <= self.window_h:
            self.cam_y = -(self.window_h - self.scaled_h) / 2
        else:
            self.cam_y = clamp(self.cam_y, 0.0, self.scaled_h - self.window_h)

    # ----------------------------
    # 屏幕坐标 -> 原图世界坐标
    # ----------------------------
    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
    # -----------------------------------------------------
    #屏幕坐标 -> “地图区域”的世界坐标（去掉封面偏移）
    #解释：
    #  - (sx+cam)/scale 得到的是“整张图片”的 world 坐标
    #  - 再减去 MAP_OFFSET，就变成“白底地图区域”的坐标
    # -----------------------------------------------------
        wx_full = (sx + self.cam_x) / self.scale
        wy_full = (sy + self.cam_y) / self.scale
        wx = wx_full - settings.MAP_OFFSET_X
        wy = wy_full - settings.MAP_OFFSET_Y
        return wx, wy

    # ----------------------------
    # 原图世界 Rect -> 屏幕 Rect（用于画框）
    # ----------------------------
    def world_rect_to_screen(self, rect: pygame.Rect) -> pygame.Rect:
    # --------------------------------------------------------
    #“地图区域坐标” -> 屏幕坐标
    #解释：
    #  rect 是地图区域坐标（不含封面）
    #  绘制到整张图上时，要先 +MAP_OFFSET 再 *scale 再减 cam
    # --------------------------------------------------------
        x_full = (rect.x + settings.MAP_OFFSET_X) * self.scale - self.cam_x
        y_full = (rect.y + settings.MAP_OFFSET_Y) * self.scale - self.cam_y
        w = rect.w * self.scale
        h = rect.h * self.scale
        return pygame.Rect(int(x_full), int(y_full), max(1, int(w)), max(1, int(h)))

    # ----------------------------
    # 处理事件：返回命中的热点（如果有）
    # ----------------------------
    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.dragging = True
            self.last_mouse = e.pos

        elif e.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = e.pos
            lx, ly = self.last_mouse
            dx, dy = mx - lx, my - ly
            self.cam_x -= dx
            self.cam_y -= dy
            self.last_mouse = (mx, my)

        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.dragging = False
            mx, my = e.pos
            wx, wy = self.screen_to_world(mx, my)

            if settings.PICK_COORD_MODE:
                print(f"[CLICK] world=({int(wx)}, {int(wy)})  scale={self.scale:.2f}")

            for h in self.hotspots:
                if h["rect"].collidepoint(wx, wy):
                    self.toast_text = f"进入：{h['name']}"
                    self.toast_timer = 120
                    print(f"[HIT] {h['id']} - {h['name']}")
                    return h  # 命中热点就返回

        elif e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()

            # 鼠标指向的“原图点”
            anchor_wx, anchor_wy = self.screen_to_world(mx, my)

            old_scale = self.scale
            if e.y > 0:
                self.scale *= settings.SCALE_STEP
            elif e.y < 0:
                self.scale /= settings.SCALE_STEP

            self.scale = clamp(self.scale, settings.SCALE_MIN, settings.SCALE_MAX)

            if abs(self.scale - old_scale) > 1e-6:
                self.rebuild_scaled_map()

                # 以鼠标为中心缩放：保持 anchor_wx 在屏幕上的位置不变
                self.cam_x = anchor_wx * self.scale - mx
                self.cam_y = anchor_wy * self.scale - my

        return None

    # ----------------------------
    # 更新（每帧）
    # ----------------------------
    def update(self):
        self.apply_camera_constraints()
        if self.toast_timer > 0:
            self.toast_timer -= 1

    # ----------------------------
    # 绘制（每帧）
    # ----------------------------
    def draw(self):
        self.screen.blit(self.scaled_map, (-int(self.cam_x), -int(self.cam_y)))

        # 热点框 + 标签
        # --- 热点可视化（暂时关闭）---
        #for h in self.hotspots:
        #   sr = self.world_rect_to_screen(h["rect"])
        #    pygame.draw.rect(self.screen, (255, 255, 0), sr, 2)
        #   label = self.font.render(h["name"], True, (255, 255, 255))
        #    self.screen.blit(label, (sr.x + 4, sr.y + 4))

        # toast
        # --- 命中热点后显示（展示关闭） ---
        #if self.toast_timer > 0 and self.toast_text:
        #    surf = self.font.render(self.toast_text, True, (0, 0, 0))
        #    pad = 10
        #    box = pygame.Rect(20, self.window_h - 60, surf.get_width() + pad * 2, 36)
        #    pygame.draw.rect(self.screen, (255, 255, 255), box, border_radius=8)
        #    self.screen.blit(surf, (box.x + pad, box.y + 8))

        # 左上角信息
        info = self.font.render(
            f"Drag | Wheel Zoom | scale={self.scale:.2f} | F11 toggle | ESC quit",
            True,
            (255, 255, 255),
        )
        self.screen.blit(info, (10, 10))