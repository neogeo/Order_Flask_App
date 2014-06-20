from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers

'''---------------------------------------------
		Order Endpoints
   ---------------------------------------------'''

'''
Create an order. Returns the id, total and price per sku; along with the given information 
lines - required - at least 1 sku is required. 
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaing
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
@app.route('/order', methods=['POST'])
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
	total = 0
	for line in lines:
		#validate line params
		sku = line.get('sku')
		quantity = int(line.get('quantity'))
		if (not sku) or (not quantity):
			return jsonify(error="Required data on line not set, specify both sku and quantity"), 400
		
		#check if product sku exists
		productType = models.ProductType.query.filter_by(sku=sku).first()
		if not productType:
			return jsonify(error="Product sku not found for sku: "+sku), 400
		
		#add up total
		lineTotal = productType.price * quantity
		total = total + lineTotal

		product = models.Product(quantity, productType, order)
		#only need to add the product to the session. SQLAlchemy is smart enough to also add the DB relationships during commit
		db.session.add(product)
		
		#add price for response
		line['price'] = helpers.convertIntToFormattedPrice( lineTotal )

	#set total
	order.total = total
	

	try:
		db.session.commit()
	#check for errors
	except exc.SQLAlchemyError as err:
		return jsonify(error="Failed to create Order"), 400

	return jsonify(formatOrderForResponse(order, lines)), 201

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
