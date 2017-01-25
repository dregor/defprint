from win32print import EnumPrinters, GetPrinter, OpenPrinter
from PyQt5 import QtCore, QtWidgets, QtGui
from ldapconmanager import LdapConManager
from main import UserManager
import sys


def get_printers():
    printers = []
    for printer in EnumPrinters(2):
        if not GetPrinter(OpenPrinter(printer[2]))[3][0:2] == 'TS':
            printers.append(printer[2].decode('cp1251'))
    printers.append(None)
    return printers


def consoleEncode(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            return s.encode('utf8').decode(sys.stdout.encoding)
        else:
            return s.encode('utf8')


class ComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent, items=[]):
        self.items = items
        super(ComboBoxDelegate, self).__init__(parent)


    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.items)
        editor.activated.connect(self.emitCommitData)        
        return editor

    def onClick(self):
        text = index.model().data(index)
        if text not in self.items:
            editor.addItem(text)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


    def emitCommitData(self):
        pass


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None, users={}, printers=[]):
        super(Window, self).__init__(parent)
        self.users, self.printers = users, printers
        self.layout = QtWidgets.QVBoxLayout()
        self.make_table()
        self.update_printers()
        self.setLayout(self.layout)


    def make_table(self):
        self.table = table = QtWidgets.QTableWidget(len(self.users.keys()), 3)
        for row, user in enumerate(self.users):
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(user))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(self.users[user]['uid']))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(self.users[user]['default_printer']))
        table.setHorizontalHeaderLabels(['sid', 'user', 'printer'])
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)
        table.setWindowTitle('Defautl printers')
        table.resizeColumnsToContents()
        self.layout.addWidget(table)


    def update_printers(self):
        if self.table is not None:
            self.table.setItemDelegateForColumn(2, ComboBoxDelegate(self, self.printers))

if __name__ == '__main__':
    domain = 'ou=Users,dc=megateks,dc=net'
    server = '10.10.0.1'
    um = UserManager(domain, server)
    app = QtWidgets.QApplication(sys.argv)

    win = Window(users=um.getUsersFromRegDict(), printers=get_printers())
    win.showMaximized()
    sys.exit(app.exec_())