from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers


'''---------------------------------------------
		ProductType Endpoints
   ---------------------------------------------'''
'''
return all product types, (becuase this could be slow for very large data sets, use the 'limit' query param)
limit - optional query param - limit the amount of results returned
/productType?limit=10
'''
@app.route('/productType', methods=['GET'])
def getAllProductTypes():
	limit = request.args.get('limit')
	if limit:
		#limit results
		productTypes = models.ProductType.query.limit(limit).all()	
	else:
		#return all
		productTypes = models.ProductType.query.all()

	return jsonify(data = map(formatProductTypeForResponse, productTypes)), 200

'''
return an ProductType by id
'''
@app.route('/productType/<id>', methods=['GET'])
def getProductType(id):
	productType = models.ProductType.query.get(id)
	if productType:
		return jsonify(formatProductTypeForResponse(productType)), 200
	else:
		return jsonify(error="Could not find ProductType"), 400

'''
create a product type:
sku - required - sku of product
price - required - price of product
inventory - optional - starting inventory amount

{
"sku":"Bunnies Large",
"inventory":"100",
"price":"$10.51"
}
'''
@app.route('/productType', methods=['POST'])
def createProductType():
	#parse json
	requestJson = request.get_json(force=True)

	#validate params
	sku = requestJson.get('sku')
	inventory = requestJson.get('inventory')
	price = requestJson.get('price')

	if (not sku) or (not price):
		return jsonify(error="One or more required data is not set"), 400
	if not inventory:
		inventory = 0
	#convert dollar formatted price to number of cents
	price = helpers.parsePrice(price)

	productType = models.ProductType(sku, inventory, price)

	db.session.add(productType)

	try:
		db.session.commit()
	#check for errors, uniquness constratint
	except exc.IntegrityError as err:
		return jsonify(error="Duplicate ProductType name not allowed"), 400
	except exc.SQLAlchemyError as err:
		return jsonify(error="Failed to create ProductType"), 400
	

	#return newly created productType
	return jsonify(formatProductTypeForResponse(productType)), 201

'''
update a productType, only update the inventory or price for now
inventory - optional - inventory to ADD
price - optional - new price

{
	id:2,
	inventory:20,
	price:$20.00
}
'''
@app.route('/productType', methods=['PUT'])
@app.route('/productType/<id>', methods=['PUT'])
def updateProductType(id=None):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	prod_id = id if id else requestJson.get('id') #get the id from the URL or body
	inventory = requestJson.get('inventory')
	price = requestJson.get('price')
	if not prod_id:
		return jsonify(error="Required data not set, specify id in URL or body"), 400

	productType = models.ProductType.query.get(prod_id)
	#update
	if productType:
		try:
			if productType and inventory:
				#increase inventory by given amount
				productType.inventory += int(inventory)

			if productType and price:
				#set new price
				productType.price = helpers.parsePrice(price)
		
			db.session.commit()
		except exc.SQLAlchemyError as err:
			return jsonify(error="Failed to update ProductType"), 400

		#return result of any updates
		return jsonify(formatProductTypeForResponse(productType)), 200
	else:
		return jsonify(error="Failed to find given ProductType"), 400

'''
delete a productType:
/productType/id
'''
@app.route('/productType/<id>', methods=['DELETE'])
def deleteProductType(id):
	productType = models.ProductType.query.get(id)

	if productType:
		#delete
		db.session.delete(productType)
		try:
			db.session.commit()
			return jsonify(id=id), 200
		except exc.SQLAlchemyError as err:
			pass

	return jsonify(error="Failed to delete ProductType"), 400

#format a ProductType model for a response from the API
def formatProductTypeForResponse(productType):
	#convert the price to a dollar format
	return {'id':productType.id, 'sku':productType.sku, 'inventory':productType.inventory, 'price':helpers.convertIntToFormattedPrice(productType.price)}
