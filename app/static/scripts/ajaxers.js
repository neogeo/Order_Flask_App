//set up all api calls
var globalSystem = {
	//set to '..' or other to set the calling url context
	ajaxContext : ''
}
$.ajaxSetup({
	headers: {
        "Cache-Control": "no-cache, must-revalidate"
    }
});



function ajaxGet(endpoint, callback, errorCallback){
	jQuery.ajax({ 	beforeSend: function(R) { R.setRequestHeader ( "Cache-Control", "no-cache, must-revalidate"); },
			            url: globalSystem.ajaxContext+ endpoint+"?format=json",
			            type: "GET", 
			            dataType: "json",
			            timeout: 60000,
			            error: function( jqXHR, textStatus, errorThrown){
							var responseJson = jqXHR.responseText;
							if(responseJson != null){
								
								//we can handle this error
								if(typeof(errorCallback) != 'undefined'){
									errorCallback(JSON.parse(responseJson));
								}else{
									//can't handle eror
									logError(textStatus + " "+ errorThrown);
									callback({});
								}
							}else{
								logError(textStatus +" "+ errorThrown);	
							}
			            },
			            success: function(returned_json_obj){
			            	//if error, return empty object
			            	if(hasError(returned_json_obj)){
			            		callback({});
			            	}
							//return JSON object
							callback( returned_json_obj );
			            }
		});
}

function ajaxPutWithBody(endpoint, body, callback){
	jQuery.ajax({ 	beforeSend: function(R) { R.setRequestHeader ( "Cache-Control", "no-cache, must-revalidate"); },
			            url: globalSystem.ajaxContext+ endpoint+"?format=json",
			            type: "PUT", 
			            beforeSend: function(xhr) {xhr.setRequestHeader('X-CSRF-Token', $('meta[name="csrf-token"]').attr('content'))},
			            dataType: "json",
			            data: body,
			            timeout: 60000,
			            error: function( jqXHR, textStatus, errorThrown){
							//var responseJson = JSON.parse(jqXHR.responseText);
							var responseJson = jqXHR.responseText;
							if(responseJson != null){
								logError(textStatus + " "+ errorThrown);
								//we can handle this error
								callback({});
							}else{
								logError(textStatus +" "+ errorThrown);	
							}
							
			            },
			            success: function(returned_json_obj){
			            	//if error, return empty object
			            	if(hasError(returned_json_obj)){
			            		callback({});
			            	}
							//return JSON object
							callback( returned_json_obj );
			            }
		});
}
