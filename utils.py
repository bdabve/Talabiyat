from PyQt5 import QtWidgets, QtGui, QtCore
import qtawesome as qta

MENU_BUTTON_COLOR = "#ffffff"
# BUTTON_PLUS_COLOR = "#25CCF7"
# BUTTON_EDIT_COLOR = "#60a3bc"
# BUTTON_DELETE_COLOR = "#EA2027"
BUTTON_PLUS_COLOR = "#ffffff"
BUTTON_EDIT_COLOR = "#ffffff"
BUTTON_DELETE_COLOR = "#ffffff"


class Utils:
    """
    Utility class for PyQt5 operations such as handling QTableWidget and QComboBox.
    """

    success_stylesheet = "color: rgb(28, 113, 216);"
    error_stylesheet = "color: rgb(192, 28, 40);"

    def interface_icons_callbacks(root):
        """
        This is the main function for callback functions
        and Icons
        """
        # PROCESS PAGE
        # -------------------
        buttons_icons_callbacks = [
            # Main Button Pages
            (
                root.ui.buttonProductPage,
                qta.icon('mdi.alpha-p-box', color=MENU_BUTTON_COLOR),
                lambda: root.goto_page(page="Products")
            ),

            (
                root.ui.buttonCustomerPage,
                qta.icon('ph.users-three-light', color=MENU_BUTTON_COLOR),
                lambda: root.goto_page(page="Customers")
            ),

            (
                root.ui.buttonOrderPage,
                qta.icon('mdi6.clipboard', color=MENU_BUTTON_COLOR),
                lambda: root.goto_page(page="Orders")
            ),

            # Details Card Buttons
            (
                root.ui.buttonCloseCard,
                qta.icon('ri.close-fill', color="#227093"),
                root.ui.dockWidget.close
            ),

            # Product Page Buttons
            (
                # product details
                root.ui.buttonProductDetails,
                qta.icon('mdi6.information-variant', color="#ffffff"),
                lambda: root.item_details(lineEditEnabled=False)
            ),
            (
                # New Product
                root.ui.buttonNewProduct,
                qta.icon('ph.plus', color=BUTTON_PLUS_COLOR),
                root.new_product
            ),
            (
                # Edit product
                root.ui.buttonEditProduct,
                qta.icon('mdi6.tooltip-edit', color=BUTTON_EDIT_COLOR),
                lambda: root.item_details(lineEditEnabled=True, operation='Edit')
            ),
            (
                # Delete Product
                root.ui.buttonDeleteProduct,
                qta.icon('mdi6.delete-outline', color=BUTTON_DELETE_COLOR),
                lambda: root.delete_item(coll_name='Products')
            ),

            (   # Activate Customer
                root.ui.buttonProductStatus,
                qta.icon('mdi6.check', color=BUTTON_DELETE_COLOR),
                lambda: root.activate_item(coll_name='Products')
            ),

            # THE SAVE BUTTON
            (
                root.ui.buttonSave,
                qta.icon('mdi.content-save', color="#ffffff"),
                root.save_new_item
            ),

            # CUSTOMERS PAGE
            (   # Customer Details
                root.ui.buttonCustomerDetails,
                qta.icon('mdi.account-question', color="#ffffff"),
                lambda: root.item_details(lineEditEnabled=False, operation="None", coll_name="Customers")
            ),

            (   # New Customer
                root.ui.buttonNewCustomer,
                qta.icon('mdi6.account-plus', color=BUTTON_PLUS_COLOR),
                lambda: root.new_customer()
            ),

            (   # Edit Customer
                root.ui.buttonEditCustomer,
                qta.icon('mdi6.account-edit', color=BUTTON_EDIT_COLOR),
                lambda: root.item_details(lineEditEnabled=True, operation="Edit", coll_name="Customers")
            ),
            (   # Delete Customer
                root.ui.buttonDeleteCustomer,
                qta.icon('mdi6.account-minus', color=BUTTON_DELETE_COLOR),
                lambda: root.delete_item(coll_name='Customers')
            ),
            (   # Activate Customer
                root.ui.buttonCustomerStatus,
                qta.icon('mdi6.check-underline', color=BUTTON_DELETE_COLOR),
                lambda: root.activate_item(coll_name='Customers')
            ),

            # ORDERS PAGE
            (   # Order Details
                root.ui.buttonOrderDetails,
                qta.icon('mdi6.information-variant', color="#ffffff"),
                lambda: root.order_details(lineEditEnabled=False)
            ),
            (
                # NEW ORDER
                root.ui.buttonNewOrder,
                qta.icon('ph.plus', color=BUTTON_PLUS_COLOR),
                root.new_order
            ),
            (
                # Button Add To Cart
                root.ui.buttonAddToCart,
                qta.icon('ph.plus', color="#ffffff"),
                lambda: root.add_product_to_table(root.ui.tableWidgetAddOrderProds)
            ),
            (
                # Delete Order
                root.ui.buttonDeleteOrder,
                qta.icon('mdi6.delete-outline', color=BUTTON_DELETE_COLOR),
                lambda: root.delete_item(coll_name='Orders')
            ),
        ]

        for button, icon, callback in buttons_icons_callbacks:
            button.setIcon(icon)
            button.clicked.connect(callback)

        # Just Icons
        root.ui.buttonOrderStatus.setIcon(qta.icon('mdi.list-status', color=MENU_BUTTON_COLOR))

        # Callback Functions
        root.ui.lineEditSearchProduct.textChanged.connect(root.search_products)
        root.ui.searchButtonIcon.clicked.connect(root.search_products)

        # => Product TableWidget
        root.ui.tableWidgetProduct.itemDoubleClicked.connect(lambda: root.item_details(lineEditEnabled=False))
        root.ui.tableWidgetProduct.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Products'))

        # => Customer TableWidget
        root.ui.tableWidgetCustomer.itemDoubleClicked.connect(
            lambda: root.item_details(lineEditEnabled=False, coll_name="Customers")
        )

        root.ui.tableWidgetCustomer.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Customers'))

        # Order Table
        root.ui.tableWidgetOrders.itemDoubleClicked.connect(lambda: root.order_details(lineEditEnabled=False))
        root.ui.tableWidgetOrders.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Orders'))

        # # search button icon
        # root.ui.searchButtonIcon.setIcon(qta.icon('ri.search-line', color="#ffffff"))

        # # resume, suspend, terminate buttons
        # root.ui.buttonTerminate.setIcon(qta.icon('mdi6.skull', color="#ffffff"))

        # root.ui.buttonResume.setIcon(qta.icon('fa5s.walking', color="#ffffff"))

        # root.ui.buttonSuspend.setIcon(qta.icon('mdi.motion-pause-outline', color="#ffffff"))

    def setup_order_status_menu(button, callback):
        """
        Sets up a QMenu for changing the order status on a QPushButton.

        :param button: The QPushButton instance.
        :param callback: Function to call when a menu item is clicked.
        """
        # Create a QMenu
        menu = QtWidgets.QMenu()
        menu.setLayoutDirection(QtCore.Qt.LeftToRight)
        menu.setStyleSheet("""
QMenu {
    background-color: #272727;
    margin: 2px; /* some spacing around the menu */
    border-color: 2px solid #4b4b4b;
    border-radius: 10px;
}

QMenu::item {
    font: 10pt "Noto Serif Thai";
    color: #ffffff;
    padding: 2px 5px 2px 5px;
    border: 1px solid transparent; /* reserve space for selection border */
    min-width: 200px;
}

QMenu::item:selected {
    background: #4b4b4b;
}

QMenu::icon:checked { /* appearance of a 'checked' icon */
    background: gray;
    border: 1px inset gray;
    position: absolute;
    top: 1px;
    right: 1px;
    bottom: 1px;
    left: 1px;
}

QMenu::indicator {
    width: 0px;
    height: 0px;
}
       """)
        # Define possible statuses
        statuses = {
            "pending": "قيد الانتظار",
            "confirmed": "مؤكد",
            "shipped": "تم الشحن",
            "delivered": "تم التوصيل",
            "cancelled": "ملغي"
        }

        # Add actions for each status
        for status_key, status_label in statuses.items():
            action = menu.addAction(status_label)
            action.setData(status_key)  # Store the status key as action data

        # Connect the menu's triggered signal to the callback function
        menu.triggered.connect(lambda action: callback(action.data()))

        # Attach the menu to the QPushButton
        button.setMenu(menu)

    def success_message(label, message, success=True):
        """
        This function display message in label
        :label: the label where to display the message
        :message: message to display like response['message']
        :success: change style sheet if sucess; else danger
        """
        label.setText(message)
        if success:
            label.setStyleSheet('color: green')
        else:
            label.setStyleSheet('color: red')

    @staticmethod
    def selected_rows(table: QtWidgets.QTableWidget) -> bool:
        """
        Check if table has a selected rows
        :table: table widget name
        :return: True or False
        """
        # TODO:  Enter this in TableWidgetFuncs class
        if len(table.selectionModel().selectedRows()) > 0: return True
        else: return False

    @staticmethod
    def table_selection_ids(table: QtWidgets.QTableWidget) -> list:
        """
        This function return column(0) for a multiple selection in a table
        :table: QTableWidget
        :return: a list of ids.
        """
        selected_rows = set(index.row() for index in table.selectedIndexes())   # return index of selected row
        if len(selected_rows) > 0:
            ids = [table.item(row, 0).text() for row in selected_rows]
        return ids

    @staticmethod
    def get_column_value(table: QtWidgets.QTableWidget, column: int) -> str:
        """
        Get the value from a specific column of the selected row in a QTableWidget.

        :param table: The QTableWidget instance.
        :param column: The column index to retrieve the value from.
        :return: The value as a string.
        """
        row = table.currentRow()
        return table.item(row, column).text()

    @staticmethod
    def populate_table_widget(table: QtWidgets.QTableWidget, rows: list, headers: list):
        """
        Populate a QTableWidget with rows and headers.

        :param table: The QTableWidget instance.
        :param rows: A list of rows where each row is a list or tuple of values.
        :param headers: A list of column headers.
        """
        table.clear()
        table.setColumnCount(len(headers))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)

        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)

    @staticmethod
    def table_column_size(table: QtWidgets.QTableWidget, columns: list) -> None:
        """
        Change table columns size
        :table: the table widget
        :column: tuple(column_index, size) ex: (1, 300), (0, 200)
        :ex: table_column_size(root.ui.tableWorkExperience, [(1, 300), (0, 200)])
        """
        for column in columns:
            c, size = column
            table.setColumnWidth(c, size)

    @staticmethod
    def populate_comboBox(combobox: QtWidgets.QComboBox, items: list):
        """
        Populate a QComboBox with a list of items.

        :param combobox: The QComboBox instance.
        :param items: A list of strings to populate the combobox.
        """
        combobox.blockSignals(True)
        combobox.clear()
        combobox.addItems(items)
        combobox.blockSignals(False)

    @staticmethod
    def pagebuttons_stats(root):
        """
        Update page button states based on the current page.
        """
        current_page = root.ui.containerStackedWidget.currentIndex()
        root.ui.buttonProductPage.setChecked(current_page == 0)
        root.ui.buttonCustomerPage.setChecked(current_page == 1)
        root.ui.buttonOrderPage.setChecked(current_page == 2)

    @staticmethod
    def create_label(parent, label_name):
        """Create a styled QLabel."""
        label = QtWidgets.QLabel(parent)

        label.setObjectName(label_name)
        label.setFont(QtGui.QFont("Monaco", 12))
        label.setWordWrap(True)
        label.setStyleSheet(
            "border: 1px solid rgb(64, 66, 72); border-top:none; border-left: none; border-right: none"
        )
        return label

    @staticmethod
    def create_lineEdit(parent, name):
        """Create a styled QLabel."""
        line_edit = QtWidgets.QLineEdit(parent)

        line_edit.setObjectName(name)
        return line_edit

    @staticmethod
    def create_spinBox(parent=None, name=None):
        """Create a styled QLabel."""
        if parent:
            spin_box = QtWidgets.QSpinBox(parent)
        else:
            spin_box = QtWidgets.QSpinBox()
        if name:
            spin_box.setObjectName(name)
        spin_box.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        spin_box.setMaximum(16777215)
        return spin_box

    @staticmethod
    def create_doubleSpinBox(parent, name):
        """Create a styled QLabel."""
        double_spinbox = QtWidgets.QDoubleSpinBox(parent)

        double_spinbox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        double_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        double_spinbox.setMaximum(16777215)
        double_spinbox.setObjectName(name)
        return double_spinbox

    @staticmethod
    def clear_details_form(form_layout):
        """Clear all widgets from a QFormLayout."""
        while form_layout.count():
            item = form_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    @staticmethod
    def show_confirm_dialog(parent, message):
        """
        Displays a confirmation dialog before deleting an item.

        :param parent: The parent widget for the dialog.
        :message: the message to display in Dialog
        :return: True if confirmed, False otherwise.
        """
        # Create the confirmation dialog
        confirm_dialog = QtWidgets.QMessageBox(parent)
        with open('./dialog_styleSheet.css') as f:
            confirm_dialog.setStyleSheet(f.read())

        confirm_dialog.setIcon(QtWidgets.QMessageBox.Warning)
        confirm_dialog.setWindowTitle("تأكيد الحذف")
        confirm_dialog.setText(message)
        confirm_dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        # Execute the dialog and get the user's response
        result = confirm_dialog.exec_()

        return result == QtWidgets.QMessageBox.Yes  # Return True if 'Yes' is clicked
