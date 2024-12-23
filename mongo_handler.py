#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------

import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal
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

            logger.warning(f"Document {document_id} not found in collection {collection_name}.")
            return {"status": "error", "message": "Document not found."}
        except Exception as err:
            logger.error(f"Error deleting document from {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    def delete_many_documents(self, collection_name, document_ids):
        """
        Deletes multiple documents from a collection based on a list of IDs.

        :param collection_name: Name of the collection.
        :param document_ids: List of IDs of the documents to delete.
        :return: Deletion status with the count of deleted documents.
        """
        try:
            # Convert string IDs to ObjectId
            object_ids = [ObjectId(doc_id) for doc_id in document_ids]

            # Perform the deletion
            result = self.db[collection_name].delete_many({"_id": {"$in": object_ids}})

            if result.deleted_count > 0:
                logger.info(f"Deleted {result.deleted_count} documents from {collection_name}.")
                return {
                    "status": "success",
                    "message": f"Deleted {result.deleted_count} documents.",
                    "deleted_count": result.deleted_count
                }

            logger.warning(f"No documents found to delete in collection {collection_name} with the given IDs.")
            return {
                "status": "error",
                "message": "No documents found to delete.",
                "deleted_count": 0
            }

        except Exception as err:
            logger.error(f"Error deleting documents from {collection_name}: {err}")
            return {"status": "error", "message": str(err)}

    def update_record_state(self, collection_name, document_id, field, new_value):
        """
        Updates a specific field for a single record in a collection.

        :param collection_name: Name of the collection (e.g., "Products", "Customers", "Orders").
        :param document_id: The ID of the document to update.
        :param field: The field to update (e.g., "is_active", "status").
        :param new_value: The new value to set for the field.
        :return: A dictionary with the status and a message.
        """
        try:
            # Perform the update
            result = self.db[collection_name].update_one(
                {"_id": ObjectId(document_id)},  # Match the document by its _id
                {"$set": {field: new_value}}     # Update the specified field
            )

            if result.matched_count > 0:
                if result.modified_count > 0:
                    logger.info(f"Updated {field} for document {document_id} in {collection_name} to {new_value}.")
                    return {"status": "success", "message": "Record updated successfully."}
                else:
                    logger.warning(f"No changes made to document {document_id} in {collection_name}.")
                    return {"status": "warning", "message": "No changes made."}
            else:
                logger.error(f"Document {document_id} not found in {collection_name}.")
                return {"status": "error", "message": "Record not found."}
        except Exception as err:
            logger.error(f"Error updating document {document_id} in {collection_name}: {err}")
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
            "qte": int(qte),
            "price": Decimal128(Decimal(price)),
            "category": category,
            "supplier": supplier,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return self.add_document("Products", product)

    def fetch_products(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches products from the Products collection.
        """
        try:
            products = self.db["Products"]
            cursor = products.find(query or {}, projection or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)

            product_list = []
            for product in cursor:
                if "price" in product:
                    product["price"] = Decimal(product["price"].to_decimal())
                product_list.append(product)

            logger.info("Fetched products successfully.")
            return {"status": "success", "documents": product_list}
        except Exception as err:
            logger.error(f"Error fetching products: {err}")
            return {"status": "error", "message": str(err)}

        # return self.fetch_documents("Products", query, projection, limit, sort)

    def update_product(self, product_id, update_data):
        """
        Updates a product in the Products collection by its product_id.

        :param product_id: The ObjectId of the product to update.
        :param update_data: A dictionary containing the fields to update.
        :return: A dictionary with the status of the operation.
        """
        try:
            # Ensure product_id is an ObjectId
            product_id = ObjectId(product_id)

            # Validate and format fields in update_data
            if "price" in update_data:
                # Ensure price is stored as Decimal128
                update_data["price"] = Decimal128(Decimal(str(update_data["price"])))

            if "qte" in update_data:
                # Ensure qte is stored as an integer
                update_data["qte"] = int(update_data["qte"])

            # Add the 'updated_at' field to track modification time
            update_data["updated_at"] = datetime.utcnow()

            # Perform the update
            result = self.db["Products"].update_one(
                {"_id": product_id},  # Match product by its _id
                {"$set": update_data}  # Set the fields to the new values
            )

            if result.matched_count == 0:
                logger.warning('Product not found')
                return {"status": "error", "message": "Product not found."}
            if result.modified_count == 0:
                logger.warning('No changes were made.')
                return {"status": "warning", "message": "No changes were made."}

            logger.info('Product updated successfully')
            return {"status": "success", "message": "Product updated successfully."}
        except Exception as err:
            logger.error(f"Error updating product: {err}")
            return {"status": "error", "message": str(err)}

    def update_product_quantity(self, product_id, quantity_change):
        """
        Updates the quantity of a product in the database.

        :param product_id: The ID of the product to update.
        :param quantity_change: The change in quantity (negative to reduce, positive to increase).
        :return: A dictionary with the status of the operation.
        """
        try:
            result = self.db["Products"].update_one(
                {"_id": ObjectId(product_id)},
                {"$inc": {"qte": quantity_change}}
            )
            if result.matched_count == 0:
                return {"status": "error", "message": f"Product with ID {product_id} not found."}

            return {"status": "success", "message": "Quantity updated successfully."}
        except Exception as err:
            logger.error(f"Error updating product quantity: {err}")
            return {"status": "error", "message": str(err)}

    # *************************************************************
    # Order Methods
    # *************************************************************
    def create_order(self, customer_id, products, order_date=None, status="pending"):
        try:
            if len(products) == 0:
                logger.error("No products selected for this order")
                return {"status": "error", "message": "عليك إضافة السلعة إلالطلبية"}

            total_price = 0
            product_updates = []    # Keep track of quantity updates to apply after
            for product in products:
                product_id = product["product_id"]
                quantity = product["quantity"]

                product_response = self.db["Products"].find_one({"_id": ObjectId(product_id)}, {"price": 1, "qte": 1})
                if not product_response:
                    return {"status": "error", "message": f"Product with ID {product_id} not found."}

                price = Decimal(product_response["price"].to_decimal())
                # Check Quantity in Stock if Available
                available_quantity = product_response.get("qte", 0)
                if quantity > available_quantity:
                    return {
                        "status": "error",
                        "message": f"insufficient stock for product with ID {product_id}. Available: {available_quantity}"
                    }
                # Calculate total price
                total_price += price * quantity

                # Prepare quantity update but do not apply it yet
                product_updates.append((product_id, -quantity))

            order = {
                "customer_id": ObjectId(customer_id),
                "products": products,
                "status": status,
                "order_date": order_date if order_date else datetime.now(),
                "total_price": Decimal128(total_price),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            result = self.db["Orders"].insert_one(order)
            # If order insertion is successful, update product quantities
            for product_id, quantity_change in product_updates:
                update_response = self.update_product_quantity(product_id, quantity_change)
                if update_response["status"] != "success":
                    # Log the failure but continue
                    logger.error(f"Failed to update quantity for product {product_id}: {update_response['message']}")

            logger.info(f"Order created successfully with ID: {result.inserted_id}")
            return {"status": "success", "order_id": str(result.inserted_id)}

        except Exception as err:
            logger.error(f"Error creating order: {err}")
            return {"status": "error", "message": str(err)}

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

            # Apply the projection in the aggregation pipeline
            if projection:
                pipeline.append({"$project": projection})

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
            logger.debug(f"Type of Price({type(product_data['price'])}) ; Qte({type(product['quantity'])})")
            if product_data:
                total_price += product_data["price"] * product["quantity"]
            else:
                logger.warning(f"Product {product['product_id']} not found.")
        return total_price

    # *************************************************************
    # Customer Methods
    # *************************************************************

    def add_customer(self, first_name, last_name, email, phone, address, client_status):
        """
        Adds a new customer to the Customers collection.
        """
        customer = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "is_active": False,
            "client_status": client_status
        }
        return self.add_document("Customers", customer)

    def fetch_customers(self, query=None, projection=None, limit=0, sort=None):
        """
        Fetches customers from the Customers collection.
        """
        return self.fetch_documents("Customers", query, projection, limit, sort)

    def fetch_customer_orders(self, customer_id):
        """
        Fetch all orders for a given customer ID.

        :param customer_id: The ID of the customer.
        :return: List of orders or an error message.
        """
        try:
            projection = {"_id": 1, "order_date": 1, "status": 1, "total_price": 1}
            orders = list(self.db["Orders"].find({"customer_id": ObjectId(customer_id)}, projection))
            logger.info(f"Fetch all orders for customer({customer_id})")
            return {"status": "success", "orders": orders}
        except Exception as e:
            logger.error(f"Error fetching order for Customer({customer_id})\n{e}")
            return {"status": "error", "message": str(e)}

    def delete_customer_and_orders(self, customer_id):
        """
        Deletes a customer and all their associated orders.
        :param customer_id: The ID of the customer to delete.
        :return: A dictionary with the result of the operation.
        """
        try:
            # Convert customer_id to ObjectId
            customer_id = ObjectId(customer_id)

            # Delete associated orders
            order_result = self.db["Orders"].delete_many({"customer_id": customer_id})

            # Delete the customer
            customer_result = self.db["Customers"].delete_one({"_id": customer_id})

            if customer_result.deleted_count > 0:
                logger.info(f"Customer {customer_id} deleted successfully.")
                logger.info(f"Deleted {order_result.deleted_count} associated orders.")
                return {
                    "status": "success",
                    "message": f"Customer and {order_result.deleted_count} associated orders deleted successfully."
                }

            logger.warning(f"Customer {customer_id} not found.")
            return {"status": "error", "message": "Customer not found."}

        except Exception as err:
            logger.error(f"Error deleting customer and orders: {err}")
            return {"status": "error", "message": str(err)}


if __name__ == "__main__":
    # Example usage
    handler = MongoDBHandler()

    # client = pymongo.MongoClient('mongodb://localhost:27017')
    # db = client['elSel3a']
    # print(db.list_collection_names())

    def print_terminal(response):
        if response['status'] == 'success':
            for document in response['documents']:
                for key, value in document.items():
                    print(f"{key} ==> {value}")
                print('-' * 30)

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
    #
    # === FETCH ALL PRODUCTS ===
    # response = handler.fetch_documents('Producs', projection={"name": 1, "price": 1, "priceType": {"$type": "$price"}}, limit=5, sort=[("price", -1)])
    # print_terminal(response)

    # === Fetch one product by its ObjectId ===
    # product_id = "6753810bbbe65eb9e57627b0"  # Replace with a valid _id from your database
    # response = handler.fetch_documents(
        # collection_name="Products",
        # query={"_id": ObjectId(product_id)},
        # projection={"name": 1, "ref": 1, "description": 1, "price": 1, "qte": 1, "_id": 0}
    # )
    # print(response['documents'][0])
    # print_terminal(response)

    # **************************************************************************
    #   Orders
    # ******************
    # Create an order
    # products = [
        # {"product_id": ObjectId("6753810bbbe65eb9e57627ad"), "quantity": 2},
        # {"product_id": ObjectId("67537018273fa34dbd8983b5"), "quantity": 3},
        # {"product_id": ObjectId("6753810bbbe65eb9e57627b3"), "quantity": 4},
    # ]
    # response = handler.create_order(customer_id=ObjectId("67571d3ae8b50300ac73202f"), products=products)
    # print(response)

    # === FETCH ORDERS
    # projection = {"_id": 0, "customer_id": 0}
    # response = handler.fetch_orders(limit=3, sort=[("order_date", -1)])
    # response = handler.fetch_orders_with_customer_names(projection=projection)
    # for res in response['orders']:
        # for key, value in res.items():
            # print(f'{key} :: {value}')
        # print('-' * 30)
    # print(response)

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
    #
    # FETCH ALL CUSTOMERS
    # -------------------
    response = handler.fetch_customers(sort=[("created_at", -1)], limit=5)
    print_terminal(response)
    #
    # FETCH ONE CUSTOMER
    # customer_id = "67588f3bbfb3c20aca9acc12"  # Example ID
    # response = handler.fetch_documents(
        # collection_name="Customers",
        # query={"_id": ObjectId(customer_id)},
        # projection={}
    # )
    # print_terminal(response)
    #
    # Update Customer
    # response = handler.update_customer(customer_id, updates={"phone": "01198765432"})
    # print(response)
    #
    # Delete a customer
    #
    # response = handler.delete_customer(customer_id="6489cde8a1d4b1d6e2f7a456")
    # print(response)

    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["elSel3a"]
    # products_collection = db["Products"]

    products = [
        {
            "name": "حاسوب محمول",
            "ref": "LAP001",
            "description": "حاسوب محمول مع شاشة 15 بوصة",
            "price": Decimal128("85000"),
            "qte": 10,
            "category": "إلكترونيات",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "هاتف ذكي",
            "ref": "PHN002",
            "description": "هاتف ذكي مزود بكاميرا 48 ميغابيكسل",
            "price": Decimal128("45000"),
            "qte": 25,
            "category": "هواتف",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "سماعات بلوتوث",
            "ref": "HDP003",
            "description": "سماعات أذن لاسلكية",
            "price": Decimal128("15000"),
            "qte": 40,
            "category": "إلكترونيات",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "طابعة",
            "ref": "PRT004",
            "description": "طابعة ليزر متعددة الوظائف",
            "price": Decimal128("30000"),
            "qte": 5,
            "category": "أجهزة مكتبية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "ثلاجة صغيرة",
            "ref": "FRG005",
            "description": "ثلاجة صغيرة بحجم 120 لتر",
            "price": Decimal128("65000"),
            "qte": 8,
            "category": "أجهزة منزلية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "فرن كهربائي",
            "ref": "OVN006",
            "description": "فرن كهربائي مزود بوظيفة الحمل الحراري",
            "price": Decimal128("40000"),
            "qte": 6,
            "category": "أجهزة منزلية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "كتاب 'برمجة بايثون'",
            "ref": "BK007",
            "description": "كتاب شامل عن أساسيات البرمجة بلغة بايثون",
            "price": Decimal128("3000"),
            "qte": 20,
            "category": "كتب",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "كرسي مكتب",
            "ref": "CHA008",
            "description": "كرسي مكتب مريح بعجلات",
            "price": Decimal128("12000"),
            "qte": 15,
            "category": "أثاث",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "ماكينة قهوة",
            "ref": "COF009",
            "description": "ماكينة لتحضير القهوة مزودة بخاصية الإسبريسو",
            "price": Decimal128("12000"),
            "qte": 7,
            "category": "أجهزة منزلية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "جهاز تكييف",
            "ref": "AC010",
            "description": "جهاز تكييف سعة 12000 وحدة",
            "price": Decimal128("85000"),
            "qte": 4,
            "category": "أجهزة منزلية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "حاسوب مكتبي",
            "ref": "DESK011",
            "description": "حاسوب مكتبي مزود بمعالج i7",
            "price": Decimal128("125000"),
            "qte": 6,
            "category": "إلكترونيات",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "كاميرا مراقبة",
            "ref": "CAM012",
            "description": "كاميرا مراقبة بدقة 1080p مع خاصية الرؤية الليلية",
            "price": Decimal128("25000"),
            "qte": 10,
            "category": "إلكترونيات",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        },
        {
            "name": "ميكروويف",
            "ref": "MW013",
            "description": "ميكروويف مزود بخاصية إذابة التجميد",
            "price": Decimal128("35000"),
            "qte": 5,
            "category": "أجهزة منزلية",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_active": True
        }
    ]

    customers = [
        {
            "first_name": "يوسف",
            "last_name": "حداد",
            "email": "youssef.haddad@example.com",
            "phone": "0555544332",
            "address": "حي الأخوة بوحجر، مستغانم",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "سهيلة",
            "last_name": "بن غبريط",
            "email": "souhaila.benghabrit@example.com",
            "phone": "0667788990",
            "address": "شارع جيش التحرير الوطني، البليدة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "عبد الرحمن",
            "last_name": "لعمامرة",
            "email": "abdelrahman.laamamra@example.com",
            "phone": "0776655432",
            "address": "حي المستقبل، تيزي وزو",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "رانية",
            "last_name": "بوخاري",
            "email": "rania.boukhari@example.com",
            "phone": "0544332211",
            "address": "حي الزيتون، الشلف",
            "is_active": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "مراد",
            "last_name": "بن شيخ",
            "email": "mourad.bencheikh@example.com",
            "phone": "0567891234",
            "address": "شارع المجاهدين، ورقلة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "محمد",
            "last_name": "بن أحمد",
            "email": "mohamed.benahmed@example.com",
            "phone": "0551123456",
            "address": "شارع 1 نوفمبر، الجزائر العاصمة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "فاطمة",
            "last_name": "بوعبد الله",
            "email": "fatima.bouabdallah@example.com",
            "phone": "0556654321",
            "address": "حي الزيتون، وهران",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "عبد القادر",
            "last_name": "سالمي",
            "email": "abdelkader.salmi@example.com",
            "phone": "0772233445",
            "address": "حي النصر، قسنطينة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "نسرين",
            "last_name": "عمراني",
            "email": "nesrine.omrani@example.com",
            "phone": "0667788990",
            "address": "حي باب الوادي، الجزائر العاصمة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "أحمد",
            "last_name": "زيتوني",
            "email": "ahmed.zeitouni@example.com",
            "phone": "0544332211",
            "address": "حي الورود، سطيف",
            "is_active": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "first_name": "ليلى",
            "last_name": "بوشيخي",
            "email": "leila.bouchikhi@example.com",
            "phone": "0561123344",
            "address": "شارع الأمير عبد القادر، عنابة",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    # Insert products
    product_result = db["Products"].insert_many(products)
    print(f"Inserted {len(product_result.inserted_ids)} products.")

    # Insert customers
    customer_result = db["Customers"].insert_many(customers)
    print(f"Inserted {len(customer_result.inserted_ids)} customers.")

    # Update all prices to Decimal128
    # for product in products_collection.find({"price": {"$type": "string"}}):
        # price_as_decimal = Decimal128(Decimal(str(product["price"])))
        # products_collection.update_one(
            # {"_id": product["_id"]},
            # {"$set": {"price": price_as_decimal}}
        # )
    # print("All prices updated to Decimal128.")

    # products = products_collection.find()
    # for product in products:
        # for key, value in product.items():
            # print(f"{key}, {type(value).__name__}")
        # print('-' * 50)
