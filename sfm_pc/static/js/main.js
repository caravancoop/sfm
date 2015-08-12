$( document ).ready(function() {
    
    
    plusSpan = $("<span>").addClass("input-group-btn ")
    btn = $("<button>").addClass("btn").addClass("btn-primary");
    icon = $("<i>").addClass("fa").addClass("fa-plus");
    
    icon.appendTo(btn);
    btn.appendTo(plusSpan);
    
    //  $('.addplus').after(plusSpan );
    

});