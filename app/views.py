from flask import render_template
from flask import jsonify
from flask import request
from sqlalchemy import exc
from app import app
from app import db, models, helpers


@app.route('/')
@app.route('/index')
def index():
    order = { 'total': '$1' }

    return render_template("index.html",
        order = order
    )

'''
create a product type:
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
	return jsonify(id=productType.id, sku=productType.sku, inventory=productType.inventory, price=helpers.convertIntToFormattedPrice(productType.price) ), 201

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

