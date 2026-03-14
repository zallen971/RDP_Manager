import sys
from PyQt6.QtWidgets import (
     QApplication, QMainWindow, QWidget, QListWidget, 
     QHBoxLayout, QPushButton)
import database
from connection_dialog import ConnectionDialog

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
sidebar = QListWidget()
sidebar.setMaximumWidth(250)

# Load from database 
connections = database.get_all_connections()
for c in connections:
    sidebar.addItem(c["name"])

# Right panel
right_panel = QWidget()

layout.addWidget(sidebar)
layout.addWidget(right_panel)

def on_connection_clicked(item):
    print(f"Clicked: {item.text()}")
    print(f"Row: {sidebar.row(item)}")

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

add_btn = QPushButton("+ Add")
add_btn.clicked.connect(open_add_dialog)
layout.addWidget(add_btn)

window.show()
sys.exit(app.exec())