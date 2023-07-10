import pandas as pd
import gspread
from PySide6.QtGui import QAction

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget, QComboBox, QTextEdit, QDialog, QDialogButtonBox, QStackedLayout, QHBoxLayout, QLineEdit, QFileDialog,
)


gc = gspread.oauth(
    credentials_filename='credentials.json',
    authorized_user_filename='authorized_user.json'
)


def correct_length(string):
    while len(string) < 10:
        string = '0' + string
    return string


def new_packages(directory):
    cm_package = gc.open('CM NSHIP PACKAGE INFORMATION 2023')
    main_file = pd.DataFrame(cm_package.worksheet('MAIN FILE').get_all_records())
    main_file['Inbound tracking'] = main_file['Inbound tracking'].astype(str)

    unreceived = pd.read_csv(directory)
    unreceived = unreceived.loc[:, 'Status':'Postal Code']

    unreceived['Inbound tracking'] = unreceived['Inbound tracking'].str[1:]
    unreceived['Outbound tracking'] = unreceived['Outbound tracking'].str[4:]

    mascara = unreceived['Inbound tracking'].isin(['link to amazon', 'Tracking Available Soon']) | \
              pd.isna(unreceived['Inbound tracking'])

    unreceived = unreceived.loc[~mascara]

    mascara = unreceived['Inbound tracking'].isin(main_file['Inbound tracking'])

    unreceived = unreceived.loc[~mascara]
    unreceived = unreceived.fillna('')

    dl = cm_package.worksheet('DL')
    dl.update([unreceived.columns.values.tolist()] + unreceived.values.tolist())


def asins(directory):
    master_file = gc.open('MASTER FILE NUEVO')
    master_file = pd.DataFrame(master_file.worksheet('DATA').get_all_records())
    master_file['ASIN\n0'] = master_file['ASIN\n0'].astype(str)
    master_file['ASIN\n0'] = master_file['ASIN\n0'].apply(correct_length)

    asins_manual = gc.open('UNRECEIVED CA')
    asins_manual = pd.DataFrame(asins_manual.worksheet('UNRECEIVED CA').get_all_records())
    asins_manual['ASIN'] = asins_manual['ASIN'].astype(str)
    asins_manual['ASIN'] = asins_manual['ASIN'].apply(correct_length)

    unreceived = pd.read_csv(directory)
    unreceived = unreceived.loc[:, ['ASIN', 'Country']]
    unreceived = unreceived.fillna(value={'Country': 'China'})
    unreceived['Country'] = unreceived['Country'].apply(lambda x: x.upper())
    unreceived['ASIN'] = unreceived['ASIN'].astype(str)

    mascara = unreceived['ASIN'].isin(master_file['ASIN\n0'])
    unreceived = unreceived.loc[~mascara]

    mascara = unreceived['ASIN'].isin(asins_manual['ASIN'])
    unreceived = unreceived.loc[~mascara]

    coo = pd.read_csv('CSV/UNRECEIVED CA - COO.csv')
    coo = coo.set_index('COUNTRY')

    unreceived['Country'] = unreceived['Country'].map(coo['ALPHA 2'])

    asin = unreceived['ASIN'].tolist()
    country = unreceived['Country'].tolist()

    return asin, country


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
        message.setReadOnly(True)
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
        self.list.addItems(['Receiving', 'Pre-manifest', 'Print Label', 'Codes', 'Problems'])
        self.items = QTextEdit()
        self.items.setAcceptRichText(False)
        self.ok_button = QPushButton('OK')
        self.ok_button.pressed.connect(self.automation)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.list)
        layout.addWidget(self.items)
        layout.addWidget(self.ok_button)

        update_unreceived = QAction('Update Unreceived', self)
        update_unreceived.triggered.connect(self.update_unreceived_file)

        update_asin = QAction('Update Codes', self)
        update_asin.triggered.connect(self.update_codes_file)

        menu = self.menuBar()
        file_menu = menu.addMenu('Update')
        file_menu.addAction(update_unreceived)
        file_menu.addAction(update_asin)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def automation(self):
        pass

    def update_unreceived_file(self):
        file_name = QFileDialog.getOpenFileName(self)[0]
        if file_name:
            new_packages(file_name)
            dlg = CustomDialog(self, 'done')
            dlg.exec()
        else:
            return

    def update_codes_file(self):
        file_name = QFileDialog.getOpenFileName(self)[0]
        if file_name:
            asin, country = asins(file_name)
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


if __name__ == '__main__':
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
