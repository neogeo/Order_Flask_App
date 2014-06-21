#!flask/bin/python
import os
import unittest

from flask import json
from config import basedir
from app import app, db
from app.models import ProductType

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def createDefaultProductType(self):
		sku = "ProductType"
		inventory = 10
		price = "$5.50"
		body = dict(sku=sku, inventory=inventory, price=price)
		
		response = self.app.post('/productType', data=json.dumps(body), content_type='application/json')
		pt_id = json.loads(response.data).get('id')
		return pt_id

	def createProductType(self, sku, inventory, price):
		body = dict(sku=sku, inventory=inventory, price=price)
		
		response = self.app.post('/productType', data=json.dumps(body), content_type='application/json')
		pt_id = json.loads(response.data).get('id')
		return pt_id

	def createDefaultOrder(self):
		pt_sku="ProductType"
		pt_id = self.createProductType(pt_sku, 10, "$1.00")

		#when an order is created
		lines = [dict(sku=pt_sku, quantity= 5 )]
		shippingAddress = {
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
		}
		billingAddress = { 'same':'true' }
		
		body = dict(
			shippingAddress=shippingAddress,
			billingAddress=billingAddress,
			lines=lines
		)

		response = self.app.post('/order', data=json.dumps(body), content_type='application/json')
		o_id = json.loads(response.data).get('id')
		return o_id

	'''
		---------------------
		PRODUCT TYPE ENDPOINT TESTS
		---------------------
	'''
	def test_ProductTypeCreate(self):
		#given no product types exist
		result = self.app.get('/productType')
		resultJson = json.loads(result.data)
		
		assert len(resultJson.get('data')) == 0

		#when the create product type endpond is call
		sku = "ProductType"
		inventory = 10
		price = "$5.50"
		body = dict(
			sku=sku,
			inventory=inventory,
			price=price
		)
		
		response = self.app.post('/productType', data=json.dumps(body), content_type='application/json')

		#then the call succeeds and product type exists
		assert response.status_code == 201
		result = json.loads(response.data)
		assert result.get('id')
		assert result.get('sku') == sku
		assert result.get('inventory') == inventory
		assert result.get('price') == price
	
	def test_ProductTypeGet(self):
		#given a product type
		sku = "ProductType"
		inventory = 10
		price = "$5.50"
		body = dict(
			sku=sku,
			inventory=inventory,
			price=price
		)
		
		response = self.app.post('/productType', data=json.dumps(body), content_type='application/json')
		pt_id = json.loads(response.data).get('id')

		#when the product type is retrieved by id
		response = self.app.get('/productType/'+str(pt_id))

		#then the prodcut type is returned
		assert response.status_code == 200
		result = json.loads(response.data)
		assert result.get('id') == pt_id
		assert result.get('sku') == sku
		assert result.get('inventory') == inventory
		assert result.get('price') == price

	def test_ProductTypeUpdate(self):
		#given a product type
		pt_id = self.createDefaultProductType()

		#when it is updated
		updated_sku = "NewProductType"
		updated_inventory = 20
		updated_price = "$10.50"
		updated_body = dict(
			sku=updated_sku,
			inventory=updated_inventory,
			price=updated_price
		)
		response = self.app.put('/productType/'+str(pt_id), data=json.dumps(updated_body), content_type='application/json')
		
		#then update succeeds
		assert response.status_code == 200
		result = json.loads(response.data)
		assert result.get('id') == pt_id
		assert result.get('sku') == updated_sku
		assert result.get('inventory') == updated_inventory
		assert result.get('price') == updated_price

	def test_ProductTypeDelete(self):
		#given a product type
		pt_id = self.createDefaultProductType()

		#delete the product type
		response = self.app.delete('/productType/'+str(pt_id), content_type='application/json')
		
		#then the product type is deleted
		assert response.status_code == 200
		result = json.loads(response.data)
		assert result.get('id') == str(pt_id)
		#verify it does not exist
		result = self.app.get('/productType')
		resultJson = json.loads(result.data)
		
		assert len(resultJson.get('data')) == 0

	'''
		---------------------
		ORDER ENDPOINT TESTS
		---------------------
	'''

	def test_OrderGetAll(self):
		#given no orders exist
		#when call get all orders
		response = self.app.get('/order')
		result = json.loads(response.data)
		
		#then no orders are turned
		assert len(result.get('data')) == 0

	def test_OrderCreate(self):
		#given a product type with inventory
		pt_sku="ProductType"
		pt_id = self.createProductType(pt_sku, 10, "$1.00")

		#when an order is created
		lines = [dict(sku=pt_sku, quantity= 5 )]
		shippingAddress = {
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
		}
		billingAddress = { 'same':'true' }
		
		body = dict(
			shippingAddress=shippingAddress,
			billingAddress=billingAddress,
			lines=lines
		)

		response = self.app.post('/order', data=json.dumps(body), content_type='application/json')
		
		#then the call succeeds and product type exists
		assert response.status_code == 201
		result = json.loads(response.data)
		assert result.get('id')
		assert result.get('total') == "$5.00"
		assert len(result.get('lines')) == 1


	def test_OrderGetAllExists(self):
		#given two orders exist
		self.createDefaultOrder();
		self.createDefaultOrder();

		#when call to get all orders
		response = self.app.get('/order')
		result = json.loads(response.data)
		
		#then two orders are returned
		assert len(result.get('data')) == 2

	
			
if __name__ == '__main__':
	unittest.main()