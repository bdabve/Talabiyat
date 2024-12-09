#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          :
# ----------------------------------------------------------------------------
from datetime import datetime
from PyQt5 import QtWidgets   # , QtCore
from bson.objectid import ObjectId

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
        self.ui.containerStackedWidget.setCurrentWidget(self.ui.ProductPage)
        Utils.pagebuttons_stats(self)

    def goto_order_page(self):
        self.all_orders()
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

    # ************************************************
    #   PRODUCT PAGE
    # *************************

    def all_products(self):
        """
        Fetches all products from the database and displays them in the table widget.
        """
        # Fetch all products
        response = self.db_handler.fetch_products(
            projection={"_id": 1, "name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "category": 1},
            sort=[("created_at", 1)]  # Sort by create time
        )

        if response["status"] == "success":
            products = response["documents"]

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
                for product in products
            ]

            # Display records in the table
            self.populate_table_widget('Products', rows)
        else:
            print(f"Error fetching products: {response['message']}")

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

        if response["status"] == "success":
            # Format rows for display
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
                for product in response["documents"]
            ]
            # Display the filtered products in the table
            self.populate_table_widget('Products', rows)
        else:
            print(f"Error fetching products: {response['message']}")

    # ************* Product Details Widget***************

    def populate_formFrame(self, response, lineEditEnabled=False):
        """
        Populate the formFrame located in the details dockWidget.

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
            "is_active": "الحالة"
        }

        # Populate the form with translated keys
        for count, (key, value) in enumerate(response.items(), start=1):
            # If the key is a date field, transform its format
            if key in ["created_at", "updated_at"] and isinstance(value, str):
                try:
                    value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y - %m - %d")
                except ValueError:
                    value = "تاريخ غير صالح"
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

    def product_details(self, lineEditEnabled):
        """Show details for a selected process."""
        product_id = Utils.get_column_value(self.ui.tableWidgetProduct, 0)

        # Config Labels
        self.ui.labelItemID.setText(str(product_id))
        self.ui.labelMongoTable.setText('Products')
        self.ui.frameDetailsID.hide()

        response = self.db_handler.fetch_documents(
            collection_name="Products",
            query={"_id": ObjectId(product_id)},
            projection={"_id": 0}
        )
        if response["status"] == "error":
            self.ui.labelErrorProductPage.setText(response["message"])
            return

        response = response["documents"][0]
        self.populate_formFrame(response, lineEditEnabled=lineEditEnabled)
        self.ui.dockWidget.show()

    def new_product(self):
        print("New Product")

    def edit_product(self):
        item_id = Utils.get_column_value()
        mongo_table = self.ui.labelMongoTable.text()
        print(f"Edit :: {item_id} :: {mongo_table}")

    def delete_product(self):
        item_id = Utils.get_column_value(self.ui.tableWidgetProduct)
        print(f"Delete :: {item_id}")

    # ********************************************
    # == Order Page
    # ********************************************
    def all_orders(self):
        """
        Fetches all products from the database and displays them in the table widget.
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
            print(f"Error fetching products: {response['message']}")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = Interface()
    dialog.show()
    sys.exit(app.exec_())
