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

    def __init__(self, total=0, shipping_street=None, shipping_state=None, shipping_city=None, shipping_zipcode=None, billing_street=None, billing_state=None, billing_city=None, billing_zipcode=None):
        self.total = total
        self.shipping_street = shipping_street
        self.shipping_state = shipping_state
        self.shipping_city = shipping_city
        self.shipping_zipcode = shipping_zipcode
        self.billing_street = billing_street
        self.billing_state = billing_state
        self.billing_city = billing_city
        self.billing_zipcode = billing_zipcode

    def setShippingAndBillingAddress(self, shippingAddress, billingAddress, sameBillingAddress="false"):
        self.setShippingAddress(shippingAddress)
        
        if sameBillingAddress == "true":
            self.setBillingAddress(shippingAddress)
        else:
            self.setBillingAddress(billingAddress)

    def setShippingAddress(self, shippingAddress):
        self.shipping_street = shippingAddress.get('street')
        self.shipping_state = shippingAddress.get('city')
        self.shipping_city = shippingAddress.get('state')
        self.shipping_zipcode = shippingAddress.get('zip')

    def setBillingAddress(self, billingAddress):
        self.billing_street = billingAddress.get('street')
        self.billing_state = billingAddress.get('city')
        self.billing_city = billingAddress.get('state')
        self.billing_zipcode = billingAddress.get('zip')

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


       