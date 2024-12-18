#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
from datetime import datetime, date
from PyQt5 import QtWidgets, QtCore
from bson.objectid import ObjectId
import qtawesome as qta
from decimal import Decimal

from h_interface import Ui_MainWindow
from utils import Utils
from mongo_handler import MongoDBHandler
from logger import logger
import arabic_dict as arabic


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
        # column size
        Utils.table_column_size(self.ui.tableWidgetProduct, [(0, 0), (1, 180), (2, 100), (3, 450), (4, 90), (5, 80)])

        # CallbackFunctions and Icons
        Utils.interface_icons_callbacks(self)

        # Remove QDockWidget Title bar
        empty_title_bar = QtWidgets.QWidget()
        self.ui.dockWidget.setTitleBarWidget(empty_title_bar)
        self.ui.dockWidget.close()

        # initial functions
        self.goto_page(page='Products')
        self.showMaximized()

    # ********** Global Functions *************#
    def goto_page(self, page: str):
        """
        Navigate to the specified page and update UI elements accordingly.
        :param page: Page to navigate to (Products | Customers | Orders).
        """
        if page == 'Products':
            # Display all products
            self.fetch_and_display_data(
                collection_name='Products',
                headers=["_id", "name", "ref", "description", "price", "qte", "category"],
            )
            self.enable_disable_buttons(page='Products')
            self.ui.labelErrorProductPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.ProductPage)

        elif page == 'Customers':
            # Display all customers
            self.fetch_and_display_data(
                collection_name='Customers',
                headers=["_id", "first_name", "last_name", "phone", "email", "address", "is_active"]
            )
            self.enable_disable_buttons(page='Customers')
            self.ui.labelErrorCustomerPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.CustomerPage)

        elif page == 'Orders':
            self.all_orders()
            self.enable_disable_buttons(page='Orders')
            self.ui.labelErrorOrderPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.OrderPage)

        Utils.pagebuttons_stats(self)

    def update_count_label(self, label, rows):
        """
        Update the count len(rows) label.
        :label: self.ui.labelCount :: the label to display count in
        :rows: the rows to count with len(rows)
        """
        label.setText(f"المجموع ({len(rows)})")

    def populate_table_widget(self, table_name, rows):
        """
        Display rows in tableWidget_name and update the count label.
        :table_name: Products | Orders
        :rows: rows to diaplay in table
        """
        if table_name == 'Products':
            table_widget = self.ui.tableWidgetProduct
            headers = arabic.prod_headers
            count_label = self.ui.labelProductTableCount

        elif table_name == 'Orders':
            table_widget = self.ui.tableWidgetOrders
            headers = arabic.order_headers
            count_label = self.ui.labelOrderTableCount

        elif table_name == 'Customers':
            table_widget = self.ui.tableWidgetCustomer
            headers = arabic.customer_headers
            count_label = self.ui.labelCustomerTableCount

        Utils.populate_table_widget(table_widget, rows, headers)
        self.update_count_label(count_label, rows)
        Utils.pagebuttons_stats(self)

    def fetch_and_display_data(self, collection_name: str, headers: list, query=None, projection=None, sort=None):
        """
        Generic function to fetch and display data in a table widget.
        :param collection_name: MongoDB collection name.
        :param headers: List of headers to display in the table widget.
        :param query: MongoDB query filter.
        :param projection: Fields to include or exclude in results.
        :param sort: Sort order.
        """
        response = self.db_handler.fetch_documents(
            collection_name=collection_name,
            query=query or {},
            projection=projection,
            sort=sort or [("created_at", 1)]
        )

        if response["status"] == "success":
            rows = [
                [doc.get(field, "") for field in headers] for doc in response["documents"]
            ]
            self.populate_table_widget(collection_name, rows)
        else:
            logger.error(f"Error fetching data from {collection_name}: {response['message']}")
            Utils.success_message(self.ui.labelErrorProductPage, response['message'], success=False)

    #
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
        elif page == "Customers":
            buttons = [
                self.ui.buttonCustomerDetails,
                self.ui.buttonEditCustomer,
                self.ui.buttonDeleteCustomer,
            ]
            table_widget = self.ui.tableWidgetCustomer
        elif page == 'Orders':
            buttons = [
                self.ui.buttonOrderDetails,
                self.ui.buttonDeleteOrder
            ]
            table_widget = self.ui.tableWidgetOrders

        for button in buttons:
            button.setEnabled(Utils.selected_rows(table_widget))

        # elif page == 'clients':
            # self.root.ui.buttonDelete.setEnabled(Utils.selected_rows(self.client_tablew))
            # self.root.ui.buttonDeleteClient.setEnabled(Utils.selected_rows(self.client_tablew))

    def item_details(self, lineEditEnabled, operation='None', coll_name="Products", item_id=None):
        """
        Show details for a selected Product.
        :lineEditEnabled: if enable line edits to update product
        :operation: the operation ( Create | Edit | None ) None is for view
        :coll_name: the collection name (Products | Customers)
        :item_id: product_id | customer_id
        """
        if coll_name == 'Customers':
            table_widget = self.ui.tableWidgetCustomer
            label_message = self.ui.labelErrorCustomerPage
        elif coll_name == 'Products':
            table_widget = self.ui.tableWidgetProduct
            label_message = self.ui.labelErrorProductPage

        if not item_id:
            item_id = Utils.get_column_value(table_widget, 0)

        # Config Labels
        self.ui.labelOperation.setText(operation)
        self.ui.labelItemID.setText(str(item_id))
        self.ui.labelMongoTable.setText(coll_name)
        self.ui.frameDetailsID.hide()

        if operation in ['Edit', 'Create']:
            projection = {"_id": 0, "created_at": 0, "updated_at": 0}
            self.ui.frameToolButton_2.show()
        else:
            projection = {"_id": 0}
            self.ui.frameToolButton_2.hide()

        response = self.db_handler.fetch_documents(
            collection_name=coll_name,
            query={"_id": ObjectId(item_id)},
            projection=projection,
        )
        if response["status"] == "error":
            Utils.success_message(label_message, response['message'], False)
            return

        response = response["documents"][0]

        self.populate_formFrame(response, lineEditEnabled=lineEditEnabled)

    def delete_item(self, coll_name):
        """
        Delete Customer
        :coll_name: ( Products | Items | Orders )
        """
        # Delete Product
        if coll_name == 'Products':
            item_id = Utils.get_column_value(self.ui.tableWidgetProduct, 0)
            label = self.ui.labelErrorProductPage

        # Delete Customer
        elif coll_name == 'Customers':
            item_id = Utils.get_column_value(self.ui.tableWidgetCustomer, 0)
            label = self.ui.labelErrorCustomerPage

        # Delete Order
        elif coll_name == 'Orders':
            item_id = Utils.get_column_value(self.ui.tableWidgetOrders, 0)
            label = self.ui.labelErrorOrderPage

        # Delete item from database
        response = self.db_handler.delete_document(coll_name, ObjectId(item_id))
        if response['status'] == 'success':
            if coll_name == 'Products': self.goto_page(page="Products")
            elif coll_name == 'Orders': self.goto_page(page="Orders")
            elif coll_name == 'Customers': self.goto_page(page="Customers")

            Utils.success_message(label, 'تم الحذف بنجاح', success=True)
        else:
            Utils.success_message(label, 'هناك خطأ أعد من جديد', success=False)

    # ************************************************
    # Form Management
    # ************************************************

    def create_form(self, fields):
        """
        Dynamically create a form for new entries.
        :param fields: A dictionary mapping keys to Arabic labels.
        """
        Utils.clear_details_form(self.ui.formLayout)
        parent = self.ui.scrollAreaWidgetContents
        for count, (key, label) in enumerate(fields.items(), start=1):
            if key == 'qte':
                value_edit = Utils.create_spinBox(parent, f"lineEdit_{key}")
                value_edit.setValue(0)
                value_edit.setEnabled(True)
            elif key == 'price':
                value_edit = Utils.create_doubleSpinBox(parent, f"lineEdit_{key}")
                value_edit.setValue(0)
                value_edit.setEnabled(True)
            else:
                value_edit = Utils.create_lineEdit(parent, f"lineEdit_{key}")
                value_edit.setText("")
                value_edit.setEnabled(True)

            key_label = Utils.create_label(parent, f"label_{key}")
            key_label.setText(label)

            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.FieldRole, value_edit)
            self.ui.formLayout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.allDetailsPage)
        self.ui.frameToolButton_2.show()
        self.ui.dockWidget.show()

    def add_product_to_table(self, table_widget):
        """
        Add a new product entry to the product table of the cart (talabiya).
        this function open a new QDialog to take (prod_id, qte)

        :param table_widget: The QTableWidget to add the product to.
        """
        # Fetch all products to populate the combo box and the spin box
        response = self.db_handler.fetch_products(
            projection={"_id": 1, "name": 1, "qte": 1},
            sort=[("name", 1)]
        )

        if response["status"] != "success" or not response["documents"]:
            QtWidgets.QMessageBox.warning(self, "خطأ", "لا توجد منتجات لإضافتها.")
            return

        # Create a QDialog for selecting the product and quantity
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("إضافة منتج")

        # Set Style Sheet
        with open('./dialog_styleSheet.css') as f:
            style_sheet = f.read()
            dialog_styleSheet = style_sheet
            dialog.setStyleSheet(dialog_styleSheet)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Create and populate the QComboBox with product names
        combo_box = QtWidgets.QComboBox()
        product_map = {}  # Map product names to ObjectIds
        for product in response["documents"]:
            product_name = product.get("name", "غير معروف")
            product_id = str(product["_id"])
            product_qte = product.get("qte", 0)

            product_map[product_name] = {"id": product_id, "qte": product_qte}
            combo_box.addItem(product_name)

        layout.addWidget(QtWidgets.QLabel("اختر منتجاً:"))
        layout.addWidget(combo_box)

        # Update QSpinBox max value when a product is selected
        def update_spinbox_qte():
            """
            Update the spinBox to fit the maximum Qte in database
            This work with combo_box.currentIndexChanged
            """
            selected_product = combo_box.currentText()
            if selected_product in product_map:
                max_qte = product_map[selected_product]["qte"]
                quantity_spinbox.setMaximum(max_qte)  # Set the maximum to available stock
                quantity_spinbox.setValue(1)  # Reset to minimum value

        # Connect the combo box selection change to the spinbox update
        combo_box.currentIndexChanged.connect(update_spinbox_qte)

        # Create a spin box for quantity
        quantity_spinbox = Utils.create_spinBox()
        layout.addWidget(QtWidgets.QLabel("الكمية:"))
        layout.addWidget(quantity_spinbox)

        # Initialize the spinbox max value for the first time
        update_spinbox_qte()

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
            product_id = product_map[selected_product_name]["id"]
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

                # Handle QDateEdit inputs for new order date
                if isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QDateEdit):
                    key = input_widget.objectName().replace("dateEditAddOrder", "order_").lower()
                    value = input_widget.date().toPyDate()
                    value = datetime.combine(value, datetime.min.time())
                    input_data[key] = value

                # Handle QComboBox inputs for NewOrders
                if isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QComboBox):
                    key = input_widget.objectName().replace("comboBoxAddOrder", "").lower()
                    if key == 'customer_id':
                        value = self.customers_map.get(input_widget.currentText().strip(), '')
                    elif key == 'status':
                        value = arabic.order_status_mapping.get(input_widget.currentText().strip(), 'None')
                    else:
                        value = input_widget.currentText().strip()
                    input_data[key] = value

                # Handle QSpinBox, QDoubleSpinBox inputs for NewOrders
                if isinstance(label_widget, QtWidgets.QLabel) and (
                        isinstance(input_widget, QtWidgets.QSpinBox) or isinstance(input_widget, QtWidgets.QDoubleSpinBox)):
                    key = input_widget.objectName().replace("lineEdit_", "")
                    value = input_widget.value()
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
        data = self.collect_form_data(self.ui.formLayout)
        if mongo_table == 'Products':
            label = self.ui.labelErrorProductPage
            logger.info(f'Save Button: Saving Product( {operation} ) \n{data}')

            # CREATE PRODUCT
            if operation == 'Create':
                response = self.db_handler.create_product(**data)
                if response['status'] == 'success':
                    # Success
                    logger.info("New product added successfully!")

                    # re-display all the Products
                    self.fetch_and_display_data(
                        collection_name='Products',
                        headers=["_id", "name", "ref", "description", "price", "qte", "category"]
                    )

                    Utils.success_message(label, response['message'], success=False)
                else:
                    logger.error(f"Failed to add product.\n{response['message']}")
                    Utils.success_message(label, response['message'], success=False)

            # UPDATE PRODUCT
            elif operation == 'Edit':
                product_id = self.ui.labelItemID.text()
                response = self.db_handler.update_product(product_id, data)
                if response['status'] == 'success':
                    logger.debug(f"Update Product({product_id})\nMessage({response['message']})")

                    Utils.success_message(label, 'تم إضافة المنتج بنجاح', success=True)
                    self.item_details(lineEditEnabled=False, operation='None', item_id=product_id)
                    # re-display all Products
                    self.fetch_and_display_data(
                        collection_name='Products',
                        headers=["_id", "name", "ref", "description", "price", "qte", "category"]
                    )
                else:
                    logger.error(response['message'])
                    Utils.success_message(label, 'هنالك خطأ إعد من جديد', success=True)

        # ------------# Customers #------------#
        elif mongo_table == 'Customers':
            # => CREATE
            label = self.ui.labelErrorCustomerPage
            if operation == 'Create':
                logger.debug(f'Create New Customer( {operation} )\nData: {data}')
                response = self.db_handler.add_customer(**data)
                if response['status'] == 'success':
                    message = "تم إضافة المشتري بنجاح"
                    Utils.success_message(label, message, success=True)

                    # re-display all customers in tableWidget
                    self.fetch_and_display_data(
                        collection_name='Customers',
                        headers=["_id", "first_name", "last_name", "phone", "email", "address", "is_active"]
                    )
                else:
                    message = "هنالك خطأ إعد من جديد"
                    Utils.success_message(label, message, success=True)

            # Update Customer
            elif operation == 'Edit':
                customer_id = self.ui.labelItemID.text()
                logger.debug(f'Edit Customer( {customer_id} )\nData: {data}')
                response = self.db_handler.update_document('Customers', customer_id, data)

                if response['status'] == 'success':
                    Utils.success_message(label, 'تم إضافة المنتج بنجاح', success=True)
                    self.item_details(lineEditEnabled=False, coll_name='Customers', operation='None', item_id=customer_id)
                    # re-display the Customers in the tableWidget
                    self.fetch_and_display_data(
                        collection_name='Customers',
                        headers=["_id", "first_name", "last_name", "phone", "email", "address", "is_active"]
                    )
                else:
                    Utils.success_message(label, 'هنالك خطأ إعد من جديد', success=True)

        # ------------# ORDERS #------------ #
        elif mongo_table == 'Order':
            # Create New Order
            label = self.ui.labelErrorOrderPage
            if operation == 'Create':
                data = self.collect_form_data(self.ui.formLayoutNewOrder)
                logger.debug(f'Save New Order with DATA: \n{data}')

                response = self.db_handler.create_order(**data)
                if response['status'] == 'success':
                    Utils.success_message(label, 'تم بنجاح')
                    self.all_orders()
                else:
                    Utils.success_message(label, response['message'], success=False)

            # Update New Order
            elif operation == 'Edit':
                # TODO: No edit for Orders
                # Edit Order
                # order_id = self.ui.labelItemID.text()
                # logger.debug(f'Edit Order ({order_id}) with DATA: \n{data}')
                pass
        else:
            logger.info('Nothing')

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
            label = self.ui.labelErrorProductPage
            message = f"Error fetching products: {response['message']}"
            Utils.success_message(label, message, success=False)

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

    # *******************************************
    #       => Product Details Widget
    # *******************************************
    def populate_formFrame(self, response, lineEditEnabled=False):
        """
        Populate the formFrame located in the details dockWidget
        and open the dockWidget work with
            - product_details, edit_product
            - order_details
            - customer_details, edit_customer

        :param response: dict The response from MongoDB (e.g., response['product']).
        :param lineEditEnabled: If details; enabled=False; else True.
        """
        # Clear the existing form
        form_layout = self.ui.formLayout
        Utils.clear_details_form(form_layout)

        for count, (key, value) in enumerate(response.items(), start=1):
            print(key, '::> ', value)
            print('-' * 30)

            # If the key is a date field, transform its format
            date_fields = ["created_at", "updated_at", "order_date"]
            if key in date_fields and (isinstance(value, str) or isinstance(value, datetime)):
                try:
                    # If the value is a string that looks like a datetime, convert it
                    if isinstance(value, str):
                        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
                    elif isinstance(value, date):
                        value = datetime.combine(value, datetime.min.time())
                    value = value.strftime("%Y-%m-%d")  # Format the datetime in '%d-%m-%Y' format
                except ValueError:
                    value = "تاريخ غير صالح"

            # Create QTableWidget to display Products for a specific Order
            if key == "products":
                # Create a QTableWidget for product details
                product_table = self.create_product_table(value)
                form_layout.setWidget(count, QtWidgets.QFormLayout.FieldRole, product_table)

                key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
                key_label.setText(arabic.arabic_mapping.get(key, key))
                form_layout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)
                continue

            if key in ["status", "is_active"]:
                value_edit = Utils.create_lineEdit(self.ui.scrollAreaWidgetContents, f"lineEdit_{key}")
                value_edit.setText(arabic.order_status_mapping_en.get(value, value))
                value_edit.setEnabled(lineEditEnabled)
                form_layout.setWidget(count, QtWidgets.QFormLayout.FieldRole, value_edit)

                key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
                key_label.setText(arabic.arabic_mapping.get(key, key))
                form_layout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)
                continue

            # Create a line edit for the value
            value_edit = Utils.create_lineEdit(self.ui.scrollAreaWidgetContents, f"lineEdit_{key}")
            value_edit.setText(str(value))
            value_edit.setEnabled(lineEditEnabled)

            # Translate the key to Arabic using the mapping and create the Label
            translated_key = arabic.arabic_mapping.get(key, key)  # Default to key if no translation exists
            key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
            key_label.setText(translated_key)

            # Add the widgets to the form layout
            form_layout.setWidget(count, QtWidgets.QFormLayout.FieldRole, value_edit)
            form_layout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.allDetailsPage)
        self.ui.dockWidget.show()

    def create_product_table(self, products):
        """
        Order Details TableWidget for products
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
                price = Decimal(product_data.get("price", 0).to_decimal())
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

    # ********************************************
    #       => CUSTOMERS PAGE
    # ********************************************

    def new_customer(self):
        """
        Add new product
        """
        fields = {
            "first_name": "الاسم",
            "last_name": "اللقب",
            "phone": "رقم الهاتف",
            "email": "الإيمايل",
            "address": "العنوان",
        }
        # init config files
        self.ui.labelTitleDetails.setText('مشتري جديد')
        self.ui.labelMongoTable.setText('Customers')
        self.ui.labelOperation.setText('Create')
        self.ui.frameDetailsID.hide()

        # TODO:
        # validate phone number

        # create the form
        self.create_form(fields)

    # ********************************************
    # == ORDERS PAGE
    # ********************************************
    def all_orders(self):
        """
        Fetches all Orders from the database and displays them in the table widget.
        """
        # Fetch all products
        response = self.db_handler.fetch_orders_with_customer_names(
            projection={
                "_id": 1,
                "customer_id": 1,
                "order_date": 1,
                "status": 1,
                "total_price": 1,
                "customer_name": 1
            },
            sort=[("created_at", 1)]  # Sort by create time
        )

        if response["status"] == "success":
            # Format rows for the table
            rows = [
                [
                    order.get("_id", ""),
                    'غير مسجل' if order.get("customer_name") is None else order.get("customer_name", "Unknown"),
                    order.get("order_date", "").strftime('%Y - %m - %d'),
                    arabic.order_status_mapping_en.get(order.get("status", ""), ""),
                    order.get("total_price", ""),
                ]
                for order in response["orders"]
            ]

            # Display records in the table
            self.populate_table_widget('Orders', rows)
        else:
            logger.error(f"Error fetching orders: {response['message']}")
            Utils.success_message(self.ui.labelErrorOrderPage, response['message'], success=False)

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

        if operation in ['Edit', 'Create']:
            projection = {"_id": 0, "created_at": 0, "updated_at": 0}
            self.ui.frameToolButton_2.show()
        else:
            projection = {"_id": 0, "customer_id": 0}
            self.ui.frameToolButton_2.hide()

        response = self.db_handler.fetch_orders_with_customer_names(
            query={"_id": ObjectId(order_id)},
            projection=projection,
        )
        if response["status"] == "error":
            self.ui.labelErrorOrderPage.setText(response["message"])
            return

        response = response["orders"][0]
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
            cust_name = f"{customer.get('first_name', '')} {customer.get('last_name')}".strip()
            cust_id = str(customer["_id"])
            self.customers_map[cust_name] = cust_id
            self.ui.comboBoxAddOrderCustomer_id.addItem(cust_name)

        # Combobox Order Status
        self.ui.comboBoxAddOrderStatus.clear()
        for status in arabic.order_status_mapping.keys():
            self.ui.comboBoxAddOrderStatus.addItem(status)

        # Set DateEdit to now
        self.ui.dateEditAddOrderDate.setDate(datetime.now())

        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.createOrderPage)
        self.ui.frameToolButton_2.show()
        self.ui.dockWidget.show()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = Interface()
    dialog.show()
    sys.exit(app.exec_())
