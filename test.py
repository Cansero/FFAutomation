from configparser import ConfigParser
from PySide6.QtWidgets import QDialog, QMainWindow, QLabel, QPushButton, QVBoxLayout, QLineEdit, QApplication, QWidget,\
    QHBoxLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QComboBox

config = ConfigParser()
config.read('settings.ini')


class Settings(QDialog):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle('Settings')

        self.section = user

        initals_layout = QHBoxLayout()
        initials_label = QLabel('Initials:')
        self.initials = QLineEdit('' if self.section == 'DEFAULT' else self.section)
        initals_layout.addWidget(initials_label)
        initals_layout.addWidget(self.initials)

        sleep_time_layout = QHBoxLayout()
        sleep_time_label = QLabel('Delay:')
        self.sleep_time = QDoubleSpinBox()
        self.sleep_time.setValue(config.getfloat(self.section, 'sleep_time'))
        self.sleep_time.setSingleStep(0.1)
        sleep_time_layout.addWidget(sleep_time_label)
        sleep_time_layout.addWidget(self.sleep_time)

        update_layout = QHBoxLayout()
        update_label = QLabel('Delay for updates:')
        self.update = QSpinBox()
        self.update.setValue(config.getint(self.section, 'update_interval'))
        self.update.setSingleStep(1)
        update_layout.addWidget(update_label)
        update_layout.addWidget(self.update)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Save
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.applyed)

        layout = QVBoxLayout()
        layout.addLayout(initals_layout)
        layout.addLayout(sleep_time_layout)
        layout.addLayout(update_layout)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def applyed(self, button):
        if button.text() == 'Save':
            user = self.initials.text() if self.initials.text() else '??'
            if user != self.section:
                config.remove_section(self.section)
                self.set_user(user)
            if not config.has_section(user):
                config.add_section(user)
            config.set(user, 'sleep_time', str(round(self.sleep_time.value(), 2)))
            config.set(user, 'name', user)
            config.set(user, 'update_interval', str(self.update.value()))

            with open('settings.ini', 'w') as file:
                config.write(file)

    @property
    def get_user(self):
        return self.section

    def set_user(self, user):
        self.section = user


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Test')

        self.user = 'DEFAULT' if not len(config.sections()) else config.sections()[0]

        label = QLabel('Test')
        ok = QPushButton('OK')
        ok.clicked.connect(self.presionado)
        button = QPushButton('Settings')
        button.clicked.connect(self.open_settings)

        self.list = QComboBox()
        self.list.addItems(['test', 'test2', 'test3', 'test4', 'test5'])

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(ok)
        layout.addWidget(button)
        layout.addWidget(self.list)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_settings(self):
        settings = Settings(self.user)
        if settings.exec():
            self.user = settings.get_user

    def presionado(self):
        text = ''
        match self.list.currentText():
            case 'test' | 'test2':
                text = 'opt1'
            # case 'test2':
            #     text = 'opt2'
            case 'test3':
                text = 'opt3'
            case 'test4':
                text = 'opt4'
            case 'test5':
                text = 'opt5'

        print(text)


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
