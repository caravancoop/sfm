var source = (function(){
  var index1, index2;
  var srcModule = {
    tempId: 0,
    sourceObjArr : [],
    fieldStrArr : [],
    modelArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      this.getAll();
    },
    cacheDom:function(){
      //the modal module
      this.$el_modal =  $('#complexFieldModal');
      this.$srcName = null;//source name
      this.$confLvl = null;//level of confidence
      this.$addBtn = null;//add button
      this.$el_popoverTrigger = null; //get the btn trigger for the modal
      this.$txtInput = null; //get the input field that corresponds to the current modal
      this.$modalHeader = null; //modal header class

      this.fieldStr = null;
      this.dataModId = null;

      // modal header div attributes
      this.$mdObjName = null;
      this.$mdObjId = null;
      this.$mdFieldName = null;
      this.$mdModalType = null;

      // this.response = null;
      this.$rowTemplate = null;
      this.$sourceList = null;
    },
    getAll:function(){
      var self = this;
      $('.modalBox').each(function(){
        var sources = $(this).data('remote').replace('/modal', "");
        var model = $(this).data('model-id');
        var fieldStr = $(this).data('field-str');
        if (self.$mdObjId === null || self.$mdObjId === undefined || self.$mdObjId === ""){
          self.$mdObjId =  $(this).data('model-object-id');
        }
        //if the fieldStr is not in array push it
        if ($.inArray(fieldStr, self.fieldStrArr) === -1){
          self.fieldStrArr.push(fieldStr);
        }
        //if the model is not in array push it
        if ($.inArray(model, self.modelArr) === -1){
          self.modelArr.push(fieldStr);
        }
        //set the source object array indexes
        self.setArrayIndexes(model, fieldStr);
        patt = new RegExp("/source");  //filter out the sources path
        $.ajax({
          async: false,
          context:self,
          type: "GET",
          url: sources,
          dataType: "json",
          // success callback function
          success: function (response) {
            for (var i in response) {
              if(patt.test(sources)){ //test if path contains sources
                this.sourceObjArr[index1][index2][this.sourceObjArr[index1][index2].length] = response[i];
              }
            }
          },
          error: function (request, status, error) {
            console.log(error);
          }
        });
      });
      // console.log(this.$mdObjId);
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      this.$el_modal.on('click', '.--src-add-btn', this.addSources.bind(this));
      this.$el_modal.on('click', '.src_del', this.deleteSource.bind(this));
      $('body').on('click', '.addPerson', this.update.bind(this));
    },
    //this function unbinds the events from the selectors
    unbindEvents:function(){

    },
    render:function(){
      // render the new list in the modal
      this.$sourceList.find('li').empty(); //delete old list
      this.sourceObjArr[this.dataModId][this.fieldStr].clean();
      for(var i = 0; i < this.sourceObjArr[this.dataModId][this.fieldStr].length; i++){
        var confidenceString;
        var sourceInfo = this.sourceObjArr[this.dataModId][this.fieldStr][i];

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
        // create list element and add it to the list in the appropriate modal
        this.$rowTemplate = $('#source-template').find('li').clone().removeClass('hide');
        this.$rowTemplate.find('.src_name').html(sourceInfo.source);
        this.$rowTemplate.find('.src_conf').html(confidenceString);
        this.$rowTemplate.find('.src_del').attr('id', sourceInfo.id);

        this.$sourceList.append(this.$rowTemplate);  //append the row to the list
      }
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
      // this.$mdObjId = this.$modalHeader.data('field-object-id');
      this.$mdFieldName = this.$modalHeader.data('field-attr-name');
      this.$mdModalType = this.$modalHeader.data('modal-type');
      this.$sourceList = $('.sources_list');
      this.fieldStr = this.$el_popoverTrigger[0].dataset.fieldStr;
      this.dataModId = this.$el_popoverTrigger[0].dataset.modelId;

      this.render();
      this.setArrayIndexes(this.$el_popoverTrigger[0].dataset.modelId, this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    update:function(){
      var name, alias;
      for(var i = 0; i < this.sourceObjArr['person']['Person_PersonName'].length; ++i){
        delete this.sourceObjArr['person']['Person_PersonName'][i].id;
        // console.log(this.sourceObjArr['person']['Person_PersonName'][i].id);
        // console.log("test");
      }
      for(var i = 0; i < this.sourceObjArr['person']['Person_PersonAlias'].length; ++i){
        delete this.sourceObjArr['person']['Person_PersonAlias'][i].id;
        // console.log(this.sourceObjArr['person']['Person_PersonName'][i].id);
        // console.log("test");
      }
      // console.log(this.sourceObjArr['person']['Person_PersonName'][0]);
      // console.log(this.sourceObjArr['person']['Person_PersonName']);

      this.sourceObjArr['person']['Person_PersonName'].clean();
      this.sourceObjArr['person']['Person_PersonAlias'].clean();
      //  var nameObj = this.sourceObjArr['person']['Person_PersonName'];
      console.log(this.sourceObjArr['person']['Person_PersonName']);
      var data = {
        Person_PersonName : {
          "value" : $("#Person_PersonName").val(),
          "sources" : this.sourceObjArr['person']['Person_PersonName'],
        },
        Person_PersonAlias : {
          "value" : $("#Person_PersonAlias").val(),
          "sources" : this.sourceObjArr['person']['Person_PersonAlias'],
        }
      };
      $.ajax({
        type: "POST",
        url: "/" + window.LANG + "/person/" + this.$mdObjId + "/",
        data: {
          csrfmiddlewaretoken: window.CSRF_TOKEN,
          person: JSON.stringify(data)
        },
        success: function(response, status){
          console.log(response);
        }
      });
    },
    // this function sets the 3 dimentional array indexes specific to the modal and the input field
    setArrayIndexes:function(el_index1, el_index2){
      //set gloabal indexes
      index1 = el_index1;
      index2 = el_index2;
      //test and set index parameters for the modal views
      if(this.sourceObjArr[index1] === undefined && this.sourceObjArr[index2] === undefined){
        this.sourceObjArr[index1]=[];
        this.sourceObjArr[index1][index2] = [];
      }else if(this.sourceObjArr[index1][index2] === undefined){
        this.sourceObjArr[index1][index2] = [];
      }
    },
    getTempId:function(){
      var id = "_" + this.tempId;
      this.tempId++;
      return id;
    },
    addSources:function(){
      this.sourceObjArr[index1][index2][this.sourceObjArr[index1][index2].length] = {source: this.$srcName.val(), confidence: this.$confLvl.val(), id: this.getTempId()};
      this.$srcName.val("");
      this.render();
    },
    deleteSource:function(event){
      for( var i = 0; i < this.sourceObjArr[this.dataModId][this.fieldStr].length; ++i){
        if(this.sourceObjArr[this.dataModId][this.fieldStr][i].id == $(event.target).closest('p').attr('id')){
          delete this.sourceObjArr[this.dataModId][this.fieldStr][i];
          break;
        }
      }
      this.render();
    }
  };
  srcModule.init();
  return {
    publicAPI: function(){
      return srcModule.sourceObjArr;
    }
  };
})();
