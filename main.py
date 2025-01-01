#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
#
# ----------------------------------------------------------------------------
from datetime import datetime       # , date
from PyQt5 import QtWidgets, QtCore
from bson.objectid import ObjectId
import qtawesome as qta
from decimal import Decimal

from gui.h_interface import Ui_MainWindow
from gui.call_dialogs import AddProductToCart, ConfirmDialog

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
        self.product_projection = ["_id", "name", "ref", "description", "price", "qte", "category"]
        self.customer_projection = ["_id", "first_name", "last_name", "phone", "email", "address", "is_active", "client_status"]

        # column size
        Utils.table_column_size(self.ui.tableWidgetProduct, [(0, 0), (1, 180), (2, 100), (3, 450), (4, 90), (5, 80)])

        # CallbackFunctions and Icons
        Utils.interface_icons_callbacks(self)

        # Remove QDockWidget Title bar
        empty_title_bar = QtWidgets.QWidget()
        self.ui.dockWidget.setTitleBarWidget(empty_title_bar)
        self.ui.dockWidget.close()

        # MENU Define the order status actions
        order_actions = [
            ({"pending": "قيد الانتظار"}, self.change_order_status, qta.icon('mdi6.clock-time-seven', color="#ffffff")),
            ({"confirmed": "مؤكد"}, self.change_order_status, qta.icon('mdi6.check-circle-outline', color="#ffffff")),
            ({"shipped": "تم الشحن"}, self.change_order_status, qta.icon('mdi6.truck-outline', color="#ffffff")),
            ({"delivered": "تم التوصيل"}, self.change_order_status, qta.icon('mdi6.check-bold', color="#ffffff")),
            ({"cancelled": "ملغي"}, self.change_order_status, qta.icon('mdi6.close-circle-outline', color="#ffffff")),
        ]
        # create the menu
        Utils.create_menu(
            root=self,
            button=self.ui.buttonOrderStatus,
            icon_name='mdi.list-status',
            actions=order_actions,
            is_action_with_icon=True
        )

        # Define the customer status actions
        customer_status_actions = [
            ({"good_client": "عميل جيد"}, self.change_customer_status, qta.icon('mdi6.thumb-up', color="#4caf50")),
            ({"bad_client": "عميل سيئ"}, self.change_customer_status, qta.icon('mdi6.thumb-down', color="#f44336")),
            ({"trusted": "موثوق"}, self.change_customer_status, qta.icon('mdi6.star', color="#ffc107")),
        ]

        Utils.create_menu(
            root=self,
            button=self.ui.buttonCustomerTrust,
            icon_name='mdi.account-circle',
            actions=customer_status_actions,
            is_action_with_icon=True
        )

        # initial functions
        self.goto_page(page='Products')
        self.showMaximized()

    # **********************
    #   => Global Functions
    # ************************
    def goto_page(self, page: str):
        """
        Navigate to the specified page and update UI elements accordingly.
        :param page: Page to navigate to (Products | Customers | Orders).
        """
        if page == 'Products':
            # Display all products
            self.fetch_and_display_data(
                collection_name='Products',
                headers=self.product_projection,
            )
            self.enable_disable_buttons(page='Products')
            self.ui.labelErrorProductPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.ProductPage)

        elif page == 'Customers':
            # Display all customers
            self.fetch_and_display_data(
                collection_name='Customers',
                headers=self.customer_projection
            )
            self.enable_disable_buttons(page='Customers')
            self.ui.labelErrorCustomerPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.CustomerPage)

        elif page == 'Orders':
            self.all_orders()
            self.enable_disable_buttons(page='Orders')
            self.ui.labelErrorOrderPage.setText('')
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.OrderPage)

        elif page == 'Statistics':
            # self.enable_disable_buttons(page='Statistics')
            self.show_statistics()
            self.ui.dockWidget.close()
            self.ui.containerStackedWidget.setCurrentWidget(self.ui.StatisticsPage)

        Utils.pagebuttons_stats(self)

    def update_count_label(self, label, rows):
        """
        Update the count len(rows) label.
        :label: self.ui.labelCount :: the label to display count in
        :rows: the rows to count with len(rows)
        """
        label.setText(f"المجموع ({len(rows)})")

    def populate_table_widget(self, table_name, response):
        """
        Display rows in tableWidget_name and update the count label.
        :table_name: tableWidget name ( Products | Orders | Customers )
        :rows: rows to diaplay in table
        :response: the response from database
        """
        # PRODUCTS
        if table_name == 'Products':
            table_widget = self.ui.tableWidgetProduct
            headers = arabic.prod_headers
            count_label = self.ui.labelProductTableCount
            rows = [
                [
                    doc.get(field, "") for field in self.product_projection
                ] for doc in response["documents"]
            ]

        # CUSTOMERS
        elif table_name == 'Customers':
            table_widget = self.ui.tableWidgetCustomer
            headers = arabic.customer_headers
            count_label = self.ui.labelCustomerTableCount
            rows = [
                [
                    doc.get('_id', ''),
                    doc.get('first_name', ''),
                    doc.get('last_name', ''),
                    doc.get('phone', ''),
                    doc.get('email', ''),
                    doc.get('address', ''),
                    arabic.status_mapping_en.get(doc.get('is_active', ''), ''),
                    arabic.status_mapping_en.get(doc.get('client_status', ''), ''),
                ] for doc in response["documents"]
            ]

        # ORDERS
        elif table_name == 'Orders':
            table_widget = self.ui.tableWidgetOrders
            headers = arabic.order_headers
            count_label = self.ui.labelOrderTableCount
            rows = [
                [
                    order.get("_id", ""),
                    order.get("customer_name", "غير مسجل"),
                    order.get("order_date", "").strftime('%Y - %m - %d'),
                    arabic.status_mapping_en.get(order.get("status", ""), ""),
                    order.get("total_price", ""),
                ] for order in response["orders"]
            ]

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
            # display data in tableWidget
            self.populate_table_widget(collection_name, response)
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
                self.ui.buttonProductStatus
            ]
            table_widget = self.ui.tableWidgetProduct
        elif page == "Customers":
            buttons = [
                self.ui.buttonCustomerDetails,
                self.ui.buttonEditCustomer,
                self.ui.buttonDeleteCustomer,
                self.ui.buttonCustomerStatus,
                self.ui.buttonCustomerOrders,
                self.ui.buttonCustomerTrust,
            ]
            table_widget = self.ui.tableWidgetCustomer
        elif page == 'Orders':
            buttons = [
                self.ui.buttonOrderDetails,
                self.ui.buttonDeleteOrder,
                self.ui.buttonOrderStatus
            ]
            table_widget = self.ui.tableWidgetOrders

        for button in buttons:
            button.setEnabled(Utils.selected_rows(table_widget))

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
            projection = {"_id": 0, "created_at": 0, "updated_at": 0, "client_status": 0}
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
        Delete Item from Database
        :coll_name: ( Products | Items | Orders )
        """
        # Delete Product
        if coll_name == 'Products':
            label = self.ui.labelErrorProductPage
            table_widget = self.ui.tableWidgetProduct
            dialog_message = 'السلعة'

        # Delete Customer
        elif coll_name == 'Customers':
            # FIXME: Work the delete_customers_and_orders or Update MongoTables value to avoid errors in GUI
            label = self.ui.labelErrorCustomerPage
            table_widget = self.ui.tableWidgetCustomer
            dialog_message = 'المشتري'

        # Delete Order
        elif coll_name == 'Orders':
            label = self.ui.labelErrorOrderPage
            table_widget = self.ui.tableWidgetOrders
            dialog_message = 'الطلبية'

        selected_rows = set(index.row() for index in table_widget.selectedIndexes())
        # check how many selected rows
        if len(selected_rows) > 1: ids = Utils.table_selection_ids(table_widget)
        else: ids = Utils.get_column_value(table_widget, 0)

        # Execute the confirm dialog
        message = f'هل أنت متأكد من حذف {dialog_message}'
        confirmDialog = ConfirmDialog(message)
        # Execute the dialog and get the user's response
        delete = confirmDialog.exec_()
        if delete:
            if isinstance(ids, list):
                # Delete Multiple
                logger.debug(f"Delete Multiple from {coll_name} :: {ids}")
                response = self.db_handler.delete_many_documents(coll_name, ids)
            else:
                # Delete One Record
                logger.debug(f"Delete One from {coll_name} :: {ids}")
                response = self.db_handler.delete_document(coll_name, ObjectId(ids))

            # Delete items from database
            if response['status'] == 'success':
                if coll_name == 'Products': self.goto_page(page="Products")
                elif coll_name == 'Orders': self.goto_page(page="Orders")
                elif coll_name == 'Customers': self.goto_page(page="Customers")

                Utils.success_message(label, 'تم الحذف بنجاح', success=True)
            else:
                Utils.success_message(label, 'هناك خطأ أعد من جديد', success=False)

    def activate_item(self, coll_name):
        """
        Change the Status Field in ( Products | Customers )
        :call_name: ( Products | Customers )
        """
        if coll_name == 'Products':
            table_widget = self.ui.tableWidgetProduct
            label = self.ui.labelErrorProductPage
        elif coll_name == 'Customers':
            table_widget = self.ui.tableWidgetCustomer
            label = self.ui.labelErrorCustomerPage

        # Change in database
        item_id = Utils.get_column_value(table_widget, 0)
        response = self.db_handler.fetch_documents(
            collection_name=coll_name,
            query={"_id": ObjectId(item_id)},
            projection={"is_active": 1, "_id": 0}
        )
        if response['status'] == 'success':
            old_status = response['documents'][0]['is_active']      # This return ( True | False )
            if not old_status:
                response = self.db_handler.update_record_state(
                    collection_name=coll_name,
                    document_id=item_id,
                    field="is_active",
                    new_value=True
                )
                self.goto_page(page=coll_name)
                Utils.success_message(label, response["message"], response["status"] == "success")

    def change_order_status(self, new_status):
        """
        Change the order status
        :new_stats: "pending" | "confirmed" | "shipped" | "delivered" | "cancelled"
        """
        logger.debug(f'Change order status to: {new_status}')
        item_id = Utils.get_column_value(self.ui.tableWidgetOrders, 0)
        if new_status == 'cancelled':
            logger.debug('Order Cancelled: the quantity must return to product')
            response = self.db_handler.cancel_order(item_id)
            Utils.success_message(self.ui.labelErrorOrderPage, response['message'], response['status'] == 'success')
            self.all_orders()
        else:
            response = self.db_handler.update_record_state(
                collection_name='Orders',
                document_id=item_id, field="status",
                new_value=new_status
            )
            Utils.success_message(self.ui.labelErrorOrderPage, response['message'], response['status'] == 'success')
            self.all_orders()

    # ************************************************
    #   => Form Management
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
            elif key == 'client_status':
                values = ["عميل جيد", "عميل سيئ", "موثوق"]
                # Create the comboBox
                value_edit = Utils.create_comboBox(parent=parent, object_name=f"lineEdit_{key}", values=values)
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
                if isinstance(label_widget, QtWidgets.QLabel) and isinstance(input_widget, QtWidgets.QLabel):
                    key = input_widget.objectName().replace("lineEdit_", "")
                    value = input_widget.text().strip()
                    input_data[key] = value

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
                    if input_widget.objectName().startswith('lineEdit'):
                        key = input_widget.objectName().replace('lineEdit_', "")
                    else:
                        key = input_widget.objectName().replace("comboBoxAddOrder", "").lower()

                    if key == 'customer_id':
                        value = self.customers_map.get(input_widget.currentText().strip(), '')
                    elif key in ['status', 'client_status']:
                        value = arabic.status_mapping.get(input_widget.currentText().strip(), 'None')
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

        # Collect data
        data = self.collect_form_data(self.ui.formLayout)
        # ------------# Products ------------#
        if mongo_table == 'Products':
            label = self.ui.labelErrorProductPage
            logger.debug(f'Save Button: Saving Product( {operation} ) \n{data}')

            # CREATE PRODUCT
            if operation == 'Create':
                response = self.db_handler.create_product(**data)
                if response['status'] == 'success':
                    # re-display all the Products
                    self.fetch_and_display_data(
                        collection_name='Products',
                        headers=self.product_projection
                    )

                Utils.success_message(self.ui.labelErrorProductPage, response['message'], response['status'] == 'success')

            # UPDATE PRODUCT
            elif operation == 'Edit':
                product_id = self.ui.labelItemID.text()
                response = self.db_handler.update_product(product_id, data)
                if response['status'] == 'success':
                    Utils.success_message(label, 'تم تعديل المنتج بنجاح', success=True)
                    self.item_details(lineEditEnabled=False, operation='None', item_id=product_id)
                    # re-display all Products
                    self.fetch_and_display_data(
                        collection_name='Products',
                        headers=self.product_projection
                    )
                else:
                    Utils.success_message(label, 'هنالك خطأ إعد من جديد', success=False)

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
                        headers=self.customer_projection
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
                    Utils.success_message(label, "تم التعديل على المشتري بنجاح", success=True)
                    self.item_details(lineEditEnabled=False, coll_name='Customers', operation='None', item_id=customer_id)
                    # re-display the Customers in the tableWidget
                    self.fetch_and_display_data(
                        collection_name='Customers',
                        headers=self.customer_projection
                    )
                else:
                    Utils.success_message(label, 'هنالك خطأ إعد من جديد', success=False)

        # ------------# ORDERS #------------ #
        elif mongo_table == 'Order':
            # => Create New Order
            label = self.ui.labelErrorOrderPage
            if operation == 'Create':
                data = self.collect_form_data(self.ui.formLayoutNewOrder)
                del data['labelCartTotal']

                response = self.db_handler.create_order(**data)
                if response['status'] == 'success':
                    Utils.success_message(label, 'تم بنجاح')
                    self.all_orders()
                else:
                    Utils.success_message(label, response['message'], success=False)

        else:
            logger.warning('[ Save Button ] Nothing to save.')

    # ************************************************
    #   PRODUCT PAGE
    # *************************
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
        response = self.db_handler.fetch_products(query=query)
        if response["status"] == "success":
            # populate in tableWidget
            self.populate_table_widget('Products', response)
        else:
            Utils.success_message(self.ui.labelErrorProductPage, response['message'], False)

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
            # If the key is a date field, transform its format
            date_fields = ["created_at", "updated_at", "order_date"]
            if key in date_fields and (isinstance(value, str) or isinstance(value, datetime)):
                value = Utils.datetime_fields(value)

            # Create QTableWidget to display Products for a specific Order
            if key == "products":
                product_table = self.create_product_table(value)
                form_layout.setWidget(count, QtWidgets.QFormLayout.FieldRole, product_table)

                key_label = Utils.create_label(self.ui.scrollAreaWidgetContents, f"label_{key}")
                key_label.setText(arabic.arabic_mapping.get(key, key))
                form_layout.setWidget(count, QtWidgets.QFormLayout.LabelRole, key_label)
                continue

            # Translate to arabic
            if key in ["status", "is_active", "client_status"]:
                value = arabic.status_mapping_en.get(value, value)

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
        headers = ["اسم المنتج", "الكمية", "السعر", "المجموع"]
        table_widget = Utils.create_qtablewidget(column_count=4, headers=headers)
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
            table_widget.setItem(row, 0, QtWidgets.QTableWidgetItem(product_name))
            table_widget.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{quantity}"))
            table_widget.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{price}"))
            table_widget.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

        return table_widget

    # ********************************************
    #       => CUSTOMERS PAGE
    # ********************************************
    def search_customers(self, search_term):
        """
        Search customers by a term and display results in the QTableWidget.

        :param search_term: The search term to filter customers by name, email, or phone.
        """
        search_text = self.ui.lineEditSearchCustomer.text().strip()
        # Define the search query for MongoDB
        query = {"$or": [
            {"first_name": {"$regex": search_term, "$options": "i"}},  # Case-insensitive search in first name
            {"last_name": {"$regex": search_term, "$options": "i"}},   # Case-insensitive search in last name
            {"email": {"$regex": search_term, "$options": "i"}},       # Case-insensitive search in email
            {"phone": {"$regex": search_term, "$options": "i"}},       # Case-insensitive search in phone
        ]} if search_text else {}

        # Fetch matching customers from the database
        response = self.db_handler.fetch_customers(query=query)
        if response["status"] == "success":
            self.populate_table_widget('Customers', response)
        else:
            Utils.success_message(self.ui.labelErrorCustomerPage, response['message'], False)

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
            "client_status": "درجة الثقة"
        }
        # init config files
        self.ui.labelTitleDetails.setText('مشتري جديد')
        self.ui.labelMongoTable.setText('Customers')
        self.ui.labelOperation.setText('Create')
        self.ui.frameDetailsID.hide()

        # create the form
        self.create_form(fields)

    def customer_orders(self):
        """
        Display all Customer Orders in Orders Page
        """
        table_widget = self.ui.tableWidgetCustomer
        customer_id = Utils.get_column_value(self.ui.tableWidgetCustomer, 0)
        customer_name = f"{Utils.get_column_value(table_widget, 1)} {Utils.get_column_value(table_widget, 2)}"

        # fetch orders
        response = self.db_handler.fetch_customer_orders(customer_id)
        if response["status"] == "success":
            if len(response["orders"]) > 0:
                # display details in Orders Page
                self.populate_table_widget('Orders', response)
                self.ui.containerStackedWidget.setCurrentWidget(self.ui.OrderPage)
            else:
                Utils.success_message(self.ui.labelErrorCustomerPage, message=f"لا يوجد طلبيات للمشتري {customer_name}")
        else:
            logger.error(response["error"])

    def change_customer_status(self, status_key):
        """
        Callback to handle customer status changes.
        :param status_key: The key of the selected status (e.g., 'good_client', 'bad_client', 'trusted').
        """
        # Get the current customer ID (you can fetch it from the UI or context)
        customer_id = Utils.get_column_value(self.ui.tableWidgetCustomer, 0)

        # Update the database with the new status
        response = self.db_handler.update_record_state(
            collection_name="Customers",
            document_id=customer_id,
            field="client_status",
            new_value=status_key
        )

        # Display success or error message
        if response["status"] == "success":
            self.goto_page(page="Customers")
            Utils.success_message(self.ui.labelErrorCustomerPage, "تم تحديث حالة العميل بنجاح", True)
        else:
            Utils.success_message(self.ui.labelErrorCustomerPage, response["message"], False)

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
            # Display records in the table
            self.populate_table_widget('Orders', response)
        else:
            logger.error(f"Error fetching orders: {response['message']}")
            Utils.success_message(self.ui.labelErrorOrderPage, response['message'], success=False)

    def search_orders(self):
        # FIXME:  There is a problem with this function
        search_term = self.ui.lineEditSearchOrder.text().strip()
        # Define the search query for MongoDB
        query = {
            "$or": [
                {"customer_name": {"$regex": search_term, "$options": "i"}},  # Case-insensitive search in customer name
                {"status": {"$regex": search_term, "$options": "i"}},         # Case-insensitive search in order status
                {"order_date": {"$regex": search_term, "$options": "i"}},     # Case-insensitive search in order date
                {"_id": {"$regex": search_term, "$options": "i"}},            # Search by order ID (string representation)
            ]
        } if search_term else {}

        # Fetch matching customers from the database
        response = self.db_handler.fetch_orders_with_customer_names(query=query)
        if response["status"] == "success":
            self.populate_table_widget('Orders', response)
        else:
            Utils.success_message(self.ui.labelErrorOrderPage, response['message'], False)

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
        # Re-order the fields
        response = {
            "order_date": response.get("order_date", ""),
            "customer_name": response.get("customer_name", ""),
            "total_price": response.get("total_price", 0),
            "status": response.get("status", ""),
            "created_at": response.get("created_at"),
            "updated_at": response.get("updated_at"),
            "products": response.get("products", []),
        }
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

        # Clear all the widget for the new order
        self.ui.comboBoxAddOrderCustomer_id.clear()     # clear the combobox
        self.ui.comboBoxAddOrderStatus.clear()
        self.ui.dateEditAddOrderDate.clear()
        self.ui.labelCartTotal.setText('0')
        self.ui.tableWidgetAddOrderProds.setRowCount(0)

        # Combobox Order Customers
        self.customers_map = {}                         # Map orders names to ObjectIds
        for customer in response['documents']:
            cust_name = f"{customer.get('first_name', '')} {customer.get('last_name')}".strip()
            cust_id = str(customer["_id"])
            self.customers_map[cust_name] = cust_id
            self.ui.comboBoxAddOrderCustomer_id.addItem(cust_name)

        # Combobox Order Status
        for status in arabic.status_mapping_neworder.keys():
            self.ui.comboBoxAddOrderStatus.addItem(status)

        # Set DateEdit to now
        self.ui.dateEditAddOrderDate.setDate(datetime.now())

        self.ui.frameToolButton_2.show()
        self.ui.stackedWidgetDetails.setCurrentWidget(self.ui.createOrderPage)
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

        product_map = {}  # Map product names to ObjectIds
        for product in response["documents"]:
            product_name = product.get("name", "غير معروف")
            product_id = str(product["_id"])
            product_qte = product.get("qte", 0)

            product_map[product_name] = {"id": product_id, "qte": product_qte}

        # Execute the dialog and add product to cart
        dialog = AddProductToCart(product_map)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            logger.debug('Adding product to cart from the QDialog')
            # Get the selected product and quantity
            selected_product_name = dialog.selected_product
            product_id = product_map[selected_product_name]["id"]
            quantity = dialog.qte

            # Update the price
            product_response = self.db_handler.db["Products"].find_one({"_id": ObjectId(product_id)}, {"price": 1})
            prod_price = Decimal(product_response["price"].to_decimal())
            total = Decimal(self.ui.labelCartTotal.text())
            total += quantity * prod_price

            self.ui.labelCartTotal.setText(f"{total}")

            # Add the selected product to the table
            table_widget.setColumnCount(5)  # Columns: Product ID, Name, Quantity, Actions
            table_widget.setHorizontalHeaderLabels(["رقم المنتج", "اسم المنتج", "الكمية", "السعر", "إزالة"])
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            table_widget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(product_id))
            table_widget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(selected_product_name))
            table_widget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(quantity)))
            table_widget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(prod_price)))

            # Add a remove button
            remove_button = QtWidgets.QPushButton(" إزالة")
            remove_button.setIcon(qta.icon('fa.trash', color="#EA2027"))
            remove_button.setIconSize(QtCore.QSize(20, 20))
            remove_button.clicked.connect(lambda: table_widget.removeRow(row_position))

            table_widget.setCellWidget(row_position, 4, remove_button)

    # ********************************************
    #       ==> STATISTICS PAGE
    # ********************************************
    def display_statistics_labels(self, stats):
        """
        Display computed statistics in text labels on the UI.
        :param stats: Dictionary containing statistics for products, orders, and customers.
        """
        self.ui.labelTotalProducts.setText(f"إجمالي المنتجات: {stats['products']['total_products']}")
        self.ui.labelTotalQuantity.setText(f"إجمالي الكمية: {stats['products']['total_quantity']}")

        self.ui.labelTotalOrders.setText(f"إجمالي الطلبات: {stats['orders']['total_orders']}")
        total_revenu = Decimal(stats['orders']['total_revenue'].to_decimal())
        self.ui.labelTotalRevenue.setText(f"إجمالي الإيرادات: ${total_revenu:.2f}")

        self.ui.labelTotalCustomers.setText(f"إجمالي العملاء: {stats['customers']['total_customers']}")
        self.ui.labelActiveCustomers.setText(f"العملاء النشطون: {stats['customers']['active_customers']}")

    def display_top_products(self, stats):
        """
        Display the top products by quantity in a QTableWidget.

        :param stats: Dictionary containing statistics for products.
        """
        top_products = stats["products"]["top_products"]

        # Clear the table and set headers
        self.ui.tableWidgetTopProducts.setRowCount(0)
        self.ui.tableWidgetTopProducts.setColumnCount(2)
        self.ui.tableWidgetTopProducts.setHorizontalHeaderLabels(["Product Name", "Quantity"])

        # Populate the table
        for row, product in enumerate(top_products):
            self.ui.tableWidgetTopProducts.insertRow(row)
            self.ui.tableWidgetTopProducts.setItem(row, 0, QtWidgets.QTableWidgetItem(product["name"]))
            self.ui.tableWidgetTopProducts.setItem(row, 1, QtWidgets.QTableWidgetItem(str(product["qte"])))

    def plot_orders_by_status(self, stats):
        """
        Plot a bar chart for orders grouped by status.

        :param stats: Dictionary containing statistics for orders.
        """
        data = stats["orders"]["orders_by_status"]
        statuses = [entry["_id"] for entry in data]
        counts = [entry["count"] for entry in data]

        from statistic import StatisticsWidget
        stats_widget = StatisticsWidget(self)
        stats_widget.axes.bar(statuses, counts, color="blue")
        stats_widget.axes.set_title("Orders by Status")
        stats_widget.axes.set_xlabel("Status")
        stats_widget.axes.set_ylabel("Count")
        stats_widget.draw()

        layout = self.ui.horizontalLayout
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        layout.addWidget(stats_widget)

    def show_statistics(self):
        """
        Show statistics in the application with embedded graphs.
        """
        # Fetch statistics
        stats = self.db_handler.generate_statistics()

        self.display_statistics_labels(stats)
        self.display_top_products(stats)
        self.plot_orders_by_status(stats)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = Interface()
    dialog.show()
    sys.exit(app.exec_())
