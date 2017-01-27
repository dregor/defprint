from win32print import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSlot
from ConfigParser import ConfigParser
from main import UserManager
from ldapconmanager import LdapConManager
import sys


def get_printers():
    printers = [None]
    printers_to_end = []
    for printer in EnumPrinters(2):
        if not GetPrinter(OpenPrinter(printer[2]))[3][0:2] == 'TS':
            printers.append(printer[2].decode('cp1251'))
        else:
            printers_to_end.append(printer[2].decode('cp1251'))
    printers.sort()
    printers = printers + printers_to_end
    return printers


def consoleEncode(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            return s.encode('utf8').decode(sys.stdout.encoding)
        else:
            return s.encode('utf8')


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, parent, items=[]):
        self.items = items
        self.editor = None
        super(ComboBoxDelegate, self).__init__(parent)


    def createEditor(self, parent, option, index):
        self.editor = editor = QComboBox(parent)
        editor.addItems(self.items)
        editor.currentIndexChanged.connect(self.emitCommitData)  
        return editor


    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


    def emitCommitData(self):
        try:
            table = self.parent().table
            sid = table.item(table.selectionModel().selectedRows()[0].row(), 0).text()
            print('LENGTH - ' + str(len(table.selectionModel().selectedRows())))
            print('ROW - ' + str(table.selectionModel().selectedRows()[0].row()))
            printer = self.editor.currentText()
            self.parent().userManager.setDefaultPrinter(sid, printer)
        except Exception as e:
            print(e)


class Window(QWidget):
    def __init__(self, userManager, parent=None, printers=[]):
        super(Window, self).__init__(parent)
        self.userManager = userManager
        self.printers = printers
        self.layout = QVBoxLayout()
        self.make_table()
        self.update_printers()
        self.setLayout(self.layout)


    def make_table(self):
        users = self.userManager.getUsersFromRegDict()
        self.table = table = QTableWidget(len(users.keys()), 3)
        for row, user in enumerate(users):
            table.setItem(row, 0, QTableWidgetItem(user))
            table.setItem(row, 1, QTableWidgetItem(users[user]['uid']))
            table.setItem(row, 2, QTableWidgetItem(users[user]['default_printer']))
            # table.setItem(row, 3, QTableWidgetItem(str(users[user]['registry'])))
        table.setHorizontalHeaderLabels(['sid', 'user', 'printer', 'registry'])
        table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setWindowTitle('Defautl printers')
        table.resizeColumnsToContents()
        for row in range(0, table.rowCount()):
            flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            table.item(row, 0).setFlags(flags)
            table.item(row, 1).setFlags(flags)
            # table.item(row, 3).setFlags(flags)
        self.layout.addWidget(table)


    def update_printers(self):
        if self.table is not None:
            self.table.setItemDelegateForColumn(2, ComboBoxDelegate(self, self.printers))

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    try:
        domain = config.get('ldap','domain')
        server = config.get('ldap','server')
    except:
        print('Can not find need section in config file!')
        sys.exit()

    app = QApplication(sys.argv)
    win = Window(userManager=UserManager(domain, server), printers=get_printers())
    win.showMaximized()
    sys.exit(app.exec_())