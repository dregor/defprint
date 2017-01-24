from win32print import EnumPrinters, GetPrinter, OpenPrinter
from PyQt5 import QtCore, QtWidgets, QtGui
from ldapconmanager import LdapConManager
from registry import Root
import sys


def consoleEncode(s):
    try:
        print(s)
    except UnicodeEncodeError:
        if sys.version_info >= (3,):
            return s.encode('utf8').decode(sys.stdout.encoding)
        else:
            return s.encode('utf8')


def get_users(domain, server):
    regRoot = Root()
    ldap_connection = LdapConManager(domain, server)
    if not isinstance( ldap_connection, str ):
        users = ldap_connection.get_user_sid()
    else:
        users = {}
    for user in users:
        users[user].update({'default_printer': get_default_printer(regRoot, users[user]['sid'])})
    return users


def get_default_printer(reg, sid):
    regRoot = reg
    try:
        tmp_vals = {}
        for item in regRoot.users(sid + r'/software/microsoft/windows nt/currentversion/windows').vals:
            tmp_vals.update({item.name: item.val})
        return tmp_vals['Device'].split(',')[0]
    except KeyError:
        return 'Empty'


def get_printers():
    printers = []
    for printer in EnumPrinters(2):
        if not GetPrinter(OpenPrinter(printer[2]))[3][0:2] == 'TS':
            printers.append(printer[2].decode('cp1251'))
    printers.append('Empty')
    return printers


def get_printer_spool(reg, sid, printer):
    regRoot = reg
    try:
        vals = regRoot.users(sid + r'/software/microsoft/windows nt/currentversion/devices').vals
        return vals[vals.index(printer)]
    except KeyError:
        return None


class ComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent, items=[]):
        self.items = items
        super(ComboBoxDelegate, self).__init__(parent)


    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        self.items.append(index.model().data(index))
        editor.addItems(self.items)
        editor.activated.connect(self.emitCommitData)        
        return editor


    def setEditorData(self, editor, index):
        editor.setCurrentIndex(self.items.index(index.model().data(index)))


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
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(self.users[user]['default_printer']))
            table.setItem(row, 2, QtWidgets.QTableWidgetItem(self.users[user]['sid']))
        table.setHorizontalHeaderLabels(['user', 'printer', 'sid'])
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)
        table.setWindowTitle('Defautl printers')
        table.resizeColumnsToContents()
        self.layout.addWidget(table)


    def update_printers(self):
        if self.table is not None:
            self.table.setItemDelegateForColumn(1, ComboBoxDelegate(self, self.printers))

if __name__ == '__main__':
    domain = 'ou=Users,dc=megateks,dc=net'
    server = '10.10.0.1'

    app = QtWidgets.QApplication(sys.argv)
    win = Window(users=get_users(domain, server), printers=get_printers())
    win.showMaximized()
    sys.exit(app.exec_())