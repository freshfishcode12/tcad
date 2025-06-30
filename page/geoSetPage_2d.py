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

class GeometrySettingPage_2d(QWidget):
    def __init__(self, graphics_scene, parameters, shape_type, shape_name):
        super().__init__()
        self.plotter = graphics_scene
        self.shape_type = shape_type
        self.shape_name = shape_name
        self.parameters = parameters
        layout = QVBoxLayout(self)

        # 参数设置区
        self.form_layout = QFormLayout()
        self.inputs = {}

        # 根据图形类型动态添加字段
        if self.shape_type == "矩形":
            fields = ("位置X", "位置Y", "宽度", "高度", "旋转角度")
        elif self.shape_type == "圆形":
            fields = ("圆心位置X", "圆心位置Y", "半径")
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
        if self.shape_type == "矩形":
            self.draw_rectangle()
        elif self.shape_type == "圆形":
            self.draw_circle()

    def draw_rectangle(self):
        try:
            x = self.resolve_input_value(self.inputs["位置X"].text())
            y = self.resolve_input_value(self.inputs["位置Y"].text())
            l = self.resolve_input_value(self.inputs["宽度"].text())
            h = self.resolve_input_value(self.inputs["高度"].text())
            angle = self.resolve_input_value(self.inputs["旋转角度"].text())  # 角度（度）
            if None in (x, y, l, h, angle):
                return  # 任一解析失败则中止
        except Exception:
            return

        # 计算矩形四个顶点
        points = np.array([
            [x, y, 0],
            [x + l, y, 0],
            [x + l, y + h, 0],
            [x, y + h, 0]
        ])

        # 计算中心点
        center = np.mean(points[:, :2], axis=0)

        # 构建旋转矩阵（绕Z轴）
        theta = np.radians(angle)
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)]
        ])

        # 应用旋转
        rotated_points = []
        for pt in points:
            vec = pt[:2] - center
            rotated = rotation_matrix @ vec + center
            rotated_points.append([rotated[0], rotated[1], 0])
        rotated_points = np.array(rotated_points)

        # 绘制
        self.plotter.clear()
        polygon = pv.PolyData(rotated_points).delaunay_2d()
        self.plotter.add_mesh(polygon, color="skyblue", show_edges=True)

        # 设置为2D视图
        self.set_2d_view()

    def draw_circle(self):
        try:
            x = self.resolve_input_value(self.inputs["圆心位置X"].text())
            y = self.resolve_input_value(self.inputs["圆心位置Y"].text())
            r = self.resolve_input_value(self.inputs["半径"].text())
            if None in (x, y, r):
                return  # 任一解析失败则中止
        except Exception:
            return

        self.plotter.clear()
        circle = pv.Circle(radius=r, resolution=100)
        circle.translate((x, y, 0), inplace=True)  # 实际效果是以 (x, y) 为圆心
        self.plotter.add_mesh(circle, color="orange", show_edges=True)
        self.set_2d_view()


    def set_2d_view(self):
        self.plotter.view_xy()
        self.plotter.camera.parallel_projection = True
        self.plotter.reset_camera()
        self.plotter.interactor_style = 'image'

        # 显示坐标轴与边界坐标刻度
        self.plotter.show_axes()
        self.plotter.show_bounds(
            grid='front',            # 在前面显示刻度线
            location='outer',        # 刻度在外部
            all_edges=True,          # 所有边都显示
            font_size=10,            # 刻度文字大小
            color='black'            # 颜色
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