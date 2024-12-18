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
    "قيد التحضير": "preparing",
    "تم الشحن": "shipped",
    "في الطريق للتوصيل": "out_for_delivery",
    "تم التوصيل": "delivered",
    "منجز": "completed",
    "ملغي": "cancelled",
    "فشل": "failed"
}

order_status_mapping_en = {
    "pending": "قيد الانتظار",
    "confirmed": "مؤكد",
    "preparing": "قيد التحضير",
    "shipped": "تم الشحن",
    "out_for_delivery": "في الطريق للتوصيل",
    "delivered": "تم التوصيل",
    "completed": "منجز",
    "cancelled": "ملغي",
    "failed": "فشل",
    # this for customer status
    True: "مفعل",
    False: "غير مفعل",
}

prod_headers = ["أيد", "الاسم", "المرجع", "الوصف", "السعر", "الكمية", "الفئة"]
customer_headers = ["إيد", "الإسم", "اللقب", "الهاتف", "إيمايل", "العنوان", "مفعل"]
order_headers = ["أيد", "المشتري", "التاريخ", "الوضعية", "المجموع"]
