var search_vars = {}

refresh_result({});

function refresh_result(search_vars){
  $.ajax({
    type: 'get',
    url: window.location + "search/",
    data: search_vars,
    dataType: 'json',
    success: function(data) {
      if(data.success == true){
        $('#object-linked-table').html("");
        $.each(data.objects, function(index, object){
          row = "<tr data-object-id='" + object['id'] + "'>";
          $.each(data.keys, function(i, key){
            row += "<td>" + object[key] + "</td>";
          })
          row += "</tr>";
          $('#object-linked-table').append(row);
        });
      }
    }
  });
}

$("select, input").on("change", function(e) {
  elem = $(e.target);
  search_vars[elem.attr('id')] = elem.val();
  refresh_result(search_vars);
});
