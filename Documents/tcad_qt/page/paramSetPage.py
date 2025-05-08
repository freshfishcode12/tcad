from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMenu, QLabel, QAbstractItemView
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve


class ParameterSettingPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # 表格
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["名称", "表达式", "值", "描述"])
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  # 右键菜单
        self.table.customContextMenuRequested.connect(self.open_menu)
        self.init_table_data()
        self.table.cellChanged.connect(self.check_last_row)    # 监控用户是否在编辑最后一行

        layout.addWidget(self.table)

    def init_table_data(self):
        """初始化表格数据"""
        data = [
            ("Cu_resis", "2.2e-8", "2.2e-8", "电阻率"),
            ("E", "1.60e-19", "1.6e-19", "电荷量"),
            ("Z", "10", "10", "点电荷有效模型")
        ]
        for name, expr, value, desc in data:
            self.add_row(name, expr, value, desc)
        self.add_row()  # 最后加一个空白行

    def add_row(self, name="", expr="", value="", desc=""):
        """添加一行"""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(name))
        self.table.setItem(row_position, 1, QTableWidgetItem(expr))
        self.table.setItem(row_position, 2, QTableWidgetItem(value))
        self.table.setItem(row_position, 3, QTableWidgetItem(desc))

    def check_last_row(self, row, column):
        """监控是否在最后一行填了内容"""
        if row == self.table.rowCount() - 1:
            # 检查这一行有没有被填写
            for col in range(4):
                item = self.table.item(row, col)
                if item and item.text().strip() != "":
                    # 在最后一行填了内容，就新增一行
                    self.add_row()
                    break
            
    def show_context_menu(self, pos):
        row = self.table.currentRow()

        # 不在任何行就直接返回（比如空白区域点了右键）
        if row == -1:
            return

        menu = QMenu(self)

        # 设置菜单样式：放大 + 悬停高亮
        menu.setStyleSheet("""
            QMenu {
                font-size: 16px;
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                background-color: white;
            }
            QMenu::item:selected {
                background-color: #3399ff;
                color: white;
            }
            QMenu::item:disabled {
                color: gray;  /* 显式设置禁用项为灰色 */
            }
        """)

        move_up_action = menu.addAction("上移")
        delete_action = menu.addAction("删除")
        move_down_action = menu.addAction("下移")

        # 动态禁用不能操作的行为
        if row == 0:
            move_up_action.setEnabled(False)  # ✅ 第一行不能上移，字体自动灰色

        if row >= self.table.rowCount() - 2:
            move_down_action.setEnabled(False)  # ✅ 倒数第二行及以下不能下移

        if row >= self.table.rowCount() - 1:  # 最后一行是空白，不能删除
            delete_action.setEnabled(False)

        # 弹出菜单
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))

        if action == delete_action:
            self.delete_selected_rows()
        elif action == move_up_action:
            self.move_row_up()
        elif action == move_down_action:
            self.move_row_down()


    def open_menu(self, position):
        """右键菜单"""
        index = self.table.indexAt(position)
        if not index.isValid():
            return

        self.table.selectRow(index.row())  # 确保右键点击那一行被选中
        self.show_context_menu(position)
        
        # menu = QMenu()
        # delete_action = QAction("删除选中行", self)
        # delete_action.triggered.connect(self.delete_selected_rows)
        # menu.addAction(delete_action)
        # menu.addAction("上移", self.move_row_up)
        # menu.addAction("下移", self.move_row_down)

        # menu.exec_(self.table.viewport().mapToGlobal(position))

    def delete_selected_rows(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        last_row = self.table.rowCount() - 1
        for row in selected_rows:
            if row < last_row:  # 只删非空白行
                self.table.removeRow(row)


    def move_row_up(self):
        row = self.table.currentRow()
        if row > 0:
            self.animate_row_move(row, row-1)

    def move_row_down(self):
        row = self.table.currentRow()
        if row < self.table.rowCount() - 2:
            self.animate_row_move(row, row+1)

    def animate_row_move(self, from_row, to_row):
        # 先保存两行的内容
        from_data = [self.table.item(from_row, col).text() if self.table.item(from_row, col) else "" for col in range(self.table.columnCount())]
        to_data = [self.table.item(to_row, col).text() if self.table.item(to_row, col) else "" for col in range(self.table.columnCount())]

        # 小动画：让行高轻微变化（假装动了一下）
        anim = QPropertyAnimation(self.table, b"rowHeight")
        anim.setDuration(200)  # 0.2秒
        anim.setStartValue(30)  # 原来高度
        anim.setEndValue(40)    # 稍微高一点
        anim.setEasingCurve(QEasingCurve.OutQuad)  # 缓出动画
        anim.start()
        self.anim = anim  # 保存，不然会被垃圾回收掉动画消失

        # 交换数据
        for col in range(self.table.columnCount()):
            self.table.setItem(from_row, col, QTableWidgetItem(to_data[col]))
            self.table.setItem(to_row, col, QTableWidgetItem(from_data[col]))

        # 重新选中移动后的那一行
        self.table.selectRow(to_row)