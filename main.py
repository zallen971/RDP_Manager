import sys
from PyQt6.QtWidgets import (
     QApplication, QMainWindow, QWidget, QListWidget, 
     QHBoxLayout, QPushButton, QVBoxLayout,
     QInputDialog, QLineEdit, QTabWidget)
import database
from connection_dialog import ConnectionDialog
from ssh_tab import SSHTab

app = QApplication(sys.argv)
database.init_db()

window = QMainWindow()
window.setWindowTitle("PyRDM")
window.resize(1100, 680)


# Central widget
central = QWidget()
window.setCentralWidget(central)

# Main Layout - Horizontal
layout = QHBoxLayout(central)

# Sidebar
sidebar_container = QWidget()
sidebar_container.setMaximumWidth(250)
sidebar_layout = QVBoxLayout(sidebar_container)
sidebar_layout.setContentsMargins(0, 0, 0, 0)
sidebar_layout.setSpacing(4)

# Connection List
sidebar = QListWidget()

# Load from database 
connections = database.get_all_connections()
for c in connections:
    sidebar.addItem(c["name"])

# Add button
add_btn = QPushButton("+ Add")

# Add list and button into sidebar_layout
sidebar_layout.addWidget(sidebar)
sidebar_layout.addWidget(add_btn)


# Right panel
tabs = QTabWidget()
tabs.setTabsClosable(True)
tabs.setMinimumWidth(600)
tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))


layout.addWidget(sidebar_container)
layout.addWidget(tabs)

def on_connection_clicked(item):
    index = sidebar.row(item)
    connection = connections[index]
    if connection["type"] == "ssh":
        password, ok = QInputDialog.getText(
            window,
            "Password",
            f"Password for {connection['username']}@{connection['host']}:",
            QLineEdit.EchoMode.Password
        )
        if ok:
            tab = SSHTab(connection, password)
            tab_index = tabs.addTab(tab, connection["name"])
            tabs.setCurrentIndex(tab_index)

sidebar.itemClicked.connect(on_connection_clicked)


def open_add_dialog():
    dlg = ConnectionDialog(window)
    if dlg.exec():
        values = dlg.get_values()
        database.add_connection(
            values["name"], values["type"], values["host"],
            values["port"], values["username"]
        )
        sidebar.clear()
        connections.clear()
        connections.extend(database.get_all_connections())
        for c in connections:
            sidebar.addItem(c["name"])


add_btn.clicked.connect(open_add_dialog)


window.show()
sys.exit(app.exec())