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
    QDialog,
    QFileDialog
)
from PyQt5.QtCore import Qt
from chatgpt import chat_gpt
import sys
from embeddings import(
    create_embedding,
    base_retriever,
    retriever,
    create_mass_embedding,
    memory_search
)

from langchain.utilities import SerpAPIWrapper




class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
        elif event.key() == Qt.Key_Return:
            self.parent().send_message()
        elif event.key() == Qt.Key_Up:
            if self.parent().message_history_index is None:
                self.parent().message_history_index += 1
            else:
                self.parent().cycle_message_history_backward()
        elif event.key() == Qt.Key_Down:
            if self.parent().message_history_index is None:
               self.parent().messsage_history_index += 1
            else:
                self.parent().cycle_message_history_forward()
        else:
            super().keyPressEvent(event)


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        self.message_history_array = []
        self.message_history_index = 0
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.chat_history = self.create_chat_history()
        self.layout.addWidget(self.chat_history)
        self.user_input = self.create_user_input()
        self.layout.addWidget(self.user_input)


        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.clear_button.clicked.connect(self.clear_chat_history)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.send_button)
        self.button_layout.addWidget(self.clear_button)

        self.large_text_input_button = QPushButton("L Input")
        self.large_text_input_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.large_text_input_button.clicked.connect(
            self.open_large_text_input)
        self.button_layout.addWidget(self.large_text_input_button)

        self.upload_button = QPushButton("Up File")
        self.upload_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.button_layout.addWidget(self.upload_button)

        self.loading_label = QLabel(self)
        self.loading_movie = QMovie("docs/gears.png")
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        self.loading_label.move(300, 200)

        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def create_chat_history(self):
        chat_history = QTextEdit()
        chat_history.setReadOnly(True)
        chat_history.ensureCursorVisible()
        chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        chat_history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chat_history.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-size: 12pt; font-weight: bold;")
        return chat_history

    def create_user_input(self):
        user_input = CustomTextEdit()
        user_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        user_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        user_input.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        user_input.setFixedHeight(50)
        user_input.textChanged.connect(self.adjust_user_input_height)
        return user_input

    def adjust_user_input_height(self):
        cursor = self.user_input.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.user_input.setTextCursor(cursor)
        height = self.user_input.document().size().height()
        if height != self.user_input.height():
            self.user_input.setFixedHeight(round(height))

    def send_message(self, user_message=None):
        if user_message is None:
            user_message = self.user_input.toPlainText()
        self.user_input.clear()
        if user_message.startswith("!"):
            self.run_command(user_message)
            self.user_input.clear()
        elif user_message.strip():
            self.message_history(self)
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + "You: " + user_message + "\n")

            self.chat_history.moveCursor(QTextCursor.End)
            self.show_loading_animation()
            response = chat_gpt(user_message)
            self.hide_loading_animation()
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + "Assistant: " + response + "\n")
            self.chat_history.moveCursor(QTextCursor.End)

    def open_large_text_input(self):
        self.large_text_input_dialog = LargeTextInputDialog(self)
        self.large_text_input_dialog.show()

    def show_loading_animation(self):
        self.loading_movie.start()
        self.loading_label.show()

    def hide_loading_animation(self):
        self.loading_movie.stop()
        self.loading_label.hide()

    def clear_chat_history(self):
        self.chat_history.clear()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select file to upload", "", "All Files (*);;PDF Files (*.pdf);;Text Files (*.txt)", options=options)
        if file_name:
            self.process_file(file_name)

    def process_file(self, file_path):
        create_embedding(file_path)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Embedding created, use !base_retrieve and !retrieve to pull relevant documents"))

    def base_retrieve(self, text):
        results = base_retriever(text)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Base search results: \n" + str(results)))

    def retrieve(self, text):
        results = retriever(text)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Compression search results: \n" + str(results)))

    def search_agent(self, text):
        results = SerpAPIWrapper().run(text)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Document store search results: \n" + str(results)))

    def mass_embed(self, file_path):
        create_mass_embedding(file_path)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Embedding created, use !base_retrieve and !retrieve to pull relevant documents"))
    def search_memory(self, text):
        results = memory_search(text)
        self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Memory search results: \n" + str(results)) + "\n\n")

    def run_command(self, text):
        if text == "!clear":
            self.message_history(message=text)
            self.clear_chat_history()
        elif text == "!save":
            self.message_history(message=text)
            self.save_chat_history()
        elif text == "!load":
            self.message_history(message=text)
            self.load_chat_history()
        elif text == "!exit":
            self.message_history(message=text)
            self.exit()
        elif text == "!help":
            self.message_history(message=text)
            self.display_help()
        elif text == "!large":
            self.message_history(message=text)
            self.open_large_text_input()
        elif text == "!embed":
            self.message_history(message=text)
            self.open_file_dialog()
        elif text.startswith("!mass_embed "):
            self.message_history(message=text)
            text = text.removeprefix("!mass_embed ")
            self.mass_embed(text)
        elif text.startswith("!base_retrieve "):
            self.message_history(message=text)
            text = text.removeprefix("!base_retrieve ")
            self.base_retrieve(text)
        elif text.startswith("!retrieve "):
            self.message_history(message=text)
            text = text.removeprefix("!retrieve ")
            self.retrieve(text)
        elif text.startswith("!search "):
            text = text.removeprefix("!search ")
            self.search_agent(text)
        elif text.startswith("!searchmem "):
            text = text.removeprefix("!searchmem ")
            self.search_memory(text)
        else:
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Command not found. Type !help for a list of commands\n"))

    def display_help(self):
        self.chat_history.setPlainText(
        self.chat_history.toPlainText() + str(
        """
        Commands:
        !help - Display this help message.
        !save - Save chat history.
        !load - Load chat history.
        !clear - Clear chat history.
        !exit - Exit the application.
        !embed - Upload a file to create embeddings.
        !base_retrieve - Uncompressed search of documents.
        !retrieve - Compressed search the documents.
        !search - Search the internet for context on a prompt then ask the prompt.
        !searchmem - Search the memory for context on a prompt then ask the prompt.
        !mass_embed - Upload multiple files to create embeddings. Follow with a space then folder path.
        """))

    def message_history(self, message):
        print(self.message_history_index)
        self.message_history_array.append(message)
        self.message_history_index += 1

    def cycle_message_history_forward(self):
        if self.message_history_index is None:
            self.message_history_index = 1
        elif self.message_history_index < len(self.message_history_array):

            self.message_history_index -= 1

        self.user_input.setPlainText(self.message_history_array[self.message_history_index - 1])

    def cycle_message_history_backward(self):
        if self.message_history_index is None:
            self.message_history_index = len(self.message_history_array) - 1
        elif self.message_history_index > 0:
            self.message_history_index -= 1

        self.user_input.setPlainText(self.message_history_array[self.message_history_index])

    def load_chat_history(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open chat history", "d:/5. coding/datastore/gptlogs/log.txt", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "r") as file:
                self.chat_history.setPlainText(file.read())


    def save_chat_history(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save chat history", "d:/5. coding/datastore/gptlogs/log.txt", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "a") as file:
                file.write(self.chat_history.toPlainText())

    def exit():
        sys.exit(0)

class ScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: 0px;")
        self.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_widget.setAutoFillBackground(False)
        self.content_widget_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_widget_layout)
        self.setWidget(self.content_widget)
        self.chat_widget = ChatWidget()
        self.content_widget_layout.addWidget(self.chat_widget)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap("docs/meg.jpg")
        self.setWindowTitle("Chappy - Coding Assistant")
        self.resize(600, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.scroll_area = ScrollArea()
        self.layout.addWidget(self.scroll_area)

    def update_background_image(self):
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(self.background_image.scaled(
            self.size())))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.update_background_image()
        super().resizeEvent(event)

class LargeTextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Large Text Input")
        self.resize(600, 400)

        self.text_input = QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 12pt; font-weight: bold;")

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.send_button.clicked.connect(self.send_large_text)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

    def send_large_text(self):
        large_text = self.text_input.toPlainText()
        if large_text.strip():
            self.parent().send_message(large_text)
            self.close()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()