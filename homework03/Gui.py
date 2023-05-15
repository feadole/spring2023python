# Gui.py

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QLabel, QDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests
import sys
import traceback


class NetworkThread(QThread):
    message_received = pyqtSignal(dict)
    status_updated = pyqtSignal(int, int)

    def __init__(self, server_url):
        super().__init__()
        self.server_url = server_url

    def run(self):
        last_message_id = 0
        while not self.isInterruptionRequested():
            try:
                response = requests.get(f'{self.server_url}/messages/{last_message_id}')
                if response.status_code == 200:
                    messages = response.json().get('messages')
                    for message in messages:
                        self.message_received.emit(message)
                        last_message_id = message['id']
                user_count, message_count = self.get_status()
                self.status_updated.emit(user_count, message_count)
                self.msleep(5000)  # Sleep for 5 seconds between requests
            except requests.exceptions.RequestException as e:
                print(f"Network request failed: {e}")

    def get_status(self):
        try:
            response = requests.get(f'{self.server_url}/status')
            if response.status_code == 200:
                status = response.json()
                user_count = status.get('user_count', 0)
                message_count = status.get('message_count', 0)
                return user_count, message_count
        except requests.exceptions.RequestException as e:
            print(f"Network request failed: {e}")
        return 0, 0


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Admin Login')
        self.setFixedSize(200, 100)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton('Login')
        login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Admin Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        password = self.password_input.text()
        self.accept()


class MessengerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Messenger')
        self.setGeometry(100, 100, 400, 500)

        # Create a text area to display messages
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Create a text input field for user input
        self.input_field = QLineEdit()

        # Create a send button
        self.send_button = QPushButton('Send')

        # Create labels for status information
        self.user_count_label = QLabel()
        self.message_count_label = QLabel()

        # Create an admin button
        self.admin_button = QPushButton('Admin Login')

        # Set style sheet for a modern and clean appearance
        self.setStyleSheet('''
            QWidget {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    padding: 5px;
    font-size: 12px;
}
QLabel {
    font-size: 12px;
}
''')

        # Create a layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        layout.addWidget(self.user_count_label)
        layout.addWidget(self.message_count_label)
        layout.addWidget(self.admin_button)

        # Set the layout margins and spacing
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialize the server URL
        self.server_url = 'http://127.0.0.1:5000'  # Change to your server IP address

        # Create a network thread
        self.network_thread = NetworkThread(self.server_url)
        self.network_thread.message_received.connect(self.display_message)
        self.network_thread.status_updated.connect(self.update_status)
        self.network_thread.start()

        # Connect the signals to slots
        self.input_field.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)
        self.admin_button.clicked.connect(self.open_admin_login)

    def send_message(self):
        message = self.input_field.text()
        try:
            response = requests.post(f'{self.server_url}/message', data={'message': message})
            if response.status_code == 200:
                message_id = response.json().get('id')
                return message_id
        except requests.exceptions.RequestException as e:
            print(f"Network request failed: {e}")
        return None

    def display_message(self, message):
        content = message.get('content', '')
        self.text_area.append(content)

    def update_status(self, user_count, message_count):
        self.user_count_label.setText(f'Users Online: {user_count}')
        self.message_count_label.setText(f'Messages Sent: {message_count}')

    def open_admin_login(self):
        try:
            dialog = AdminLoginDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                password = dialog.password_input.text()
                if password == 'feadole':
                    self.admin_actions()
                else:
                    QMessageBox.warning(self, 'Login Failed', 'Incorrect admin password')
        except Exception as e:
            print(traceback.format_exc())

    def admin_actions(self):
        # Perform the necessary actions when the admin is logged in
        # For example, you can open a new window or perform admin-specific tasks
        QMessageBox.information(self, 'Login Successful', 'Admin logged in successfully')


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        messenger = MessengerGUI()
        messenger.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(traceback.format_exc())

