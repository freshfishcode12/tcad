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
from pyvistaqt import QtInteractor
import pyvista as pv

from page.paramSetPage import ParameterSettingPage
from page.geoSetPage_2d import GeometrySettingPage_2d
from page.geoSetPage_3d import GeometrySettingPage_3d
from draw3D import ThreeDGraphicsView

# class ZoomableGraphicsView(QGraphicsView):
#     def __init__(self):
#         super().__init__()
#         self.setDragMode(QGraphicsView.ScrollHandDrag)
#         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setRenderHint(QPainter.Antialiasing)

#     def wheelEvent(self, event):
#         factor = 1.25 if event.angleDelta().y() > 0 else 0.8
#         self.scale(factor, factor)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("仿COMSOL界面")
        self.resize(1200, 800)
        self.is_2d = None
        self.dimension_locked = False

        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # 左侧tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.init_tree()
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_tree_menu)
        main_splitter.addWidget(self.tree)

        # 中间 settings stack
        self.settings_stack = QStackedWidget()
        main_splitter.addWidget(self.settings_stack)

        # 右侧 graphics view + info box
        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(right_splitter)

        self.graphics_container = QWidget()
        self.graphics_layout = QVBoxLayout(self.graphics_container)
        self.graphics_layout.setContentsMargins(0, 0, 0, 0)

        # self.graphics_view = ZoomableGraphicsView()
        # self.graphics_scene = QGraphicsScene()
        # self.graphics_view.setScene(self.graphics_scene)
        # self.graphics_layout.addWidget(self.graphics_view)
        self.plotter = QtInteractor(self.graphics_container)
        self.graphics_layout.addWidget(self.plotter)

        right_splitter.addWidget(self.graphics_container)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setPlaceholderText("信息/日志输出...")
        right_splitter.addWidget(self.info_box)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setStretchFactor(2, 3)
        right_splitter.setStretchFactor(0, 250)
        right_splitter.setStretchFactor(1, 1)

        self.init_settings_pages()
        self.geometry_pages = {}

    def init_tree(self):
        '''
        初始化界面最左面的树形结构
        '''
        self.root = QTreeWidgetItem(self.tree, ["全局定义"])
        QTreeWidgetItem(self.root, ["参数"])
        QTreeWidgetItem(self.root, ["Materials"])

        self.component = QTreeWidgetItem(self.tree, ["组件"])
        self.geometry_root = QTreeWidgetItem(self.component, ["几何"])

        self.tree.expandAll()

    def init_settings_pages(self):
        '''
        设置第一列树形界面对应的第二列的界面
        '''
        self.default_page = QLabel("请选择一个组件")
        self.default_page.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.param_page = ParameterSettingPage()

        self.material_page = QLabel("材料设置界面")
        self.material_page.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.component_page = QWidget()
        component_layout = QVBoxLayout(self.component_page)

        self.dim_selector = QComboBox()
        self.dim_selector.addItem("请选择维度")
        self.dim_selector.addItems(["2D", "3D"])
        self.dim_selector.currentIndexChanged.connect(self.on_dimension_changed)
    
        component_layout.addWidget(QLabel("请选择建模维度（2D 或 3D）："))
        component_layout.addWidget(self.dim_selector)
        component_layout.addStretch()

        self.settings_stack.addWidget(self.default_page)
        self.settings_stack.addWidget(self.param_page)
        self.settings_stack.addWidget(self.material_page)
        self.settings_stack.addWidget(self.component_page)

        self.page_map = {
            "参数": 1,
            "Materials": 2,
            "组件": 3,
            "几何": 0,
        }

    def on_dimension_changed(self, index):
        '''
        组件维度选择，关乎到几何组件创建的图形，一旦选定后，整个程序无法更改
        '''
        if self.dimension_locked:
            return

        dimension = self.dim_selector.currentText()
        if dimension == "2D":
            self.is_2d = True
            # self.switch_to_2d_view()
            self.info_box.append("建模维度已设置为 2D")
        elif dimension == "3D":
            self.is_2d = False
            # self.switch_to_3d_view()
            self.info_box.append("建模维度已设置为 3D")
        else:
            return

        self.dimension_locked = True
        self.dim_selector.setEnabled(False)

    def on_tree_item_clicked(self, item, column):
        '''
        点击树形结构的item，切换到对应的设置界面
        '''
        text = item.text(0)
        # print(f"左键: {item.text(0)},self.is_2d: {self.is_2d}")
        if self.is_2d is None:
            if text == "组件":
                # 组件时未选择维度，跳转到component_page
                self.settings_stack.setCurrentWidget(self.component_page)
                self.info_box.append("请选择建模维度（2D 或 3D）")
                return
            else:
                # 其他地方直接进入对应界面
                index = self.page_map.get(text, 0)
                self.settings_stack.setCurrentIndex(index)
                self.info_box.append(f"选中: {text}")
        else:
            if item.parent() == self.geometry_root:  # 如果是几何项
                page = self.geometry_pages.get(text)
                if page:
                    self.settings_stack.setCurrentWidget(page)
                    page.construct_shape()  # 点击时重画
                    self.info_box.append(f"选中图形: {text}")
                else:
                    self.settings_stack.setCurrentIndex(0)
            else:
                index = self.page_map.get(text, 0)
                self.settings_stack.setCurrentIndex(index)
                self.info_box.append(f"选中: {text}")

    def open_tree_menu(self, position):
        '''
        鼠标右键菜单，根据选择的维度，显示创建不同的图形
        '''
        item = self.tree.itemAt(position)
        if not item:
            return

        # print(f"右键: {item.text(0)} at position: {position},self.is_2d: {self.is_2d}")
        menu = QMenu()

        if self.is_2d is None:
            QMessageBox.warning(self, "未选择建模维度", "请先选择建模维度！")
            # 自动跳到“组件”页面，提示用户选择维度
            self.settings_stack.setCurrentWidget(self.component_page)
            self.info_box.append("请先选择建模维度（2D 或 3D）")
            return
        
        elif self.is_2d is not None and self.is_2d == True:
            if item.text(0) == "几何":
                new_rect_action = menu.addAction("新建矩形")
                new_circle_action = menu.addAction("新建圆形")

                action = menu.exec_(self.tree.viewport().mapToGlobal(position))

                if action in (new_rect_action, new_circle_action):
                    shape_type = "矩形" if action == new_rect_action else "圆形"
                    shape_name, ok = QInputDialog.getText(self, "命名图形", f"请输入{shape_type}名称：")
                    if ok and shape_name:
                        self.add_new_shape(shape_type, shape_name)

            elif item.parent() == self.geometry_root:  # 是几何子项
                copy_action = menu.addAction("复制图形")
                delete_action = menu.addAction("删除图形")
                rename_action = menu.addAction("重命名图形")
                action = menu.exec_(self.tree.viewport().mapToGlobal(position))

                shape_name = item.text(0)

                if action == copy_action:
                    new_name, ok = QInputDialog.getText(self, "复制图形", "输入新图形名称：")
                    if ok and new_name:
                        if new_name in self.geometry_pages:
                            self.info_box.append(f"名称 {new_name} 已存在，复制失败！")
                        else:
                            old_page = self.geometry_pages[shape_name]
                            new_page = GeometrySettingPage_2d(self.graphics_scene, old_page.shape_type, new_name)

                            for key, input_field in old_page.inputs.items():
                                if key in new_page.inputs:
                                    new_page.inputs[key].setText(input_field.text())

                            new_item = QTreeWidgetItem(self.geometry_root, [new_name])
                            new_item.setIcon(0, item.icon(0))
                            self.geometry_pages[new_name] = new_page
                            self.settings_stack.addWidget(new_page)
                            self.info_box.append(f"已复制图形 {shape_name} 为 {new_name}")

                elif action == rename_action:
                    new_name, ok = QInputDialog.getText(self, "重命名图形", "输入新名称：", text=shape_name)
                    if ok and new_name and new_name != shape_name:
                        if new_name in self.geometry_pages:
                            self.info_box.append(f"名称 {new_name} 已存在，重命名失败！")
                        else:
                            # 更新 Tree 文字
                            item.setText(0, new_name)

                            # 更新 geometry_pages 字典 key
                            page = self.geometry_pages.pop(shape_name)
                            page.shape_name = new_name
                            self.geometry_pages[new_name] = page

                            self.info_box.append(f"图形 {shape_name} 已重命名为 {new_name}")

                elif action == delete_action:
                    if shape_name in self.geometry_pages:
                        page = self.geometry_pages.pop(shape_name)
                        self.settings_stack.removeWidget(page)
                        self.geometry_root.removeChild(item)
                        self.info_box.append(f"图形 {shape_name} 已删除")

                # 不管是否有action，都在右键结束后重新触发一下左键逻辑，保证界面正常
        
        elif self.is_2d is not None and self.is_2d == False:
            if item.text(0) == "几何":
                new_cube_action = menu.addAction("新建长方体")
                new_sphere_action = menu.addAction("新建球体")
                new_cylinder_action = menu.addAction("新建圆柱体")
                new_cone_action = menu.addAction("新建圆锥体")

                action = menu.exec_(self.tree.viewport().mapToGlobal(position))

                if action in (new_cube_action, new_sphere_action, new_cylinder_action, new_cone_action):
                    if action == new_cube_action:
                        shape_type = "长方体"
                    elif action == new_sphere_action:
                        shape_type = "球体"
                    elif action == new_cylinder_action:
                        shape_type = "圆柱体"
                    elif action == new_cone_action:
                        shape_type = "圆锥体"

                    shape_name, ok = QInputDialog.getText(self, "命名图形", f"请输入{shape_type}名称：")
                    if ok and shape_name:
                        self.add_new_shape(shape_type, shape_name)

            
            elif item.parent() == self.geometry_root:
                copy_action = menu.addAction("复制图形")
                delete_action = menu.addAction("删除图形")
                rename_action = menu.addAction("重命名图形")
                action = menu.exec_(self.tree.viewport().mapToGlobal(position))

                shape_name = item.text(0)

                if action == copy_action:
                    new_name, ok = QInputDialog.getText(self, "复制图形", "输入新图形名称：")
                    if ok and new_name:
                        if new_name in self.geometry_pages:
                            self.info_box.append(f"名称 {new_name} 已存在，复制失败！")
                        else:
                            old_page = self.geometry_pages[shape_name]
                            new_page = GeometrySettingPage_2d(self.graphics_view, old_page.shape_type, new_name, is_2d=False)

                            for key, input_field in old_page.inputs.items():
                                if key in new_page.inputs:
                                    new_page.inputs[key].setText(input_field.text())

                            new_item = QTreeWidgetItem(self.geometry_root, [new_name])
                            new_item.setIcon(0, item.icon(0))
                            self.geometry_pages[new_name] = new_page
                            self.settings_stack.addWidget(new_page)
                            self.info_box.append(f"已复制图形 {shape_name} 为 {new_name}")

                elif action == rename_action:
                    new_name, ok = QInputDialog.getText(self, "重命名图形", "输入新名称：", text=shape_name)
                    if ok and new_name and new_name != shape_name:
                        if new_name in self.geometry_pages:
                            self.info_box.append(f"名称 {new_name} 已存在，重命名失败！")
                        else:
                            # 更新 Tree 文字
                            item.setText(0, new_name)

                            # 更新 geometry_pages 字典 key
                            page = self.geometry_pages.pop(shape_name)
                            page.shape_name = new_name
                            self.geometry_pages[new_name] = page

                            self.info_box.append(f"图形 {shape_name} 已重命名为 {new_name}")

                elif action == delete_action:
                    if shape_name in self.geometry_pages:
                        page = self.geometry_pages.pop(shape_name)
                        self.settings_stack.removeWidget(page)
                        self.geometry_root.removeChild(item)
                        self.info_box.append(f"图形 {shape_name} 已删除")

    def add_new_shape(self, shape_type, shape_name):
        if self.is_2d is None:
            QMessageBox.warning(self, "未选择建模维度", "请先选择建模维度！")
            return
        
        if shape_name in self.geometry_pages:
            self.info_box.append(f"名称 {shape_name} 已存在，不能重复！")
            return

        shape_item = QTreeWidgetItem(self.geometry_root, [shape_name])
        self.tree.expandItem(self.geometry_root)

        if self.is_2d:
            page = GeometrySettingPage_2d(self.plotter, shape_type, shape_name)
        else:
            page = GeometrySettingPage_3d(self.plotter, shape_type, shape_name) # 先使用2D的界面
        self.geometry_pages[shape_name] = page
        self.settings_stack.addWidget(page)

        self.info_box.append(f"创建了新的{shape_type}: {shape_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
