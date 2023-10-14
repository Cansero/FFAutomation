import sys

from PySide6 import QtGui
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QTextEdit, QFileDialog,
)

import ffautomation
import fileupdate
from win_utils import EmittingStream, CustomDialog, InputWin
from win_settings import Settings


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('FF Automation')
        self.setMinimumSize(QSize(350, 450))

        self.settings = Settings(parent=self)
        self.user = None
        self.sleep_time = None
        self.name = None
        self.minimized = None
        self.update_data()

        sys.stdout = EmittingStream(textWritten=self.normal_output_written)

        self.text = QLabel('Select an option:')
        self.list = QComboBox()
        self.list.addItems(['Receiving', 'Pre-manifest', 'Print Label', 'Problems'])  # Codes option removed
        self.items = QTextEdit()
        self.items.setAcceptRichText(False)
        self.ok_button = QPushButton('OK')
        self.ok_button.pressed.connect(self.automation)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.list)
        layout.addWidget(self.items)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.terminal)

        update_unreceived = QAction('Update Unreceived', self)
        update_unreceived.triggered.connect(self.update_unreceived_file)

        update_asin = QAction('Update Codes', self)
        update_asin.triggered.connect(self.update_codes_file)

        settings = QAction('Settings', self)
        settings.triggered.connect(self.open_settings)

        menu = self.menuBar()
        file_menu = menu.addMenu('Update')
        file_menu.addAction(update_unreceived)
        file_menu.addAction(update_asin)
        menu.addAction(settings)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def automation(self):
        option = self.list.currentText()
        info = self.items.toPlainText()
        self.items.clear()
        text = ''

        match option:
            case 'Receiving':
                packages = info.split()

                cheking = packages[1::2]
                if not all(map(lambda x: True if x[0:2] == 'NS' or x[0:2] == 'N/' else False, cheking)):
                    alert = CustomDialog(parent=self, text='Incorrect information provided')
                    alert.exec()
                    return

                packages_nship = [[A, B] for A, B in zip(packages[0::2], packages[1::2])]
                repeated, holds, problems, not_found = ffautomation.receiving(packages_nship, self.sleep_time,
                                                                              run_minimized=self.minimized)
                dictionary = {"Repeated": repeated, "Holds": holds, "Problems": problems, "Not found": not_found}

                for category in dictionary:
                    if dictionary[category]:
                        text += f"{category}:\n"
                        for value in dictionary[category]:
                            text += value + '\n'
                if not text:
                    text += 'All packages found'

                print('\n' + text)

            case 'Pre-manifest':
                outbounds = info.split()
                state = ffautomation.pre_manifest(outbounds, self.sleep_time, run_minimized=self.minimized)
                state = [x.split() for x in state]
                result = []
                for x in state:
                    if x[3] != 'Pre-manifested':
                        result.append(" ".join(x))
                if not result:
                    print('All packages pre-manifested')
                else:
                    print("\n".join(result))

            case 'Print Label':
                packages = info.split()
                message = ffautomation.print_label(packages)
                text = "\n".join(message)

                dlg = CustomDialog(parent=self, text=text)
                dlg.exec()

            case 'Codes':
                asins = info.split()
                message = ffautomation.codes(asins)
                text = "\n".join(message)

                dlg = CustomDialog(parent=self, text=text)
                dlg.exec()

            case 'Problems':
                a = InputWin(parent=self)
                if a.exec():
                    message = ffautomation.problemas(info.split(), a.user_input.split(),
                                                     initials=self.name, run_minimized=self.minimized)
                    text = "\n".join(message)

                    dlg = CustomDialog(parent=self, text=text)
                    dlg.exec()
                else:
                    return

    def update_unreceived_file(self):
        file_name = QFileDialog.getOpenFileName(self)[0]
        if file_name:
            fileupdate.new_packages(file_name)
            print('Unreceived File Updated')
        else:
            return

    def update_codes_file(self):
        file_name = QFileDialog.getOpenFileName(self)[0]
        if file_name:
            asin, country = fileupdate.asins(file_name)
            text = f'{len(asin)} rows need to be added'
            dlg = CustomDialog(self, text)
            dlg.exec()
            text = "\n".join(asin)
            dlg = CustomDialog(self, text)
            dlg.exec()
            text = "\n".join(country)
            dlg = CustomDialog(self, text)
            dlg.exec()

        else:
            return

    def normal_output_written(self, text):
        cursor = self.terminal.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.terminal.setTextCursor(cursor)
        self.terminal.ensureCursorVisible()

    def open_settings(self):
        if self.settings.exec():
            self.update_data()

    def update_data(self):
        self.user = self.settings.get_user
        self.sleep_time = self.settings.get_item('sleep_time', 'float')
        self.name = self.settings.get_item('name')
        self.minimized = self.settings.get_item('run_minimized', 'boolean')


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
