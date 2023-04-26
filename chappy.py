import sys
from PyQt5.QtGui import (
    QTextCursor,
    QPixmap,
    QPalette,
    QBrush,
    QMovie
)
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
    QTextEdit,
    QPushButton,
    QDialog
)
from PyQt5.QtCore import Qt
from chatgpt import chat_gpt
import time
from hotkey import send_clipboard_contents

#setup ctrl-alt-v hotkey to send clipboard contents to app
send_clipboard_contents()


# Custom text edit for handling key press events
class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
        elif event.key() == Qt.Key_Return:
            self.parent().send_message()
        else:
            super().keyPressEvent(event)
# Chat widget for managing user input, chat history, and interactions with the chatbot
class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.ensureCursorVisible()
        self.chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.chat_history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_history.setStyleSheet(
            "QTextEdit {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
        )
        self.user_input = CustomTextEdit()
        self.user_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.user_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_input.setStyleSheet(
            "QTextEdit {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
        )
        self.user_input.setFixedHeight(50)
        self.user_input.textChanged.connect(self.adjust_user_input_height)
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "QPushButton {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
            "QPushButton:hover {background-color: #430351;}"
        )
        self.send_button.clicked.connect(self.send_message)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.user_input)
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.send_button)
        self.large_text_input_button = QPushButton("Large Text Input")
        self.large_text_input_button.setStyleSheet(
            "QPushButton {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
            "QPushButton:hover {background-color: #430351;}"
        )
        self.large_text_input_button.clicked.connect(self.open_large_text_input)
        self.button_layout.addWidget(self.large_text_input_button)
        self.large_text_input_button.clicked.connect(self.open_large_text_input)
        self.button_layout.addWidget(self.large_text_input_button)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)
        self.loading_label = QLabel(self)
        self.loading_movie = QMovie("docs/gears.png")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        self.loading_label.move(300, 200)
        self.setFocusProxy(self.user_input)

# Connect textChanged signal to adjust height of the user input field
    def adjust_user_input_height(self):
        cursor = self.user_input.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.user_input.setTextCursor(cursor)
        height = self.user_input.document().size().height()
        if height != self.user_input.height():
            self.user_input.setFixedHeight(round(height))


# Interact with the ChatGPT model to get the response
    def send_message(self, user_message=None):
        if user_message is None:
            user_message = self.user_input.toPlainText()
        self.user_input.clear()
        if user_message.strip():
            self.chat_history.setPlainText(self.chat_history.toPlainText() + "You: " + user_message + "\n")
            self.chat_history.moveCursor(QTextCursor.End)
            self.show_loading_animation()
            response = chat_gpt(user_message.strip())
            self.hide_loading_animation()
            self.chat_history.setPlainText(self.chat_history.toPlainText() + "Assistant: " + response + "\n")
            self.chat_history.moveCursor(QTextCursor.End)


    def open_large_text_input(self):
        self.large_text_input_dialog = LargeTextInputDialog(self)
        self.large_text_input_dialog.show()

# Start loading animation while waiting for the chatbot's response
    def show_loading_animation(self):
        self.loading_movie.start()
        self.loading_label.show()

# Stop loading animation and display the response from ChatGPT
    def hide_loading_animation(self):
        self.loading_movie.stop()
        self.loading_label.hide()

# Scroll area containing chat_widget, required for auto-resizing and scrollbar functionality
class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea {background-color: #430351;}")
        self.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_widget.setAutoFillBackground(False)
        self.content_widget_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_widget_layout)
        self.setWidget(self.content_widget)
        self.chat_widget = ChatWidget()
        self.content_widget_layout.addWidget(self.chat_widget)

# Creating and adding chat_widget to the content_widget_layout
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap('docs/meg.jpg')
        self.setWindowTitle("Chappy - Coding Assistant")
        self.resize(600, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.scroll_area = ScrollArea()
        self.layout.addWidget(self.scroll_area)
        self.update_background_image()

# MainWindow for the application containing a background image, scroll area, and QVBoxLayout
    def update_background_image(self):
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(self.background_image.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

# Update the background image whenever the window is resized
    def resizeEvent(self, event):
        self.update_background_image()
        super().resizeEvent(event)

# Dialog widget for large input text messages
class LargeTextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Large Text Input")
        self.resize(600, 400)
        self.text_input = QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet(
            "QTextEdit {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
        )
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "QPushButton {background-color: #430351; color: #f5f5f5; font-size: 12pt; font-weight: bold;}"
            "QPushButton:hover {background-color: #430351;}"
        )
        self.send_button.clicked.connect(self.send_large_text)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

# Send the text from the large input text dialog to the chat widget
    def send_large_text(self):
        large_text = self.text_input.toPlainText()
        if large_text.strip():
            self.parent().send_message(large_text)
            self.close()

# Main function responsible for setting up and executing the application
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()