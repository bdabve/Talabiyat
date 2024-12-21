#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------

from PyQt5 import QtWidgets, QtCore
from gui.h_confirmDialog import Ui_Dialog
from gui.h_addToCartDialog import Ui_AddToCart


class ConfirmDialog(QtWidgets.QDialog):
    def __init__(self, message):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set Focus
        self.setModal(True)

        self.ui.labelTitle.setText('تأكيد الحذف')
        self.ui.labelMessage.setText(message)

        self.ui.buttonConfirm.setText('حذف')
        self.ui.buttonCancel.setText('إلغاء')

        self.ui.buttonConfirm.clicked.connect(self.accept)
        self.ui.buttonCancel.clicked.connect(self.reject)


class AddProductToCart(QtWidgets.QDialog):
    def __init__(self, product_map):
        super().__init__()
        self.ui = Ui_AddToCart()
        self.ui.setupUi(self)

        self.product_map = product_map
        self.selected_product = ''
        self.qte = 0

        # Remove title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set Focus
        self.setModal(True)

        # Populate the combobox
        self.ui.comboBoxProduct.clear()
        for key in product_map.keys():
            self.ui.comboBoxProduct.addItem(key)

        # Callbacks
        self.ui.comboBoxProduct.currentIndexChanged.connect(self.update_spinbox_qte)

        self.ui.buttonConfirm.clicked.connect(self.return_values)
        self.ui.buttonCancel.clicked.connect(self.reject)

        # Initial setup
        self.update_spinbox_qte()

    def update_spinbox_qte(self):
        """
        Update the spinBox to fit the maximum Qte in database
        This work with combo_box.currentIndexChanged
        """
        selected_product = self.ui.comboBoxProduct.currentText()
        if selected_product in self.product_map:
            max_qte = self.product_map[selected_product]["qte"]
            self.ui.spinBoxQte.setMaximum(max_qte)  # Set the maximum to available stock
            self.ui.spinBoxQte.setValue(1)  # Reset to minimum value

    def return_values(self):
        self.selected_product = self.ui.comboBoxProduct.currentText()
        qte = self.ui.spinBoxQte.value()
        if qte == 0:
            self.reject()
        else:
            self.qte = qte
            self.accept()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # dialog = ConfirmDialog('هل أنت متأكد من حذف السلعة')
    dialog = AddProductToCart()
    dialog.show()
    sys.exit(app.exec_())
