# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from ldapconmanager import LdapConManager
import sys
# from win32print import EnumPrinters, GetDefaultPrinter


class ComboBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent, items=[]):
        self.items = items
        super(ComboBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.items)
        editor.activated.connect(self.emitCommitData)
        return editor

    def setEditorData(self, editor, index):
        pos = 0
        editor.setCurrentIndex(pos)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())

    def emitCommitData(self):
        pass

class TableW(QtWidgets.QWidget):
    def __init__(self, parent=None, users={}, printers=[]):
        super(TableW, self).__init__(parent)
        self.itemsTable = QtWidgets.QTableWidget(len(users.keys()), 3)
        self.itemsTable.setItemDelegateForColumn(1, ComboBoxDelegate(self, printers)) #for column number 1
        for row, user in enumerate(users):
            self.itemsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(user))
            self.itemsTable.setItem(row, 1, QtWidgets.QTableWidgetItem('empty'))
            self.itemsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(users[user])))
        layout = QtWidgets.QVBoxLayout()
        self.itemsTable.setHorizontalHeaderLabels(['user', 'printer', 'sid'])
        self.itemsTable.resizeColumnsToContents()
        layout.addWidget(self.itemsTable)
        self.setLayout(layout)


if __name__ == '__main__':
    domain = 'ou=Users,dc=megateks,dc=net'
    server = '172.16.0.111'
    ldap_connection = LdapConManager(domain, server)
    if not isinstance( ldap_connection, str ):
        users = ldap_connection.get_user_sid()
    else:
        users = {}

    printers = ['test1','test2']
    # for i in EnumPrinters(2):
    #     printers.append(i[2])

    app = QtWidgets.QApplication(sys.argv)
    table = TableW(users=users, printers=printers)
    table.setWindowTitle('Defautl printers')
    table.setGeometry(0, 20,500,1024)
    
    table.showMaximized()

    sys.exit(app.exec_())