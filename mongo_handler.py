#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------

import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
from logger import logger


class MongoDBHandler:
    """
    A class to handle MongoDB operations for Products and Orders.
    """

    def __init__(self, uri="mongodb://localhost:27017/", database="elSel3a"):
        """
        Initializes the MongoDBHandler class.

        :param uri: MongoDB connection URI. Default is localhost.
        :param database: Name of the database to connect to.
        """

        # Check if MongoDB is running
        if not self.is_mongodb_running(uri):
            raise ConnectionError("MongoDB service is not running. Please start it and try again.")

        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[database]
            logger.info("Connected to MongoDB successfully.")
        except Exception as err:
            # logger.error(f"Error connecting to MongoDB: {err}")
            raise ConnectionError(f"Error connecting to MongoDB: {err}")

    def is_mongodb_running(self, uri):
        """
        Checks if the MongoDB service is running.

        :return: True if MongoDB is running, False otherwise.
        """
        try:
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")  # Test the connection
            logger.info("MongoDB service is running.")
            return True
        except ConnectionFailure:
            # logger.error(f"MongoDB service is not running: {e}")
            return False

    # Product Methods
    def register_product(self, name, ref, description, qte, price, category, supplier):
        """
        Registers a new product in the database.

        :param name: Product name.
        :param ref: Product reference.
        :param description: Product description.
        :param qte: Product quantity.
        :param price: Product price.
        :param category: Product category.
        :param supplier: Supplier information.
        :return: Inserted product's ID.
        """
        try:
            product = {
                "name": name,
                "ref": ref,
                "description": description,
                "qte": qte,
                "price": price,
                "category": category,
                "supplier": supplier,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }
            result = self.db["Products"].insert_one(product)
            logger.info(f"Product registered successfully with ID: {result.inserted_id}")
            return {"status": "success", "product_id": str(result.inserted_id)}
        except Exception as err:
            logger.error(f"Error registering product: {err}")
            return {"status": "error", "message": str(err)}

    def fetch_products(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches products from the database.

        :param query: Filter criteria. Default is None (fetch all).
        :param projection: Fields to include or exclude. Default is None (include all).
        :param limit: Maximum number of documents to fetch. Default is 0 (no limit).
        :param sort: Sort order as a list of tuples (e.g., [("price", -1)]).
        :return: List of fetched products.
        """
        try:
            cursor = self.db["Products"].find(query or {}, projection or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
            logger.info("Fetched products successfully.")
            return {"status": "success", "products": list(cursor)}
        except Exception as err:
            logger.error(f"Error fetching products: {err}")
            return {"status": "error", "message": str(err)}

    def fetch_one_product(self, product_id):
        """
        Fetches a single product from the database.

        :param query: Filter criteria (e.g., {"ref": "LPT123"}).
        :param projection: Fields to include or exclude. Default is None (include all).
        :return: The fetched product document or an error message.
        """
        try:
            # Convert the product_id to ObjectId
            object_id = ObjectId(product_id)
            product = self.db["Products"].find_one({"_id": object_id}, {"_id": 0})
            if product:
                logger.info(f"Product fetched successfully: {product}")
                return {"status": "success", "product": product}
            else:
                logger.warning("Product not found.")
                return {"status": "error", "message": "Product not found."}
        except Exception as err:
            logger.error(f"Error fetching product: {err}")
            return {"status": "error", "message": str(err)}

    def delete_product(self, product_id):
        """
        Deletes a product from the database.

        :param product_id: The ID of the product to delete.
        :return: Deletion status.
        """
        try:
            result = self.db["Products"].delete_one({"_id": product_id})
            if result.deleted_count > 0:
                logger.info(f"Product {product_id} deleted successfully.")
                return {"status": "success", "message": "Product deleted."}
            logger.warning(f"Product {product_id} not found.")
            return {"status": "error", "message": "Product not found."}
        except Exception as err:
            logger.error(f"Error deleting product: {err}")
            return {"status": "error", "message": str(err)}

    # *************************************************************
    #  Order Methods
    # **************
    def create_order(self, customer_id, products, status="Pending"):
        """
        Creates a new order in the database.

        :param customer_id: The ID of the customer placing the order.
        :param products: A list of product dictionaries with `product_id` and `quantity`.
        :param status: Initial status of the order. Default is 'Pending'.
        :return: Inserted order's ID.
        """
        try:
            order = {
                "customer_id": customer_id,
                "products": products,
                "order_date": datetime.now(),
                "status": status,
                "total_price": self.calculate_total_price(products),        # Calculate the total price
            }
            result = self.db["Orders"].insert_one(order)
            logger.info(f"Order created successfully with ID: {result.inserted_id}")
            return {"status": "success", "order_id": str(result.inserted_id)}
        except Exception as err:
            logger.error(f"Error creating order: {err}")
            return {"status": "error", "message": str(err)}

    def fetch_orders(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches orders from the database.

        :param query: Filter criteria. Default is None (fetch all).
        :param projection: Fields to include or exclude. Default is None (include all).
        :param limit: Maximum number of documents to fetch. Default is 0 (no limit).
        :param sort: Sort order as a list of tuples (e.g., [("order_date", -1)]).
        :return: List of fetched orders.
        """
        try:
            cursor = self.db["Orders"].find(query or {}, projection or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
            logger.info("Fetched orders successfully.")
            return {"status": "success", "orders": list(cursor)}
        except Exception as err:
            logger.error(f"Error fetching orders: {err}")
            return {"status": "error", "message": str(err)}

    def calculate_total_price(self, products):
        """
        Calculates the total price of an order based on product quantities and prices.

        :param products: List of product dictionaries with `product_id` and `quantity`.
        :return: Total price of the order.
        """
        try:
            total_price = 0
            for product in products:
                product_data = self.db["Products"].find_one(
                    {"_id": product["product_id"]}, {"price": 1}
                )
                if product_data:
                    total_price += product_data["price"] * product["quantity"]
                else:
                    logger.warning(f"Product {product['product_id']} not found.")
            return total_price
        except Exception as err:
            logger.error(f"Error calculating total price: {err}")
            return 0

    # *************************************************************
    #  Customers Methods
    # *******************

    def add_customer(self, first_name, last_name, email, phone, address):
        """
        Adds a new customer to the database.

        :param first_name: Customer's first name.
        :param last_name: Customer's last name.
        :param email: Customer's email.
        :param phone: Customer's phone number.
        :param address: Customer's address.
        :return: Inserted customer's ID.
        """
        try:
            customer = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "address": address,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True
            }
            result = self.db["Customers"].insert_one(customer)
            logger.info(f"Customer added successfully with ID: {result.inserted_id}")
            return {"status": "success", "customer_id": str(result.inserted_id)}
        except Exception as err:
            logger.error(f"Error adding customer: {err}")
            return {"status": "error", "message": str(err)}

    def fetch_customers(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches customers from the database.

        :param query: Filter criteria. Default is None (fetch all).
        :param projection: Fields to include or exclude. Default is None (include all).
        :param limit: Maximum number of documents to fetch. Default is 0 (no limit).
        :param sort: Sort order as a list of tuples (e.g., [("created_at", -1)]).
        :return: List of fetched customers.
        """
        try:
            customers = self.db["Customers"]
            cursor = customers.find(query or {}, projection or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
            logger.info("Fetched customers successfully.")
            return {"status": "success", "customers": list(cursor)}
        except Exception as err:
            logger.error(f"Error fetching customers: {err}")
            return {"status": "error", "message": str(err)}

    def update_customer(self, customer_id, updates):
        """
        Updates a customer's details.

        :param customer_id: The ID of the customer to update.
        :param updates: A dictionary of fields to update.
        :return: Update status.
        """
        try:
            updates["updated_at"] = datetime.now()
            result = self.db["Customers"].update_one({"_id": ObjectId(customer_id)}, {"$set": updates})
            if result.modified_count > 0:
                logger.info(f"Customer {customer_id} updated successfully.")
                return {"status": "success", "message": "Customer updated."}
            logger.warning(f"Customer {customer_id} not found or no changes made.")
            return {"status": "error", "message": "Customer not found or no changes made."}
        except Exception as err:
            logger.error(f"Error updating customer: {err}")
            return {"status": "error", "message": str(err)}

    def delete_customer(self, customer_id):
        """
        Deletes a customer from the database.

        :param customer_id: The ID of the customer to delete.
        :return: Deletion status.
        """
        try:
            result = self.db["Customers"].delete_one({"_id": ObjectId(customer_id)})
            if result.deleted_count > 0:
                logger.info(f"Customer {customer_id} deleted successfully.")
                return {"status": "success", "message": "Customer deleted."}
            logger.warning(f"Customer {customer_id} not found.")
            return {"status": "error", "message": "Customer not found."}
        except Exception as err:
            logger.error(f"Error deleting customer: {err}")
            return {"status": "error", "message": str(err)}


if __name__ == "__main__":
    # Example usage
    handler = MongoDBHandler()

    # *************
    #   Products
    # ******************
    # response = handler.register_product(
        # name="Laptop",
        # ref="LPT123",
        # description="15-inch screen, 8GB RAM",
        # qte=10,
        # price=1500.00,
        # category="Electronics",
        # supplier="TechSupplier Inc."
    # )
    # print(response)

    # Fetch a product by reference
    # response = handler.fetch_one_product(query={"ref": "LPT123"}, projection={
        # "name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "_id": 0
    # })

    # print(response)
    # if response["status"] == "success":
        # print("Product Details:")
        # print(response["product"])
    # else:
        # print("Error:", response["message"])

    # Sample Products
    # Fetch products
    # response = handler.fetch_products(limit=5, sort=[("price", -1)])
    # if response['status'] == 'success':
        # for prod in response['products']:
            # for key, value in prod.items():
                # print(f"{key}  :: {value}")
            # print('-' * 30)
    # else:
        # print(response['message'])

    # print(response)

    # *************
    #   Orders
    # ******************
    # Create an order
    # products = [
        # {"product_id": "123456", "quantity": 2},
        # {"product_id": "123456789", "quantity": 1}
    # ]
    # response = handler.create_order(customer_id="znanda", products=products)
    # print(response)

    # Fetch orders
    response = handler.fetch_orders(limit=3, sort=[("order_date", -1)])
    if response['status'] == 'success':
        for order in response['orders']:
            for key, value in order.items():
                print(f"{key} :: {value}")
            print('-' * 30)

    # *************
    # Customers
    # ******************
    response = handler.add_customer(
        first_name="أحمد",
        last_name="السيد",
        email="ahmed@example.com",
        phone="01012345678",
        address="123 شارع النيل، القاهرة"
    )
    print(response)

    # Fetch all customers
    response = handler.fetch_customers(sort=[("created_at", -1)], limit=5)
    print(response)

    # Update a customer
    customer_id = "6489cde8a1d4b1d6e2f7a456"  # Example ID
    response = handler.update_customer(customer_id, updates={"phone": "01198765432"})
    print(response)

    # Delete a customer
    response = handler.delete_customer(customer_id="6489cde8a1d4b1d6e2f7a456")
    print(response)
