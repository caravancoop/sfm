var source = (function(){
  var index1, index2;
  var srcModule = {
    tempId: 0,
    srcObjArr : [],
    fieldStrArr : [],
    fieldArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      this.getAll();
    },
    cacheDom:function(){
      //the modal module
      this.$el_modal =  $('#complexFieldModal');
    },
    getAll:function(){
      var self = this;
      $('.modalBox').each(function(){
        var sources = $(this).data('remote').replace('/modal', "");
        var model = $(this).data('model-id');
        var fieldStr = $(this).data('field-str');
        // console.log(fieldStr);
        if (self.$mdObjId === null || self.$mdObjId === undefined || self.$mdObjId === ""){
          self.$mdObjId =  $(this).data('model-object-id');
        }
        //if the fieldStr is not in array push it in
        if ($.inArray(fieldStr, self.fieldStrArr) === -1){
          // this will be used to create the id of every field with an option box
          self.fieldStrArr.push(fieldStr);
          self.fieldArr.push({model:model,field:fieldStr});
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
          success: function (response) {
            for (var i in response) {
              if(patt.test(sources) && typeof response[i] !== 'function'){ //test if path contains sources
                this.srcObjArr[index1][index2][this.srcObjArr[index1][index2].length] = response[i];
              }
            }
          },
          error: function (request, status, error) {
            console.log(error);
          }
        });
      });
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      this.$el_modal.on('click', '.--src-add-btn', this.addSources.bind(this));
      this.$el_modal.on('click', '.src_del', this.deleteSource.bind(this));
      $('body').on('click', '.addPerson', this.update.bind(this));
    },
    render:function(){
      // render the new list in the modal
      this.$sourceList.find('li').empty(); //delete old list
      this.srcObjArr[this.dataModId][this.fieldStr].clean();
      for(var i = 0; i < this.srcObjArr[this.dataModId][this.fieldStr].length; i++){
        var confidenceString;
        var sourceInfo = this.srcObjArr[this.dataModId][this.fieldStr][i];
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
      // this.getAll(event);
      this.render();
      this.setArrayIndexes(this.$el_popoverTrigger[0].dataset.modelId, this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    // this function sets the 3 dimentional array indexes specific to the modal and the input field
    setArrayIndexes:function(el_index1, el_index2){
      //set gloabal indexes
      index1 = el_index1;
      index2 = el_index2;
      //test and set index parameters for the modal views
      if(this.srcObjArr[index1] === undefined && this.srcObjArr[index2] === undefined){
        this.srcObjArr[index1]=[];
        this.srcObjArr[index1][index2] = [];
      }else if(this.srcObjArr[index1][index2] === undefined){
        this.srcObjArr[index1][index2] = [];
      }
    },
    getTempId:function(){
      var id = "_" + this.tempId;
      this.tempId++;
      return id;
    },
    addSources:function(){
      this.srcObjArr[index1][index2][this.srcObjArr[index1][index2].length] = {source: this.$srcName.val(), confidence: this.$confLvl.val(), id: this.getTempId()};
      this.$srcName.val("");
      this.render();
    },
    deleteSource:function(event){
      for( var i = 0; i < this.srcObjArr[this.dataModId][this.fieldStr].length; ++i){
        if(this.srcObjArr[this.dataModId][this.fieldStr][i].id == $(event.target).closest('p').attr('id')){
          delete this.srcObjArr[this.dataModId][this.fieldStr][i];
          break;
        }
      }
      this.render();
    },
    update:function(){
      this.ref_model = null; //referece model
      var objArr = [];
      var modelArr = Object.keys(this.srcObjArr);
      for(var x = 0; x < modelArr.length; ++x){
        for (var model in this.srcObjArr[modelArr[x]]){
          if (typeof this.srcObjArr[modelArr[x]][model] !== 'function') {
            for (var index in this.srcObjArr[modelArr[x]][model]){
              if (typeof this.srcObjArr[modelArr[x]][model][index] !== 'function') {
                var obj = {};
                obj[model] = {};
                obj[model].source = this.srcObjArr[modelArr[x]][model][index].source;
                obj[model].confidence = this.srcObjArr[modelArr[x]][model][index].confidence;
                objArr.push(obj);
                // this.ref_model = model;
              }
            }
          }
        }
      }
      postData = {};
      for(var j = 0; j < objArr.length; ++j){
        var fieldId = String(Object.keys(objArr[j]));

          //remove the field id's and models that have been accounted for
          for (var i = 0; i < this.fieldArr.length; i++){
            if (this.fieldArr[i].field && this.fieldArr[i].field === fieldId) {
                this.fieldArr.splice(i, 1);
                break;
            }
          }


        postData[fieldId]={};
        postData[fieldId].value = $('#'+ fieldId).val(); //assign input field value to the object key value pair
        for(var k = 0; k < objArr.length; ++k){
          //if the sources key doesn't exist, create it
          if(postData[fieldId].sources === undefined){
            postData[fieldId].sources = [];
          }
          // if the object exists add it to the approporiate object array
          if(objArr[k][fieldId] !== undefined ){
            postData[fieldId].sources[postData[fieldId].sources.length] = objArr[k][fieldId];
          }
        }
      }
      // for fields without sources, add the text field value
      for(var s = 0; s < this.fieldArr.length; s++){
        if(postData[this.fieldArr[s].field] === undefined){
          postData[this.fieldArr[s].field]={};
        }
        postData[this.fieldArr[s].field].value = $("#"+this.fieldArr[s].field).val();
          // console.log($("#"+this.fieldArr[s].field).val());
      }
      // console.log(postData);
      console.log(JSON.stringify(postData));
      if(this.$mdObjId === 0){
        this.$mdObjId = "add";
      }

      $.ajax({
        type: "POST",
        url: window.location,
        data: {
          csrfmiddlewaretoken: window.CSRF_TOKEN,
          person: JSON.stringify(postData)
        },
        success: function(response, status){
          console.log(response);
          var err_str, err_id;
          for(var key in response.errors){
            err_str = response.errors[key];
            err_id = Object.keys(response.errors)[0];
            $("#" + err_id).siblings('.error-message').html("* " + err_str);
          }
        },
        error: function(requestObject, error, errorThrown) {
          console.log(requestObject);
        }
      });
    },
  };
  srcModule.init();
  return {
    publicAPI: function(){
      return srcModule.srcObjArr;
    }
  };
})();
