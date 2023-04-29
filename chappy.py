import sys
from PyQt5.QtCore import Qt
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
    QFileDialog,
    QMessageBox,
    QComboBox
)
from chatgpt import (
    chat_gpt,
    change_selected_model,
    change_context_module
)
from embeddings import (
    create_embedding,
    base_retriever,
    retriever,
    create_mass_embedding,
    memory_search
)
from langchain import OpenAI
from langchain.utilities import GoogleSerperAPIWrapper, GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, load_tools
from scrappy import scrape_site
from embed_project import run_embed_project



# -------------- Langchain Variables -------------- #

llm = OpenAI(temperature=0)
tools = load_tools(["google-serper"], llm=llm)
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)


# -------------- Custom Text Edit -------------- #

class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(CustomTextEdit, self).__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.insertPlainText("\n")
        elif event.key() == Qt.Key_Return:
            self.parent().send_message()
        elif event.key() == Qt.Key_Enter:
            self.parent().send_message()
        else:
            super().keyPressEvent(event)


# -------------- Chat Widget -------------- #

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.error_handling = ErrorHandling(parent)

    # Initialize the UI
    def init_ui(self):
        self.create_widgets()
        self.set_widget_properties()
        self.create_widget_layouts()
        self.set_widget_connections()
        self.setLayout(self.layout)

    def create_widgets(self):
        self.layout = QVBoxLayout()
        self.chat_history = self.create_chat_history()
        self.user_input = self.create_user_input()


        self.send_button = QPushButton("Send")
        self.clear_button = QPushButton("Clear")
        self.large_text_input_button = QPushButton("L Input")
        self.upload_button = QPushButton("Up File")

        self.loading_label = QLabel(self)
        self.loading_movie = QMovie("docs/gears.png")
        self.combo_box = QComboBox(self)

        self.button_layout = QHBoxLayout()

    def set_widget_properties(self):
        self.user_input.setFocus()

        self.send_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

        self.clear_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

        self.large_text_input_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

        self.upload_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        self.loading_label.move(300, 200)

        self.combo_box.addItem("gpt-3.5-turbo")
        self.combo_box.addItem("gpt-4")
        self.combo_box.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

    def create_widget_layouts(self):
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.loading_label)
        self.layout.addWidget(self.combo_box)

        self.button_layout.addWidget(self.send_button)
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.large_text_input_button)
        self.button_layout.addWidget(self.upload_button)

        self.layout.addLayout(self.button_layout)

    def set_widget_connections(self):
        self.send_button.clicked.connect(self.send_message)
        self.clear_button.clicked.connect(self.clear_chat_history)
        self.large_text_input_button.clicked.connect(
            self.open_large_text_input)
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.combo_box.currentIndexChanged.connect(
            self.on_combobox_changed)

    # Drop down menu change
    def on_combobox_changed(self, index):
        selected_option = self.combo_box.itemText(index)
        change_selected_model(selected_option)
        self.chat_history.setPlainText(
            self.chat_history.toPlainText() + selected_option + "\n\n")
        self.chat_history.moveCursor(QTextCursor.End)


    # Create Chat History
    def create_chat_history(self):
        chat_history = QTextEdit()
        chat_history.setReadOnly(True)
        chat_history.ensureCursorVisible()
        chat_history.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        chat_history.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chat_history.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-size: 12pt; font-weight: bold;")
        return chat_history

    # Create User Input
    def create_user_input(self):
        user_input = CustomTextEdit()
        user_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        user_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        user_input.setStyleSheet(
            "background-color: rgba(67, 3, 81, 0.7); color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        user_input.setFixedHeight(50)
        user_input.textChanged.connect(self.adjust_user_input_height)
        return user_input

    # Adjust if program height is changed
    def adjust_user_input_height(self):
        cursor = self.user_input.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.user_input.setTextCursor(cursor)
        height = self.user_input.document().size().height()
        if height != self.user_input.height():
            self.user_input.setFixedHeight(round(height))

    # Send a message
    def send_message(self, user_message=None):
        if user_message is None:
            user_message = self.user_input.toPlainText()
        self.user_input.clear()
        if user_message.startswith("!"):
            self.run_command(user_message)
            self.user_input.clear()
        elif user_message.strip():
            change_context_module(new_context=user_message)
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + "You: " + user_message + "\n")
            self.chat_history.moveCursor(QTextCursor.End)
            self.show_loading_animation()
            response = chat_gpt(user_message)
            self.hide_loading_animation()
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + "Assistant: " + response + "\n")
            self.chat_history.moveCursor(QTextCursor.End)

    #/Open the large input text box
    def open_large_text_input(self):
        try:
            self.large_text_input_dialog = LargeTextInputDialog(self)
            self.large_text_input_dialog.show()
        except Exception as e:
            self.error_handling.handle_error(e)

    # Show the loading animation
    def show_loading_animation(self):
        try:
            self.loading_movie.start()
            self.loading_label.show()
        except Exception as e:
            self.error_handling.handle_error(e)

    # Hide the loading animation

    def hide_loading_animation(self):
        try:
            self.loading_movie.stop()
            self.loading_label.hide()
        except Exception as e:
            self.error_handling.handle_error(e)

    # Clear the Chat History
    def clear_chat_history(self):
        try:
            self.chat_history.clear()
        except Exception as e:
            self.error_handling.handle_error(e)


    # Open a file dialog for embedding a file
    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setStyleSheet("background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            self.process_file(file_name)

    # Process the selected file for embedding
    def process_file(self, file_path):
        try:
            create_embedding(file_path)
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Embedding created, use !docslong and !docs to pull relevant documents" + "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Pull uncompressed documents from database
    def base_retrieve(self, text):
        try:
            results = base_retriever(text)
            self.chat_history.setPlainText(
            self.chat_history.toPlainText() + str("Base search results: \n" + str(results)+ "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Pull compressed documents from database
    def retrieve(self, text):
        try:
            results = retriever(text)
            self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Compression search results: \n" + str(results + "\n\n")))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Search the internet for a query
    def search_agent(self, text):
        try:
            results = agent.run(text)
            self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Simple internet search results: \n" + str(results) + "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Embed an entire directory
    def mass_embed(self, file_path):
        try:
            create_mass_embedding(file_path)
            self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Embedding created, use !docslong and !docs to pull relevant documents, and !searchmem to query the database \n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Query the database
    def search_memory(self, text):
        try:
            results = memory_search(text)
            self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Memory search results: \n" + str(results)) + "\n\n")
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Add a file to the database
    def add_to_db(self, text):
        try:
            results = scrape_site(url=text)
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Added to database: \n" + str(results) + "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Add a project to the database
    def add_project_to_db(self, text):
        try:
            results = run_embed_project(file_path=text)
            self.chat_history.setPlainText(
                self.chat_history.toPlainText() + str("Added to database: \n" + str(results) + "\n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Run the ! commands
    def run_command(self, text):
        try:
            if text == "!clear":
                self.clear_chat_history()
            if text == "!save":
                self.save_chat_history()
            if text == "!load":
                self.load_chat_history()
            if text == "!exit":
                exit()
            if text == "!help":
                self.display_help()
            if text == "!large":
                self.open_large_text_input()
            if text == "!embed":
                self.open_file_dialog()
            if text.startswith("!mass_embed "):
                text = text.removeprefix("!mass_embed ")
                self.mass_embed(text)
            if text.startswith("!docslong "):
                text = text.removeprefix("!docslong ")
                self.base_retrieve(text)
            if text.startswith("!docs "):
                text = text.removeprefix("!docs ")
                self.retrieve(text)
            if text.startswith("!search "):
                text = text.removeprefix("!search ")
                self.search_agent(text)
            if text.startswith("!searchmem "):
                text = text.removeprefix("!searchmem ")
                self.search_memory(text)
            if text.startswith("!addmem"):
                text = text.removeprefix("!addmem ")
                self.add_to_db(text)
            if text.startswith("!addproject "):
                text = text.removeprefix("!addproject ")
                self.add_project_to_db(text)
            else:
                self.chat_history.setPlainText(
                    self.chat_history.toPlainText() + str("Command not found. Type !help for a list of commands \n\n"))
            self.chat_history.moveCursor(QTextCursor.End)
        except Exception as e:
            self.error_handling.handle_error(e)
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
        !docslong - Uncompressed search of documents.
        !docs - Compressed search the documents.
        !search - Search the internet for context on a prompt then ask the prompt.
        !searchmem - Search the memory for context on a prompt then ask the prompt.
        !addmem - Add a list of comma delineated website to the database.
        !embed - Upload a file to create embeddings.
        !mass_embed - Upload multiple files to create embeddings. Follow with a space then folder path.
        !addproject - Add a project to the database. Follow with a space then folder path. Note this sends your project file information to the OpenAI API.
        """))

    # Load file into chat
    def load_chat_history(self):
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setStyleSheet("background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

            file_dialog.setFileMode(QFileDialog.ExistingFile)

            if file_dialog.exec_() == QFileDialog.Accepted:
                file_name = file_dialog.selectedFiles()[0]
                with open(file_name, "r") as file:
                    self.chat_history.setPlainText(file.read())
        except Exception as e:
            self.error_handling.handle_error(e)

    # save chat history to file
    def save_chat_history(self):
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setStyleSheet("background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")

            file_dialog.setFileMode(QFileDialog.ExistingFile)

            if file_dialog.exec_() == QFileDialog.Accepted:
                file_name = file_dialog.selectedFiles()[0]
                with open(file_name, "a") as file:
                    file.write("\n\n" + self.chat_history + "\n\n")
        except Exception as e:
            self.error_handling.handle_error(e)

    # Exit
    def exit():
        sys.exit(0)

# -------------- Scroll Area -------------- #

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

# -------------- Main Window -------------- #

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
        try:
            palette = QPalette()
            palette.setBrush(QPalette.Background, QBrush(self.background_image.scaled(
                self.size())))
            self.setPalette(palette)
        except Exception as e:
            self.error_handling.handle_error(e)

    def resizeEvent(self, event):
        self.update_background_image()
        super().resizeEvent(event)

# -------------- Large Text Input Dialog -------------- #

class LargeTextInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_handling = ErrorHandling(parent)
        self.setWindowTitle("Large Text Input")
        self.resize(400, 600)

        self.text_input = QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_input.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 12pt; font-weight: bold;")

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_input)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

        try:
            self.send_button.clicked.connect(self.send_large_text)
        except Exception as e:
            self.error_handling.handle_error(e)

    # Send the large textbox message
    def send_large_text(self):
        large_text = self.text_input.toPlainText()
        if large_text.strip():
            try:
                self.parent().send_message(large_text)
            except Exception as e:
                self.error_handling.handle_error(e)
            self.close()

class ErrorHandling():
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def handle_error(self, error_message):
        while True:
            error_dialog = QMessageBox(self.parent)
            error_dialog.setStyleSheet("background-color: #430351; color: #f9f9f9; font-size: 14pt; font-weight: bold;")
            error_dialog.setText(str(error_message))
            error_dialog.exec_()
            print(error_message)
            break


# -------------- Main Program -------------- #

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()