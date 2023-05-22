# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QTextCursor, QPixmap, QPalette, QBrush, QIcon, QColor, QKeyEvent
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
    QComboBox,
    QSizeGrip,
    QStylePainter,
)
from chatgpt import GPTChatbot
from embeddings import create_embedding, create_mass_embedding
from embed_project import run_embed_project
from scrappy import scrape_site, scrape_site_map
from custom_agents import CustomAgents
from dotenv import load_dotenv

load_dotenv()
from typing import Any
from PyQt5.QtWidgets import QTextEdit
import queue

global data_base_retriever
global base_retriever
base_retriever = CustomAgents.base_retriever
data_base_memory_search = CustomAgents.base_retriever


class CustomTextEdit(QTextEdit):
    """
    A custom text edit that handles key press events.

    Args:
        args (Any): Variable length argument list.
        kwargs (Any): Arbitrary keyword arguments.

    Attributes:
        None
    """


class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
        elif event.key() == Qt.Key_Return:
            self.parent().send_message("")
        elif event.key() == Qt.Key_Enter:
            self.parent().send_message("")
        else:
            super().keyPressEvent(event)


class ChatWidget(QWidget):
    def __init__(self, message_queue, gpt_chatbot, parent=None):
        super().__init__(parent)
        self.init_ui()
        print("init ui")
        self.message_queue = message_queue
        self.gpt_chatbot = gpt_chatbot

    def send_queue(self, user_message):
        try:
            self.message_queue.put(user_message, block=True, timeout=1)
        except queue.Full:
            print("-- message queue is full")

    def add_response(self, response):
        try:
            self.message_queue.put(response, block=True, timeout=1)
        except queue.Full:
            print("-- message queue is full")

    # Initialize the UI
    def init_ui(self):
        self.create_widgets()
        self.set_widget_properties()
        self.create_widget_layouts()
        self.set_widget_connections()
        self.setLayout(self.layout)
        print("create chat widget")

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
        print("creating chat history")

    # Create the chat history widget
    def set_widget_properties(self):
        self.user_input.setFocus()
        self.send_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;"
        )
        self.clear_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9;font-family: 'Cascadia Code';  font-size: 14pt; font-weight: bold; height: 50px; width: 100px;"
        )
        self.large_text_input_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;"
        )
        self.upload_button.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold; height: 50px; width: 100px;"
        )
        self.combo_box.addItem("GPT-3.5-Turbo")
        self.combo_box.addItem("GPT-4")
        self.combo_box.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;height: 50px; width: 100px;"
        )
        print("styling loaded")

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
        print("layout loaded")

    # Create the event connections
    def set_widget_connections(self):
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_chat_history)
        self.large_text_input_button.clicked.connect(self.open_large_text_input)
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)
        print("connections loaded")

    # Drop down menu change
    def on_combobox_changed(self, index):
        selected_option = self.combo_box.itemText(index)
        self.gpt_chatbot.change_selected_model(selected_option)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + selected_option + "\n\n"
        )
        self.chat_history.moveCursor(QTextCursor.End)
        print("dropdown menu changed")

    # Create Chat History
    def create_chat_history(self):
        chat_history = QTextEdit()
        chat_history.setReadOnly(True)
        chat_history.ensureCursorVisible()
        self._extracted_from_create_user_input_5(chat_history)
        return chat_history

    # Create User Input
    def create_user_input(self):
        self.user_input = CustomTextEdit()
        self._extracted_from_create_user_input_5(self.user_input)
        self.user_input.setFixedHeight(50)
        self.user_input.textChanged.connect(self.adjust_user_input_height)
        return self.user_input

    # TODO Rename this here and in `create_chat_history` and `create_user_input`
    def _extracted_from_create_user_input_5(self, arg0):
        arg0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        arg0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        arg0.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.8);color: white; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;"
        )

    # Adjust if program height is changed
    def adjust_user_input_height(self):
        height = self.user_input.document().size().height()
        if height != self.user_input.height():
            self.user_input.setFixedHeight(round(height))
            print("adjusted height")

    # Send a message
    def send_message(self, user_message):
        user_message = self.user_input.toPlainText()
        self.user_input.clear()
        if user_message.startswith("!"):
            print(user_message)
        elif user_message.strip():
            return self.add_to_message_queue(user_message)


    def add_to_message_queue(self, user_message):
        """
        Sends a message to the chatbot and displays the conversation history.
        """
        # Add user message to chat history
        self.chat_history.setPlainText(
            f"{self.chat_history.toPlainText()}You: {user_message}\n\n"
        )
        self.chat_history.moveCursor(QTextCursor.End)

        # Get response from chatbot
        response = self.send_queue(user_message)

        # Add chatbot response to chat history
        self.chat_history.setPlainText(
            f"{self.chat_history.toPlainText()}Assistant: {response}\n\n"
        )
        self.chat_history.moveCursor(QTextCursor.End)

        # Print debugging statement (optional)
        print(f"Sent message: {response}")

        # Return chatbot response
        return response


    # /Open the large input text box
    def open_large_text_input(self):
        self.large_text_input_dialog = LargeTextInputDialog(self)
        self.large_text_input_dialog.show()
        print("clear history")

    # Clear the Chat History
    def clear_chat_history(self):
        self.chat_history.clear()
        print("clear history")
        return self.chat_history

    # Open a file dialog for embedding a file
    def open_file_dialog(self):
        file_dialog = self._extracted_from_save_chat_history_2()
        if file_dialog.exec_() == QFileDialog.Accepted:
            return self._extracted_from_open_file_dialog_8(file_dialog)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Embedding failed" + "\n\n")
        )
        self.chat_history.moveCursor(QTextCursor.End)
        return "error embedding file"

    # TODO Rename this here and in `open_file_dialog`
    def _extracted_from_open_file_dialog_8(self, file_dialog):
        file_name = file_dialog.selectedFiles()[0]
        results = create_embedding(file_name)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText()
            + str(
                "Embedding created, use !docslong and !docs to pull relevant documents"
                + "\n\n"
            )
        )
        self.chat_history.moveCursor(QTextCursor.End)
        print(f"added file to database {str(results)}")
        return results

    # Pull uncompressed documents from database
    def use_base_retriever(self, text):
        if results := base_retriever(text):
            return self._extracted_from_add_map_db_3(
                "Base search results: \n", results, "base search results: "
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "Base search failed",
                "base search failed",
                "error retrieving documents",
            )

    # Embed an entire directory
    def mass_embed(self, text):
        if results := create_mass_embedding(folder_path=text):
            self.chat_history.setPlainText(
                self.chat_history.toPlainText()
                + str(
                    f"Embedding created, use !docslong and !docs to pull relevant documents, and !searchmem to query the database{str(results)}"
                    + "\n\n"
                )
            )
            return self._extracted_from__extracted_from_add_project_to_db_11_12(
                "Added to memory", results
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "Embedding failed",
                "Failed to add to memory",
                "error embedding file",
            )

    # Query the database
    def search_memory(self, text):
        if results := data_base_memory_search(user_query=text):
            self.chat_history.setPlainText(
                self.chat_history.toPlainText()
                + str("Memory search results: \n" + str(results))
                + "\n\n"
            )
            return self._extracted_from__extracted_from_add_map_db_3_9(
                "Search memory: ", results
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "No results found", "No results found", "No results found"
            )

    # Add a file to the database
    def add_to_db(self, text):
        if results := scrape_site(url=text):
            return self._extracted_from_add_map_db_3(
                "Added to database: \n", results, "add site: "
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "Failed to add to database",
                "Failed to add to database",
                "Failed to add to database",
            )

    def add_map_db(self, text, collection_name):
        url = text
        if results := scrape_site_map(url, collection_name):
            return self._extracted_from_add_map_db_3(
                "Added to database: \n", results, "embeded site map: "
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "Failed to add to database",
                "Failed to add to database",
                "Failed to add to database",
            )

    # Add a project to the database
    def _extracted_from_add_map_db_3(self, arg0, results, arg2):
        self.chat_history.setPlainText(
            (self.chat_history.toPlainText() + str(arg0 + str(results) + "\n\n"))
        )
        return self._extracted_from__extracted_from_add_map_db_3_9(arg2, results)

    # TODO Rename this here and in `use_base_retriever`, `mass_embed`, `search_memory`, `add_to_db`, `add_map_db` and `add_project_to_db`
    def _extracted_from__extracted_from_add_map_db_3_9(self, arg0, results):
        self.chat_history.moveCursor(QTextCursor.End)
        print(arg0 + str(results))
        return results

    # TODO Rename this here and in `use_base_retriever`, `mass_embed`, `search_memory`, `add_to_db`, `add_map_db` and `add_project_to_db`
    def add_project_to_db(self, text):
        if results := run_embed_project(file_path=text):
            self.chat_history.setPlainText(
                self.chat_history.toPlainText()
                + str("Added to database: \n" + str(results) + "\n\n")
            )
            return self._extracted_from__extracted_from_add_project_to_db_11_12(
                "run ! commands", results
            )
        else:
            return self._extracted_from_add_project_to_db_11(
                "Failed to add to database",
                "Failed to add to database",
                "Failed to add to database",
            )

    # TODO Rename this here and in `use_base_retriever`, `mass_embed`, `search_memory`, `add_to_db`, `add_map_db` and `add_project_to_db`
    def _extracted_from_add_project_to_db_11(self, arg0, arg1, arg2):
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str(arg0 + "\n\n")
        )
        return self._extracted_from__extracted_from_add_project_to_db_11_12(arg1, arg2)

    # TODO Rename this here and in `use_base_retriever`, `mass_embed`, `search_memory`, `add_to_db`, `add_map_db` and `add_project_to_db`
    def add_project_to_db(self, project_name, project_data):
        self.chat_history.moveCursor(QTextCursor.End)
        # Removed debugging statement
        print(f"Adding project {project_name} to database")
        return project_data

    # Run the ! commands
    def run_command(self, text):
        if text == "!help":
            self.display_help()
            return
        if text == "!exit":
            self.exit()
            return
        if text == "!clear":
            self.clear_chat_history()
            return
        if text == "!save":
            return (
                results
                if (results := self.save_chat_history())
                else "Error creating loading"
            )
        if text == "!load":
            if results := self.load_chat_history():
                return results
            else:
                return "Error creating loading"
        if text == "!embed":
            if results := self.open_file_dialog():
                return results
            else:
                return "Error creating embedding"
        if text.startswith("!massembed"):
            text = text.removeprefix("!massembed ")
            if results := self.mass_embed(text):
                return results
            else:
                return "Error creating embedding"
        if text.startswith("!searchmem"):
            text = text.removeprefix("!searchmem ")
            if not (results := self.search_memory(text)):
                return "No results found"
            print(results)
            return results
        if text.startswith("!docs"):
            text = text.removeprefix("!docs ")
            if not (results := self.use_base_retriever(text)):
                return "No results found"
            print(results)
            return results
        if text.startswith("!addmem"):
            text = text.removeprefix("!addmem ")
            if not (results := self.add_to_db(text)):
                return "Error adding to database"
            print(results)
            return results
        if text.startswith("!addmap"):
            return self._extracted_from_run_command_(text, results)
        if text.startswith("!addproject"):
            text = text.removeprefix("!addproject ")
            if results := self.add_project_to_db(text):
                return results
            else:
                return "Error creating loading"
        if text.startswith("!background"):
            text = text.removeprefix("!background ")
            image = QPixmap(f"img/0000{str(text)}.png")
            if results := MainWindow.change_background_image(image):
                return results
            else:
                return "Error creating loading"
        elif text.startswith("!"):
            self.chat_history.setPlainText(
                (
                    self.chat_history.toPlainText()
                    + "Command not found. Type !help for a list of commands \n\n"
                )
            )
            self.chat_history.moveCursor(QTextCursor.End)
            return

    # TODO Rename this here and in `run_command`
    def _extracted_from_run_command_(self, text, results):
        text = text.removeprefix("!addmap ")
        split_text = text.split(" ")
        text = split_text[0]
        collection_name = split_text[1]
        print(text, collection_name)
        return (
            results
            if (results := self.add_map_db(text, collection_name))
            else "Error creating loading"
        )

    print("print help")
    # Help info

    def display_help(self):
        self.chat_history.setPlainText(
            (
                self.chat_history.toPlainText()
                + """
    Commands:
!help       - Display this help message.
!save       - Save chat history.
!load       - Load chat history.
!clear      - Clear chat history.
!exit       - Exit the application.
!docs       - Search the database for related docs.
!searchmem  - Search the database for context on a
                prompt then ask for a more detailed
                response.
!addmem     - [http] Add a list of comma delineated
                website to the database.
!addmap     - [.xml] - Add all the sites froma sitemap
                it to the database.
!embed      - Upload a file to create embeddings.
!massembed  - [dir] - Upload multiple files to create
                embeddings. Follow dir with a space
                then folder path.
!addproject - [dir] - Add python project files to the
                database. Follow with a space then
                folder path. Note this sends your
                project file information to the OpenAI
                API.
!background - Change the background image.
        """
            )
        )

    print("load file into chat")
    # Load file into chat

    def load_chat_history(self):
        file_dialog = self._extracted_from_save_chat_history_2()
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, "r") as file:
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str(file.read()) + "\n\n"
                )
            print("save chat history to file")

    # save chat history to file
    def save_chat_history(self):
        file_dialog = self._extracted_from_save_chat_history_2()
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            with open(file_name, "a") as file:
                file.write(
                    str(
                        self.chat_history.setPlainText(
                            self.chat_history.toPlainText() + "\n\n"
                        )
                    )
                )
            print("exit")

    # TODO Rename this here and in `open_file_dialog`, `load_chat_history` and `save_chat_history`
    def _extracted_from_save_chat_history_2(self):
        result = QFileDialog(self)
        result.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family: 'Cascadia Code'; font-size: 14pt; font-weight: bold;"
        )
        result.setFileMode(QFileDialog.ExistingFile)
        return result

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
        self.setStyleSheet(
            """
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
        """
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos is not None:
            self.parent().move(self.parent().pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

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
            "QPushButton:hover {background-color: #430351;}"
        )

        min_button = QPushButton()
        min_button.clicked.connect(self.parent().showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setIconSize(QSize(30, 30))
        min_button.setIcon(QIcon("imgs/min.png"))
        min_button.setStyleSheet(
            "QPushButton {background-color: rgba(67, 3, 81, 0.4);}"
            "QPushButton:hover {background-color: #430351;}"
        )

        max_button = QPushButton()
        max_button.clicked.connect(self.maximumSize)
        max_button.setFixedSize(30, 30)
        max_button.setIconSize(QSize(30, 30))
        max_button.setIcon(QIcon("imgs/max.png"))
        max_button.setStyleSheet(
            "QPushButton {background-color: rgba(67, 3, 81, 0.4);}"
            "QPushButton:hover {background-color: #430351;}"
        )

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
    print("intializing the main window")
    def __init__(self, message_queue, parent=None):
        super().__init__(parent)
        self.resize(800, 800)
        print("Settings Flags:")
        self.flags = Qt.WindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setWindowFlags(self.flags)

        print("Setting Layout:")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        print("Setting Size Grip:")
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("width: 10px; height: 5px; margin 0px;")
        self.layout.addWidget(self.size_grip)

        print("Setting Title Bar:")
        self.titleBar = CustomTitleBar(self)
        self.layout.addWidget(self.titleBar)

        print("Setting Scroll Area:")
        self.scroll_area = ScrollArea()
        self.layout.addWidget(self.scroll_area)

        print("Initializing Chat Bot:")
        self.gpt_chatbot = GPTChatbot(message_queue)

        print("Initializing Chat Widget:")
        self.chat_widget = ChatWidget(message_queue, self.gpt_chatbot)
        self.scroll_area.content_widget_layout.addWidget(self.chat_widget)

        print("Setting Background Image:")
        self.image = "./imgs/00002.png"
        self.background = self.change_background_image(self.image)

    def change_background_image(self, image=None):
        self.image = image
        image_choice = QPixmap(self.image)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(image_choice.scaled(self.size())))
        self.setPalette(palette)
        return image_choice


print("Large Text Input Dialog")


class LargeTextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Large Text Input")
        self.resize(400, 600)
        self.text_input = QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family 'Cascadia Code'; font-size: 12pt; font-weight: bold;"
        )
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color:rgba(67, 3, 81, 0.7); color: #f9f9f9; font-family 'Cascadia Code'; font-size: 14pt; font-weight: bold;"
        )
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_large_text)

    print("send large text")
    # Send the large textbox message

    def send_large_text(self):
        large_text = self.text_input.toPlainText()
        if large_text.strip():
            self.parent().send_message(self, large_text)
        self.close()


def main():

    print("Initializing QApplication")
    app = QApplication(sys.argv)

    print("Initializing icon")
    icon = QIcon("imgs/favicon.ico")
    app.setWindowIcon(icon)

    print("Initializing message_queue")
    message_queue = queue.Queue()

    print("Initializing main window")
    main_window = MainWindow(message_queue, parent=None)
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
