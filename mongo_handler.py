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
    A class to handle MongoDB operations for Products, Orders, and Customers.
    """

    def __init__(self, uri="mongodb://localhost:27017/", database="elSel3a"):
        """
        Initializes the MongoDBHandler class and checks MongoDB service.

        :param uri: MongoDB connection URI. Default is localhost.
        :param database: Name of the database to connect to.
        """
        self.uri = uri
        self.database_name = database

        # Check if MongoDB is running
        if not self.is_mongodb_running():
            raise ConnectionError("MongoDB service is not running. Please start it and try again.")

        try:
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[self.database_name]
            logger.info("Connected to MongoDB successfully.")
        except Exception as err:
            logger.error(f"Error connecting to MongoDB: {err}")
            raise ConnectionError(f"Error connecting to MongoDB: {err}")

    def is_mongodb_running(self):
        """
        Checks if the MongoDB service is running.

        :return: True if MongoDB is running, False otherwise.
        """
        try:
            client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            logger.info("MongoDB service is running.")
            return True
        except ConnectionFailure:
            logger.error("MongoDB service is not running.")
            return False

    # *************************************************************
    # Base Methods
    # *************************************************************

    def add_document(self, collection_name, document):
        """
        Adds a new document to a collection.

        :param collection_name: Name of the collection.
        :param document: The document to insert.
        :return: Inserted document's ID.
        """
        try:
            document["created_at"] = datetime.now()
            document["updated_at"] = datetime.now()
            result = self.db[collection_name].insert_one(document)
            logger.info(f"Document added successfully to {collection_name} with ID: {result.inserted_id}")
            return {"status": "success", "id": str(result.inserted_id)}
        except Exception as err:
            logger.error(f"Error adding document to {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    def fetch_documents(self, collection_name, query=None, projection=None, limit=0, sort=None):
        """
        Fetches documents from a collection.

        :param collection_name: Name of the collection.
        :param query: Filter criteria. Default is None (fetch all).
        :param projection: Fields to include or exclude. Default is None (include all).
        :param limit: Maximum number of documents to fetch. Default is 0 (no limit).
        :param sort: Sort order as a list of tuples (e.g., [("created_at", -1)]).
        :return: List of fetched documents.
        """
        try:
            cursor = self.db[collection_name].find(query or {}, projection or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
            logger.info(f"Fetched documents successfully from {collection_name}.")
            return {"status": "success", "documents": list(cursor)}
        except Exception as err:
            logger.error(f"Error fetching documents from {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    def update_document(self, collection_name, document_id, updates):
        """
        Updates a document in a collection.

        :param collection_name: Name of the collection.
        :param document_id: The ID of the document to update.
        :param updates: A dictionary of fields to update.
        :return: Update status.
        """
        try:
            updates["updated_at"] = datetime.now()
            result = self.db[collection_name].update_one({"_id": ObjectId(document_id)}, {"$set": updates})
            if result.modified_count > 0:
                logger.info(f"Document {document_id} updated successfully in {collection_name}.")
                return {"status": "success", "message": "Document updated."}
            logger.warning(f"Document {document_id} not found or no changes made.")
            return {"status": "error", "message": "Document not found or no changes made."}
        except Exception as err:
            logger.error(f"Error updating document in {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    def delete_document(self, collection_name, document_id):
        """
        Deletes a document from a collection.

        :param collection_name: Name of the collection.
        :param document_id: The ID of the document to delete.
        :return: Deletion status.
        """
        try:
            result = self.db[collection_name].delete_one({"_id": ObjectId(document_id)})
            if result.deleted_count > 0:
                logger.info(f"Document {document_id} deleted successfully from {collection_name}.")
                return {"status": "success", "message": "Document deleted."}
            logger.warning(f"Document {document_id} not found.")
            return {"status": "error", "message": "Document not found."}
        except Exception as err:
            logger.error(f"Error deleting document from {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    # *************************************************************
    # Product Methods
    # *************************************************************

    def create_product(self, name, ref, description, qte, price, category, supplier):
        """
        Adds a new product to the Products collection.
        """
        product = {
            "name": name,
            "ref": ref,
            "description": description,
            "qte": qte,
            "price": price,
            "category": category,
            "supplier": supplier,
            "is_active": True
        }
        return self.add_document("Products", product)

    def fetch_products(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches products from the Products collection.
        """
        return self.fetch_documents("Products", query, projection, limit, sort)

    # *************************************************************
    # Order Methods
    # *************************************************************

    def create_order(self, customer_id, products, status="Pending"):
        """
        Creates a new order in the Orders collection.
        """
        order = {
            "customer_id": customer_id,
            "products": products,
            "status": status,
            "order_date": datetime.now(),
            "total_price": self.calculate_total_price(products)
        }
        return self.add_document("Orders", order)

    def fetch_orders(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches orders from the Orders collection.
        """
        return self.fetch_documents("Orders", query, projection, limit, sort)

    def fetch_orders_with_customer_names(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches orders from the database and includes customer names.

        :param query: Filter criteria for orders. Default is None (fetch all).
        :param projection: Fields to include or exclude. Default is None (include all).
        :param limit: Maximum number of documents to fetch. Default is 0 (no limit).
        :param sort: Sort order as a list of tuples (e.g., [("order_date", -1)]).
        :return: List of fetched orders with customer names.
        """
        try:
            pipeline = [
                {"$match": query or {}},  # Filter orders based on the query
                {
                    "$lookup": {
                        "from": "Customers",  # The name of the Customers collection
                        "localField": "customer_id",  # The field in Orders to match
                        "foreignField": "_id",  # The field in Customers to match
                        "as": "customer_details"  # Alias for joined customer details
                    }
                },
                {
                    "$addFields": {
                        "customer_name": {
                            "$concat": [
                                {"$arrayElemAt": ["$customer_details.first_name", 0]},
                                " ",
                                {"$arrayElemAt": ["$customer_details.last_name", 0]}
                            ]
                        }
                    }
                },
                {"$unset": "customer_details"}  # Remove the raw customer details after extracting name
            ]

            if sort:
                pipeline.append({"$sort": dict(sort)})

            if limit > 0:
                pipeline.append({"$limit": limit})

            # Execute the aggregation pipeline
            orders = list(self.db["Orders"].aggregate(pipeline))
            logger.info("Fetched orders with customer names successfully.")
            return {"status": "success", "orders": orders}
        except Exception as err:
            logger.error(f"Error fetching orders: {err}")
            return {"status": "error", "message": str(err)}

    def calculate_total_price(self, products):
        """
        Calculates the total price of an order.
        """
        total_price = 0
        for product in products:
            product_data = self.db["Products"].find_one({"_id": ObjectId(product["product_id"])}, {"price": 1})
            if product_data:
                total_price += product_data["price"] * product["quantity"]
            else:
                logger.warning(f"Product {product['product_id']} not found.")
        return total_price

    # *************************************************************
    # Customer Methods
    # *************************************************************

    def add_customer(self, first_name, last_name, email, phone, address):
        """
        Adds a new customer to the Customers collection.
        """
        customer = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "is_active": True
        }
        return self.add_document("Customers", customer)

    def fetch_customers(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches customers from the Customers collection.
        """
        return self.fetch_documents("Customers", query, projection, limit, sort)


if __name__ == "__main__":
    # Example usage
    handler = MongoDBHandler()

    # *************
    #   Products
    # ******************
    #
    # Add a new product
    # response = handler.create_product(
        # name="لابتوب",
        # ref="LPT123",
        # description="شاشة 15 بوصة، 8 جيجابايت رام",
        # qte=10,
        # price=1500.00,
        # category="إلكترونيات",
        # supplier="تقنيات المستقبل"
    # )
    # print(response)

    # === FETCH ALL PRODUCTS ===
    # response = handler.fetch_products(limit=5, sort=[("price", -1)])
    # if response['status'] == 'success':
        # for prod in response['documents']:
            # for key, value in prod.items():
                # print(f"{key}  :: {value}")
            # print('-' * 30)
    # else:
        # print(response['message'])

    # === Fetch one product by its ObjectId ===
    # product_id = "6753810bbbe65eb9e57627b0"  # Replace with a valid _id from your database
    # response = handler.fetch_documents(
        # collection_name="Products",
        # query={"_id": ObjectId(product_id)},
        # projection={"name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "_id": 0}
    # )
    # print(response['documents'][0])
    # if response["status"] == "success":
        # print("Product Details:")
        # print(response["documents"][0])
    # else:
        # print("Error:", response["message"])

    # **************************************************************************
    #   Orders
    # ******************
    # Create an order
    # products = [
        # {"product_id": ObjectId("6753810bbbe65eb9e57627b3"), "quantity": 2},
        # {"product_id": ObjectId("67571d3ae8b50300ac73202f"), "quantity": 3},
    # ]
    # response = handler.create_order(customer_id=ObjectId("67571d3ae8b50300ac73202f"), products=products)
    # print(response)

    # === FETCH ORDERS
    response = handler.fetch_orders_with_customer_names()
    # response = handler.fetch_orders(limit=3, sort=[("order_date", -1)])
    print(response)
    if response['status'] == 'success':
        for order in response['orders']:
            for key, value in order.items():
                print(f"{key} :: {value}")
            print('-' * 30)

    # *******************************************************************************
    # Customers
    # ******************
    # response = handler.add_customer(
        # first_name="أحمد",
        # last_name="السيد",
        # email="ahmed@example.com",
        # phone="01012345678",
        # address="شارع الإمير عبدالقادر - تيبازة"
    # )
    # print(response)

    # Fetch all customers
    # response = handler.fetch_customers(sort=[("created_at", -1)], limit=5)
    # print(response)

    # Update a customer
    # customer_id = "6489cde8a1d4b1d6e2f7a456"  # Example ID
    # response = handler.update_customer(customer_id, updates={"phone": "01198765432"})
    # print(response)

    # Delete a customer
    # response = handler.delete_customer(customer_id="6489cde8a1d4b1d6e2f7a456")
    # print(response)
