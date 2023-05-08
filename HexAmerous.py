# -*- coding: utf-8 -*-
from ye_logger_of_yor import get_logger
from embed_project import run_embed_project
from scrappy import scrape_site, scrape_site_map
from custom_agents import (
    base_retriever,
    retriever,
    memory_search
)
from highlighter import CustomSyntaxHighlighter
import sys
import os
import random
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import (
    QTextCursor,
    QPixmap,
    QPalette,
    QBrush,
    QMovie,
    QIcon,
    QImage,
    QColor
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
    QFileDialog,
    QMessageBox,
    QComboBox,
    QSizeGrip,
    QStylePainter,
)
from chatgpt import (
    chat_gpt,
    change_selected_model
)
from embeddings import (
    create_embedding,
    create_mass_embedding,
)
from langchain import OpenAI, Wikipedia
from langchain.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, load_tools, Tool
from langchain.agents import AgentType
from langchain.agents.react.base import DocstoreExplorer
docstore = DocstoreExplorer(Wikipedia())


logger = get_logger()
# Global Variables
logger.info('loading langchain variables')
llm = OpenAI(temperature=0)
tools = [
    Tool(
        name="Search",
        func=docstore.search,
        description="useful for when you need to ask with search"
    ),
    Tool(name="Lookup",
         func=docstore.lookup,
         description="useful for when you need to ask with lookup"
         )
]
agent = initialize_agent(tools, llm, agent="react-docstore", verbose=True)
# Text Edit Widget
logger.info('CustomTextEdit')


class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)
    # Handling key events
    logger.info('keyPressEvent')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
        elif event.key() == Qt.Key_Return:
            self.parent().send_message('')
        elif event.key() == Qt.Key_Enter:
            self.parent().send_message('')
        else:
            super().keyPressEvent(event)


# Chat Widget
logger.info('loading chatwidget')


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    logger.info('init ui')
    # Initialize the UI

    def init_ui(self):
        self.create_widgets()
        self.set_widget_properties()
        self.create_widget_layouts()
        self.set_widget_connections()
        self.setLayout(self.layout)
    logger.info('create chat widget')
    # Create the widgets

    def create_widgets(self):
        self.layout = QVBoxLayout()
        self.chat_history = self.create_chat_history()
        self.user_input = self.create_user_input()
        self.send_button = QPushButton("Send")
        self.clear_button = QPushButton("Clear")
        self.large_text_input_button = QPushButton("L Input")
        self.upload_button = QPushButton("Up File")
        self.combo_box = QComboBox(self)
        self.button_layout = QHBoxLayout()
    logger.info('creating chat history')
    # Create the chat history widget

    def set_widget_properties(self):
        self.user_input.setFocus()
        self.send_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;")
        self.clear_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9;font-family: 'Cascadia Code';  font-size: 14pt; font-weight: bold; height: 50px; width: 100px;")
        self.large_text_input_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;")
        self.upload_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;")
        self.combo_box.addItem("GPT-3.5-Turbo")
        self.combo_box.addItem("GPT-4")
        self.combo_box.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;height: 50px; width: 100px;")
    logger.info('creating layout')
    # Create the layout

    def create_widget_layouts(self):
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.combo_box)
        self.button_layout.addWidget(self.send_button)
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.large_text_input_button)
        self.button_layout.addWidget(self.upload_button)
        self.layout.addLayout(self.button_layout)

    logger.info('creating event connections')
    # Create the event connections

    def set_widget_connections(self):
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_chat_history)
        self.large_text_input_button.clicked.connect(
            self.open_large_text_input)
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.combo_box.currentIndexChanged.connect(
            self.on_combobox_changed)
    logger.info('change drop down menu')
    # Drop down menu change

    def on_combobox_changed(self, index):
        selected_option = self.combo_box.itemText(index)
        change_selected_model(selected_option)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + selected_option + "\n\n")
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('chat history options')
    # Create Chat History

    def create_chat_history(self):
        chat_history = QTextEdit()
        chat_history.setReadOnly(True)
        chat_history.ensureCursorVisible()
        chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        chat_history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        custom_highlighter = CustomSyntaxHighlighter(chat_history.document())
        chat_history.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.8); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        return chat_history
    logger.info('create user input')
    # Create User Input

    def create_user_input(self):
        user_input = CustomTextEdit()
        user_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        user_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        user_input.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.8); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        user_input.setFixedHeight(50)
        user_input.textChanged.connect(self.adjust_user_input_height)
        return user_input
    logger.info('height change')
    # Adjust if program height is changed

    def adjust_user_input_height(self):
        cursor = self.user_input.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.user_input.setTextCursor(cursor)
        height = self.user_input.document().size().height()
        if height != self.user_input.height():
            self.user_input.setFixedHeight(round(height))
    logger.info('handle messages')
    # Send a message

    def send_message(self, user_message):
        user_message = self.user_input.toPlainText()
        self.user_input.clear()
        if user_message is not None:
            if user_message.startswith("!"):
                self.run_command(user_message)
                self.user_input.clear()
            elif user_message.strip():
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + "You: " + user_message + "\n\n")
                self.chat_history.moveCursor(QTextCursor.End)
                response = chat_gpt(user_message)
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + "Assistant: " + response + "\n\n")
                self.chat_history.moveCursor(QTextCursor.End)
    logger.info('open large input box')
    # /Open the large input text box

    def open_large_text_input(self):
        self.large_text_input_dialog = LargeTextInputDialog(self)
        self.large_text_input_dialog.show()
    logger.info('clear history')
    # Clear the Chat History

    def clear_chat_history(self):
        self.chat_history.clear()
    logger.info('running embed file from Hex')
    # Open a file dialog for embedding a file

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self.process_file(file_name)
    logger.info('run !embed from Hex')
    # Process the selected file for embedding

    def process_file(self, file_path):
        create_embedding(file_path)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Embedding created, use !docslong and !docs to pull relevant documents" + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run long docs')
    # Pull uncompressed documents from database

    def base_retrieve(self, text):
        results = base_retriever(text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Base search results: \n" + str(results) + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run compressed docs')
    # Pull compressed documents from database

    def retrieve(self, text):
        results = retriever(text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Compression search results: \n" + str(results + "\n\n")))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run search agent')
    # Search the internet for a query

    def search_agent(self, text):
        results = agent.run(text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Simple internet search results: \n" + str(results) + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run embed dir')
    # Embed an entire directory

    def mass_embed(self, text):
        result = create_mass_embedding(folder_path=text)
        if result:
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Embedding created, use !docslong and !docs to pull relevant documents, and !searchmem to query the database" + str(result) + "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
    logger.info('query memory')
    # Query the database

    def search_memory(self, text):
        results = memory_search_with_score(text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Memory search results: \n" + str(results)) + "\n\n")
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run addmem')
    # Add a file to the database

    def add_to_db(self, text):
        results = scrape_site(url=text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Added to database: \n" + str(results) + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run add sitemap')

    def add_map_db(self, text, collection_name):
        url = text
        results = scrape_site_map(url, collection_name)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Added to database: \n" + str(results) + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run embed project')
    # Add a project to the database

    def add_project_to_db(self, text):
        results = run_embed_project(file_path=text)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Added to database: \n" + str(results) + "\n\n"))
        self.chat_history.moveCursor(QTextCursor.End)
    logger.info('run ! commands')
    # Run the ! commands

    def run_command(self, text):
        if text == "!clear":
            self.clear_chat_history()
            return
        if text == "!save":
            self.save_chat_history()
            return
        if text == "!load":
            self.load_chat_history()
            return
        if text == "!exit":
            exit()
            return
        if text == "!help":
            self.display_help()
            return
        if text == "!large":
            self.open_large_text_input()
            return
        if text == "!embed":
            self.open_file_dialog()
            return
        if text.startswith("!massembed"):
            text = text.removeprefix("!massembed ")
            self.mass_embed(text)
            return
        if text.startswith("!docs"):
            text = text.removeprefix("!docs ")
            self.base_retrieve(text)
            return
        if text.startswith("!search"):
            text = text.removeprefix("!search ")
            data_base_memory_search(text)
            return
        if text.startswith("!hybrid"):
            text = text.removeprefix("!hybrid ")
            self.search_agent(text)
            return
        if text.startswith("!searchmem"):
            text = text.removeprefix("!searchmem ")
            self.memory_search_with_score(text)
            return
        if text.startswith("!addmem"):
            text = text.removeprefix("!addmem ")
            self.add_to_db(text)
            return
        if text.startswith("!addmap"):
            text = text.removeprefix("!addmap ")
            split_text = text.split(" ")
            text = split_text[0]
            collection_name = split_text[1]
            logger.info(text, collection_name)
            self.add_map_db(text, collection_name)
            return
        if text.startswith("!addproject"):
            text = text.removeprefix("!addproject ")
            self.add_project_to_db(text)
            return
        if text.startswith("!background"):
            text = text.removeprefix("!background ")
            image = QPixmap("img/0000"+str(text)+".png")
            result = MainWindow.change_background_image(image)
            return
        else:
            if text.startswith("!"):
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Command not found. Type !help for a list of commands \n\n"))
                self.chat_history.moveCursor(QTextCursor.End)
                return

    logger.info('logger.info help')
    # Help info

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
        !docs - Pull documents from the vectore store related to your query.
        !search - Search the internet for context on a prompt then ask the prompt.
        !searchmem - Search the database for context on a prompt then ask the prompt.
        !hybrid - Search docs and/or internet for context.
        !addmem - [http] Add a list of comma delineated website to the database.
        !addmap [.xml] - Find site map and add all the sites from it to the database.
        !embed - Upload a file to create embeddings.
        !massembed [dir] - Upload multiple files to create embeddings. Follow with a space then folder path.
        !addproject [dir] - Add python project files to the database. Follow with a space then folder path. Note this sends your project file information to the OpenAI API.
        !background - Change the background image.
        """))
    logger.info('load file into chat')
    # Load file into chat

    def load_chat_history(self):
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, "r") as file:
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str(file.read()) + "\n\n")
    logger.info('save chat history to file')
    # save chat history to file

    def save_chat_history(self):
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, "a") as file:
                file.write(str(self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + "\n\n")))
    logger.info('exit')
    # Exit

    def exit():
        sys.exit(0)


class CustomTitleBar(QWidget):

    def __init__(self, parent=None):
        super(CustomTitleBar, self).__init__(parent)
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # Add title label
        self.titleLabel = QLabel(self)
        layout.addWidget(self.titleLabel)
        self.titleLabel.setObjectName("HexAmerous")
        self.titleLabel.setText("HexAmerous")
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setFixedHeight(30)
        layout.addWidget(self.buttons())

        # Set stylesheet
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: rgba(67, 3, 81, 0.3);
                color: #f9f9f9;
            }
            QPushButton:hover {
                background-color: rgba(67, 3, 81, 0.7);;
                color: #f9f9f9;
            }
            QPushButton:pressed {
                background-color: #430351;
                color: #f9f9f9;
            }
            QLabel {
                background-color: rgba(67, 3, 81, 0.7);
                color: #f9f9f9;
                font-size: 20pt;
                font-weight: bold;
                text-align: center;
                font-family: 'Cascadia Code';

            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()
            logger.info('mouse press event')

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.parent().move(self.parent().pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
            logger.info('mouse move event')

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = None
            event.accept()

    def paintEvent(self, event):
        super(CustomTitleBar, self).paintEvent(event)
        painter = QStylePainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawRect(self.rect())

    # Buttons
    def buttons(self):
        close_button = QPushButton()
        close_button.clicked.connect(self.parent().close)
        close_button.setFixedSize(30, 30)
        close_button.setIconSize(QSize(30, 30))
        close_button.setIcon(QIcon("imgs/close.png"))
        close_button.setStyleSheet(
            "QPushButton {background-color: rgba(67, 3, 81, 0.4);}"
            "QPushButton:hover {background-color: #430351;}")

        min_button = QPushButton()
        min_button.clicked.connect(self.parent().showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setIconSize(QSize(30, 30))
        min_button.setIcon(QIcon("imgs/min.png"))
        min_button.setStyleSheet(
            "QPushButton {background-color: rgba(67, 3, 81, 0.4);}"
            "QPushButton:hover {background-color: #430351;}")

        max_button = QPushButton()
        max_button.clicked.connect(self.maximumSize)
        max_button.setFixedSize(30, 30)
        max_button.setIconSize(QSize(30, 30))
        max_button.setIcon(QIcon("imgs/max.png"))
        max_button.setStyleSheet(
            "QPushButton {background-color: rgba(67, 3, 81, 0.4);}"
            "QPushButton:hover {background-color: #430351;}")

        button_layout = QHBoxLayout()

        button_layout.addWidget(min_button)
        button_layout.addWidget(max_button)
        button_layout.addWidget(close_button)
        button_layout.setAlignment(Qt.AlignRight)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        widget = QWidget()
        widget.setLayout(button_layout)
        widget.setFixedHeight(30)
        widget.setFixedWidth(90)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setStyleSheet("background-color: rgba(67, 3, 81, 0.7);")
        return widget


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


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(800, 800)
        self.flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint |
                                    Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.flags)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("width: 10px; height: 5px; margin 0px;")
        self.layout.addWidget(self.size_grip)
        self.titleBar = CustomTitleBar(self)
        self.layout.addWidget(self.titleBar)
        self.chat_widget = ChatWidget()
        self.layout.addWidget(self.chat_widget)

        self.image = ''
        self.background = self.change_background_image()

    def change_background_image(self, image="./imgs/00001.png"):
        self.image = image
        image_choice = QPixmap(self.image)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(image_choice.scaled(
            self.size())))
        self.setPalette(palette)
        return image_choice


logger.info('Large Text Input Dialog')


class LargeTextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Large Text Input")
        self.resize(400, 600)
        self.text_input = QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family 'Cascadia Code'; font-size: 12pt; font-weight: bold;")
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color:rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family 'Cascadia Code'; font-size: 14pt; font-weight: bold;")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_large_text)
    logger.info('send large text')
    # Send the large textbox message

    def send_large_text(self):
        large_text = self.text_input.toPlainText()
        if large_text.strip():
            self.parent().send_message(large_text)
        self.close()


# -------------- Main Program -------------- #
logger.info('main')


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    icon = QIcon("imgs/favicon.ico")
    app.setWindowIcon(icon)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
