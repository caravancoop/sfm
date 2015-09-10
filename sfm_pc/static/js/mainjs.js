var personObject = [],
personN = [];

$('.modalBox').on('click', function () {

	var person = $('.modalBox').data('field-object-name');
	var person_id = $('.modalBox').data('field-object-id');
	var name = $('.modalBox').data('field-attr-name');

	console.log(person + " " + person_id + " " + name);

	$.ajax({
		type: "GET",
		url: "/source/" + person + "/" + person_id + "/" + name,
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		crossdomain: true,
		success: OnGetSourcesSuccess,
		error: OnGetSourcesError
	});

});

function grabData() {

	var field_str = $('.modalBox').data('field-str');
	var model_id = $('.modalBox').data('model-id');

	var source = $(".modal-body").find("." + model_id + "_src_addSource").val();
	var confidence = $(".modal-body").find("." + model_id + "_src_addConfidence").val();
	console.log(field_str + " " + source + " " + confidence);

	personN.push({"sources": [source, confidence]});

	if(personObject !== undefined) {
		personObject[field_str] = {
			values : name,
			sources : personN
		}
	}

	console.log(personObject);
	createList(personObject);
}


function createList (personObject) {

	for(var i = 0; i < personObject.Person_PersonName.sources.length; i++) {
		console.log(personObject.Person_PersonName.sources[i]);

		var sourceInfo = '<div class="row clickableRow"><li><p class="col-sm-4">' + personObject.Person_PersonName.sources[i].sources[0] + '</p>' +
		'<p class="col-sm-6">' + personObject.Person_PersonName.sources[i].sources[1] + '</p>' +
		'<div class="col-sm-2 sources_list_remove" id="' + personObject.Person_PersonName.sources[i].sources[0] + '"><span title="Delete Source"><i class="fa fa-trash fa-lg"></i></span></div>' +
		'</li></div>';

		$('#sources_list').append(sourceInfo);

	}
}


$(document).on("click", ".sources_list_remove", function (event) {

	for(var i = 0; i < personObject.Person_PersonName.sources.length; i++) {
		var id = personObject.Person_PersonName.sources[i].sources[0];
		if(personObject.Person_PersonName.sources[i].sources[0] === id) {
			console.log(id);
			delete personObject.Person_PersonName.sources[i].sources;
			console.log(personObject);
		}
	}
});

function OnGetSourcesSuccess(response, status) {
	var data = response;
	console.log(response);
	// release lock
}

function OnGetSourcesError(request, status, error) {
	console.log("error:" + error);
	// release lock
}
