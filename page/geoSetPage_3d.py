from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFormLayout, 
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen

from thirdparty.pygmsh.tests.helpers import compute_volume
import pygmsh
import numpy as np
import meshio
import pyvista as pv

class GeometrySettingPage_3d(QWidget):
    def __init__(self, graphics_scene, parameters, shape_type, shape_name,all_shapes_global_cache=None):
        super().__init__()
        self.plotter = graphics_scene
        self.shape_type = shape_type
        self.shape_name = shape_name
        self.parameters = parameters
        self.global_shapes = all_shapes_global_cache if all_shapes_global_cache is not None else []
        layout = QVBoxLayout(self)

        # 参数设置区
        self.form_layout = QFormLayout()
        self.inputs = {}

        # 根据图形类型动态添加字段
        if self.shape_type == "长方体":
            self.fields = ("原点位置X", "原点位置Y", "原点位置Z", "长度", "宽度", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        elif self.shape_type == "球体":
            self.fields = ("球心位置X", "球心位置Y", "球心位置Z", "半径")
        elif self.shape_type == "圆柱体":
            self.fields = ("底面中心X", "底面中心Y", "底面中心Z", "半径", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        elif self.shape_type == "圆锥体":
            self.fields = ("底面中心X", "底面中心Y", "底面中心Z", "底面半径", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        else:
            self.fields = ()

        for field in self.fields:
            line_edit = QLineEdit()
            self.inputs[field] = line_edit
            self.form_layout.addRow(field, line_edit)

        layout.addLayout(self.form_layout)

        # 构造/更新单个图形按钮
        self.construct_button = QPushButton("更新图形")
        self.construct_button.clicked.connect(self.construct_shape)
        layout.addWidget(self.construct_button)

        # 构造全部图形按钮
        self.construct_all_button = QPushButton("构建全部图形")
        self.construct_all_button.clicked.connect(self.construct_all_shapes)
        layout.addWidget(self.construct_all_button)

        # 图形列表缓存（用于全部构建）
        self.all_shapes_parameters = []

    def construct_all_shapes(self):
        self.plotter.clear()
        for shape_type, param_dict in self.global_shapes:
            resolved_params = {}
            for key, val in param_dict.items():
                resolved_params[key] = self.resolve_input_value(val)
            self.draw_shape_from_data(shape_type, resolved_params)

    def draw_shape_from_data(self, shape_type, data):
        if shape_type == "长方体":
            x = data.get("原点位置X", 0)
            y = data.get("原点位置Y", 0)
            z = data.get("原点位置Z", 0)
            l = data.get("长度", 1)
            w = data.get("宽度", 1)
            h = data.get("高度", 1)
            rx = data.get("旋转角度X", 0)
            ry = data.get("旋转角度Y", 0)
            rz = data.get("旋转角度Z", 0)
            center = (x + l / 2, y + w / 2, z + h / 2)
            cube = pv.Cube(center=(0, 0, 0), x_length=l, y_length=w, z_length=h)
            cube.rotate_x(rx, point=(0, 0, 0), inplace=True)
            cube.rotate_y(ry, point=(0, 0, 0), inplace=True)
            cube.rotate_z(rz, point=(0, 0, 0), inplace=True)
            cube.translate(center, inplace=True)
            self.plotter.add_mesh(cube, color="orange", show_edges=True, edge_color="black",lighting="none")

        elif shape_type == "球体":
            x = data.get("球心位置X", 0)
            y = data.get("球心位置Y", 0)
            z = data.get("球心位置Z", 0)
            r = data.get("半径", 1)
            sphere = pv.Sphere(center=(x, y, z), radius=r)
            self.plotter.add_mesh(sphere, color="skyblue", show_edges=True)

        elif shape_type == "圆柱体":
            x = data.get("底面中心X", 0)
            y = data.get("底面中心Y", 0)
            z = data.get("底面中心Z", 0)
            r = data.get("半径", 1)
            h = data.get("高度", 1)
            rx = data.get("旋转角度X", 0)
            ry = data.get("旋转角度Y", 0)
            rz = data.get("旋转角度Z", 0)
            center = (0, 0, h / 2)
            cyl = pv.Cylinder(center=center, direction=(0, 0, 1), radius=r, height=h)
            cyl.rotate_x(rx, point=(0, 0, 0), inplace=True)
            cyl.rotate_y(ry, point=(0, 0, 0), inplace=True)
            cyl.rotate_z(rz, point=(0, 0, 0), inplace=True)
            cyl.translate((x, y, z), inplace=True)
            self.plotter.add_mesh(cyl, color="lightgreen", show_edges=True)

        elif shape_type == "圆锥体":
            x = data.get("底面中心X", 0)
            y = data.get("底面中心Y", 0)
            z = data.get("底面中心Z", 0)
            r = data.get("底面半径", 1)
            h = data.get("高度", 1)
            rx = data.get("旋转角度X", 0)
            ry = data.get("旋转角度Y", 0)
            rz = data.get("旋转角度Z", 0)
            center = (0, 0, h / 2)
            cone = pv.Cone(center=center, direction=(0, 0, 1), height=h, radius=r)
            cone.rotate_x(rx, point=(0, 0, 0), inplace=True)
            cone.rotate_y(ry, point=(0, 0, 0), inplace=True)
            cone.rotate_z(rz, point=(0, 0, 0), inplace=True)
            cone.translate((x, y, z), inplace=True)
            self.plotter.add_mesh(cone, color="pink", show_edges=True)

    def construct_shape(self):
        if self.shape_type == "长方体":
            self.draw_rectangle()
        elif self.shape_type == "球体":
            self.draw_circle()
        elif self.shape_type == "圆柱体":
            self.draw_cylinder()
        elif self.shape_type == "圆锥体":
            self.draw_cone()

    def draw_rectangle(self):
        try:
            x = self.resolve_input_value(self.inputs["原点位置X"].text())
            y = self.resolve_input_value(self.inputs["原点位置Y"].text())
            z = self.resolve_input_value(self.inputs["原点位置Z"].text())
            l = self.resolve_input_value(self.inputs["长度"].text())
            w = self.resolve_input_value(self.inputs["宽度"].text())
            h = self.resolve_input_value(self.inputs["高度"].text())
            rx = self.resolve_input_value(self.inputs["旋转角度X"].text())
            ry = self.resolve_input_value(self.inputs["旋转角度Y"].text())
            rz = self.resolve_input_value(self.inputs["旋转角度Z"].text())
            if None in (x, y, z, l, w, h, rx, ry, rz):
                return  # 任一解析失败则中止
        except Exception:
            return

        print(f"Drawing rectangle at ({x}, {y}, {z}) with size ({l}, {w}, {h}) and rotation ({rx}, {ry}, {rz})")
        # 把给定原点转换为中心点
        center = (x + l / 2, y + w / 2, z + h / 2)

        # 构建长方体（默认以 center 为中心）
        cube = pv.Cube(center=(0, 0, 0), x_length=l, y_length=w, z_length=h)

        # 应用旋转（以几何中心旋转）
        cube.rotate_x(rx, point=(0, 0, 0), inplace=True)
        cube.rotate_y(ry, point=(0, 0, 0), inplace=True)
        cube.rotate_z(rz, point=(0, 0, 0), inplace=True)

        # 平移几何体中心至 center
        cube.translate(center, inplace=True)

        self.set_3d_view(cube)

        self.global_shapes.append(("长方体", {k: v.text() for k, v in self.inputs.items()}))

    def draw_circle(self):
        try:
            x = self.resolve_input_value(self.inputs["球心位置X"].text())
            y = self.resolve_input_value(self.inputs["球心位置Y"].text())
            z = self.resolve_input_value(self.inputs["球心位置Z"].text())
            r = self.resolve_input_value(self.inputs["半径"].text())
            if None in (x, y, z, r):
                return  # 任一解析失败则中止
        except Exception:
            return

        # 构建球体
        sphere = pv.Sphere(center=(x, y, z), radius=r, theta_resolution=64, phi_resolution=64)
        self.set_3d_view(sphere)
        self.global_shapes.append(("球体", {k: v.text() for k, v in self.inputs.items()}))

    def draw_cylinder(self):
        '''
        绘制圆柱体
        '''
        try:
            x = self.resolve_input_value(self.inputs["底面中心X"].text())
            y = self.resolve_input_value(self.inputs["底面中心Y"].text())
            z = self.resolve_input_value(self.inputs["底面中心Z"].text())
            r = self.resolve_input_value(self.inputs["半径"].text())
            h = self.resolve_input_value(self.inputs["高度"].text())
            rx = self.resolve_input_value(self.inputs["旋转角度X"].text())
            ry = self.resolve_input_value(self.inputs["旋转角度Y"].text())
            rz = self.resolve_input_value(self.inputs["旋转角度Z"].text())
            if None in (x, y, z, r, h, rx, ry, rz):
                return  # 任一解析失败则中止
        except Exception:
            return

        # 构建圆柱体（以底面中心为基准）
        center = (0, 0, h / 2)
        cylinder = pv.Cylinder(center=center, direction=(0, 0, 1), radius=r, height=h, resolution=64)

        # 应用旋转
        cylinder.rotate_x(rx, point=(0, 0, 0), inplace=True)
        cylinder.rotate_y(ry, point=(0, 0, 0), inplace=True)
        cylinder.rotate_z(rz, point=(0, 0, 0), inplace=True)

        # 平移到底面中心
        cylinder.translate((x, y, z), inplace=True)

        self.set_3d_view(cylinder)

        self.global_shapes.append(("圆柱体", {k: v.text() for k, v in self.inputs.items()}))

    def draw_cone(self):
        '''
        绘制圆锥体
        '''
        try:
            x = self.resolve_input_value(self.inputs["底面中心X"].text())
            y = self.resolve_input_value(self.inputs["底面中心Y"].text())
            z = self.resolve_input_value(self.inputs["底面中心Z"].text())
            r = self.resolve_input_value(self.inputs["底面半径"].text())
            h = self.resolve_input_value(self.inputs["高度"].text())
            rx = self.resolve_input_value(self.inputs["旋转角度X"].text())
            ry = self.resolve_input_value(self.inputs["旋转角度Y"].text())
            rz = self.resolve_input_value(self.inputs["旋转角度Z"].text())
            if None in (x, y, z, r, h, rx, ry, rz):
                return  # 任一解析失败则中止
        except Exception:
            return

        # 构建圆锥体（默认中心在锥体中心，高度方向 Z+）
        center = (0, 0, h / 2)
        cone = pv.Cone(center=center, direction=(0, 0, 1), height=h, radius=r, resolution=64)

        # 应用旋转
        cone.rotate_x(rx, point=(0, 0, 0), inplace=True)
        cone.rotate_y(ry, point=(0, 0, 0), inplace=True)
        cone.rotate_z(rz, point=(0, 0, 0), inplace=True)

        # 平移到底面中心
        cone.translate((x, y, z), inplace=True)

        self.set_3d_view(cone)

        self.global_shapes.append(("圆锥体", {k: v.text() for k, v in self.inputs.items()}))

    def set_3d_view(self, mesh):
        self.plotter.clear()
        self.plotter.add_mesh(mesh, color="orange", show_edges=True)
        self.plotter.current_mesh = mesh  # 存储当前 mesh
        self.plotter.reset_camera()
        self.plotter.show_axes()
        self.plotter.show_bounds(
            grid='front',
            location='outer',
            all_edges=True,
            font_size=10,
            color='black'
        )

    def resolve_input_value(self, text):
        try:
            # 尝试直接解析为数字
            return float(text)
        except ValueError:
            # 解析失败：认为是参数名
            param_info = self.parameters.get_parameters().get(text)
            if param_info:
                return float(param_info["value"])
        return None  # 无法解析


