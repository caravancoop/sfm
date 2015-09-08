var personObject = [],
personName = [],
personAlias = [];

var count = 0;

$("a[name='people_ae_name']").on('click', function() {
	count = 1;
});

$("a[name='people_ae_alias']").on('click', function() {
	count = 2;
});

function grabData() {
	if(count === 1) {

		var source = $("#people_src_title").val();
		var confidence = $("#people_src_confidence").val();
		personName.push({source, confidence});
	}
	else {
		var source = $("#people_src_title").val();
		var confidence = $("#people_src_confidence").val();
		personAlias.push({source, confidence});
	}
	createObject();
}

function createObject() {

	var name = $("a").closest("div.options").find("input[id='people_ae_name']").val();
	var alias = $("a").closest("div.options").find("input[id='people_ae_alias']").val();
	var notes = $("input[id='people_ae_notes']").val();

	if(personObject != undefined) {
		personObject = {Person_PersonName : {values :  name, sources : personName}, Person_PersonAlias : {values : alias, sources : personAlias}, Person_PersonNotes : {values : notes}};
	}

	console.log(personObject);
	$('#sources_list').empty();
	createList(personObject);
}

function createList (personObject) {

	for(var i = 0; i < personObject.Person_PersonName.sources.length; i++) {
		console.log(personObject.Person_PersonName.sources[i]);

		var sourceInfo = '<div class="row clickableRow"><li><p class="col-sm-4">' + personObject.Person_PersonName.sources[i].source + '</p>' +
		'<div class="form-group dropdown col-sm-7">' +
		'<select id="people_src_confidence_data">' +
				'<option>Level of Confidence</option>' +
				'<option value="">low</option>' +
				'<option value="">medium</option>' +
				'<option value="">high</option>' +
			'</select></div>' +
		'<div class="col-sm-1 sources_list_remove" id="' + personObject.Person_PersonName.sources[i].source + '"><span title="Delete Source"><i class="fa fa-trash fa-lg"></i></span></div>' +
		'</li></div>';

		$('#sources_list').append(sourceInfo);
		$('select').selectpicker('show');
	}
}

$(document).on("click", ".sources_list_remove", function (event) {
    var id = $(this).attr('id');

		console.log(id);
		delete personObject.Person_PersonName.sources[id];
		console.log(personObject);

		for(var i = 0; i < personObject.Person_PersonName.sources.length; i++) {

			console.log(personObject.Person_PersonName.sources[i]);
			console.log(personObject.Person_PersonName.sources[i].source);

			if(personObject.Person_PersonName.sources[i].source === id) {
				delete personObject.Person_PersonName.sources[i];
			}
		}

		console.log(personObject);
});
