(function(){
  var sourceModule = {
     genericObjArr : [],
     sourceObjArr : [],
    //  objName,
    //  objId,
    //  filedName,
    init:function(){
      this.cacheDom();
      this.bindEvents();
    },
    cacheDom:function(){
      //the modal module
      this.$el_modal =  $('#complexFieldModal');
      this.$srcName = this.$el_modal.find('.--src-name');   //source name
      this.$confLvl = this.$el_modal.find('.--src-conf');   //level of confidence
      this.$addBtn = this.$el_modal.find('.--src-add-btn'); //add button
      this.$el_popover =  $('.modalBox[data-target='+ this.$el_modal.attr('id') +']');//
      // this.$txtInput =  $el_modal;
      console.log(this.$el_popover);
    },
    bindEvents:function(){

    },
    // render
  };
  sourcesModule.init();
})();
//
// $('#complexFieldModa').on('show.bs.modal', function (event) {
//   var button = $(event.relatedTarget); // Button that triggered the modal
//   var recipient = button.data('whatever'); // Extract info from data-* attributes
//   // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
//   // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
//   var modal = $(this);
//   modal.find('.modal-title').text('New message to ' + recipient);
//   modal.find('.modal-body input').val(recipient);
// });
