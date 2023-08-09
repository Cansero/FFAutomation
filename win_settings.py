from configparser import ConfigParser
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QDialogButtonBox, \
    QVBoxLayout

config = ConfigParser()
config.read('settings.ini')


class Settings(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')

        self.section = config.sections()[0] if len(config.sections()) else 'DEFAULT'

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

        btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Save
        self.buttonBox = QDialogButtonBox(btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.clicked.connect(self.applied)

        layout = QVBoxLayout()
        layout.addLayout(initals_layout)
        layout.addLayout(sleep_time_layout)
        layout.addLayout(update_layout)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def applied(self, button):
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

    def get_settings(self):
        return config.items(self.section)

    def get_item(self, item, as_type='str'):
        match as_type:
            case 'str':
                return config.get(self.section, item)
            case 'int':
                try:
                    return config.getint(self.section, item)
                except ValueError:
                    return config.get(self.section, item)
            case 'float':
                try:
                    return config.getfloat(self.section, item)
                except ValueError:
                    return config.get(self.section, item)
            case 'boolean':
                try:
                    return config.getboolean(self.section, item)
                except ValueError:
                    return config.get(self.section, item)
