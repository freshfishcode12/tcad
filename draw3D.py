from OpenGL.GL import *
from OpenGL.GLU import *
import math
from math import sin, cos, radians
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QStackedWidget, QLabel, QGraphicsView, QGraphicsScene, QPushButton, QFormLayout, 
    QLineEdit, QMenu, QTextEdit, QSplitter, QInputDialog, QOpenGLWidget
)
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter
import sys

class ThreeDGraphicsView(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.shapes = []  # 3D形状列表

        # 摄像机控制参数
        self.camera_distance = 10
        self.camera_rot_x = 20
        self.camera_rot_y = -30
        self.last_mouse_pos = None

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        self.setAutoFillBackground(False)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h != 0 else 1, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
        glClearColor(0.2, 0.2, 0.8, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 摄像机位置
        gluLookAt(
            self.camera_distance * sin(radians(self.camera_rot_y)) * cos(radians(self.camera_rot_x)),
            self.camera_distance * sin(radians(self.camera_rot_x)),
            self.camera_distance * cos(radians(self.camera_rot_y)) * cos(radians(self.camera_rot_x)),
            0, 0, 0,   # 看向原点
            0, 1, 0    # 上方向
        )

        # 先画网格，再画坐标轴，再画你的图形
        self.draw_grid()
        self.draw_axes()

        for shape in self.shapes:
            self.draw_shape(shape)

    def draw_shape(self, shape):
        from OpenGL.GL import (
            glPushMatrix, glPopMatrix, glTranslatef, glRotatef, glScalef
        )
        from OpenGL.GLUT import glutSolidCube, glutSolidSphere

        glPushMatrix()
        x = shape.get('x', 0)
        y = shape.get('y', 0)
        z = shape.get('z', 0)
        glTranslatef(x, y, z)

        if shape['type'] == 'cube':
            length = shape.get('length', 1)
            width = shape.get('width', 1)
            height = shape.get('height', 1)

            # 先缩放成矩形长方体
            glScalef(length, height, width)
            glutSolidCube(1)

        elif shape['type'] == 'sphere':
            radius = shape.get('radius', 1)
            glutSolidSphere(radius, 20, 20)

        glPopMatrix()


    def drawCube(self, size):
        w, h, d = size
        glScalef(w, h, d)
        glBegin(GL_QUADS)
        # 前面
        glColor3f(1, 0, 0)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # 后面
        glColor3f(0, 1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # 其他四面...
        glEnd()

    def drawSphere(self, radius):
        glColor3f(0, 0, 1)
        quad = gluNewQuadric()
        gluSphere(quad, radius, 20, 20)

    # === 鼠标控制 ===
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.camera_rot_y += dx * 0.5
            self.camera_rot_x += dy * 0.5
            self.last_mouse_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01
        self.camera_distance = max(2, min(50, self.camera_distance))
        self.update()

    def draw_axes(self, length=10.0):
        from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor3f, GL_LINES

        glBegin(GL_LINES)

        # X轴 红色
        glColor3f(1.0, 0.0, 0.0)  
        glVertex3f(0, 0, 0)
        glVertex3f(length, 0, 0)

        # Y轴 绿色
        glColor3f(0.0, 1.0, 0.0)  
        glVertex3f(0, 0, 0)
        glVertex3f(0, length, 0)

        # Z轴 蓝色
        glColor3f(0.0, 0.0, 1.0)  
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, length)

        glEnd()

    def draw_grid(self, size=100, step=1):
        from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor3f, GL_LINES

        glColor3f(0.7, 0.7, 0.7)  # 淡灰色网格
        glBegin(GL_LINES)

        for i in range(-size, size + 1, step):
            # 画X方向线
            glVertex3f(i, -size, 0)
            glVertex3f(i, size, 0)
            # 画Y方向线
            glVertex3f(-size, i, 0)
            glVertex3f(size, i, 0)

        glEnd()

