from datetime import datetime, date
from PyQt5 import QtWidgets, QtGui, QtCore
import qtawesome as qta

MENU_BUTTON_COLOR = "#ffffff"
BUTTON_PLUS_COLOR = "#1abc9c"
BUTTON_EDIT_COLOR = "#7ed6df"
BUTTON_DELETE_COLOR = "#e74c3c"
BUTTON_CHECK_COLOR = "#ffbe76"


class Utils:
    """
    Utility class for PyQt5 operations such as handling QTableWidget and QComboBox.
    """

    success_stylesheet = "color: #1abc9c;"
    error_stylesheet = "color: #e74c3c;"

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
            (
                root.ui.buttonStatisticsPage,
                qta.icon('mdi6.chart-bar-stacked', color=MENU_BUTTON_COLOR),
                lambda: root.goto_page(page="Statistics")
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
                qta.icon('mdi6.information-variant', color=MENU_BUTTON_COLOR),
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
                qta.icon('mdi6.check', color=BUTTON_CHECK_COLOR),
                lambda: root.activate_item(coll_name='Products')
            ),

            # THE SAVE BUTTON
            (
                root.ui.buttonSave,
                qta.icon('mdi.content-save', color=BUTTON_EDIT_COLOR),
                root.save_new_item
            ),

            # ------------------------------------------------------------------------
            # CUSTOMERS PAGE
            (   # Customer Details
                root.ui.buttonCustomerDetails,
                qta.icon('mdi.account-question', color=MENU_BUTTON_COLOR),
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
                qta.icon('mdi6.check', color=BUTTON_CHECK_COLOR),
                lambda: root.activate_item(coll_name='Customers')
            ),
            (   # Orders Customer
                root.ui.buttonCustomerOrders,
                qta.icon('mdi6.badge-account-horizontal', color=MENU_BUTTON_COLOR),
                root.customer_orders
            ),

            # ------------------------------------------------------------------------
            # ORDERS PAGE
            (   # Order Details
                root.ui.buttonOrderDetails,
                qta.icon('mdi6.information-variant', color=MENU_BUTTON_COLOR),
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
                qta.icon('ph.plus', color=BUTTON_PLUS_COLOR),
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

        # Callback Functions [ LineEditSearch and his Button ]
        root.ui.lineEditSearchProduct.textChanged.connect(root.search_products)
        root.ui.searchButtonIcon.clicked.connect(root.search_products)

        root.ui.lineEditSearchCustomer.textChanged.connect(root.search_customers)   # Customers

        root.ui.lineEditSearchOrder.textChanged.connect(root.search_orders)   # Orders

        # => Product TableWidget
        root.ui.tableWidgetProduct.itemDoubleClicked.connect(lambda: root.item_details(lineEditEnabled=False))
        root.ui.tableWidgetProduct.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Products'))

        # => Customer TableWidget
        root.ui.tableWidgetCustomer.itemDoubleClicked.connect(
            lambda: root.item_details(lineEditEnabled=False, coll_name="Customers")
        )
        root.ui.tableWidgetCustomer.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Customers'))

        # => Order TableWidget
        root.ui.tableWidgetOrders.itemDoubleClicked.connect(lambda: root.order_details(lineEditEnabled=False))
        root.ui.tableWidgetOrders.itemSelectionChanged.connect(lambda: root.enable_disable_buttons('Orders'))

        # # search button icon
        # root.ui.searchButtonIcon.setIcon(qta.icon('ri.search-line', color="#ffffff"))

        # # resume, suspend, terminate buttons
        # root.ui.buttonTerminate.setIcon(qta.icon('mdi6.skull', color="#ffffff"))

    def create_menu(root, button: QtWidgets.QPushButton, icon_name: str, actions: list, is_action_with_icon=False):
        """
        Helper function to create a dynamic menu for a QPushButton.

        :param root: The parent widget (usually the main window).
        :param button: The QPushButton to which the menu will be attached.
        :param icon_name: The icon name for the button (e.g., 'mdi.list-status').
        :param actions: A list of tuples where each tuple contains:
                        - A dictionary mapping data to the visible label (e.g., {"pending": "قيد الانتظار"}).
                        - The callback function (callable).
                        - Optional: The icon (if is_action_with_icon is True).
        :param is_action_with_icon: Whether the actions include icons.

        :example usage:
            order_actions = [
                ({"pending": "قيد الانتظار"}, self.change_order_status, qta.icon('mdi6.clock-time-seven', color="#ffffff")),
                ({"confirmed": "مؤكد"}, self.change_order_status, qta.icon('mdi6.check-circle-outline', color="#ffffff")),
            ]
            Utils.create_menu(
                root=self,
                button=self.ui.buttonOrderStatus,
                icon_name='mdi.list-status',
                actions=order_actions,
                is_action_with_icon=True
            )
        """
        # Set the icon for the button
        button.setIcon(qta.icon(icon_name, color='#ffffff'))

        # Create the menu
        menu = QtWidgets.QMenu(root)

        for action in actions:
            action_name, callback = action[:2]  # Get the action dictionary and callback function
            action_icon = action[2] if is_action_with_icon else None  # Get the icon if applicable

            # Add menu items based on the action dictionary
            for data, label in action_name.items():
                menu_action = menu.addAction(label)
                menu_action.setData(data)  # Store the data (e.g., "pending")
                if action_icon:
                    menu_action.setIcon(action_icon)

                # Connect the menu action to the callback
                menu_action.triggered.connect(lambda _, d=data, cb=callback: cb(d))

        # Attach the menu to the button
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

        table.horizontalHeader().setStretchLastSection(True)
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
        root.ui.buttonCustomerPage.setChecked(current_page == 1)
        root.ui.buttonOrderPage.setChecked(current_page == 2)
        root.ui.buttonStatisticsPage.setChecked(current_page == 3)

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
    def create_qtablewidget(column_count: int, headers: list):
        """
        Create a QTableWidget and set all options
        """
        table_widget = QtWidgets.QTableWidget()
        table_widget.setColumnCount(column_count)   # Columns Like: product_id, name, quantity, total
        table_widget.setHorizontalHeaderLabels(headers)
        # Adjust table settings
        table_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table_widget.resizeColumnsToContents()
        table_widget.verticalHeader().setVisible(False)
        table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # Make the table read-only
        table_widget.horizontalHeader().setStretchLastSection(True)
        return table_widget

    @staticmethod
    def create_comboBox(parent, object_name, values):
        """
        Dynamically creates a QComboBox and populates it with the given values.

        :param parent: The parent widget for the QComboBox.
        :param object_name: The object name to set for the QComboBox.
        :param values: A list of values to populate in the comboBox.
        :return: The created QComboBox instance.
        """
        # Create the QComboBox
        combo_box = QtWidgets.QComboBox(parent)
        combo_box.setObjectName(object_name)
        # Add the values to the comboBox
        combo_box.addItems(values)
        return combo_box

    @staticmethod
    def clear_details_form(form_layout):
        """Clear all widgets from a QFormLayout."""
        while form_layout.count():
            item = form_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    @staticmethod
    def datetime_fields(self, value):
        """
        Transform datetime fields
        """
        try:
            # If the value is a string that looks like a datetime, convert it
            if isinstance(value, str):
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
            elif isinstance(value, date):
                value = datetime.combine(value, datetime.min.time())
            value = value.strftime("%Y-%m-%d")  # Format the datetime in '%d-%m-%Y' format
        except ValueError:
            value = "تاريخ غير صالح"

        return value
