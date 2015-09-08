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
		console.log(source);
		console.log(personName);
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
		personObject = '{"Person_PersonName" : {"values" : ' + name + '}, "sources" : [' + personName + '], "Person_PersonAlias" : {"values" :' + alias + '}, "sources" : [' + personAlias + '], "Person_PersonNotes" : {"values" : ' + notes + '} ' + '}';
	}

	console.log(personObject);
	console.log(personObject.Person_PersonName.sources + "data");

	for(var i = 0; i < personObject.length; i++) {

	}
}
