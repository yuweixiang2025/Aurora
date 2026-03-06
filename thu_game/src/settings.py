# src/settings.py
# ============================================================
# 配置文件：把“经常改的参数”集中放这里
# ============================================================

MAP_IMAGE_PATH = "assets/campus_map.jpg"

WINDOWED_SIZE = (960, 540)
START_FULLSCREEN = True

# 是否打印点击坐标（用来标定热点）
PICK_COORD_MODE = True

# 缩放参数
SCALE_MIN = 0.10
SCALE_MAX = 2.50
SCALE_STEP = 1.10

HOTSPOTS_JSON_PATH = "data/hotspots.json"

# 白底“地图区域”在整张图片中的左上角偏移（先填 0，测出来再改）
MAP_OFFSET_X = 405
MAP_OFFSET_Y = 3160