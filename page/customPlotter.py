from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
import pyvista as pv
import numpy as np
import time
from threading import Timer

class CustomPlotter(QtInteractor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clipping_widgets = []

    def contextMenuEvent(self, event):
        menu = QMenu()

        info_action = menu.addAction("显示当前状态")
        clear_action = menu.addAction("清除图形")
        export_action = menu.addAction("导出视图")

        # 创建裁剪子菜单
        clip_menu = menu.addMenu("裁剪")
        plane_clip = clip_menu.addAction("裁剪平面")
        box_clip = clip_menu.addAction("裁剪框")
        sphere_clip = clip_menu.addAction("裁剪球体")
        cylinder_clip = clip_menu.addAction("裁剪圆柱体")

        menu.addSeparator()
        clear_clip = menu.addAction("移除裁剪")

        # 显示菜单
        action = menu.exec_(event.globalPos())

        # 响应操作
        if action == info_action:
            print("选中了显示当前状态")
        elif action == clear_action:
            self.clear()
        elif action == export_action:
            self.screenshot("export.png")
        elif action == plane_clip:
            self.add_plane_clip()
        elif action == box_clip:
            self.add_box_clip()
        elif action == sphere_clip:
            self.add_sphere_clip()
        elif action == cylinder_clip:
            self.add_cylinder_clip()
        elif action == clear_clip:
            self.remove_clipping_widgets()

    def add_plane_clip(self):
        if hasattr(self, 'current_mesh') and self.current_mesh is not None:
            def callback(normal, origin):
                clipped = self.current_mesh.clip(normal=normal, origin=origin)
                self.clear()  # 清除旧的 mesh
                self.add_mesh(clipped, color='orange', show_edges=True)
            
            self.add_plane_widget(callback=callback, normal='x', color='blue', outline_translation=True)

    def add_box_clip(self):
        if hasattr(self, 'current_mesh') and self.current_mesh is not None:
            def callback(normal, origin):
                clipped = self.current_mesh.clip(normal=normal, origin=origin)
                self.clear()  # 清除旧的 mesh
                self.add_mesh(clipped, color='orange', show_edges=True)
            
            self.add_box_widget(callback=callback, rotation_enabled=True, outline_translation=True)

    def add_sphere_clip(self):
        if hasattr(self, 'current_mesh') and self.current_mesh is not None:
            def callback(normal, origin):
                clipped = self.current_mesh.clip(normal=normal, origin=origin)
                self.clear()  # 清除旧的 mesh
                self.add_mesh(clipped, color='orange', show_edges=True)

        self.add_sphere_widget(callback)

    def add_cylinder_clip(self):
        if hasattr(self, 'current_mesh') and self.current_mesh is not None:
            def callback(normal, origin):
                clipped = self.current_mesh.clip(normal=normal, origin=origin)
                self.clear()  # 清除旧的 mesh
                self.add_mesh(clipped, color='orange', show_edges=True)

        self.add_cylinder_widget(
            callback
        )

    def remove_clipping_widgets(self):
        for widget in self.clipping_widgets:
            try:
                widget.enabled = False
            except Exception as e:
                print(f"移除裁剪控件失败: {e}")
        self.clipping_widgets.clear()
