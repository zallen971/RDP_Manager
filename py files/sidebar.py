from PyQt6.QtWidgets import QTreeWidget
from PyQt6.QtCore import pyqtSignal, Qt


class SidebarTree(QTreeWidget):
    item_dropped = pyqtSignal(int, object) # conn_id, group_id or None

    def dropEvent(self, event):
        dragged_item = self.currentItem()
        if not dragged_item:
            super().dropEvent(event)
            return
        
        dragged_data = dragged_item.data(0, Qt.ItemDataRole.UserRole)
        if not dragged_data or dragged_data["_type"] != "connection":
            super().dropEvent(event)
            return
        
        conn_id = dragged_data["id"]

        # Let Qt handle the visual move first
        super().dropEvent(event)


        # Determine the new parent
        new_parent = dragged_item.parent()
        if new_parent:
            parent_data = new_parent.data(0, Qt.ItemDataRole.UserRole)
            if parent_data and parent_data["_type"] == "group":
                self.item_dropped.emit(conn_id, parent_data["id"])
                return
            
            self.item_dropped.emit(conn_id, None)