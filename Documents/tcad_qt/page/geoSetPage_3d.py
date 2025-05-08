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
    def __init__(self, graphics_scene, shape_type, shape_name):
        super().__init__()
        self.plotter = graphics_scene
        self.shape_type = shape_type
        self.shape_name = shape_name
        layout = QVBoxLayout(self)

        # 参数设置区
        self.form_layout = QFormLayout()
        self.inputs = {}

        # 根据图形类型动态添加字段
        if self.shape_type == "长方体":
            fields = ("原点位置X", "原点位置Y", "原点位置Z", "长度", "宽度", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        elif self.shape_type == "球体":
            fields = ("球心位置X", "球心位置Y", "球心位置Z", "半径")
        elif self.shape_type == "圆柱体":
            fields = ("底面中心X", "底面中心Y", "底面中心Z", "半径", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        elif self.shape_type == "圆锥体":
            fields = ("底面中心X", "底面中心Y", "底面中心Z", "底面半径", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
        else:
            fields = ()

        for field in fields:
            line_edit = QLineEdit()
            self.inputs[field] = line_edit
            self.form_layout.addRow(field, line_edit)

        layout.addLayout(self.form_layout)

        # 构造/更新图形按钮
        self.construct_button = QPushButton("更新图形")
        self.construct_button.clicked.connect(self.construct_shape)
        layout.addWidget(self.construct_button)
    
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
            x = float(self.inputs["原点位置X"].text())
            y = float(self.inputs["原点位置Y"].text())
            z = float(self.inputs["原点位置Z"].text())
            l = float(self.inputs["长度"].text())
            w = float(self.inputs["宽度"].text())
            h = float(self.inputs["高度"].text())
            rx = float(self.inputs["旋转角度X"].text())
            ry = float(self.inputs["旋转角度Y"].text())
            rz = float(self.inputs["旋转角度Z"].text())
        except (KeyError, ValueError):
            return

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


    def draw_circle(self):
        try:
            x = float(self.inputs["球心位置X"].text())
            y = float(self.inputs["球心位置Y"].text())
            z = float(self.inputs["球心位置Z"].text())
            r = float(self.inputs["半径"].text())
        except (KeyError, ValueError):
            return

        # 构建球体
        sphere = pv.Sphere(center=(x, y, z), radius=r, theta_resolution=64, phi_resolution=64)

        # 绘制
        # self.plotter.clear()
        # self.plotter.add_mesh(sphere, color="orange", show_edges=True)
        # self.plotter.reset_camera()
        self.set_3d_view(sphere)

    def draw_cylinder(self):
        '''
        绘制圆柱体
        '''
        try:
            x = float(self.inputs["底面中心X"].text())
            y = float(self.inputs["底面中心Y"].text())
            z = float(self.inputs["底面中心Z"].text())
            r = float(self.inputs["半径"].text())
            h = float(self.inputs["高度"].text())
            rx = float(self.inputs["旋转角度X"].text())
            ry = float(self.inputs["旋转角度Y"].text())
            rz = float(self.inputs["旋转角度Z"].text())
        except (KeyError, ValueError):
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

    def draw_cone(self):
        '''
        绘制圆锥体
        '''
        try:
            x = float(self.inputs["底面中心X"].text())
            y = float(self.inputs["底面中心Y"].text())
            z = float(self.inputs["底面中心Z"].text())
            r = float(self.inputs["底面半径"].text())
            h = float(self.inputs["高度"].text())
            rx = float(self.inputs["旋转角度X"].text())
            ry = float(self.inputs["旋转角度Y"].text())
            rz = float(self.inputs["旋转角度Z"].text())
        except (KeyError, ValueError):
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


    def set_3d_view(self,mesh):
        self.plotter.clear()
        self.plotter.add_mesh(mesh, color="orange", show_edges=True)
        self.plotter.reset_camera()

        # 显示坐标轴与边界坐标刻度
        self.plotter.show_axes()
        self.plotter.show_bounds(
            grid='front',            # 在前面显示刻度线
            location='outer',        # 刻度在外部
            all_edges=True,          # 所有边都显示
            font_size=10,            # 刻度文字大小
            color='black'            # 颜色
        )


