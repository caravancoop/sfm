var personObject = [];

$('.modalBox').on('click', function () {
	var field_str = $(this).data('field-str');
	var model_id = $(this).data('model-id');
	console.log(field_str + " " + model_id);
});

function grabData() {

	var source = $(".modal").find("src_confidence").val();
	var confidence = $("#people_src_confidence").val();
	personName.push({source, confidence});

	createObject();
}

function createObject() {

	var name = $("a").closest("div.options").find("input[id='people_ae_name']").val();
	var alias = $("a").closest("div.options").find("input[id='people_ae_alias']").val();
	var notes = $("input[id='people_ae_notes']").val();

	var formId = "person";

	if(personObject != undefined) {
		personObject = {
			Person_PersonName : {
				values :  name,
				sources : personName
			},
			Person_PersonAlias : {
				values : alias,
				sources : personAlias},
				Person_PersonNotes : {values : notes}

			};
		}

		console.log(personObject);
		createList(personObject);
	}

	function createList (personObject) {

		for(var i = 0; i < personObject.Person_PersonName.sources.length; i++) {
			console.log(personObject.Person_PersonName.sources[i]);

			var sourceInfo = '<div class="row clickableRow"><li><p class="col-sm-4">' + personObject.Person_PersonName.sources[i].source + '</p>' +
			'<div class="form-group dropdown col-sm-6">' +
			'<select id="people_src_confidence_data">' +
			'<option>Level of Confidence</option>' +
			'<option value="">low</option>' +
			'<option value="">medium</option>' +
			'<option value="">high</option>' +
			'</select></div>' +
			'<div class="col-sm-2 sources_list_remove" id="' + personObject.Person_PersonName.sources[i].source + '"><span title="Delete Source"><i class="fa fa-trash fa-lg"></i></span></div>' +
			'</li></div>';

			$('#sources_list').append(sourceInfo);
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
