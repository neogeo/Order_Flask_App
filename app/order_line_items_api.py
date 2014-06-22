from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers, order_api, product_type_api
from flask_sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse
from app import register
'''
Add lineItems to an existing order. If the line item already exists, then it is ignored (use /order/id/lineItems PUT to upate a line items quantity)
There must also be enough inventory to add the line item
lines - required - at least 1 sku is required. 
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning
				   sku - required - the sku of the product type to order
				   quantity - required - the amount of this product type to order
request:
{
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
'''
@register('/order/<id>/lineItems', method="POST",
	notes='Add lineItems to an existing order. If the line item already exists, then it is ignored (use /order/id/lineItems PUT to upate a line items quantity)<br>\
There must also be enough inventory to add the line item<br>\
lines - required - at least 1 sku is required. <br>\
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning<br>\
				   sku - required - the sku of the product type to order<br>\
				   quantity - required - the amount of this product type to order<br>\
request:<br>\
{<br>\
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
}',
  parameters=[
  ApiParameter(
        name="id",
        description="The id of an order",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False),
    ApiParameter(
        name="body",
        description="The body",
        required=True,
        dataType="str",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The Order object"),
    ApiErrorResponse(400, "Not enough inventory for sku"),
    ApiErrorResponse(400, "Failed to find given Order")
  ],
  nickname="order_api")
#@app.route('/order/<id>/lineItems', methods=['POST'])
def createProductsForOrder(id):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	lines = requestJson.get('lines')

	if not lines:
		return jsonify(error="Required data 'lines' is not set"), 400
	if len(lines)<1:
		return jsonify(error="Required data not set, specify at least 1 product sku"), 400

	order = models.Order.query.get(id)

	if order:
		#get all product types for this order
		productTypes = db.session.query(models.ProductType).join(models.Product).filter(models.Product.order_id == order.id)
	
		#get a list of all the skus, lambdas are so fancy :)
		skus = map((lambda x: x.sku), productTypes)

		#add each line item		
		for line in lines:
			#validate line params
			sku = line.get('sku')
			quantity = line.get('quantity')
			if (not sku) or (not quantity):
				return jsonify(error="Required data on line item not set, specify both sku and quantity"), 400
			quantity = int(quantity)
			
			#check if product sku exists
			productType = models.ProductType.query.filter_by(sku=sku).first()
			#inventory check and update
			if not productType:
				return jsonify(error="Product sku not found for sku: "+sku), 400
			elif not productType.verifyAndUpdateInventory(quantity):
				return jsonify(error="Not enough inventory for sku: "+sku), 400

			#add product to this order if it is not already on the order
			if sku not in skus:
				product = models.Product(quantity, productType, order)
				db.session.add(product)
				#add up total
				lineTotal = productType.price * quantity
				order.increaseTotal(lineTotal)
			#else, order already has product type, ignore	

		try:
			db.session.commit()
			return jsonify(order_api.formatOrderForGetResponse(order)), 200
		except exc.SQLAlchemyError as err:
			return jsonify(error="Failed to add line item to Order"), 400
	else:
		return jsonify(error="Failed to find given Order"), 400


'''
Update the quantities of line items on an order. If the line item does not exist, then it is ignored.
There must also be enough inventory of a line item
lines - required - 
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning
				   sku - required - the sku of the product type to order
				   quantity - required - the new amount of the line item. If set to less than 1, it is ignored (use order/<id>/removeLineItems to remove line items)
request:
{
	"lines" : [
      {
	      "sku":"hot dogs",
	      "quantity":"10"
      },
      {
	      "sku":"markers",
	      "quantity":"6"
      }
  	]
}
'''
@register('/order/<id>/lineItems', method="PUT",
	notes='Update the quantities of line items on an order. If the line item does not exist, then it is ignored.<br>\
There must also be enough inventory of a line item<br>\
lines - required - <br>\
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning<br>\
				   sku - required - the sku of the product type to order<br>\
				   quantity - required - the new amount of the line item. If set to less than 1, it is ignored (use order/<id>/removeLineItems to remove line items)<br>\
request:<br>\
{<br>\
	"lines" : [<br>\
      {<br>\
	      "sku":"hot dogs",<br>\
	      "quantity":"10"<br>\
      },<br>\
      {<br>\
	      "sku":"markers",<br>\
	      "quantity":"6"<br>\
      }<br>\
  	]<br>\
}',
  parameters=[
  ApiParameter(
        name="id",
        description="The id of an order",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False),
    ApiParameter(
        name="body",
        description="The body for update",
        required=True,
        dataType="str",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, "The order"),
    ApiErrorResponse(400, "Not enough inventory for sku"),
    ApiErrorResponse(400, "Failed to update line items on Order")
  ],
  nickname="order_api")
#@app.route('/order/<id>/lineItems', methods=['PUT'])
def updateProductsFromOrder(id):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	lines = requestJson.get('lines')

	if not lines:
		return jsonify(error="Required data 'lines' is not set"), 400
	if len(lines)<1:
		return jsonify(error="Required data not set, specify at least 1 product sku"), 400

	order = models.Order.query.get(id)

	if order:

		for line in lines:
			#validate line params
			sku = line.get('sku')
			quantity = line.get('quantity')
			if (not sku) or (not quantity):
				return jsonify(error="Required data on line item not set, specify both sku and quantity"), 400
			quantity = int(quantity)
			if quantity < 1:
				#ignore, and continue
				continue

			#check if product type sku exists
			productType = models.ProductType.query.filter_by(sku=sku).first()
			#check and update inventory
			if not productType:
				return jsonify(error="Product sku not found for sku: "+sku), 400
			elif not productType.verifyAndUpdateInventory(quantity):
				return jsonify(error="Not enough inventory for sku: "+sku), 400		

			#get the product
			product = models.Product.query.filter_by(order_id=order.id, product_type_id=productType.id ).first()
			#update total, reduce or increase price based on quantity
			order.adjustTotalForQuantity(product.quantity, quantity, productType.price)
			
			#update the product quantity
			product.quantity = quantity
	
		try:
			db.session.commit()
			return jsonify(order_api.formatOrderForGetResponse(order)), 200
		except exc.SQLAlchemyError as err:
			return jsonify(error="Failed to update line items on Order"), 400

	else:
		return jsonify(error="Failed to find given Order"), 400

'''
Remove lineItems from an existing order. If the line item does not exist, then it is ignored 
lines - required - 
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning
				   sku - required - the sku of the product type to order
request:
{
	"lines" : [
      {
	      "sku":"hot dogs"
      },
      {
	      "sku":"markers"
      }
  	]
}
'''
@register('/order/<id>/removeLineItems', method="DELETE",
	notes='Remove lineItems from an existing order. If the line item does not exist, then it is ignored <br>\
lines - required - <br>\
				   The sku of a given Product must already exist, and there must also be available inventory of that sku remaning<br>\
				   sku - required - the sku of the product type to order<br>\
request:<br>\
{<br>\
	"lines" : [<br>\
      {<br>\
	      "sku":"hot dogs"<br>\
      },<br>\
      {<br>\
	      "sku":"markers"<br>\
      }<br>\
  	]<br>\
}',
  parameters=[
    ApiParameter(
        name="id",
        description="The id of an order",
        required=True,
        dataType="str",
        paramType="param",
        allowMultiple=False),
    ApiParameter(
        name="body",
        description="The the body",
        required=True,
        dataType="str",
        paramType="body",
        allowMultiple=False)
  ],
  responseMessages=[
    ApiErrorResponse(200, ""),
    ApiErrorResponse(400, "Failed to remove line items from Order"),
    ApiErrorResponse(400, "Failed to find given Order")
  ],
  nickname="order_api")
#@app.route('/order/<id>/removeLineItems', methods=['PUT'])
def deleteProductsFromOrder(id):
	#parse json
	requestJson = request.get_json(force=True)
	#validate params
	lines = requestJson.get('lines')

	if not lines:
		return jsonify(error="Required data 'lines' is not set"), 400

	order = models.Order.query.get(id)
	if order:
		#validate line params
		skusToRemove = validateLineItemsToRemove(lines)
		if skusToRemove == None:
			return jsonify(error="Required data on line item not set, specify a sku"), 400
		
		#get all product types for this order
		productTypes = db.session.query(models.ProductType).join(models.Product).filter(models.Product.order_id == order.id)

		for productType in productTypes:
			if productType.sku in skusToRemove:
				#get product
				product = models.Product.query.filter_by(order_id=order.id, product_type_id=productType.id ).first()
				#reduce total
				lineTotal = productType.price * product.quantity
				order.decreaseTotal(lineTotal)
				#remove product
				db.session.delete(product)

		try:
			db.session.commit()
			return jsonify(order_api.formatOrderForGetResponse(order)), 200
		except exc.SQLAlchemyError as err:
			return jsonify(error="Failed to remove line items from Order"), 400

	else:
		return jsonify(error="Failed to find given Order"), 400

#create a list of sku's and validate that each lineItem contains a sku. if not, return None
def validateLineItemsToRemove(lines):
	skus = []
	#validate line params
	for line in lines:
		sku = line.get('sku')
		if not sku:
			return None
		else:
			skus.append(sku)
	return skus
	