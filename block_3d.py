import pyvista as pv
import numpy as np

GRID_SIZE = 6
MAX_HEIGHT = 6

CURSOR_COLOR = [1, 1, 1]
BLOCK_COLOR = [0.8, 0.5, 0.3]
TARGET_COLOR = [0.9, 0.7, 0.4]
PLAYER_PROJECTION_COLOR = [0.5, 0.5, 0.5]
SUCCESS_COLOR = [0, 1, 0]

# ===================== 难度逐级递增关卡（共8关） =====================
level_configs = [
    # 第1关：入门，单层横向3块
    {"target_3d": {(0,0,0), (1,0,0), (2,0,0)}},
    # 第2关：单根4层立柱，练习高度堆叠
    {"target_3d": {(3,2,0), (3,2,1), (3,2,2), (3,2,3)}},
    # 第3关：L型立体（底层L，其中一格加高2层）
    {"target_3d": {(1,1,0), (2,1,0), (1,2,0), (1,1,1), (1,1,2)}},
    # 第4关：阶梯造型，高低错落
    {"target_3d": {(0,3,0), (1,3,0), (1,3,1), (2,3,0), (2,3,1), (2,3,2)}},
    # 第5关：2×2底座 + 中间加高立柱
    {"target_3d": {(2,2,0), (3,2,0), (2,3,0), (3,3,0), (2,2,1), (2,2,2), (2,2,3)}},
    # 第6关：复杂错落造型（高难度，多个位置不同高度）
    {"target_3d": {(1,0,0), (1,0,1), (1,0,2),
                   (2,1,0), (2,1,1),
                   (3,0,0),
                   (3,2,0), (3,2,1), (3,2,2), (3,2,3)}},
    # 第7关【困难】：多立柱组合，多处高低不同，投影重叠
    {"target_3d": {(1,1,0), (1,1,1), (1,1,2), (1,1,3),
                   (2,3,0), (2,3,1),
                   (4,2,0), (4,2,1), (4,2,2)}},
    # 第8关【终极挑战】：分散立体组合，多处不同高度，三视图极易看错
    {"target_3d": {(0,1,0), (0,1,1),
                   (2,0,0), (2,0,1), (2,0,2),
                   (3,3,0), (3,3,1), (3,3,2), (3,3,3),
                   (4,1,0),
                   (4,4,0), (4,4,1)}}
]

current_level_idx = 0
placed_blocks = set()  # 玩家积木 (x,y,z)
target_blocks_3d = set()
cursor = np.array([0, 0])
show_success_text = False
plotter = None

static_actors = []
dynamic_actors = []


# 获取当前光标位置最高积木高度
def get_stack_height(x, y):
    h = 0
    while (x, y, h) in placed_blocks:
        h += 1
    return h


def build_static_scene():
    global static_actors
    static_actors.clear()

    # 底板
    floor = pv.Plane(
        center=(GRID_SIZE / 2, GRID_SIZE / 2, 0),
        direction=(0, 0, 1),
        i_size=GRID_SIZE,
        j_size=GRID_SIZE,
    )
    static_actors.append(plotter.add_mesh(floor, color="#eeeeee", opacity=0.6))

    for i in range(GRID_SIZE + 1):
        static_actors.append(plotter.add_mesh(pv.Line((i, 0, 0), (i, GRID_SIZE, 0)), color="white", line_width=1))
        static_actors.append(plotter.add_mesh(pv.Line((0, i, 0), (GRID_SIZE, i, 0)), color="white", line_width=1))

    # 左墙 Y=-2 【前视图 Y-Z平面】
    wall_left = pv.Plane(
        center=(GRID_SIZE / 2, -2, GRID_SIZE / 2),
        direction=(0, 1, 0),
        i_size=GRID_SIZE,
        j_size=GRID_SIZE,
    )
    static_actors.append(plotter.add_mesh(wall_left, color="#e8edf2", opacity=0.7))

    for i in range(GRID_SIZE + 1):
        static_actors.append(plotter.add_mesh(pv.Line((i, -2, 0), (i, -2, GRID_SIZE)), color="white", line_width=1))
        static_actors.append(plotter.add_mesh(pv.Line((0, -2, i), (GRID_SIZE, -2, i)), color="white", line_width=1))

    # 右墙 X=-2 【侧视图 X-Z平面】
    wall_right = pv.Plane(
        center=(-2, GRID_SIZE / 2, GRID_SIZE / 2),
        direction=(1, 0, 0),
        i_size=GRID_SIZE,
        j_size=GRID_SIZE,
    )
    static_actors.append(plotter.add_mesh(wall_right, color="#e8edf2", opacity=0.7))

    for i in range(GRID_SIZE + 1):
        static_actors.append(plotter.add_mesh(pv.Line((-2, i, 0), (-2, i, GRID_SIZE)), color="white", line_width=1))
        static_actors.append(plotter.add_mesh(pv.Line((-2, 0, i), (-2, GRID_SIZE, i)), color="white", line_width=1))


def update_dynamic_scene():
    global dynamic_actors
    for actor in dynamic_actors:
        plotter.remove_actor(actor)
    dynamic_actors.clear()

    # ========== 目标3D积木橙色三视图投影 ==========
    for (x, y, z) in target_blocks_3d:
        # 左墙 Y-Z投影
        left_proj = pv.Cube(center=(x + 0.5, -2, z + 0.5), x_length=0.92, y_length=0.08, z_length=0.92)
        dynamic_actors.append(plotter.add_mesh(left_proj, color=TARGET_COLOR, opacity=0.7))
        # 右墙 X-Z投影
        right_proj = pv.Cube(center=(-2, y + 0.5, z + 0.5), x_length=0.08, y_length=0.92, z_length=0.92)
        dynamic_actors.append(plotter.add_mesh(right_proj, color=TARGET_COLOR, opacity=0.7))

    # ========== 玩家积木：3D实体 + 灰色三视图投影 ==========
    for (x, y, z) in placed_blocks:
        # 3D积木实体
        cube = pv.Cube(center=(x + 0.5, y + 0.5, z + 0.5), x_length=0.92, y_length=0.92, z_length=0.92)
        dynamic_actors.append(plotter.add_mesh(cube, color=BLOCK_COLOR))

        # 左墙 Y-Z 前视图投影
        left_proj = pv.Cube(center=(x + 0.5, -2, z + 0.5), x_length=0.92, y_length=0.08, z_length=0.92)
        dynamic_actors.append(plotter.add_mesh(left_proj, color=PLAYER_PROJECTION_COLOR, opacity=0.7))

        # 右墙 X-Z 侧视图投影
        right_proj = pv.Cube(center=(-2, y + 0.5, z + 0.5), x_length=0.08, y_length=0.92, z_length=0.92)
        dynamic_actors.append(plotter.add_mesh(right_proj, color=PLAYER_PROJECTION_COLOR, opacity=0.7))

    # 光标（底层）
    cx, cy = cursor
    cursor_cube = pv.Cube(center=(cx + 0.5, cy + 0.5, 0.06), x_length=0.9, y_length=0.9, z_length=0.06)
    dynamic_actors.append(plotter.add_mesh(cursor_cube, color=CURSOR_COLOR, opacity=0.8))

    # 文字提示
    txt1 = plotter.add_text(
        "WASD:Move, Space:Place, Backspace:Delete, C:Clear, N:Next",
        position="upper_left", font_size=11, color="white")
    dynamic_actors.append(txt1)

    if show_success_text:
        txt2 = plotter.add_text("SUCCESS! YOU CLEARED THIS LEVEL!", position="lower_left", font_size=22, color=SUCCESS_COLOR)
        dynamic_actors.append(txt2)

    plotter.render()


def check_win():
    global show_success_text
    # 玩家积木集合 和目标3D积木完全相等才算通关
    show_success_text = (placed_blocks == target_blocks_3d)


def key_w():
    global cursor
    cx, cy = cursor
    cy = min(cy + 1, GRID_SIZE - 1)
    cursor = np.array([cx, cy])
    update_dynamic_scene()


def key_s():
    global cursor
    cx, cy = cursor
    cy = max(cy - 1, 0)
    cursor = np.array([cx, cy])
    update_dynamic_scene()


def key_a():
    global cursor
    cx, cy = cursor
    cx = max(cx - 1, 0)
    cursor = np.array([cx, cy])
    update_dynamic_scene()


def key_d():
    global cursor
    cx, cy = cursor
    cx = min(cx + 1, GRID_SIZE - 1)
    cursor = np.array([cx, cy])
    update_dynamic_scene()


def key_space():
    global placed_blocks
    cx, cy = cursor
    h = get_stack_height(cx, cy)
    if h < MAX_HEIGHT:
        placed_blocks.add((cx, cy, h))
    check_win()
    update_dynamic_scene()


def key_backspace():
    global placed_blocks
    cx, cy = cursor
    h = get_stack_height(cx, cy) - 1
    if h >= 0:
        placed_blocks.remove((cx, cy, h))
    check_win()
    update_dynamic_scene()


def key_c():
    global placed_blocks
    placed_blocks.clear()
    check_win()
    update_dynamic_scene()


def key_n():
    global current_level_idx, placed_blocks, target_blocks_3d, show_success_text, cursor
    if current_level_idx < len(level_configs) - 1:
        current_level_idx += 1
        placed_blocks.clear()
        cfg = level_configs[current_level_idx]
        target_blocks_3d = cfg["target_3d"]
        show_success_text = False
        cursor = np.array([0, 0])
    update_dynamic_scene()


def init_level():
    global target_blocks_3d, placed_blocks, show_success_text, cursor
    placed_blocks.clear()
    cfg = level_configs[current_level_idx]
    target_blocks_3d = cfg["target_3d"]
    show_success_text = False
    cursor = np.array([0, 0])


def start_3d_game(start_level):
    global current_level_idx, plotter
    current_level_idx = start_level - 1
    plotter = pv.Plotter()
    plotter.set_background("#223344")

    build_static_scene()

    plotter.add_key_event("w", key_w)
    plotter.add_key_event("s", key_s)
    plotter.add_key_event("a", key_a)
    plotter.add_key_event("d", key_d)
    plotter.add_key_event("space", key_space)
    plotter.add_key_event("BackSpace", key_backspace)
    plotter.add_key_event("c", key_c)
    plotter.add_key_event("n", key_n)

    init_level()
    update_dynamic_scene()
    plotter.show()


if __name__ == "__main__":
    start_3d_game(1)
