/******************************
 * system helpers
 ******************************/
function hasError(jsonObj){
	if (jsonObj != null && typeof(jsonObj.error) != 'undefined') {
		return true;
	}
	return false;
}
// logs an error to the console
function logError(msg) {
    setTimeout(function() {
        throw new Error(msg);
    }, 0);
}

function stringContains(str, containsMe){
	return (str.indexOf(containsMe) != -1 )
}

function stringStartsWith(str, startsWithMe)
{
    return str.slice(0, startsWithMe.length) == startsWithMe;
}

function stringEndsWith(str, endsWithMe)
{
    return str.slice(-endsWithMe.length) == endsWithMe;
}

//remove null or undefeined elements in an array, and return new array
function cleanArray(actual){
  var newArray = new Array();
  for(var i = 0; i<actual.length; i++){
      if (actual[i]){
        newArray.push(actual[i]);
    }
  }
  return newArray;
}
/**
 * 
 * @param {string} val
 */
function isNotEmpty(txt){
	if (txt == null || txt.length < 1){
		return false;
	}else if(txt.split){
		 if(txt.split(" ").join("").length < 1){
		 	return false;
		 }else{
		 	return true;
		 }
	}else{
		return true;
	}
}
function isEmpty(txt){
	return !isNotEmpty(txt);
}
//trim from front and back
function trimString(str){
	return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}
/*
* is object empty. mainly used with jsonObj's
* @param {obj}
*/
function isObjEmpty(obj) {
	var hasOwnProperty = Object.prototype.hasOwnProperty;

    // null and undefined are empty
    if (obj == null) return true;
    // Assume if it has a length property with a non-zero value
    // that that property is correct.
    if (obj.length && obj.length > 0)    return false;
    if (obj.length === 0)  return true;

    for (var key in obj) {
        if (hasOwnProperty.call(obj, key))    return false;
    }

    return true;
}