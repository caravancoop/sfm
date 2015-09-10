var genericObject = [];

function grabData() {

	var field_str = $('.modalBox').data('field-str');
	var model_id = $('.modalBox').data('model-id');

	var source = $(".modal-body").find("." + model_id + "_src_addSource").val();
	var confidence = $(".modal-body").find("." + model_id + "_src_addConfidence").val();
	console.log(field_str + " " + source + " " + confidence);

	genericObject.push({source, confidence});

	console.log(genericObject);
	createList(genericObject);
}


function createList (genericObject) {

	for(var i = 0; i < genericObject.length; i++) {
		console.log(genericObject[i]);
		console.log(genericObject[i].source);
		console.log(genericObject[i].confidence);

		var sourceInfo = '<div class="row clickableRow"><li><p class="col-sm-4">' + genericObject[i].source + '</p>' +
		'<p class="col-sm-6">' + genericObject[i].confidence + '</p>' +
		'<div class="col-sm-2 sources_list_remove" id="' + genericObject[i].source + '"><span title="Delete Source"><i class="fa fa-trash fa-lg"></i></span></div>' +
		'</li></div>';

		$('#sources_list').prepend(sourceInfo);

	}
}

$('#complexFieldModal').on('shown.bs.modal', function () {

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

function separateObjects(response) {

	for (var i in response) {
		console.log(response[i]);
		genericObject.push(response[i]);
	}

	createList(genericObject);
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
