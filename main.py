import sys
from PyQt6.QtWidgets import (
     QApplication, QMainWindow, QWidget, QListWidget, QHBoxLayout
)

import database

app = QApplication(sys.argv)

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

window.show()
sys.exit(app.exec())