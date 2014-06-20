from decimal import Decimal

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

   	print "price converstion tests pass"

