from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter


class CustomSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        # Regex patterns for each word type
        variable_names_pattern = QRegularExpression(r"\b\[A-Za-z_\]\w*\B")
        variable_definitions_pattern = QRegularExpression(r"(?<=\=\s)\w+")
        function_references_pattern = QRegularExpression(r"\b\w+\(")
        function_definitions_pattern = QRegularExpression(r"\bdef \w+\\(")
        keywords_pattern = QRegularExpression(
            r"\b(if|else|for|while|True|False)\b")
        property_names_pattern = QRegularExpression(r"(?<=\.)\w+")
        property_definitions_pattern = QRegularExpression(r"(?<=\.)\w+\s*=")
        tag_names_pattern = QRegularExpression(r"</?\w+[^>]*>")
        type_names_pattern = QRegularExpression(
            r"\b(?:int|float|str|list|tuple|dict|set)\b")
        class_names_pattern = QRegularExpression(r"\bclass (\w+)\b")
        attribute_names_pattern = QRegularExpression(r"\bself\.\w+\b")
        comments_pattern = QRegularExpression(r"#.*")
        strings_pattern = QRegularExpression(
            r"(?<!\\')'(?:\\.|[^\"])*0'(?<!\\)")
        numbers_pattern = QRegularExpression(r"\b\d+(?:\.\d+)?\b")
        operators_pattern = QRegularExpression(r"[-!%^&*+=|;:,.<>?/\\\\~]")
        square_brackets_pattern = QRegularExpression(r"[[\]]")
        angle_brackets_pattern = QRegularExpression(r"[<>]")

        self.variable_names_format = QTextCharFormat()
        self.variable_names_format.setForeground(QColor('#e6d200'))
        self.variable_definitions_format = QTextCharFormat()
        self.variable_definitions_format.setForeground(QColor('#aa95fe'))
        self.function_references_format = QTextCharFormat()
        self.function_references_format.setForeground(QColor('#1dd777'))
        self.keywords_format = QTextCharFormat()
        self.keywords_format.setForeground(QColor('#ff14c0'))
        self.property_names_format = QTextCharFormat()
        self.property_names_format.setForeground(QColor('#3b91e8'))
        self.property_definitions_format = QTextCharFormat()
        self.property_definitions_format.setForeground(QColor('#ffffff'))
        self.tag_names_format = QTextCharFormat()
        self.tag_names_format.setForeground(QColor('#96afca'))
        self.type_names_format = QTextCharFormat()
        self.type_names_format.setForeground(QColor('#f99090'))
        self.class_names_format = QTextCharFormat()
        self.class_names_format.setForeground(QColor('#fe8a58'))
        self.attribute_names_format = QTextCharFormat()
        self.attribute_names_format.setForeground(QColor('#9dbddd'))
        self.comments_format = QTextCharFormat()
        self.comments_format.setForeground(QColor('#3df078'))
        self.strings_format = QTextCharFormat()
        self.strings_format.setForeground(QColor('#3df078'))
        self.numbers_format = QTextCharFormat()
        self.numbers_format.setForeground(QColor('#ff6161'))
        self.operators_format = QTextCharFormat()
        self.operators_format.setForeground(QColor('#d7befe'))
        self.square_brackets_format = QTextCharFormat()
        self.square_brackets_format.setForeground(QColor('#a9cafe'))
        self.angle_brackets_format = QTextCharFormat()
        self.angle_brackets_format.setForeground(QColor('#8afffd'))

        self.highlighting_rules = [
            (variable_names_pattern, self.variable_names_format),
            (variable_definitions_pattern, self.variable_definitions_format),
            (function_references_pattern, self.function_references_format),
            (keywords_pattern, self.keywords_format),
            (property_names_pattern, self.property_names_format),
            (property_definitions_pattern, self.property_definitions_format),
            (tag_names_pattern, self.tag_names_format),
            (type_names_pattern, self.type_names_format),
            (class_names_pattern, self.class_names_format),
            (attribute_names_pattern, self.attribute_names_format),
            (comments_pattern, self.comments_format),
            (strings_pattern, self.strings_format),
            (numbers_pattern, self.numbers_format),
            (operators_pattern, self.operators_format),
            (square_brackets_pattern, self.square_brackets_format),
            (angle_brackets_pattern, self.angle_brackets_format)
        ]


def highlightBlock(self, text):
    for pattern, fmt in self.highlighting_rules:
        iterator = pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
