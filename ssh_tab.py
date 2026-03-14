import threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, QObject
import paramiko

class SSHWorker(QObject):
    output_received = pyqtSignal(str)
    connected = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, host, port, username, password):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._channel = None
        self._client = None
        self._running = False

    def connect(self):
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            self._channel = self._client.invoke_shell(term="xterm")
            self._running = True
            self.connected.emit()

            thread = threading.Thread(target=self._read_loop, daemon=True)
            thread.start()
        
        except Exception as e:
            self.error_occurred.emit(str(e))

    
    def _read_loop(self):
        import time
        while self._running and self._channel:
            try:
                if self._channel.recv_ready():
                    data = self._channel.recv(4096).decode("utf-8", errors="replace")
                    self.output_received.emit(data)
                if self._channel.closed:
                    break
                time.sleep(0.05)
            except Exception:
                break

    def send(self, text):
        if self._channel and not self._channel.closed:
            self._channel.send(text)
    
    def disconnect(self):
        self._running = False
        if self._channel:
            self._channel.close()
        if self._client:
            self._client.close()
    

class SSHTab(QWidget):
    def __init__(self, connection, password):
        super().__init__()
        self.connection = connection
        self.password = password
        self.worker = None
        self._build_ui()
        self._connect()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        self.output = QTextEdit()
        self.output.setReadOnly(True)
        font = QFont("Courier New", 11)
        self.output.setFont(font)
        self.output.setStyleSheet("background: #1e1e1e; color: #d4d4d4; border: none;")


        self.input_line = QLineEdit()
        self.input_line.setFont(font)
        self.input_line.setStyleSheet("background: #252526; color: #d4d4d4; border: none; padding: 4px;")
        self.input_line.setPlaceholderText("Type command and press Enter")
        self.input_line.setEnabled(False)
        self.input_line.returnPressed.connect(self._send_command)


        layout.addWidget(self.output)
        layout.addWidget(self.input_line)
    
    def _connect(self):
        self.output.append(f"Connection to {self.connection['host']}...")
        self.worker = SSHWorker(
            self.connection["host"],
            self.connection["port"],
            self.connection["username"],
            self.password

        )

        self.worker.output_received.connect(self.output.insertPlainText)
        self.worker.connected.connect(self._on_connected)
        self.worker.error_occurred.connect(self._on_error)
        
        thread = threading.Thread(target=self.worker.connect, daemon=True)
        thread.start()

    def _on_connected(self):
        self.output.append("Connected. \n")
        self.input_line.setEnabled(True)
        self.input_line.setFocus()

    def _on_error(self, message):
        self.output.append(f"\nError: {message}")

    def _send_command(self):
        cmd = self.input_line.text()
        self.input_line.clear()
        if self.worker:
            self.worker.send(cmd + "\n")
