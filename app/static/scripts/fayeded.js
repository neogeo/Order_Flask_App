/**
 * REQUIRES js/faye.js
 */


var faye;
var globalFaye = {
		isConnected: false,
		channel: { subscribeTo: "/productType" 
				}
	};
/**
 * 
 * @param {Object} debug$ an element to put debug info into, like connection status
 */
function setUpFayeded(debug$, connectedCallback )
{
	//faye = new Faye.Client('http://192.168.1.2:9292/faye',
	faye = new Faye.Client('http://neogeo098.webfactional.com/faye',
						{
							timeout: 120,
							retry: 5
						});


	//make sure nothing happened in set up	
	if (typeof(faye) != 'undefined') {
		//this does not mean we are connected yet
		//subscribe to stuff. this does not automatically mean we are connected
		var subbed = faye.subscribe( globalFaye.channel.subscribeTo, function(jsonObj) {
			if (jsonObj.msg == "UPDATE_INVENTORY") {//when inventory is updated
				if(typeof(debug$) != 'undefined' && debug$.length != 0){
					debug$.prepend("UPDATE_INVENTORY "+jsonObj.productType.id + "<br>");
				}
				//update UI
				updateProductTypeRow(jsonObj.productType.id, jsonObj.productType.inventory);
				
			}else if (jsonObj.msg == "UPDATE_PRODUCT_TYPE") {//when product types are updated
				if(typeof(debug$) != 'undefined' && debug$.length != 0){
					debug$.prepend("UPDATE_PRODUCT_TYPE "+jsonObj.productType.id + "<br>");
				}
				//update UI
				updateProductTypeRow(jsonObj.productType.id, jsonObj.productType.inventory);
				
			}else if (jsonObj.msg == "CREATE_PRODUCT_TYPE") {//when product types are updated
				if(typeof(debug$) != 'undefined' && debug$.length != 0){
					debug$.prepend("CREATE_PRODUCT_TYPE "+jsonObj.productType.id + "<br>");
				}
				//update UI, if it does not already exist
				if($('#'+jsonObj.productType.id).length < 1){
					createProductTypeRow(jsonObj.productType.id, jsonObj.productType.sku, jsonObj.productType.price, jsonObj.productType.inventory);
				}else{
					//update existing
					$("#inventory_"+jsonObj.productType.id).html(jsonObj.productType.inventory);
					$("#row_inventory"+jsonObj.productType.id).stop(true,true).effect("highlight", {queue:false, duration:800});
					if(jsonObj.productType.inventory < 1){
						$("#row_inventory"+jsonObj.productType.id).addClass('empty');
					}else{
						$("#row_inventory"+jsonObj.productType.id).removeClass('empty');
					}
				}
			}else if (jsonObj.msg == "DELETE_PRODUCT_TYPE") {//when product types are updated
				if(typeof(debug$) != 'undefined' && debug$.length != 0){
					debug$.prepend("DELETE_PRODUCT_TYPE "+jsonObj.productType.id + "<br>");
				}
				//remove this product type if it exists
				if($('#product_type_'+jsonObj.productType.id).length > 0){
					$('#product_type_'+jsonObj.productType.id).remove();
				}
			}
		});

		//did we connect to faye
		subbed.callback(function() {
			globalFaye.isConnected = true;
			if(typeof(debug$) != 'undefined' && debug$.length != 0){
				debug$.html('Subscription is now active!');
			}

			//run call back if present
			if(typeof(connectedCallback) != 'undefined'){
				connectedCallback();
			}
		});
		//failed to connect 
		subbed.errback(function(error) {
			globalFaye.isConnected = false;
			if(typeof(debug$) != 'undefined' && debug$.length != 0){
				debug$.html(error.message);
			}
		});
		
		
	}else{
		//set up failed
		if(typeof(debug$) != 'undefined' && debug$.length != 0){
			debug$.html('Failed to connect to message server');
		}
	}

}

//are we connected to faye
function hasFayededConnection(){
	return globalFaye.isConnected;
}