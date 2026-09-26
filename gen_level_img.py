import pyvista as pv
import numpy as np

# 关卡1目标方块
target_blocks = {(0,0,0), (1,0,0), (0,1,0)}

def create_block(x,y,z,color="#f6be4b"):
    cube = pv.Cube(center=(x,y,z), x_length=0.95, y_length=0.95, z_length=0.95)
    return cube, color

# 生成正视图 l1_front.png
p1 = pv.Plotter(off_screen=True)
for (x,y,z) in target_blocks:
    mesh,c = create_block(x,y,z)
    p1.add_mesh(mesh, color=c)
p1.camera_position = 'xz'
p1.screenshot("l1_front.png")
p1.close()

# 生成侧视图 l1_side.png
p2 = pv.Plotter(off_screen=True)
for (x,y,z) in target_blocks:
    mesh,c = create_block(x,y,z)
    p2.add_mesh(mesh, color=c)
p2.camera_position = 'yz'
p2.screenshot("l1_side.png")
p2.close()

# 生成俯视图 l1_top.png
p3 = pv.Plotter(off_screen=True)
for (x,y,z) in target_blocks:
    mesh,c = create_block(x,y,z)
p3.add_mesh(mesh, color=c)
p3.camera_position = 'xy'
p3.screenshot("l1_top.png")
p3.close()

print("✅ 三张图片生成完成！")
print("文件：l1_front.png、l1_side.png、l1_top.png")
