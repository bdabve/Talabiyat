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
    "client_status": "درجة الثقة"
}

status_mapping = {
    "قيد الانتظار": "pending",
    "مؤكد": "confirmed",
    "تم الشحن": "shipped",
    "تم التوصيل": "delivered",
    "ملغي": "cancelled",
    # customer status mapping
    "موثوق": "trusted",
    "عميل جيد": "good_client",
    "عميل سيئ": "bad_client",
}

status_mapping_en = {
    "pending": "قيد الانتظار",
    "confirmed": "مؤكد",
    "shipped": "تم الشحن",
    "delivered": "تم التوصيل",
    "cancelled": "ملغي",
    # this for customer status
    True: "مفعل",
    False: "غير مفعل",
    "trusted": "موثوق",
    "good_client": "عميل جيد",
    "bad_client": "عميل سيئ",
}

prod_headers = ["أيد", "الاسم", "المرجع", "الوصف", "السعر", "الكمية", "الفئة"]
customer_headers = ["إيد", "الإسم", "اللقب", "الهاتف", "إيمايل", "العنوان", "مفعل", "درجة الثقة"]
order_headers = ["أيد", "المشتري", "التاريخ", "الوضعية", "المجموع"]
