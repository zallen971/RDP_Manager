import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QPushButton, QVBoxLayout,
    QInputDialog, QLineEdit, QTabWidget, QMenu, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
import database
from connection_dialog import ConnectionDialog
from ssh_tab import SSHTab
from rdp_launcher import launch_rdp
import credentials
from sidebar import SidebarTree

app = QApplication(sys.argv)
database.init_db()

window = QMainWindow()
window.setWindowTitle("PyRDM")
window.resize(1100, 680)

central = QWidget()
window.setCentralWidget(central)

main_layout = QHBoxLayout(central)

# Sidebar
sidebar_container = QWidget()
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

def on_item_Moved(item, old_parent):
    data = item.data(0, Qt.ItemDataRole.UserRole)
    if not data or data["_type"] != "connection":
        return
    
    new_parent = item.parent()
    if new_parent:
        parent_data = new_parent.data(0, Qt.ItemDataRole.UserRole)
        if parent_data and parent_data["_type"] == "group":
            database.update_connection_group(data["id"], parent_data["id"])
        else:
            database.update_connection_group(data["id"], None)

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

refresh_sidebar()

btn_layout = QHBoxLayout()
add_btn = QPushButton("+ Add")
add_group_btn = QPushButton("+ Group")
btn_layout.addWidget(add_btn)
btn_layout.addWidget(add_group_btn)

sidebar_layout.addWidget(sidebar)
sidebar_layout.addLayout(btn_layout)

# Tabs
tabs = QTabWidget()
tabs.setTabsClosable(True)
tabs.setMinimumWidth(600)
tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))

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
            values["host"], values["port"], values["username"]
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
            values["port"], values["username"]
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

window.show()
sys.exit(app.exec())