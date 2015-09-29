var genericObject = [];
var sourceObject = [];
var versionObject = [];
var object_name, object_id, field_name;

// grabData bound to add button in souce modal
function grabData() {

	//these values are taken from the link in the drop down select menu
	var field_str = $('.modalBox').data('field-str');
	var model_id = $('.modalBox').data('model-id');


	//grab the value from the modal input field
	var source = $(".modal-body").find("." + model_id + "_src_addSource").val();
	//grab the value from the modal select field
	var confidence = $(".modal-body").find("." + model_id + "_src_addConfidence").val();

	//push the values as an object literal in an object array
	genericObject.push({source: source, confidence: confidence});

// the two next functions combined refresh the list
	removeListElements();//destroy the list
	createSourcesList(genericObject);//regenerate the list
}


// bound to the save button
// adds the person to the database by way of ajax POST
// $('.addPerson').on('click', function() {
//
//
// 	var model_object_id = $('.modalBox').data('model-object-id');
//
// 	// if user is not 0, then you are updating the user
// 	if(model_object_id == 0) {
// 		model_object_id = "add";
// 	}
//
// 	var name = document.getElementById('Person_PersonName').value;
// 	var alias = document.getElementById('Person_PersonAlias').value;
// 	var notes = document.getElementById('Person_PersonNotes').value;
//
// 	var data = {
// 		Person_PersonName : {
// 			"value" : name,
// 			"sources" : sourceObject
// 		},
// 		Person_PersonAlias : {
// 			"value" : alias,
// 			"sources" : versionObject
// 		},
// 		Person_PersonNotes : {
// 			"value" : notes
// 		},
// 	};
// 	$.ajax({
// 		type: "POST",
// 		url: "/" + window.LANG + "/person/" + model_object_id + "/",
// 		data: {
// 			csrfmiddlewaretoken: window.CSRF_TOKEN,
// 			person: JSON.stringify(data)
// 		},
// 		success: function(response, status){
// 			console.log(response);
// 		}
// 	});
// });

// autocomplete for translate language
// function autoFill () {
// 	$("#modal_tr_language").autocomplete({
// 		// request.term needs to be passed up to the server.
//
// 		source: "/translate/languages/autocomplete",
// 		success: function (response, status) {
// 			console.log(response);
// 		},
// 		error: function (request, status, error) {
// 			console.log(error);
// 		}
// 	});
// }

//remove all the li elements
// function removeListElements () {
// 	// remove this element from the dom
// 	$('#sources_list > li').remove();
// }


// $('#complexFieldModal').on('shown.bs.modal', function () {
//
// // update selectpicker after changes for dynamic reasons
// 	$('select').selectpicker('refresh');
//
// 	// modal header div attributes
// 	object_name = $('.modal-header').data('field-object-name');
// 	object_id = $('.modal-header').data('field-object-id');
// 	field_name = $('.modal-header').data('field-attr-name');
// 	modal_type = $('.modal-header').data('modal-type');
// 	var getURL = "/" + modal_type + "/" + object_name + "/" + object_id + "/" + field_name;
//
// 	// console.log(modal_type);
// 	// console.log(object_name + " " + object_id + " " + field_name);
//
// 	genericGetFunction(object_name, object_id, field_name, modal_type, getURL);
//
// });

//Genric AJAX call to get info for the modals
function genericGetFunction (object_name, object_id, field_name, modal_type, getURL) {

	// console.log(object_id);

	//if this is the version modal
	if (modal_type === "version") {
		// get the language value from the select option
		var language = document.getElementById('people_vr_language').value;
		// add the language to the current path
		getURL = getURL + "/" + language;
	}
	// this is useless ****
	else if (modal_type === "source" || modal_type === "translate"){
		getURL = getURL;
	}
	// *****

	$.ajax({
		type: "GET",
		url: getURL,
		dataType: "json",
		// sucess callback function
		success: function (response, status) { //no point in passing the status as an argument
			// console.log(getURL);
			// console.log(response);
			separateObjects(response, modal_type);
		},
		error: function (request, status, error) {
			console.log(error);
		}
	});
}

//Remove sources from the source modal
// $(document).on("click", ".sources_list_remove", function (event) {
// 	var id = $(this).attr('id');
//
// 	for(var i = 0; i < genericObject.length; i++) {
// 		if(genericObject[i].source === id) {
// 			genericObject.splice(i, 1);
// 		}
// 	}
//
// 	//Remove all elements from the existing list and create a new one.
// 	removeListElements();
// 	createSourcesList(genericObject);
// });

// function separateObjects(response, modal_type) {
// 	//Setting the content of genericObject to an empty object
// 	genericObject = [];
//
// 	for (var i in response) {
// 		// console.log(response[i]);
// 		//push the values of the objetc property in the genericObjecct array
// 		genericObject.push(response[i]);
// 	}
//
// 	if (modal_type === "source" ) {
// 		createSourcesList(genericObject);
// 	}
// 	else if (modal_type === "version") {
// 		createVersionsList(genericObject);
// 	}
// 	else if (modal_type === "translate"){
// 		// createTranslationsList(genericObject);
// 	}
//
// }

// function createSourcesList (genericObject) {
// 	sourceObject = genericObject;
// 	// console.log(sourceObject);
//
// 	// Get a reference to the sources list in the main DOM.
// 	var sourcesList = document.getElementById('sources_list');
//
// 	for(var i = 0; i < genericObject.length; i++) {
//
// 		var confidenceString;
// 		var sourceInfo = genericObject[i];
//
// 		switch(sourceInfo.confidence) {
//
// 			case "1":
// 			confidenceString = "Low";
// 			break;
//
// 			case "2":
// 			confidenceString = "Medium";
// 			break;
//
// 			case "3":
// 			confidenceString = "High";
// 			break;
//
// 			default:
// 			confidenceString = "Def";
//
// 		}
//
// 		// var tmpl = document.getElementById('source-template').content.cloneNode(true);
// 		//
// 		// tmpl.querySelector('.src_name').textContent = sourceInfo.source;
// 		// tmpl.querySelector('.src_confidence').textContent = confidenceString;
// 		// tmpl.querySelector('.sources_list_remove').id = sourceInfo.source;
// 		//
// 		// sourcesList.appendChild(tmpl);
// 	}
// }

function createVersionsList (genericObject) {
	versionObject = genericObject;
	console.log(versionObject);

	$('#versions_list').find("tr:not(:has(th))").remove();

	// Get a reference to the versions list in the main DOM.
	var versionsList = document.getElementById('versions_list');

	for(var i = 0; i < genericObject.length; i++) {

		var versionSources = "";
		var versionInfo = genericObject[i];
		var versiontempl = document.getElementById('version_template').content.cloneNode(true);

		versiontempl.querySelector('.version').textContent = versionInfo.value;
		console.log(genericObject[i]);
		if(genericObject[i].sources != undefined) {
			for (var j = 0; j < genericObject[i].sources.length; j++) {

				var confidenceString;

				switch(genericObject[i].sources[j].confidence) {

					case "1":
					confidenceString = "Low";
					break;

					case "2":
					confidenceString = "Medium";
					break;

					case "3":
					confidenceString = "High";
					break;

					default:
					confidenceString = "Def";

				}

				versionSources += genericObject[i].sources[j].source + " - " + confidenceString + String.fromCharCode(10);
				versiontempl.querySelector('#versions_sub_list').textContent = versionSources;

				// console.log(versionSources);
			}
		versionSources = null;
		versiontempl.querySelector('.revertButton').value = versionInfo.id;
		versionsList.appendChild(versiontempl);
	}
	}
}

// function createTranslationsList (genericObject) {
//
// 	$('#translate_table').find("tr:not(:has(th))").remove();
//
// 	// Get a reference to the translation list in the main DOM.
// 	var translateList = document.getElementById('translate_table');
//
// 	for(var i = 0; i < genericObject.length; i++) {
//
// 		var translateInfo = genericObject[i];
// 		var tmpl = document.getElementById('translate_template').content.cloneNode(true);
//
// 		tmpl.querySelector('.tr_language').textContent = translateInfo.lang;
// 		tmpl.querySelector('.tr_value').textContent = translateInfo.value;
//
// 		translateList.appendChild(tmpl);
// 	}
// }

function changeLanguage () {

	// console.log("Change Language");
	var language = document.getElementById('people_vr_language').value;

	$.ajax({
		type: "GET",
		url: "/version/" + object_name + "/" + object_id + "/" + field_name + "/" + language,
		dataType: "json",
		success: function (response, status) {
			console.log(response);
			separateObjects(response, "version");
		},
		error: function (request, status, error) {
			console.log(error);
		}
	});
}

function revertVersion () {

	version_id = $('.revertButton').attr('value');
	var data = {
		"lang" : "en",
		"id" : version_id
	};

	$.ajax({
		type: "POST",
		url: "/" + window.LANG + "/version/revert/" + object_name + "/" + object_id + "/" + field_name + "/",
		// dataType: 'json',
		data: {
			csrfmiddlewaretoken: window.CSRF_TOKEN,
			revert: JSON.stringify(data)
		},
		success: function (response, status) {
			console.log(response);
			var language = document.getElementById('people_vr_language').value;
			getURL = "/version/" + object_name + "/" + object_id + "/" + field_name + "/" + language;
			genericGetFunction(object_name, object_id, field_name, "version", getURL);
		},
		error: function (request, status, error) {
			console.log(error);
		}
	});
}

// function getTranslation () {
//
// 	$.ajax({
// 		type: "GET",
// 		url: "/translate/" + object_name + "/" + object_id + "/" + field_name,
// 		dataType: "json",
// 		crossdomain: true,
// 		success: function (response, status) {
// 			console.log(response + "get Translation");
// 			separateObjects(response, "translate");
// 		},
// 		error: function (request, status, error) {
// 			console.log(error + "error in Translation");
// 		}
// 	});
//
// }

// function addTranslation () {
//
// 	var field_language_value = document.getElementById('modal_tr_value').value;
// 	var field_language_translation = document.getElementById('modal_tr_language').value;
// 	var data = {
// 		"value" : field_language_value,
// 		"lang" : field_language_translation
// 	};
//
// 	$.ajax({
// 		type: "POST",
// 		url: "/" + window.LANG + "/translate/" + object_name + "/" + object_id + "/" + field_name + "/",
// 		data: {
// 			csrfmiddlewaretoken: window.CSRF_TOKEN,
// 			translation: JSON.stringify(data)
// 		},
// 		success: function (response, status) {
// 			console.log(response);
// 			getTranslation();
// 		},
// 		error: function (request, status, error) {
// 			console.log(status);
// 			console.log(error);
// 		}
// 	});
// }
