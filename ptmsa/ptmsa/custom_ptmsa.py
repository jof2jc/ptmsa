# -*- coding: utf-8 -*-
# Copyright (c) 2015, jonathan and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate
from collections import defaultdict

# test_records = frappe.get_test_records('testdoctype')

def set_purchase_receipt_per_billed(self, method):
	if self.docstatus == 1 or self.docstatus == 2:
		for d in self.items:
			if d.purchase_receipt:
				ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabPurchase Receipt Item`
				where parent=%s""", (d.purchase_receipt))[0][0])
				print 'ref_doc_qty=' + cstr(ref_doc_qty)
	
				billed_qty = flt(frappe.db.sql("""SELECT ifnull(sum(qty), 0) as billed_qty FROM `tabPurchase Invoice` si INNER JOIN `tabPurchase Invoice Item` it 
						ON si.name=it.parent where si.docstatus=1 and it.purchase_receipt=%s and si.name=%s""", (d.purchase_receipt, self.name))[0][0])
				#billed_qty = 100
				print 'billed_qty=' + cstr(billed_qty)

				per_billed = ((ref_doc_qty if billed_qty > ref_doc_qty else billed_qty)\
					/ ref_doc_qty)*100
				print 'per_billed=' + cstr(per_billed)

				doc = frappe.get_doc("Purchase Receipt", d.purchase_receipt)

				#frappe.throw(_("doc.per_billed = {0} per_billed = {1}").format(doc.per_billed, per_billed))

				if doc.per_billed < 100:
					doc.db_set("per_billed", "100")
					doc.set_status(update=True)

				if self.docstatus == 2:
					doc.db_set("per_billed", "0")
					doc.set_status(update=True)

def set_delivery_status_per_billed(self, method):
	#frappe.msgprint("hi..")
	if self.docstatus == 1 or self.docstatus == 2:
		for d in self.items:
			if d.delivery_note:
				ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabDelivery Note Item`
				where parent=%s""", (d.delivery_note))[0][0])
				print 'ref_doc_qty=' + cstr(ref_doc_qty)
	
				billed_qty = flt(frappe.db.sql("""SELECT ifnull(sum(qty), 0) as billed_qty FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` it 
						ON si.name=it.parent where si.docstatus=1 and it.delivery_note=%s and si.name=%s""", (d.delivery_note, self.name))[0][0])
				#billed_qty = 100
				print 'billed_qty=' + cstr(billed_qty)

				per_billed = ((ref_doc_qty if billed_qty > ref_doc_qty else billed_qty)\
					/ ref_doc_qty)*100
				print 'per_billed=' + cstr(per_billed)

				doc = frappe.get_doc("Delivery Note", d.delivery_note)

				#frappe.msgprint(_("doc.per_billed = {0} per_billed = {1}").format(doc.per_billed, per_billed))

				if doc.per_billed < 100:
					doc.db_set("per_billed", "100")
					doc.set_status(update=True)

				if self.docstatus == 2:
					doc.db_set("per_billed", "0")
					doc.set_status(update=True)
				

def patch_delivery_status_per_billed():
	_list = frappe.db.sql ("""SELECT it.delivery_note, ifnull(sum(qty), 0) as billed_qty FROM `tabSales Invoice` si INNER JOIN `tabSales Invoice Item` it 
			ON si.name=it.parent where si.docstatus=1 and it.delivery_note <> '' group by it.delivery_note""", as_dict=1)
	print _list

	for d in _list:
		print 'd.delivery_note=' + cstr(d.delivery_note)
		ref_doc_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabDelivery Note Item`
				where parent=%s""", (d.delivery_note))[0][0])
		print 'ref_doc_qty=' + cstr(ref_doc_qty)

		#billed_qty = flt(frappe.db.sql("""select ifnull(sum(qty), 0) from `tabSales Invoice Item` 
				#where delivery_note=%s and docstatus=1""", (d.delivery_note))[0][0])
		print 'd.billed_qty=' + cstr(d.billed_qty)

		per_billed = ((ref_doc_qty if d.billed_qty > ref_doc_qty else d.billed_qty)\
				/ ref_doc_qty)*100
		print 'per_billed=' + cstr(per_billed)

		doc = frappe.get_doc("Delivery Note", d.delivery_note)

		if doc.per_billed < 100:
			doc.db_set("per_billed", per_billed)
			doc.set_status(update=True)
