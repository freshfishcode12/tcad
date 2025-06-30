from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem,
    QMenu, QSizePolicy, QAbstractItemView
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
import re
import math

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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


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
        """监控表达式变动，解析并计算带单位表达式"""
        if column == 1 and row != self.table.rowCount() - 1:  # 第二列表达式修改
            expr_item = self.table.item(row, 1)
            if expr_item:
                expr_text = expr_item.text().strip()
                try:
                    variables = self.get_defined_variables()
                    value_with_unit = self.evaluate_expression_with_units(expr_text, variables)
                    self.table.setItem(row, 2, QTableWidgetItem(value_with_unit))
                except Exception as e:
                    self.table.setItem(row, 2, QTableWidgetItem(f"错误: {e}"))

        # 检查是否在最后一行输入
        if row == self.table.rowCount() - 1:
            for col in range(4):
                item = self.table.item(row, col)
                if item and item.text().strip() != "":
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

    def evaluate_expression_with_units(self, expr, variables=None):
        if variables is None:
            variables = {}

        unit_factors = {
            'm': 1,
            'cm': 1e-2,
            'mm': 1e-3,
            'um': 1e-6,
            'nm': 1e-9,
            'pm': 1e-12,
        }

        # 单位乘法中幂次数量收集
        unit_power = {}

        def unit_to_m_factor(unit_str):
            """支持单位和幂，如 um, cm^2 等"""
            print(f"处理单位: {unit_str}")
            if unit_str in unit_factors:
                power = 1
                base = unit_str
            elif '^' in unit_str:
                base, p = unit_str.split('^')
                power = int(p)
                if base not in unit_factors:
                    raise ValueError(f"未知单位: {base}")
            else:
                raise ValueError(f"未知单位: {unit_str}")

            factor = unit_factors[base] ** power
            unit_power[base] = unit_power.get(base, 0) + power
            return factor

        def replace_units(match):
            number = match.group(1)
            unit_expr = match.group(2)
            # print(f"替换单位: {number}, {unit_expr}")
            factor = unit_to_m_factor(unit_expr)
            return f"({number}) * ({factor})"

        float_unit_pattern = r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*\[\s*([\w^]+)\s*\]'
        expr_with_units = re.sub(float_unit_pattern, replace_units, expr)
        # print(f"替换后的表达式: {expr_with_units}")

        # 替换变量（包含单位处理）
        for name, val_info in variables.items():
            val = val_info["value"]
            unit = val_info["unit"]

            if unit and unit != "1":
                try:
                    factor = unit_to_m_factor(unit)
                    replacement = f"({val} * {factor})"
                except Exception as e:
                    print(f"单位解析错误: {e}")
                    replacement = f"({val})"
            else:
                replacement = f"({val})"

            expr_with_units = re.sub(rf'\b{name}\b', replacement, expr_with_units)
            print(f"替换变量: {name} -> {replacement}, 表达式: {expr_with_units}")

        result = eval(expr_with_units, {"__builtins__": {}, "math": math})

        # 合并单位显示（统一用 m, m^2, m^3 等）
        final_unit = ""
        total_power = sum(unit_power.values())
        if total_power == 1:
            final_unit = "m"
        elif total_power > 1:
            final_unit = f"m^{total_power}"
        return f"{result:.6g} {final_unit}"

    
    def get_defined_variables(self):
        variables = {}
        row_count = self.table.rowCount()
        for row in range(row_count - 1):  # 不包含最后空白行
            name_item = self.table.item(row, 0)
            value_item = self.table.item(row, 2)
            if name_item and value_item:
                name = name_item.text().strip()
                value_text = value_item.text().strip()
                parts = value_text.split()
                try:
                    value = float(parts[0])
                    unit = parts[1] if len(parts) > 1 else "1"
                    variables[name] = {"value": value, "unit": unit}
                except:
                    continue
        return variables
    
    def get_parameters(self):
        """
        返回当前表格中定义的所有有效参数：
        格式为字典：{name: {"value": float, "unit": str, "desc": str}}
        """
        parameters = {}
        row_count = self.table.rowCount()
        for row in range(row_count - 1):  # 忽略最后一行空白行
            name_item = self.table.item(row, 0)
            value_item = self.table.item(row, 2)
            desc_item = self.table.item(row, 3)

            if name_item and value_item:
                name = name_item.text().strip()
                value_text = value_item.text().strip()
                desc = desc_item.text().strip() if desc_item else ""

                parts = value_text.split()
                try:
                    value = float(parts[0])
                    unit = parts[1] if len(parts) > 1 else "1"
                    parameters[name] = {
                        "value": value,
                        "unit": unit,
                        "desc": desc
                    }
                except:
                    continue  # 跳过无效数据行

        return parameters




