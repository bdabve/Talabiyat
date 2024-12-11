from PyQt5 import QtWidgets, QtGui    # , QtCore
import qtawesome as qta

MENU_BUTTON_COLOR = "#ffffff"


class Utils:
    """
    Utility class for PyQt5 operations such as handling QTableWidget and QComboBox.
    """

    success_stylesheet = "color: rgb(28, 113, 216);"
    error_stylesheet = "color: rgb(192, 28, 40);"

    dialog_styleSheet = """
QDialog {
    background-color: #2c2c2c;
}

/********************
    QComboBox
***********************/
QComboBox {
    font: italic 12pt "Droid Sans Fallback";
    background-color: transparent;
    color: #ffffff;
    border-radius: 5px;
    border: 1px solid rgb(64, 66, 72);
    padding: 5px;
    padding-left: 10px;
    combobox-popup: 0;
}
QComboBox:hover{
    border: 2px solid rgb(64, 71, 88);
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-right-width: 3px;
    border-right-color: rgb(64, 66, 72);
    border-right-style: solid;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    background-image: url(:/icons/icons/cil-arrow-bottom.png);
    background-position: center;
    background-repeat: no-reperat;
 }

QComboBox QAbstractItemView {
    color: #4b7bec; /*rgb(255, 121, 198);	*/
    background-color: transparent;
    padding: 10px 7px;
    selection-background-color: rgb(39, 44, 54);
    border: 2px solid rgb(64, 71, 88);
    border-top: none;
    border-radius: 3px;
}

QComboBox QAbstractItemView::item {
    padding: 12px;
}

/********************
    QSpinBox
***********************/
QSpinBox {
    font: italic 12pt "Droid Sans Fallback";
    background: transparent;
    color: #ffffff;
    border: none;
    padding: 5px;
}

QSpinBox:enabled
{
    background-color: rgba(51, 50, 50, 172);
    border-bottom: 2px solid #4c4c4c;
}

QSpinBox:focus {
    border-bottom: 2px solid rgb(178, 178, 178);
}
    """

    def interface_icons_callbacks(root):
        """
        This is the main function for callback functions
        and Icons
        """
        # PROCESS PAGE
        # -------------------
        buttons_icons_callbacks = [
            # Main Button Pages
            (root.ui.buttonProductPage, qta.icon('mdi.alpha-p-box', color=MENU_BUTTON_COLOR), root.goto_product_page),
            (root.ui.buttonOrderPage, qta.icon('mdi6.clipboard', color=MENU_BUTTON_COLOR), root.goto_order_page),

            # Details Card Buttons
            (root.ui.buttonCloseCard, qta.icon('ri.close-fill', color="#227093"), root.ui.dockWidget.close),

            # Product Page Buttons
            (
                # product details
                root.ui.buttonProductDetails,
                qta.icon('mdi6.information-variant', color="#ffffff"),
                lambda: root.product_details(lineEditEnabled=False)
            ),
            (
                # new product
                root.ui.buttonNewProduct,
                qta.icon('ph.plus-circle-thin', color="#ffffff"),
                root.new_product
            ),
            (
                # edit product
                root.ui.buttonEditProduct,
                qta.icon('mdi6.tooltip-edit', color="#16a085"),
                lambda: root.product_details(lineEditEnabled=True, operation='Edit')
            ),
            (
                # delete product
                root.ui.buttonDeleteProduct,
                qta.icon('mdi6.delete-outline', color="#EA2027"),
                root.delete_product
            ),
            # THE SAVE BUTTON
            (
                root.ui.buttonSave,
                qta.icon('mdi.content-save', color="#ffffff"),
                root.save_new_item
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
                qta.icon('ph.plus-circle-thin', color="#ffffff"),
                root.new_order
            ),
            (
                root.ui.buttonAddToCart,
                qta.icon('ph.plus', color="#ffffff"),
                lambda: root.add_product_to_table(root.ui.tableWidgetAddOrderProds)
            ),

            (
                # EDIT ORDER
                root.ui.buttonEditOrder,
                qta.icon('mdi6.tooltip-edit', color="#16a085"),
                lambda: root.order_details(lineEditEnabled=True, operation="Edit")
            ),
            (
                root.ui.buttonDeleteOrder,
                qta.icon('mdi6.delete-outline', color="#EA2027"),
                root.delete_order
            ),
        ]

        for button, icon, callback in buttons_icons_callbacks:
            button.setIcon(icon)
            button.clicked.connect(callback)

        # Callback Functions
        root.ui.lineEditSearchProduct.textChanged.connect(root.search_products)
        root.ui.searchButtonIcon.clicked.connect(root.search_products)

        # Table Widgets
        root.ui.tableWidgetProduct.itemDoubleClicked.connect(lambda: root.product_details(lineEditEnabled=False))
        root.ui.tableWidgetProduct.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Products'))

        root.ui.tableWidgetOrders.itemDoubleClicked.connect(lambda: root.order_details(lineEditEnabled=False))
        root.ui.tableWidgetOrders.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Orders'))

        # # search button icon
        # root.ui.searchButtonIcon.setIcon(qta.icon('ri.search-line', color="#ffffff"))

        # # resume, suspend, terminate buttons
        # root.ui.buttonTerminate.setIcon(qta.icon('mdi6.skull', color="#ffffff"))

        # root.ui.buttonResume.setIcon(qta.icon('fa5s.walking', color="#ffffff"))

        # root.ui.buttonSuspend.setIcon(qta.icon('mdi.motion-pause-outline', color="#ffffff"))

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
    def display_table_records(table: QtWidgets.QTableWidget, rows: list, headers: list):
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
        root.ui.buttonOrderPage.setChecked(current_page == 1)

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
        line_edit.setFont(QtGui.QFont("Monaco", 12))
        # label.setStyleSheet(
            # "border: 1px solid rgb(64, 66, 72); border-top:none; border-left: none; border-right: none"
        # )
        return line_edit

    @staticmethod
    def create_spinBox(parent, name):
        """Create a styled QLabel."""
        line_edit = QtWidgets.QSpinBox(parent)

        line_edit.setObjectName(name)
        line_edit.setFont(QtGui.QFont("Monaco", 12))
        # label.setStyleSheet(
            # "border: 1px solid rgb(64, 66, 72); border-top:none; border-left: none; border-right: none"
        # )
        return line_edit

    @staticmethod
    def create_doubleSpinBox(parent, name):
        """Create a styled QLabel."""
        line_edit = QtWidgets.QDoubleSpinBox(parent)

        line_edit.setObjectName(name)
        line_edit.setFont(QtGui.QFont("Monaco", 12))
        # label.setStyleSheet(
            # "border: 1px solid rgb(64, 66, 72); border-top:none; border-left: none; border-right: none"
        # )
        return line_edit

    @staticmethod
    def clear_details_form(form_layout):
        """Clear all widgets from a QFormLayout."""
        while form_layout.count():
            item = form_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
