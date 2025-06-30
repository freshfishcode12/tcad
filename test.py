import pyvista as pv
from pyvistaqt import BackgroundPlotter

plotter = BackgroundPlotter()
mesh = pv.Sphere()  # 示例模型
plotter.add_mesh(mesh, show_edges=True)

def plane_callback(normal, origin):
    print("裁剪参数：", normal, origin)
    clipped = mesh.clip(normal=normal, origin=origin)
    plotter.clear()  # 清除原图
    plotter.add_mesh(clipped, color="orange")  # 添加裁剪结果

plotter.add_plane_widget(
    callback=plane_callback,
    normal=(1.0, 0.0, 0.0),
    origin=(0.0, 0.0, 0.0)
)
