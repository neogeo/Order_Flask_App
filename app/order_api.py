from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers
from flask_sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse
from app import register
'''---------------------------------------------
		Order Endpoints
   ---------------------------------------------'''

'''
return all orders, (becuase this could be slow for very large data sets, use the 'limit' query param)
limit - optional query param - limit the amount of results returned
/order?limit=10
'''
@register('/order', method="GET",
notes="return all orders, (becuase this could be slow for very large data sets, use the 'limit' query param)<br>\
limit - optional query param - limit the amount of results returned",
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
    ApiErrorResponse(200, 'Array of orders')
  ],
  nickname="order_api")
#@app.route('/order', methods=['GET'])
def getAllOrders():
	limit = request.args.get('limit')
	if limit:
		#limit results
		orders = models.Order.query.limit(limit).all()	
	else:
		#return all
		orders = models.Order.query.all()

	return jsonify(data = map(formatOrderForGetResponse, orders)), 200

'''
return an Order by id
'''
@register('/order/<id>', method="GET",
	notes='return an Order by id',
  parameters=[
    ApiParameter(
        name="id",
        description="The id of the order",
        required=True,
        dataType="str",
        paramType="path",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The Order object"),
    ApiErrorResponse(400, "Could not find Order")
  ],
  nickname="order_api")
#@app.route('/order/<id>', methods=['GET'])
def getOrder(id):
	order = models.Order.query.get(id)
	if order:
		return jsonify(formatOrderForGetResponse(order)), 200
	else:
		return jsonify(error="Could not find Order"), 400


'''
Create an order. Returns the id, total and price per sku; along with the given information 
lines - required - at least 1 sku is required. 
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning
				   sku - required - the sku of the product type to order
				   quantity - required - the amount of this product type to order
billingAddress - "same:true" can be used to indicate the same address information as shippingAddres (e.g. "billingAddress":{"same":"true"} )

request:
{
	"shippingAddress" : {
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
	},
	"billingAddress" : {
		"same":"true"
			OR
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
   	},
	"lines" : [
      {
	      "sku":"hot dogs",
	      "quantity":"10"
      },
      {
	      "sku":"markers",
	      "quantity":"5"
      }
  	]
}

response:{
	id:order_id,
	total: "$15.00",
	"shippingAddress":{...},
	"billingAddress":{...},
	"lines":[{"price":...}]
}
'''
@register('/order', method="POST",
	notes='Create an order. Returns the id, total and price per sku; along with the given information <br>\
lines - required - at least 1 sku is required. <br>\
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning<br>\
				   sku - required - the sku of the product type to order<br>\
				   quantity - required - the amount of this product type to order<br>\
billingAddress - "same:true" can be used to indicate the same address information as shippingAddres (e.g. "billingAddress":{"same":"true"} )<br>\
<br>\
request:<br>\
{<br>\
	"shippingAddress" : {<br>\
		"street" : "6th",<br>\
		"city" : "Austin",<br>\
		"state" : "Texas",<br>\
		"zip" : "777777"<br>\
	},<br>\
	"billingAddress" : {<br>\
		"same":"true"<br>\
			OR<br>\
		"street" : "6th",<br>\
		"city" : "Austin",<br>\
		"state" : "Texas",<br>\
		"zip" : "777777"<br>\
   	},<br>\
	"lines" : [<br>\
      {<br>\
	      "sku":"hot dogs",<br>\
	      "quantity":"10"<br>\
      },<br>\
      {<br>\
	      "sku":"markers",<br>\
	      "quantity":"5"<br>\
      }<br>\
  	]<br>\
}<br>\
<br>\
response:{<br>\
	id:order_id,<br>\
	total: "$15.00",<br>\
	"shippingAddress":{...},<br>\
	"billingAddress":{...},<br>\
	"lines":[{"price":...}]<br>\
}',
  parameters=[
    ApiParameter(
        name="id",
        description="The id of the order",
        required=True,
        dataType="str",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(201, "The Order object"),
    ApiErrorResponse(400, "Failed to create order")
  ],
  nickname="order_api")
#@app.route('/order', methods=['POST'])
def createOrder():
	#parse json
	requestJson = request.get_json(force=True)

	#validate params
	shippingAddress = requestJson.get('shippingAddress')
	billingAddress = requestJson.get('billingAddress')
	lines = requestJson.get('lines')

	if (not shippingAddress) or (not billingAddress) or (not lines):
		return jsonify(error="One or more required data is not set"), 400
	if len(lines)<1:
		return jsonify(error="Required data not set, specify at least 1 product sku"), 400

	#create an order
	order = models.Order()
	#check for 'same' billing address
	sameAddress = billingAddress.get('same') if billingAddress.get('same') else "false"

	order.setShippingAndBillingAddress(shippingAddress, billingAddress, sameAddress)

	#for each line item
	for line in lines:
		#validate line params
		sku = line.get('sku')
		quantity = line.get('quantity')
		if (not sku) or (not quantity):
			return jsonify(error="Required data on line not set, specify both sku and quantity"), 400
		quantity = int(quantity)

		#check if product sku exists
		productType = models.ProductType.query.filter_by(sku=sku).first()
		#check and update inventory
		if not productType:
			return jsonify(error="Product sku not found for sku: "+sku), 400
		elif not productType.verifyAndUpdateInventory(quantity):
			return jsonify(error="Not enough inventory for sku: "+sku), 400

		#add up total
		lineTotal = productType.price * quantity
		order.increaseTotal(lineTotal)

		product = models.Product(quantity, productType, order)
		#only need to add the product to the session. SQLAlchemy is smart enough to also add the DB relationships during commit
		db.session.add(product)
		
		#add price for response
		line['price'] = helpers.convertIntToFormattedPrice( lineTotal )

	try:
		db.session.commit()
	#check for errors
	except exc.SQLAlchemyError as err:
		return jsonify(error="Failed to create Order"), 400

	return jsonify(formatOrderForResponse(order, lines)), 201

'''
Update an orders shipping or billing address. Use the /order/<id>/lineItems endpoints to update the line items
request:
{
	"shippingAddress" : {
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
	},
	"billingAddress" : {
		"street" : "6th",
		"city" : "Austin",
		"state" : "Texas",
		"zip" : "777777"
   	}
}
'''
@register('/order', method="PUT",
	notes = ' Update an orders shipping or billing address. Use the /order/<id>/lineItems endpoints to update the line items.<br>\
request:<br>\
{<br>\
	"shippingAddress" : {<br>\
		"street" : "6th",<br>\
		"city" : "Austin".<br>\
		"state" : "Texas".<br>\
		"zip" : "777777"<br>\
	},<br>\
	"billingAddress" : {<br>\
		"street" : "6th",<br>\
		"city" : "Austin",<br>\
		"state" : "Texas",<br>\
		"zip" : "777777"<br>\
   	}<br>\
}',
  parameters=[
    ApiParameter(
        name="body",
        description="contains shippingAddress or billingAddress",
        required=False,
        dataType="object",
        paramType="form",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The Order object"),
    ApiErrorResponse(400, "Failed to update Order")
  ],
  nickname="order_api")
#@app.route('/order/<id>', methods=['PUT'])
def updateOrder(id):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	shippingAddress = requestJson.get('shippingAddress')
	billingAddress = requestJson.get('billingAddress')

	order = models.Order.query.get(id)
	#update
	if order:
		try:
			if order and shippingAddress:
				order.setShippingAddress(shippingAddress)

			if order and billingAddress:
				order.setBillingAddress(billingAddress)
		
			db.session.commit()
		except exc.SQLAlchemyError as err:
			return jsonify(error="Failed to update Order"), 400

		#return result of any updates
		return jsonify(formatOrderForGetResponse(order)), 200
	else:
		return jsonify(error="Failed to find given Order"), 400

'''
delete an order:
/order/id
'''
@register('/order/<id>', method="DELETE",
	notes='Delete an order',
  parameters=[
    ApiParameter(
        name="id",
        description="The id of the order",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, ""),
    ApiErrorResponse(400, "Failed to delete order")
  ],
  nickname="order_api")
#@app.route('/order/<id>', methods=['DELETE'])
def deleteOrder(id):
	order = models.Order.query.get(id)

	if order:
		#delete
		#each assicated product
		for product in order.products:
			db.session.delete(product)

		db.session.delete(order)
		try:
			db.session.commit()
			return jsonify(id=id), 200
		except exc.SQLAlchemyError as err:
			pass

	return jsonify(error="Failed to delete order"), 400

#format a Order model for a response from the API
def formatOrderForResponse(order, lines):
	shippingAddress = {
		'street' : order.shipping_street,
		'city' : order.shipping_state,
		'state' : order.shipping_city,
		'zip' : order.shipping_zipcode
	}
	billingAddress = {
		'street' : order.billing_street,
		'city' : order.billing_state,
		'state' : order.billing_city,
		'zip' : order.billing_zipcode
	}

	return { 
		'id':order.id, 
		'total':helpers.convertIntToFormattedPrice(order.total),
		'shippingAddress':shippingAddress,
		'billingAddress':billingAddress,
		'lines': lines
	}

#format a Order model for a response from the API
def formatOrderForGetResponse(order):
	shippingAddress = {
		'street' : order.shipping_street,
		'city' : order.shipping_state,
		'state' : order.shipping_city,
		'zip' : order.shipping_zipcode
	}
	billingAddress = {
		'street' : order.billing_street,
		'city' : order.billing_state,
		'state' : order.billing_city,
		'zip' : order.billing_zipcode
	}
	lines = map(formatProductForResponse, order.products)
	return { 
		'id':order.id, 
		'total':helpers.convertIntToFormattedPrice(order.total),
		'shippingAddress':shippingAddress,
		'billingAddress':billingAddress,
		'lines': lines
	}

def formatProductForResponse(product):
	productType = models.ProductType.query.get(product.product_type_id)
	
	price = helpers.convertIntToFormattedPrice( productType.price )
	return { 'quantity':product.quantity, 'price':price, 'sku':productType.sku}
