import sys
from configparser import ConfigParser
from PySide6.QtWidgets import QDialog, QMainWindow, QLabel, QPushButton, QVBoxLayout, QLineEdit, QApplication, QWidget, \
    QHBoxLayout, QSpinBox, QDoubleSpinBox

config = ConfigParser()
config.read('settings.ini')


class Settings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')

        section = 'DEFAULT'
        if len(config.sections()):
            section = config.sections()[0]

        section_layout = QHBoxLayout()
        section_label = QLabel('Settings:')
        self.section_name = QLineEdit(section)
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_name)

        sleep_time_layout = QHBoxLayout()
        sleep_time_label = QLabel('Delay: ')
        self.sleep_time = QDoubleSpinBox()
        self.sleep_time.setValue(config.getfloat(section, 'sleep_time'))
        self.sleep_time.setSingleStep(0.1)
        sleep_time_layout.addWidget(sleep_time_label)
        sleep_time_layout.addWidget(self.sleep_time)

        layout = QVBoxLayout()
        layout.addLayout(section_layout)
        layout.addLayout(sleep_time_layout)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Test')

        self.settings = Settings()

        label = QLabel('Test')
        button = QPushButton('Settings')
        button.clicked.connect(self.open_settings)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_settings(self):
        if self.settings.isVisible():
            self.settings.hide()
        else:
            self.settings.show()


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
