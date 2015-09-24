(function(){
  var index1, index2;
  var arrIndex = 0;
  var srcArr = [];
  var  dataArry = [];
  var sourceModule = {
     sourceObjArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      this.getAll();
    },
    getAll:function(){
      var self = this;
      $('.modalBox').each(function($el, self){
        var sources = $(this).data('remote').replace('/modal', "");
        var model = $(this).data('model-id');
        var fieldStr = $(this).data('field-str');
        // dataArry
        $.ajax({
          type: "GET",
          url: sources,
          dataType: "json",
          // success callback function
          success: function (response) { //no point in passing the status as an argument
            // self.parseRes(response);
            self.setArrayIndexes(model, fieldStr);
          },
          error: function (request, status, error) {
            console.log(error);
          }
        });

      });

    },
    cacheDom:function(){
      //the modal module
      this.$el_modal =  $('#complexFieldModal');
      this.$srcNamer = null;//source name
      this.$confLvlr = null;//level of confidence
      this.$addBtnr = null;//add button
      this.$el_popoverTriggerr = null; //get the btn trigger for the modal
      this.$txtInputr = null; //get the input field that corresponds to the current modal
      this.$modalHeader = null; //modal header class
      // modal header div attributes
      this.$mdObjNamer = null;
      this.$mdObjIdr = null;
      this.$mdFieldNamer = null;
      this.$mdModalTyper = null;

      this.table = null;
      this.response = null;
      this.$tblRowTemplate = null;
      this.$sourceList = null;
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      this.$el_modal.on('click', '.--src-add-btn', this.addSources.bind(this));
    },
    //this function unbinds the events from the selectors
    unbindEvents:function(){

    },
    //this function dynamically assigns the element vars everytime a modal is triggered
    dynamicAssignments:function(event){
      $('select').selectpicker('refresh');  //refresh the select box
      this.$el_popoverTrigger = $(event.relatedTarget);
      // console.log(this.$el_popoverTrigger[0]);
      this.$srcName = this.$el_modal.find('.--src-name');   //source name
      this.$confLvl = this.$el_modal.find('.--src-conf');   //level of confidence
      this.$addBtn = this.$el_modal.find('.--src-add-btn')[0]; //add button
      this.$txtInput = $('#' + this.$el_popoverTrigger[0].dataset.fieldStr);
      this.$modalHeader = this.$el_modal.find('.modal-header');
      this.$mdObjName = this.$modalHeader.data('field-object-name');
    	this.$mdObjId = this.$modalHeader.data('field-object-id');
    	this.$mdFieldName = this.$modalHeader.data('field-attr-name');
    	this.$mdModalType = this.$modalHeader.data('modal-type');
      this.$table = this.$el_modal.find('.table');
      this.$sourceList = $('.sources_list');
      console.log(this.$mdFieldName);
      this.getSources();
      this.setArrayIndexes(this.$el_popoverTrigger[0].dataset.modelId, this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    // this function sets the 3 dimentional array indexes specific to the modal and the input field
    setArrayIndexes:function(el_index1, el_index2){
      //set indexes
      index1 = el_index1;
      index2 = el_index2;
      // index1 = this.$el_modal.find('.modal-header')[0].dataset.fieldObjectName;
      // index2 = this.$el_modal.find('.modal-header')[0].dataset.fieldAttrName;
      //test and seet index parameters for the modal views
      if(this.sourceObjArr[index1] === undefined && this.sourceObjArr[index2] === undefined){
        this.sourceObjArr[index1]=[];
        this.sourceObjArr[index1][index2] = [];
      }else if(this.sourceObjArr[index1][index2] === undefined){
        this.sourceObjArr[index1][index2] = [];
      }
    },
    addSources:function(){
      this.sourceObjArr[index1][index2][this.sourceObjArr[index1][index2].length] = {source: this.$srcName.val(), confidence: this.$confLvl.val()};
      ++arrIndex;
      // render()
      // TODO: delete this functioin after testing
      console.log("------------------------------------------------------------------------");
      console.log(index1 + ", " + index2);
      for(x = 0; x < arrIndex; ++ x){
        if(this.sourceObjArr[index1][index2][x] !== undefined){
          console.log(this.sourceObjArr[index1][index2][x]);
        }
      }
      console.log("index count: " + this.sourceObjArr[index1][index2].length);
      console.log("------------------------------------------------------------------------");

      // this.updatelist()
    },
    deleteSource:function(){
      // delete this.sourceObjArr[index1][index2][arrIndex];
    },
    getSources:function(){
      var self = this;
      	$.ajax({
      		type: "GET",
      		url: "/" + this.$mdModalType  + "/" + this.$mdObjName + "/" + this.$mdObjId + "/" + this.$mdFieldName,
      		dataType: "json",
      		// success callback function
      		success: function (response) { //no point in passing the status as an argument
      			self.parseRes(response);
      		},
      		error: function (request, status, error) {
      			console.log(error);
      		}
      	});
    },
    parseRes:function(response){
      this.srcArr = [];
      for (var i in response) {
    		//push the values of the objetc property in the genericObjecct array
    		this.srcArr.push(response[i]);
    	}
      this.render();
    },
    render:function(){
      // render the new list in the modal
      this.$sourceList.find('li').empty();
      console.log(this.srcArr);
      for(var i = 0; i < this.srcArr.length; i++){
        var confidenceString;
        var sourceInfo = this.srcArr[i];
        switch(sourceInfo.confidence) {
          case "1":
          confidenceString = "Low";
          break;

          case "2":
          confidenceString = "Medium";
          break;

          case "3":
          confidenceString = "High";
          break;

          default:
          confidenceString = "Def";
        }
        this.$tblRowTemplate = $('#source-template2').clone().removeClass('hide');
        this.$tblRowTemplate.find('.src_name').html(sourceInfo.source);
        this.$tblRowTemplate.find('.src_conf').html(confidenceString);
        this.$tblRowTemplate.find('.src_del').attr('id', sourceInfo.id);


        this.$sourceList.append(this.$tblRowTemplate);  //append the row to the list
        // console.log(sourceInfo.source);
      }
    }
  };
  sourceModule.init();
})();
