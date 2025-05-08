"""Creates a mesh on a cube.
"""
from helpers import compute_volume
import pyvista as pv
import pygmsh


def test():
    with pygmsh.geo.Geometry() as geom:
        geom.add_box(0, 1, 0, 1, 0, 1, 1.0)
        mesh = geom.generate_mesh()

    ref = 1.0
    assert abs(compute_volume(mesh) - ref) < 1.0e-2 * ref
    return mesh


if __name__ == "__main__":
    test().write("cube.vtu")
    mesh = pv.read("cube.vtu")

    # 创建一个绘图器并显示
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=True)
    plotter.show()