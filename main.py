import ffautomation
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget, QComboBox, QTextEdit, QDialog, QDialogButtonBox, QStackedLayout, QHBoxLayout, QLineEdit,
)


class OptionSelection(QDialog):
    def __init__(self, labels=None, desc=None):
        super().__init__()
        self.setMinimumSize(QSize(450, 150))
        self.selection = None
        self.item_desc = desc
        self.setWindowTitle('Options')

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()

        etiquetas = labels
        if labels:
            for label in etiquetas:
                btn = QPushButton(label)
                btn.setAutoDefault(False)
                btn.clicked.connect(self.select_option)
                layout.addWidget(btn)

        label_text = QHBoxLayout()
        option = QLabel('Not Correct?')
        self.text = QLineEdit()
        self.text.returnPressed.connect(self.try_match)
        label_text.addWidget(option)
        label_text.addWidget(self.text)

        layout.addLayout(label_text)

        self.setLayout(layout)

    def select_option(self):
        self.selection = self.sender().text()
        self.accept()

    def try_match(self):
        palabra = self.text.text().upper()
        self.text.clear()
        if palabra in self.item_desc:
            self.selection = palabra
            self.accept()

    @property
    def get_selection(self):
        return self.selection


class CustomDialog(QDialog):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(450, 150))
        self.setWindowTitle("Attention")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QTextEdit()
        message.setPlainText(text)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('FF Automation')
        self.setMinimumSize(QSize(350, 450))

        self.sleep_time = 0.5

        self.text = QLabel('Select an option:')
        self.list = QComboBox()
        self.list.addItems(['Receiving', 'Pre-manifest', 'Print Label', 'Codes'])
        self.items = QTextEdit()
        self.items.setAcceptRichText(False)
        self.ok_button = QPushButton('OK')
        self.ok_button.pressed.connect(self.automation)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.list)
        layout.addWidget(self.items)
        layout.addWidget(self.ok_button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def automation(self):
        option = self.list.currentText()
        info = self.items.toPlainText()
        self.items.clear()
        text = ''

        if option == 'Receiving':
            packages = info.split()
            packages_nship = [[A, B] for A, B in zip(packages[0::2], packages[1::2])]
            repeated, holds, problems, not_found = ffautomation.receiving(packages_nship, self.sleep_time)
            dictionary = {"Repeated": repeated, "Holds": holds, "Problems": problems, "Not found": not_found}

            for category in dictionary:
                if dictionary[category]:
                    text += "{}:\n".format(category)
                    for value in dictionary[category]:
                        text += value + '\n'
            if not text:
                text += 'All packages found'

        elif option == 'Pre-manifest':
            outbounds = info.split()
            state = ffautomation.pre_manifest(outbounds, self.sleep_time)
            text = "\n".join(state)

        elif option == 'Print Label':
            packages = info.split()
            message = ffautomation.print_label(packages)
            text = "\n".join(message)

        elif option == 'Codes':
            self.widget.setLayout(self.layout2)

        dlg = CustomDialog(parent=self, text=text)
        dlg.exec()


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
