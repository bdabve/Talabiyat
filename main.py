#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from bson.objectid import ObjectId
import qtawesome as qta

from h_interface import Ui_MainWindow
from utils import Utils
from mongo_handler import MongoDBHandler
from logger import logger


class Interface(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setup the mongo client
        try:
            self.db_handler = MongoDBHandler()
        except Exception as err:
            logger.error(err)
            exit()

        # TABLE WIDGETS SETTINGS
        self.prod_headers = ["أيد", "الاسم", "المرجع", "الوصف", "السعر", "الكمية", "الفئة"]
        self.order_headers = ["أيد", "المشتري", "التاريخ", "الوضعية", "المجموع"]
        # column size
        Utils.table_column_size(self.ui.tableWidgetProduct, [(0, 0), (1, 180), (2, 100), (3, 450), (4, 90), (5, 80)])

        # CallbackFunctions and Icons
        Utils.interface_icons_callbacks(self)

        # Remove QDockWidget Title bar
        empty_title_bar = QtWidgets.QWidget()
        self.ui.dockWidget.setTitleBarWidget(empty_title_bar)
        self.ui.dockWidget.close()

        # initial functions
        self.goto_product_page()
        self.showMaximized()

    # ********** Global Functions *************#

    def goto_product_page(self):
        self.all_products()
        self.enable_disable_buttons(page='Products')
        self.ui.containerStackedWidget.setCurrentWidget(self.ui.ProductPage)
        Utils.pagebuttons_stats(self)

    def goto_order_page(self):
        self.all_orders()
        self.enable_disable_buttons(page='Orders')
        self.ui.containerStackedWidget.setCurrentWidget(self.ui.OrderPage)
        Utils.pagebuttons_stats(self)

    def update_count_label(self, label, rows):
        """
        Update the process count label.
        :label: self.ui.labelCount :: the label to display count in
        :rows: the rows to count with len(rows)
        """
        label.setText(f"المجموع ({len(rows)})")

    def populate_table_widget(self, table_name, rows):
        """
        Display processes in the process table widget.
        :table_name: Products | Orders
        :rows: rows to diaplay in table
        """
        if table_name == 'Products':
            table_widget = self.ui.tableWidgetProduct
            headers = self.prod_headers
            count_label = self.ui.labelProductTableCount

        elif table_name == 'Orders':
            table_widget = self.ui.tableWidgetOrders
            headers = self.order_headers
            count_label = self.ui.labelOrderTableCount

        Utils.display_table_records(table_widget, rows, headers)
        self.update_count_label(count_label, rows)
        Utils.pagebuttons_stats(self)

    def enable_disable_buttons(self, page: str):
        """
        This function Enable/Disable details/update/delete button if tableWidget has at least one selected rows
        :page: [ Products | Orders | Customers ]
        """
        if page == 'Products':
            buttons = [
                self.ui.buttonProductDetails,
                self.ui.buttonEditProduct,
                self.ui.buttonDeleteProduct,
            ]
            table_widget = self.ui.tableWidgetProduct
        elif page == 'Orders':
            buttons = [
                self.ui.buttonOrderDetails,
                self.ui.buttonEditOrder,
                self.ui.buttonDeleteOrder
            ]
            table_widget = self.ui.tableWidgetOrders

        for button in buttons:
            button.setEnabled(Utils.selected_rows(table_widget))

        # elif page == 'clients':
            # self.root.ui.buttonDelete.setEnabled(Utils.selected_rows(self.client_tablew))
            # self.root.ui.buttonDeleteClient.setEnabled(Utils.selected_rows(self.client_tablew))

    # ************************************************
    # Form Management
    # ************************************************

    def create_form(self, fields):
        """
        Dynamically create a form for new entries.
        :param fields: A dictionary mapping keys to Arabic labels.
        """
        Utils.clear_details_form(self.ui.formLayout)
        for count, (key, label) in enumerate(fields.items(), start=1):
            value_edit = Utils.create_lineEdit(self.ui.scrollAreaWidgetContents, f"lineEdit_{key}")
            value_edit.setText("")
            value_edit.setEnabled(True)

            key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
            key_label.setText(label)

            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.FieldRole, value_edit)
            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.allDetailsPage)
        self.ui.dockWidget.show()

    def add_product_to_table(self, table_widget):
        """
        Add a new product entry to the product table using a QComboBox.
        this function open a new QDialog to take (prod_id, qte)

        :param table_widget: The QTableWidget to add the product to.
        """
        # Fetch all products to populate the combo box
        response = self.db_handler.fetch_products(
            projection={"_id": 1, "name": 1},
            sort=[("name", 1)]
        )

        if response["status"] != "success" or not response["documents"]:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد منتجات لإضافتها.")
            return

        # Create a QDialog for selecting the product and quantity
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة منتج")
        dialog.setStyleSheet(Utils.dialog_styleSheet)
        layout = QtWidgets.QVBoxLayout(dialog)

        # Create and populate the QComboBox with product names
        combo_box = QtWidgets.QComboBox()
        product_map = {}  # Map product names to ObjectIds
        for product in response["documents"]:
            product_name = product.get("name", "غير معروف")
            product_id = str(product["_id"])
            product_map[product_name] = product_id
            combo_box.addItem(product_name)
        layout.addWidget(QtWidgets.QLabel("اختر منتجاً:"))
        layout.addWidget(combo_box)

        # Create a spin box for quantity
        quantity_spinbox = QtWidgets.QSpinBox()
        quantity_spinbox.setRange(1, 1000)
        layout.addWidget(QtWidgets.QLabel("الكمية:"))
        layout.addWidget(quantity_spinbox)

        # Add OK and Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Execute the dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            logger.debug('Adding product to cart from the QDialog')
            # Get the selected product and quantity
            selected_product_name = combo_box.currentText()
            product_id = product_map[selected_product_name]
            quantity = quantity_spinbox.value()

            # Add the selected product to the table
            table_widget.setColumnCount(4)  # Columns: Product ID, Name, Quantity, Actions
            table_widget.setHorizontalHeaderLabels(["رقم المنتج", "اسم المنتج", "الكمية", "إزالة"])
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            table_widget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(product_id))
            table_widget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(selected_product_name))
            table_widget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(quantity)))

            # Add a remove button
            remove_button = QtWidgets.QPushButton(" إزالة")
            remove_button.setIcon(qta.icon('fa.trash', color="#EA2027"))
            remove_button.setIconSize(QtCore.QSize(20, 20))
            remove_button.clicked.connect(lambda: table_widget.removeRow(row_position))

            table_widget.setCellWidget(row_position, 3, remove_button)

    def collect_form_data(self, formLayout):
        """
        Collect data from formFrame QLineEdit fields and product table.
        :formLayout: the layout to collect data from ( self.ui.formLayout | self.ui.formLayoutNewOrder )
        :return: A dictionary containing the input data.
        """
        input_data = {}
        for i in range(formLayout.rowCount()):
            label_item = formLayout.itemAt(i, QtWidgets.QFormLayout.LabelRole)
            input_item = formLayout.itemAt(i, QtWidgets.QFormLayout.FieldRole)

            if label_item and input_item:
                label_widget = label_item.widget()
                input_widget = input_item.widget()

                # Handle QLineEdit inputs
                if isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QLineEdit):
                    key = input_widget.objectName().replace("lineEdit_", "")
                    value = input_widget.text().strip()
                    input_data[key] = value

                # Handle QComboBox inputs for NewOrders
                if isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QComboBox):
                    key = input_widget.objectName().replace("comboBoxAddOrder", "").lower()
                    if key == 'customer_id':
                        value = self.customers_map.get(input_widget.currentText().strip(), '')
                    elif key == 'status':
                        value = self.order_status_mapping.get(input_widget.currentText().strip(), 'None')
                    else:
                        value = input_widget.currentText().strip()
                    input_data[key] = value

                # Handle QTableWidget for products
                elif isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QTableWidget):
                    products = []
                    for row in range(input_widget.rowCount()):
                        product_id = input_widget.item(row, 0).text()
                        quantity = int(input_widget.item(row, 2).text())
                        products.append({"product_id": product_id, "quantity": quantity})
                    input_data["products"] = products

        return input_data

    # ************************************************
    #   PRODUCT PAGE
    # *************************

    def display_product_data(self, response):
        """
        Display the table data in tableWidget
        This function work with both all_products and search_product
        """
        if response["status"] == "success":
            # Format rows for the table
            rows = [
                [
                    product.get("_id", ""),
                    product.get("name", ""),
                    product.get("ref", ""),
                    product.get("description", ""),
                    product.get("price", ""),
                    product.get("qte", ""),
                    product.get("category", "")
                ]
                for product in response['documents']
            ]

            # Display records in the table
            self.populate_table_widget('Products', rows)
        else:
            self.ui.labelErrorProductPage.setText(f"Error fetching products: {response['message']}")

    def all_products(self):
        """
        Fetches all products from the database and displays them in the table widget.
        """
        # Fetch all products
        response = self.db_handler.fetch_products(
            projection={"_id": 1, "name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "category": 1},
            sort=[("created_at", 1)]  # Sort by create time
        )
        self.display_product_data(response)

    def search_products(self):
        """
        Searches for products in the database and updates the table display.
        """
        # Get the search text
        search_text = self.ui.lineEditSearchProduct.text().strip()

        # Build the query
        query = {"$or": [
            {"name": {"$regex": search_text, "$options": "i"}},      # Search in name
            {"ref": {"$regex": search_text, "$options": "i"}},       # Search in reference
            {"description": {"$regex": search_text, "$options": "i"}},  # Search in description
            {"category": {"$regex": search_text, "$options": "i"}},  # Search in category
        ]} if search_text else {}

        # Fetch matching products
        response = self.db_handler.fetch_products(query=query, projection={
            "name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "category": 1, "_id": 1
        })
        self.display_product_data(response)

    def new_product(self):
        """
        Add new product
        """
        fields = {
            "name": "الاسم",
            "ref": "المرجع",
            "description": "الوصف",
            "price": "السعر",
            "qte": "الكمية",
            "category": "الفئة",
            "supplier": "المورد"
        }
        # init config files
        self.ui.labelTitleDetails.setText('سلعة جديدة')
        self.ui.labelMongoTable.setText('Product')
        self.ui.labelOperation.setText('Create')
        self.ui.frameDetailsID.hide()

        # create the form
        self.create_form(fields)

    def save_new_item(self):
        """
        Save new ( Product | Order | Customer ) in database
        when saveNewProduct is clicked
        """
        operation = self.ui.labelOperation.text()
        mongo_table = self.ui.labelMongoTable.text()

        if operation == 'None':
            logger.debug('Returning from save do Nothing.')
            return

        # ------------# Products ------------#
        if mongo_table == 'Product':
            logger.debug(f'SAVE BUTTON: Product( {operation} )')

            data = self.collect_form_data(self.ui.formLayout)
            logger.debug(data)
            if operation == 'Create':
                # CREATE PRODUCT
                response = self.db_handler.create_product(**data)
                if response['status'] == 'success':
                    logger.info("New product added successfully!")
                    self.all_products()
                else:
                    logger.error(f"Failed to add product.\n{response['message']}")
                    self.ui.labelErrorProductPage.setText(f"{response['massage']}")
            elif operation == 'Edit':
                # Edit Product
                product_id = self.ui.labelItemID.text()
                logger.debug(f"Save Edit Product ({product_id})")

        # ------------# Customers #------------#
        elif mongo_table == 'Customer':
            logger.info(f'Customer( {operation} )')
            print(data)

        # ------------# ORDERS #------------ #
        elif mongo_table == 'Order':
            if operation == 'Create':
                # Create New Order
                data = self.collect_form_data(self.ui.formLayoutNewOrder)
                logger.debug(f'Save New Order with DATA: \n{data}')
            elif operation == 'Edit':
                # Edit Order
                # order_id = self.ui.labelItemID.text()
                # logger.debug(f'Edit Order ({order_id}) with DATA: \n{data}')
                pass
        else:
            logger.info('Nothing')

    # *******************************************
    # Product Details Widget
    # *******************************************
    def populate_formFrame(self, response, lineEditEnabled=False):
        """
        Populate the formFrame located in the details dockWidget
        and open the dockWidget work with

        :param response: dict The response from MongoDB (e.g., response['product']).
        :param lineEditEnabled: If details; enabled=False; else True.
        """
        # Clear the existing form
        Utils.clear_details_form(self.ui.formLayout)

        # Mapping of column names from English to Arabic
        arabic_mapping = {
            "name": "الاسم",
            "ref": "المرجع",
            "description": "الوصف",
            "price": "السعر",
            "qte": "الكمية",
            "category": "الفئة",
            "supplier": "المورد",
            "created_at": "تاريخ الإضافة",
            "updated_at": "تاريخ التحديث",
            "is_active": "الحالة",
            "status": "الحالة",
            "order_date": "التاريخ",
            "total_price": "المجموع",
            "products": "السلعة",
            "customer_id": "المشتري",
        }

        # Populate the form with translated keys
        for count, (key, value) in enumerate(response.items(), start=1):
            # If the key is a date field, transform its format
            if key in ["created_at", "updated_at"] and isinstance(value, str):
                try:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y - %m - %d")
                except ValueError:
                    value = "تاريخ غير صالح"
            if key == "products":
                # Create a QTableWidget for product details
                product_table = self.create_product_table(value)
                self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.FieldRole, product_table)

                key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
                key_label.setText(arabic_mapping.get(key, key))
                self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)
                continue

            # Create a line edit for the value
            value_edit = Utils.create_lineEdit(self.ui.scrollAreaWidgetContents, f"lineEdit_{key}")
            value_edit.setText(str(value))
            value_edit.setEnabled(lineEditEnabled)

            # Translate the key to Arabic using the mapping
            translated_key = arabic_mapping.get(key, key)  # Default to key if no translation exists

            # Create a label for the key
            key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
            key_label.setText(translated_key)

            # Add the widgets to the form layout
            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.FieldRole, value_edit)
            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.allDetailsPage)
        self.ui.dockWidget.show()

    def create_product_table(self, products):
        """
        Order Details TableWidget
        Create a QTableWidget to display products for a specific order.

        :param products: List of product dictionaries (e.g., [{"product_id": "...", "quantity": 2}, ...]).
        :return: QTableWidget instance populated with product data.
        """
        table_widget = QtWidgets.QTableWidget()
        table_widget.setColumnCount(5)  # Columns: product_id, name, quantity, total
        table_widget.setHorizontalHeaderLabels(["رقم المنتج", "اسم المنتج", "الكمية", "السعر", "المجموع"])
        table_widget.setRowCount(len(products))

        # Populate the table with product data
        for row, product in enumerate(products):
            product_id = product.get("product_id", "")
            quantity = product.get("quantity", 0)
            product_name = "غير معروف"
            total = 0

            # Fetch product name and price from the database
            product_response = self.db_handler.fetch_documents(
                collection_name="Products",
                query={"_id": ObjectId(product_id)},
                projection={"name": 1, "price": 1}
            )

            if product_response["status"] == "success" and product_response["documents"]:
                product_data = product_response["documents"][0]
                product_name = product_data.get("name", "غير معروف")
                price = product_data.get("price", 0)
                total = price * quantity

            # Fill the row with product data
            table_widget.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{product_id}"))
            table_widget.setItem(row, 1, QtWidgets.QTableWidgetItem(product_name))
            table_widget.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{quantity}"))
            table_widget.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price}"))
            table_widget.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

        # Adjust table settings
        table_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table_widget.resizeColumnsToContents()
        table_widget.verticalHeader().setVisible(False)
        table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # Make the table read-only
        table_widget.horizontalHeader().setStretchLastSection(True)
        return table_widget

    def product_details(self, lineEditEnabled, operation='None'):
        """
        Show details for a selected process.
        :lineEditEnabled: if enable line edits to update product
        :operation: the operation ( Create | Edit | None )
        """
        product_id = Utils.get_column_value(self.ui.tableWidgetProduct, 0)

        # Config Labels
        self.ui.labelOperation.setText(operation)
        self.ui.labelItemID.setText(str(product_id))
        self.ui.labelMongoTable.setText('Product')
        self.ui.frameDetailsID.hide()

        if operation == 'Edit':
            projection = {"_id": 0, "created_at": 0, "updated_at": 0}
        else:
            projection = {"_id": 0}

        response = self.db_handler.fetch_documents(
            collection_name="Products",
            query={"_id": ObjectId(product_id)},
            projection=projection,
        )
        if response["status"] == "error":
            self.ui.labelErrorProductPage.setText(response["message"])
            return

        response = response["documents"][0]

        self.populate_formFrame(response, lineEditEnabled=lineEditEnabled)

    def edit_product(self):
        """
        Edit Product
        """
        item_id = Utils.get_column_value()
        mongo_table = self.ui.labelMongoTable.text()
        print(f"Edit :: {item_id} :: {mongo_table}")

    def delete_product(self):
        """
        Delete Product
        """
        item_id = Utils.get_column_value(self.ui.tableWidgetProduct, 0)
        response = self.db_handler.delete_document('Products', ObjectId(item_id))
        if response['status'] == 'success':
            self.goto_product_page()
            logger.info(f"Delete Products :: {response['message']}")
            self.ui.labelErrorProductPage.setText(response['message'])
        else:
            self.ui.labelErrorProductPage.setText(f"Error {response['message']}")

    # ********************************************
    # == ORDERS PAGE
    # ********************************************
    def all_orders(self):
        """
        Fetches all Orders from the database and displays them in the table widget.
        """
        # Fetch all products
        response = self.db_handler.fetch_orders_with_customer_names(
            projection={"_id": 1, "customer_id": 1, "order_date": 1, "status": 1, "total_price": 1, "customer_name": 1},
            sort=[("created_at", 1)]  # Sort by create time
        )

        if response["status"] == "success":
            # Format rows for the table
            rows = [
                [
                    order.get("_id", ""),
                    'غير مسجل' if order.get("customer_name") is None else order.get("customer_name", "Unknown"),
                    order.get("order_date", "").strftime('%Y - %m - %d'),
                    order.get("status", ""),
                    order.get("total_price", ""),
                ]
                for order in response["orders"]
            ]

            # Display records in the table
            self.populate_table_widget('Orders', rows)
        else:
            self.ui.labelErrorOrderPage.setText(f"Error fetching orders: {response['message']}")

    def order_details(self, lineEditEnabled, operation='None'):
        """
        Show details for a selected Order.
        :lineEditEnabled: if enable line edits to update product
        :operation: the operation ( Create | Edit | None )
        """
        order_id = Utils.get_column_value(self.ui.tableWidgetOrders, 0)

        # Config Labels
        self.ui.labelOperation.setText(operation)
        self.ui.labelItemID.setText(str(order_id))
        self.ui.labelMongoTable.setText('Order')
        self.ui.frameDetailsID.hide()

        if operation == 'Edit':
            projection = {"_id": 0, "created_at": 0, "updated_at": 0}
        else:
            projection = {"_id": 0}

        response = self.db_handler.fetch_documents(
            collection_name="Orders",
            query={"_id": ObjectId(order_id)},
            projection=projection,
        )
        if response["status"] == "error":
            self.ui.labelErrorOrderPage.setText(response["message"])
            return

        response = response["documents"][0]
        self.populate_formFrame(response, lineEditEnabled=lineEditEnabled)

    def new_order(self):
        """
        Create New Order
        Prepare the new order form and go to stackedWidgetNewOrder
        """
        self.ui.labelTitleDetails.setText('طلبية جديدة')
        self.ui.labelMongoTable.setText('Order')
        self.ui.labelOperation.setText('Create')
        self.ui.frameDetailsID.hide()

        # Display the form
        self.new_order_form()

    def new_order_form(self):
        """
        customers: response['documents']
        """
        # Fetch all products to populate the combo box
        response = self.db_handler.fetch_customers(
            projection={"_id": 1, "first_name": 1, "last_name": 1},
            sort=[("name", 1)]
        )
        if response['status'] == 'error':
            logger.debug(response['message'])
            return

        # Combobox Order Customers
        self.customers_map = {}  # Map orders names to ObjectIds
        for customer in response['documents']:
            cust_name = f"{customer.get('first_name', '')} {customer.get('last_name')}"
            cust_id = str(customer["_id"])
            self.customers_map[cust_name] = cust_id
            self.ui.comboBoxAddOrderCustomer_id.addItem(cust_name)

        # Combobox Order Status
        self.order_status_mapping = {
            "قيد الانتظار": "pending",
            "مؤكد": "confirmed",
            "قيد التحضير": "preparing",
            "تم الشحن": "shipped",
            "في الطريق للتوصيل": "out_for_delivery",
            "تم التوصيل": "delivered",
            "منجز": "completed",
            "ملغي": "cancelled",
            "فشل": "failed"
        }
        self.ui.comboBoxAddOrderStatus.clear()
        for status in self.order_status_mapping.keys():
            self.ui.comboBoxAddOrderStatus.addItem(status)

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.createOrderPage)
        self.ui.dockWidget.show()

    def delete_order(self):
        """
        Delete Order
        """
        item_id = Utils.get_column_value(self.ui.tableWidgetOrders, 0)
        response = self.db_handler.delete_document('Orders', item_id)
        if response['status'] == 'success':
            self.ui.labelErrorOrderPage.setText(response['message'])
            self.ui.labelErrorOrderPage.setStyleSheet(Utils.success_stylesheet)
        else:
            self.ui.labelErrorOrderPage.setText(response['message'])
            self.ui.labelErrorOrderPage.setStyleSheet(Utils.error_stylesheet)

        self.ui.dockWidget.close()
        self.goto_order_page()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = Interface()
    dialog.show()
    sys.exit(app.exec_())
