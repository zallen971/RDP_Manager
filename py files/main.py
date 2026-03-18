import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QPushButton, QVBoxLayout,
    QInputDialog, QLineEdit, QTabWidget, QMenu, QMessageBox, QAbstractItemView,
    QLabel, QStatusBar
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
import database
from connection_dialog import ConnectionDialog
from ssh_tab import SSHTab
from rdp_launcher import launch_rdp
import credentials
from sidebar import SidebarTree

app = QApplication(sys.argv)
app.setStyle("Fusion")
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
palette.setColor(QPalette.ColorRole.WindowText, QColor("#cccccc"))
palette.setColor(QPalette.ColorRole.Base, QColor("#252526"))
palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1e1e1e"))
palette.setColor(QPalette.ColorRole.Text, QColor("#cccccc"))
palette.setColor(QPalette.ColorRole.Button, QColor("#2d2d2d"))
palette.setColor(QPalette.ColorRole.ButtonText, QColor("#cccccc"))
palette.setColor(QPalette.ColorRole.Highlight, QColor("#094771"))
palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
app.setPalette(palette)

app.setStyleSheet("""
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #cccccc;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }

    QTreeWidget {
        background-color: #252526;
        border: none;
        padding: 4px;
        outline: none;
        color: #cccccc;
    }
    QTreeWidget::item {
        padding: 3px 4px;
        border-radius: 3px;
    }
    QTreeWidget::item:hover {
        background-color: #2a2d2e;
    }
    QTreeWidget::item:selected {
        background-color: #094771;
        color: #ffffff;
    }

    QPushButton {
        background-color: #2d2d2d;
        color: #cccccc;
        border: 1px solid #454545;
        border-radius: 3px;
        padding: 4px 10px;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
        border: 1px solid #555555;
    }
    QPushButton:pressed {
        background-color: #094771;
    }

    QTabWidget::pane {
        border: none;
        background-color: #1e1e1e;
    }
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #969696;
        border: none;
        padding: 6px 16px;
        margin-right: 2px;
        font-size: 12px;
        min-width: 100px;
    }
    QTabBar::tab:selected {
        background-color: #1e1e1e;
        color: #ffffff;
        border-top: 2px solid #0e639c;
    }
    QTabBar::tab:hover {
        background-color: #252526;
        color: #cccccc;
    }

    QLineEdit, QSpinBox, QComboBox {
        background-color: #3c3c3c;
        color: #cccccc;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 4px 8px;
        selection-background-color: #094771;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 1px solid #0e639c;
    }

    QScrollBar:vertical {
        background: #1e1e1e;
        width: 6px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #424242;
        border-radius: 3px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #555555;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }

    QDialog {
        background-color: #252526;
    }
    QMenu {
        background-color: #252526;
        border: 1px solid #454545;
        padding: 2px;
    }
    QMenu::item {
        padding: 5px 20px;
        border-radius: 3px;
    }
    QMenu::item:selected {
        background-color: #094771;
    }
    QCheckBox::indicator {
        width: 13px;
        height: 13px;
        border: 1px solid #555555;
        border-radius: 2px;
        background: #3c3c3c;
    }
    QCheckBox::indicator:checked {
        background: #0e639c;
        border: 1px solid #0e639c;
    }
    QMessageBox {
        background-color: #252526;
    }
    QLabel {
        color: #cccccc;
    }
""")

database.init_db()

window = QMainWindow()
window.setWindowTitle("PyRDM")
window.resize(1100, 680)

central = QWidget()
window.setCentralWidget(central)

main_layout = QHBoxLayout(central)

# Sidebar
sidebar_container = QWidget()
sidebar_container.setStyleSheet("background-color: #252526; border-right: 1px solid #3c3c3c;")
sidebar_container.setMaximumWidth(250)
sidebar_layout = QVBoxLayout(sidebar_container)
sidebar_layout.setContentsMargins(0, 0, 0, 0)
sidebar_layout.setSpacing(4)

sidebar = SidebarTree()
sidebar.setHeaderHidden(True)
sidebar.setDragEnabled(True)
sidebar.setAcceptDrops(True)
sidebar.setDropIndicatorShown(True)
sidebar.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

connections = []


def refresh_sidebar():
    sidebar.clear()
    groups = database.get_all_groups()
    connections.clear()
    connections.extend(database.get_all_connections())

    group_items = {}
    for g in groups:
        group_item = QTreeWidgetItem([f"📁 {g['name']}"])
        group_item.setData(0, Qt.ItemDataRole.UserRole, {"_type": "group", "id": g["id"]})
        sidebar.addTopLevelItem(group_item)
        group_item.setExpanded(True)
        group_items[g["id"]] = group_item

    for c in connections:
        icon = "🖥 " if c["type"] == "rdp" else "🖵 "
        conn_item = QTreeWidgetItem([icon + c["name"]])
        conn_item.setData(0, Qt.ItemDataRole.UserRole, {"_type": "connection", "id": c["id"]})
        if c.get("group_id") and c["group_id"] in group_items:
            group_items[c["group_id"]].addChild(conn_item)
        else:
            sidebar.addTopLevelItem(conn_item)
            
    # Update status bar
    if 'status_bar' in globals():
        status_bar.showMessage(f"  {len(groups)} groups   {len(connections)} connections")

refresh_sidebar()

btn_layout = QHBoxLayout()
add_btn = QPushButton("+ Add")
add_group_btn = QPushButton("+ Group")
btn_layout.addWidget(add_btn)
btn_layout.addWidget(add_group_btn)

sidebar_layout.addWidget(sidebar)
sidebar_layout.addLayout(btn_layout)

# Tabs
welcome = QLabel("Double-click a connection to open a session")
welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
welcome.setStyleSheet("color: #555555; font-size: 14px;")
tabs = QTabWidget()
tabs.setTabsClosable(True)
tabs.setMinimumWidth(600)
tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index) if index != 0 else None)

tabs.addTab(welcome, "Home")
tabs.tabBar().setTabButton(0, tabs.tabBar().ButtonPosition.RightSide, None)

main_layout.addWidget(sidebar_container)
main_layout.addWidget(tabs)


def on_connection_clicked(item, column):
    data = item.data(0, Qt.ItemDataRole.UserRole)
    if not data or data["_type"] == "group":
        return

    connection = next((c for c in connections if c["id"] == data["id"]), None)
    if not connection:
        return

    password = credentials.get_password(connection["id"])

    if not password:
        password, ok = QInputDialog.getText(
            window,
            "Password",
            f"Password for {connection['username']}@{connection['host']}:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return

    if connection["type"] == "ssh":
        tab = SSHTab(connection, password)
        tab_index = tabs.addTab(tab, connection["name"])
        tabs.setCurrentIndex(tab_index)

    elif connection["type"] == "rdp":
        success, message = launch_rdp(connection, password)
        if not success:
            QMessageBox.critical(window, "RDP Error", message)


def open_edit_dialog(connection):
    dlg = ConnectionDialog(window, connection)
    if dlg.exec():
        values = dlg.get_values()
        database.update_connection(
            connection["id"], values["name"], values["type"],
            values["host"], values["port"], values["username"], values["group_id"]
        )
        if values["save_password"] and values["password"]:
            credentials.save_password(connection["id"], values["password"])
        refresh_sidebar()


def delete_connection(connection):
    reply = QMessageBox.question(
        window, "Delete",
        f"Delete '{connection['name']}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
        credentials.delete_password(connection["id"])
        database.delete_connection(connection["id"])
        refresh_sidebar()


def show_context_menu(pos):
    item = sidebar.itemAt(pos)
    if not item:
        return

    data = item.data(0, Qt.ItemDataRole.UserRole)
    if not data:
        return

    menu = QMenu()

    if data["_type"] == "group":
        delete_group_action = menu.addAction("Delete Group")
        action = menu.exec(sidebar.mapToGlobal(pos))
        if action == delete_group_action:
            database.delete_group(data["id"])
            refresh_sidebar()
    else:
        connection = next((c for c in connections if c["id"] == data["id"]), None)
        if not connection:
            return
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec(sidebar.mapToGlobal(pos))
        if action == edit_action:
            open_edit_dialog(connection)
        elif action == delete_action:
            delete_connection(connection)


def open_add_dialog():
    dlg = ConnectionDialog(window)
    if dlg.exec():
        values = dlg.get_values()
        conn_id = database.add_connection(
            values["name"], values["type"], values["host"],
            values["port"], values["username"], values["group_id"]
        )
        if values["save_password"] and values["password"]:
            credentials.save_password(conn_id, values["password"])
        refresh_sidebar()


def open_add_group_dialog():
    name, ok = QInputDialog.getText(window, "New Group", "Group name:")
    if ok and name.strip():
        database.add_group(name.strip())
        refresh_sidebar()

def on_item_dropped(conn_id, new_group_id):
    database.update_connection_group(conn_id, new_group_id)
    print(f"Saved connection {conn_id} to group {new_group_id}")
    refresh_sidebar()


sidebar.itemDoubleClicked.connect(on_connection_clicked)
sidebar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
sidebar.customContextMenuRequested.connect(show_context_menu)
sidebar.item_dropped.connect(on_item_dropped)

add_btn.clicked.connect(open_add_dialog)
add_group_btn.clicked.connect(open_add_group_dialog)

status_bar = QStatusBar()
status_bar.setStyleSheet("background-color: #094771; color: #ffffff; font-size: 12px;")
window.setStatusBar(status_bar)

def update_status():
    total = len(connections)
    groups = database.get_all_groups()
    status_bar.showMessage(f"  {len(groups)} groups   {total} connections")

window.show()
sys.exit(app.exec())