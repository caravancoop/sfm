$("select.artists, select#id_artist").change( function(){
    
    $.getJSON("/ajax/artists/"+$(this).val()+"/releases/", function(jsonData){
        
        if (jsonData['code'] == '200') {
            cb = '<option value="">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</option>';
            $.each(jsonData['result'], function(i,data){
                if (data.title) {
                    if ($("#selected_release").val() == data.id) {
                        cb+='<option value="'+data.id+'" selected="selected">'+data.title+'</option>';
                    }else{
                        cb+='<option value="'+data.id+'">'+data.title+'</option>';
                    }
                }
            });
        }
        $(".releases, select#id_release").html(cb);
    });
});


$("select.artists, select#id_artist").change( function(){
    
    $.getJSON("/ajax/artists/"+$(this).val()+"/project/", function(jsonData){
        
        if (jsonData['code'] == '200') {
            cb = '<option value="">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</option>';
            $.each(jsonData['result'], function(i,data){
                
                if (data.name) {
                    if ($("#selected_project").val() == data.id) {
                        cb+='<option value="'+data.id+'" selected="selected">'+data.name+'</option>';
                    }else{
                        cb+='<option value="'+data.id+'">'+data.name+'</option>';
                    }
                }
            });
        }
        $(".project, select#project_id").html(cb);
    });
});