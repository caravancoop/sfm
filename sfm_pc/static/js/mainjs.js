var genericObject = [];

function grabData() {

	var field_str = $('.modalBox').data('field-str');
	var model_id = $('.modalBox').data('model-id');

	var source = $(".modal-body").find("." + model_id + "_src_addSource").val();
	var confidence = $(".modal-body").find("." + model_id + "_src_addConfidence").val();
	console.log(field_str + " " + source + " " + confidence);

	genericObject.push({source, confidence});

	console.log(genericObject);
	removeListElements();
	createList(genericObject);
}

function removeListElements () {
	$('#sources_list > li').remove();
}


function createList (genericObject) {

	// Get a reference to the comments list in the main DOM.
	var sourcesList = document.getElementById('sources_list');

	for(var i = 0; i < genericObject.length; i++) {

		var sourceInfo = genericObject[i];

		var confidenceString;
		// console.log(typeof(sourceInfo.confidence));
		// console.log(sourceInfo.confidence);
		switch(sourceInfo.confidence) {

			case 1:
			confidenceString = "Low";
			break;

			case 2:
			confidenceString = "Medium";
			break;

			case 3:
			confidenceString = "High";
			break;

			default:
			confidenceString = "Def";

			var tmpl = document.getElementById('source-template').content.cloneNode(true);
			tmpl.querySelector('.src_name').innerText = sourceInfo.source;
			tmpl.querySelector('.src_confidence').innerText = confidenceString;
			// tmpl.querySelector('.sources_list_remove').id = sourceInfo.source;

			sourcesList.appendChild(tmpl);
		}
	}
}

$('#complexFieldModal').on('shown.bs.modal', function () {

	$('select').selectpicker('show');
	$('select').selectpicker('refresh');

	var object_name = $('.modal-header').data('field-object-name');
	var object_id = $('.modal-header').data('field-object-id');
	var field_name = $('.modal-header').data('field-attr-name');

	console.log(object_name + " " + object_id + " " + field_name);

	$.ajax({
		type: "GET",
		url: "/source/" + object_name + "/" + object_id + "/" + field_name,
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		crossdomain: true,
		success: OnGetSourcesSuccess,
		error: OnGetSourcesError
	});

});

$(document).on("click", ".sources_list_remove", function (event) {

	for(var i = 0; i < genericObject.length; i++) {
		var id = genericObject[i].source;
		if(genericObject[i].source === id) {
			console.log(id);
			delete genericObject[i];
			console.log(genericObject);
		}
	}

	createList(genericObject);
});

// var data = [
//   "Apple",
//   "Orange",
//   "Pineapple",
//   "Strawberry",
//   "Mango"
//   	];
//
//
//
// function autoFill () {
//
// 	$( "#modal_tr_language" ).autocomplete({
// 		source : data
// 	});
//
// }

function separateObjects(response) {

	for (var i in response) {
		console.log(response[i]);
		genericObject.push(response[i]);
	}

	createList(genericObject);
}

function addTranslation () {
	var object_name = $('.modal-header').data('field-object-name');
	var object_id = $('.modal-header').data('field-object-id');
	var field_name = $('.modal-header').data('field-attr-name');

	var field_language_value = document.getElementById('modal_tr_language').value;
	var field_language_translation = document.getElementById('modal_tr_value').value;
	console.log(field_language_value);

	console.log(object_name + " " + object_id + " " + field_name);

	$.ajax({
		type: "POST",
		url: "/" + window.LANG + "/translate/" + object_name + "/" + object_id + "/" + field_name + "/",
		contentType: "application/json; charset=utf-8",
		data: {
			csrfmiddlewaretoken: window.CSRF_TOKEN,
			"translate": {
				"value" : field_language_value,
				"lang" : field_language_translation
			}
		},
		dataType: "json",
		// crossdomain: true,
		success: OnSendTranslationSuccess,
		error: OnSendTranslationError
	});
}


//Response after GetSources request
function OnGetSourcesSuccess(response, status) {
	console.log(response);
	separateObjects(response);
	// release lock
}

function OnGetSourcesError(request, status, error) {
	console.log("error:" + error);
	// release lock
}
//Response after GetSources request

//Response after AutoFill request
function OnAutoFillSuccess(response, status) {
	console.log(response);
	separateObjects(response);
	// release lock
}

function OnAutoFillError(request, status, error) {
	console.log("error:" + error);
	// release lock
}
//Response after AutoFill request

//Response after SendTranslation request
function OnSendTranslationSuccess(response, status) {
	console.log(response);
	separateObjects(response);
	// release lock
}

function OnSendTranslationError(request, status, error) {
	console.log("error:" + error);
	// release lock
}
//Response after Sendtranslation request
