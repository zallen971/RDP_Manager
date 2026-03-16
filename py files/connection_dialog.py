from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDialogButtonBox, QCheckBox
)

class ConnectionDialog(QDialog):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("Edit Connection" if connection else "New Connection")
        self.setMinimumWidth(350)
        self._build_ui()
        if connection:
            self.populate(connection)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Server")
        form.addRow("Name", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["ssh", "rdp"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Type", self.type_combo)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("192.168.1.1")
        form.addRow("Host", self.host_edit)

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        form.addRow("Port", self.port_spin)

        self.username_edit = QLineEdit()
        form.addRow("Username", self.username_edit)


        self.save_password_check = QCheckBox("Save password to keychain")
        self.save_password_check.setChecked(True)
        form.addRow("", self.save_password_check)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Leave blank to enter on connect")
        form.addRow("Password", self.password_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox (
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_type_changed(self, type_):
        self.port_spin.setValue(22 if type_ == "ssh" else 3389)

    def get_values(self):
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "host": self.host_edit.text().strip(),
            "port": self.port_spin.value(),
            "username": self.username_edit.text().strip(),
            "password": self.password_edit.text(),
            "save_password": self.save_password_check.isChecked(),
        }
    
    def _populate(self, c):
        self.name_edit.setText(c["name"])
        idx = self.type_combo.findText(c["type"])
        if idx >= 0:
            self.type_combo.setCurrentindex(idx)
        self.host_edit.setText(c["host"])
        self.port_spin.setValue(c["port"])
        self.username_edit.setText(c["username"] or "")
    