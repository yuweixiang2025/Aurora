# src/hotspots.py
# ============================================================
# 热点（可交互地点）：Rect 使用“原图世界坐标”
# 后续你用点击打印的 world=(x,y) 来精确替换这些 Rect
# ============================================================

# src/hotspots.py
# src/hotspots.py
# ============================================================
# 从 data/hotspots.json 读取热点数据，并转成 pygame.Rect
# ============================================================

from __future__ import annotations
import json
from pathlib import Path
import pygame

from . import settings


def load_hotspots() -> list[dict]:
    """
    返回格式：
    [
      {"id": "...", "name": "...", "rect": pygame.Rect(...)},
      ...
    ]
    """

    # 用“项目根目录”来定位文件，避免 VS Code 工作目录不同导致找不到文件
    project_root = Path(__file__).resolve().parents[1]   # .../thu_game
    json_path = project_root / settings.HOTSPOTS_JSON_PATH

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    hotspots: list[dict] = []
    for item in data:
        rid = item["id"]
        name = item["name"]

        r = item["rect"]
        x, y, w, h = int(r["x"]), int(r["y"]), int(r["w"]), int(r["h"])

        hotspots.append({
            "id": rid,
            "name": name,
            "rect": pygame.Rect(x, y, w, h),
        })

    return hotspots