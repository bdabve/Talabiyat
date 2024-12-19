#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# author        : el3arbi bdabve@gmail.com
# created       :
# desc          : this file containe the Arabic Mapping
# ----------------------------------------------------------------------------

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
    "customer_name": "المشتري",
    # customers
    "first_name": "الإسم",
    "last_name": "اللقب",
    "email": "إيمايل",
    "phone": "الهاتف",
    "address": "العنوان",
    True: "مفعل",
    False: "غير مفعل",
}

order_status_mapping = {
    "قيد الانتظار": "pending",
    "مؤكد": "confirmed",
    "تم الشحن": "shipped",
    "تم التوصيل": "delivered",
    "ملغي": "cancelled",
}

order_status_mapping_en = {
    "pending": "قيد الانتظار",
    "confirmed": "مؤكد",
    "shipped": "تم الشحن",
    "delivered": "تم التوصيل",
    "cancelled": "ملغي",
    # this for customer status
    True: "مفعل",
    False: "غير مفعل",
}

prod_headers = ["أيد", "الاسم", "المرجع", "الوصف", "السعر", "الكمية", "الفئة"]
customer_headers = ["إيد", "الإسم", "اللقب", "الهاتف", "إيمايل", "العنوان", "مفعل"]
order_headers = ["أيد", "المشتري", "التاريخ", "الوضعية", "المجموع"]
