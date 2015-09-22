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
      this.$srcName;//source name
      this.$confLvl;//level of confidence
      this.$addBtn;//add button
      this.$el_popoverTrigger; //get the btn trigger for the modal
      this.$txtInput; //get the input field that corresponds to the current modal

    },
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
    },
    dynamicAssignments:function(event){
      this.$el_popoverTrigger = $(event.relatedTarget);
      this.$srcName = this.$el_modal.find('.--src-name');   //source name
      this.$confLvl = this.$el_modal.find('.--src-conf');   //level of confidence
      this.$addBtn = this.$el_modal.find('.--src-add-btn'); //add button
      this.$txtInput = $('#' + this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    // render
  };
  sourceModule.init();
})();
