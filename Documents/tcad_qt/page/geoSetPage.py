from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFormLayout, 
    QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen

class GeometrySettingPage(QWidget):
    def __init__(self, graphics_scene, shape_type, shape_name, is_2d=True):
        super().__init__()
        self.graphics_scene = graphics_scene
        self.shape_type = shape_type
        self.shape_name = shape_name
        self.is_2d = is_2d
        layout = QVBoxLayout(self)

        # 参数设置区
        self.form_layout = QFormLayout()
        self.inputs = {}

        if self.is_2d:
            # 根据图形类型动态添加字段
            if self.shape_type == "矩形":
                fields = ("位置X", "位置Y", "宽度", "高度", "旋转角度")
            elif self.shape_type == "圆形":
                fields = ("位置X", "位置Y", "半径", "旋转角度")
            else:
                fields = ()

            for field in fields:
                line_edit = QLineEdit()
                self.inputs[field] = line_edit
                self.form_layout.addRow(field, line_edit)

            layout.addLayout(self.form_layout)

        else:
            # 根据图形类型动态添加字段
            if self.shape_type == "长方体":
                fields = ("位置X", "位置Y", "位置Z", "长度", "宽度", "高度", "旋转角度X", "旋转角度Y", "旋转角度Z")
            elif self.shape_type == "球体":
                fields = ("位置X", "位置Y", "位置Z", "半径")
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
        if self.is_2d:
            self.construct_shape_2d()
        else:
            self.construct_shape_3d()
    
    def construct_shape_2d(self):
        self.graphics_scene.clear()
        rect = None
        try:
            x = float(self.inputs["位置X"].text())
            y = float(self.inputs["位置Y"].text())
            angle = float(self.inputs["旋转角度"].text())
        except (KeyError, ValueError):
            return

        if self.shape_type == "矩形":
            try:
                w = float(self.inputs["宽度"].text())
                h = float(self.inputs["高度"].text())
            except (KeyError, ValueError):
                return
            rect = self.graphics_scene.addRect(x, y, w, h, QPen(Qt.black), QBrush(QColor(200, 200, 255)))

        elif self.shape_type == "圆形":
            try:
                r = float(self.inputs["半径"].text())
            except (KeyError, ValueError):
                return
            rect = self.graphics_scene.addEllipse(x, y, 2*r, 2*r, QPen(Qt.black), QBrush(QColor(200, 255, 200)))

        if rect is not None:
            rect.setTransformOriginPoint(rect.boundingRect().center())
            rect.setRotation(angle)

        self.graphics_scene.setSceneRect(self.graphics_scene.itemsBoundingRect())

    def construct_shape_3d(self):
        # 清除上一次绘制
        self.graphics_scene.shapes.clear()
        try:
            x = float(self.inputs["位置X"].text())
            y = float(self.inputs["位置Y"].text())
        except (KeyError, ValueError):
            return

        if self.shape_type == "长方体":
            try:
                z = float(self.inputs["位置Z"].text())
                length = float(self.inputs["长度"].text())
                width = float(self.inputs["宽度"].text())
                height = float(self.inputs["高度"].text())
                angle_x = float(self.inputs["旋转角度X"].text())
                angle_y = float(self.inputs["旋转角度Y"].text())
                angle_z = float(self.inputs["旋转角度Z"].text())
            except (KeyError, ValueError):
                return

            # 添加立方体到3D画布
            self.graphics_scene.shapes.append({
                'type': 'cube',
                'x': x, 'y': y, 'z': z,
                'length': length,
                'width': width,
                'height': height,
                'angle_x': angle_x,
                'angle_y': angle_y,
                'angle_z': angle_z,
            })
        elif self.shape_type == "球体":
            try:
                z = float(self.inputs["位置Z"].text())
                r = float(self.inputs["半径"].text())
            except (KeyError, ValueError):
                return

            # 添加球到3D画布
            self.graphics_scene.shapes.append({
                'type': 'sphere',
                'x': x, 'y': y, 'z': z,
                'radius': r,
            })

        # 刷新绘制
        self.graphics_scene.update()

