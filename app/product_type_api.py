from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers
from flask_sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse
from app import register

'''---------------------------------------------
		ProductType Endpoints
   ---------------------------------------------'''
'''
return all product types, (becuase this could be slow for very large data sets, use the 'limit' query param)
limit - optional query param - limit the amount of results returned
/productType?limit=10
'''
@register('/productType', method="GET",
 	notes="return all product types, (becuase this could be slow for very large data sets, use the 'limit' query param)<br>\
 	imit - optional query param - limit the amount of results returned",
  parameters=[
    ApiParameter(
        name="limit",
        description="limit the amount of results returned",
        required=False,
        dataType="str",
        paramType="param",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "Array of Product Types"),
  ],
  nickname="order_api")
#@app.route('/productType', methods=['GET'])
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
@register('/productType/<id>', method="GET",
 	notes="return an ProductType by id",
  parameters=[
    ApiParameter(
        name="id",
        description="The id of the product type",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The prodcut type object"),
    ApiErrorResponse(400, "Could not find ProductType")
  ],
  nickname="order_api")
#@app.route('/productType/<id>', methods=['GET'])
def getProductType(id):
	productType = models.ProductType.query.get(id)
	if productType:
		return jsonify(formatProductTypeForResponse(productType)), 200
	else:
		return jsonify(error="Could not find ProductType"), 400

'''
return a ProductType by sku
sku - required - the sku to return

request:
/productTypeBySku?sku=Hot%20Dogs
'''
@register('/productTypeBySku', method="GET",
 	notes="return a ProductType by sku<br>\
 	sku - required - the sku to return<br>\
<br>\
request:<br>\
/productTypeBySku?sku=Hot%20Dogs",
  parameters=[
    ApiParameter(
        name="sku",
        description="The sku of the product type",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The prodcut type object"),
    ApiErrorResponse(400, "Product sku not found for sku")
  ],
  nickname="order_api")
#@app.route('/productTypeBySku', methods=['GET'])
def getProductTypeBySku():
	#validate query param
	sku = request.args.get('sku')
	if not sku:
		return jsonify(error="Required query param not set, 'sku'"), 400

	productType = models.ProductType.query.filter_by(sku=sku).first()
	if not productType:
		return jsonify(error="Product sku not found for sku: "+sku), 400
	else:
		return jsonify(formatProductTypeForResponse(productType)), 200


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
@register('/productType', method="POST",
 	notes='create a product type:<br>\
sku - required - sku of product<br>\
price - required - price of product<br>\
inventory - optional - starting inventory amount<br>\
<br>\
{<br>\
"sku":"Bunnies Large",<br>\
"inventory":"100",<br>\
"price":"$10.51"<br>\
}',
  parameters=[
    ApiParameter(
        name="body",
        description="The sku of the product type",
        required=True,
        dataType="objec",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(201, "The prodcut type object"),
    ApiErrorResponse(400, "Failed to create ProductType")
  ],
  nickname="order_api")
#@app.route('/productType', methods=['POST'])
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
update a ProductType with a new inventory, sku or price
inventory - optional - inventory amount (this does affect line items that have already been ordered)
price - optional - new price

{
	"sku": "new name",
	"inventory":"20",
	"price":"$20.00"
}
'''
@register('/productType/<id>', method="PUT",
 	notes='update a ProductType with a new inventory, sku or price<br>\
inventory - optional - inventory amount (this does affect line items that have already been ordered)<br>\
price - optional - new price<br>\
<br>\
{<br>\
	"sku": "new name",<br>\
	"inventory":"20",<br>\
	"price":"$20.00"<br>\
}',
  parameters=[
  ApiParameter(
        name="id",
        description="The id of the product type",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False),
    ApiParameter(
        name="body",
        description="The body",
        required=True,
        dataType="obj",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, ""),
    ApiErrorResponse(400, "Failed to update ProductType"),
    ApiErrorResponse(400, "Failed to find given ProductType")

  ],
  nickname="order_api")
#@app.route('/productType/<id>', methods=['PUT'])
def updateProductType(id):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	sku = requestJson.get('sku')
	inventory = requestJson.get('inventory')
	price = requestJson.get('price')

	productType = models.ProductType.query.get(id)
	#update
	if productType:
		try:
			if productType and sku:
				#change sku
				productType.sku = sku

			if productType and inventory:
				#increase inventory by given amount
				productType.inventory = int(inventory)

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
@register('/productType/<id>', method="DELETE",
 	notes="Delete a ProductType",
  parameters=[
    ApiParameter(
        name="id",
        description="The id of the product type",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, ""),
    ApiErrorResponse(400, "Failed to delete ProductType")
  ],
  nickname="order_api")
#@app.route('/productType/<id>', methods=['DELETE'])
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
