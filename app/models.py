from app import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #Type is Integer, so the price can be stored in cents. 
    #This mitigates any floating point or decimal coersion and possible loss of precision
    total = db.Column(db.Integer, unique = False)
    shipping_street = db.Column(db.String(64), unique = False)
    shipping_state = db.Column(db.String(64), unique = False)
    shipping_city = db.Column(db.String(64), unique = False)
    shipping_zipcode = db.Column(db.String(64), unique = False)
    billing_street = db.Column(db.String(64), unique = False)
    billing_state = db.Column(db.String(64), unique = False)
    billing_city = db.Column(db.String(64), unique = False)
    billing_zipcode = db.Column(db.String(64), unique = False)

    def __init__(self, total, shipping_street, shipping_state, shipping_city, shipping_zipcode, billing_street, billing_state, billing_city, billing_zipcode):
        self.total = total
        self.shipping_street = shipping_street
        self.shipping_state = shipping_state
        self.shipping_city = shipping_city
        self.shipping_zipcode = shipping_zipcode
        self.billing_street = billing_street
        self.billing_state = billing_state
        self.billing_city = billing_city
        self.billing_zipcode = billing_zipcode

    def __repr__(self):
        return '<Order %r>' % (self.total)


class ProductType(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sku = db.Column(db.String(64), unique = True)
    inventory = db.Column(db.Integer, unique = False)
    price = db.Column(db.Integer, unique = False)

    def __init__(self, sku, inventory, price):
        self.sku = sku
        self.inventory = inventory
        self.price = price

    def __repr__(self):
        return '<ProductType %r>' % (self.sku)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, unique = False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    order = db.relationship('Order',
        backref=db.backref('products', lazy='dynamic'))
    #must always have a product_type
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_type.id'), nullable=False)
    product_type = db.relationship('ProductType',
        backref=db.backref('products', lazy='dynamic'))

    def __init__(self, quantity, product_type, order):
        self.quantity = quantity
        self.order = order
        self.product_type = product_type

    def __repr__(self):
        return '<Product %r>' % (self.quantity)


       