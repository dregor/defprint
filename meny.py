# -*- coding: utf-8 -*-
from PyQt5 import QtCore,QtWidgets
from win32print import EnumPrinters, GetDefaultPrinter


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
    def __init__(self, parent=None, printers=[]):
        super(TableW, self).__init__(parent, QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint)
        items = ['one','two','three']        
        self.itemsTable = QtWidgets.QTableWidget(len(items), 2)
        self.itemsTable.setItemDelegateForColumn(1, ComboBoxDelegate(self, printers)) #for column number 1
        for row, item in enumerate(items):
            name = QtWidgets.QTableWidgetItem(item)
#           name.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.itemsTable.setItem(row, 0, name)
            self.itemsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(GetDefaultPrinter()))
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.itemsTable)
        self.setLayout(layout)


if __name__ == '__main__':
    printers = []
    for i in EnumPrinters(2):
        printers.append(i[2])
    import sys
    app = QtWidgets.QApplication(sys.argv)
    table = TableW(printers=printers)
    
    table.show()
    res = app.exec_()
    table = 0
    sys.exit(res)