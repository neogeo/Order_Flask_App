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

	def createProductType(self):
		sku = "ProductType"
		inventory = 10
		price = "$5.50"
		body = data=dict(
			sku=sku,
			inventory=inventory,
			price=price
		)
		
		response = self.app.post('/productType', data=json.dumps(body), content_type='application/json')
		pt_id = json.loads(response.data).get('id')
		return pt_id

	def test_ProductTypeCreate(self):
		#given no product types exist
		result = self.app.get('/productType')
		resultJson = json.loads(result.data)
		
		assert len(resultJson.get('data')) == 0

		#when the create product type endpond is call
		sku = "ProductType"
		inventory = 10
		price = "$5.50"
		body = data=dict(
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
		body = data=dict(
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
		pt_id = self.createProductType()

		#when it is updated
		updated_sku = "NewProductType"
		updated_inventory = 20
		updated_price = "$10.50"
		updated_body = data=dict(
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
		pt_id = self.createProductType()

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

if __name__ == '__main__':
	unittest.main()