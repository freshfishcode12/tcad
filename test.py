import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pyvistaqt import QtInteractor
import pyvista as pv
import meshio

from thirdparty.pygmsh.tests.helpers import compute_volume
import pygmsh


def test():
    with pygmsh.geo.Geometry() as geom:
        geom.add_circle(
            [0.0, 0.0, 0.0],
            1.0,
            mesh_size=0.1,
            num_sections=4,
            compound=True,
        )
        mesh = geom.generate_mesh()

    ref = 3.1363871677682247
    assert abs(compute_volume(mesh) - ref) < 1.0e-2 * ref
    return mesh


def display_geometry(meshio_mesh, plotter):
    plotter.clear()
    points = meshio_mesh.points
    cells = meshio_mesh.cells_dict

    if "triangle" in cells:
        faces = cells["triangle"]
        
        # Create the faces list with "3" indicating each triangle (3 vertices)
        faces_pv = np.array([[3, *tri] for tri in faces], dtype=np.int64)

        # Flatten the faces
        faces_flat = faces_pv.flatten()

        # Create the surface mesh
        surf = pv.PolyData(points, faces_flat)
        plotter.add_mesh(surf, show_edges=True, color="lightblue")
        plotter.reset_camera()
        plotter.render()
    else:
        print("No triangle cells found in the mesh.")


class MainWindow(QMainWindow):
    def __init__(self, mesh):
        super().__init__()
        self.setWindowTitle("PyVistaQt Mesh Viewer")

        self.frame = QWidget()
        self.layout = QVBoxLayout()
        self.plotter = QtInteractor(self.frame)
        self.layout.addWidget(self.plotter.interactor)
        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        display_geometry(mesh, self.plotter)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mesh = test()
    window = MainWindow(mesh)
    window.show()

    sys.exit(app.exec_())
