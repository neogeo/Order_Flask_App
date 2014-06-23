from decimal import Decimal
from threading import Thread
import requests
import json

ONEPLACE = Decimal(10)
TWOPLACES = Decimal(10) ** -2

#parse a string price in dollar format ($1.00), converts to an Integer representing the number of cents
def parsePrice(strPrice):
	#remove white space and split on '$''
	strArr = strPrice.strip(' "').split('$')
	#get the price. in index 1 if str contained '$', otherwise index 0
	strPrice = strArr[1] if len(strArr)==2 else strArr[0]

	#if empty, return 0
	if not strPrice:
		return 0
	else:
		#we have a price
		#convert to a decimal and round to 2 decimal places
		dec = Decimal(strPrice).quantize(TWOPLACES)
		#convert to cents
		dec = dec * 100
		#remove trailing zeros and convert to int
		finalPrice = int(dec.quantize(ONEPLACE))
		
		return finalPrice

#given an int as cents and returns a formatted dollar value (e.g. 10051 => $10.51)
def convertIntToFormattedPrice(intPriceInCents):
	#force intPrice to two decimal places and convert to dollar amount
	dec = Decimal(intPriceInCents).quantize(TWOPLACES) / 100
	#format
	return "$"+str(dec)

#publish an update to the faye server
def publishUpdate(msg, productType):
	thread = Thread(target = publish, args = (msg, productType))
	thread.start()

#publish the creation of an order. send a message for each product type inventory that was updated
#products - a list of id, inventory tuples
def publishCreateOrder(msg, products):
	for product in products:
		publishUpdate(msg, product)

def publish(msg, productType):
	url = "http://neogeo098.webfactional.com/faye"
	
	message = dict(
	  channel = "/productType", 
	  data = dict( msg = msg, productType = productType )
	)

	headers = {'content-type': 'application/json'}
	r = requests.post(url, data=json.dumps(message), headers=headers)


#UNIT TESTS
#verify that a round trip through parsing and converstion generates the expected values
if __name__=='__main__':
	
	x = "$200.00"
   	assert x == convertIntToFormattedPrice(parsePrice(x))

   	x = "$200.51 "
   	assert "$200.51" == convertIntToFormattedPrice(parsePrice(x))

   	x = " 10.51"
   	assert "$10.51" == convertIntToFormattedPrice(parsePrice(x))

   	x = "0.00 "
   	assert "$0.00" == convertIntToFormattedPrice(parsePrice(x))

   	x = ""
   	assert "$0.00" == convertIntToFormattedPrice(parsePrice(x))

   	x = "         "
   	assert "$0.00" == convertIntToFormattedPrice(parsePrice(x))

   	print "price conversion tests pass"

