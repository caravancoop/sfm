var source = (function(){
  var field_id;
  var srcModule = {
    tempId: 0,
    objects: {},
    actualObject: "",
    actualElement: null,
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
      this.actualObject = moduleController.getActualObjectName();
      this.objects[this.actualObject] = {};
      this.actualElement = moduleController.getActualObject()['element']
      this.$el_modal =  $('#complexFieldModal');
    },
    getAll:function(){
      var self = this;
      object = this.objects[this.actualObject];
      $('.modalBox.source').each(function(){
        var sources_url= $(this).data('remote').replace('/modal', "");
        var model = $(this).data('model-id');
        var fieldStr = $(this).data('field-str');
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
          url: sources_url,
          dataType: "json",
          success: function (response) {
            object[field_id] = {}
            object[field_id]['sources'] = response['sources'];
            object[field_id]['confidence'] = response['confidence'];
          },
          error: function (request, status, error) {
            console.log(error);
          }
        });
      });
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      this.$el_modal.on('change', '.--src-conf', this.updateConfidence.bind(this));
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      this.$el_modal.on('click', '.--src-add-btn', this.addSources.bind(this));
      this.$el_modal.on('click', '.src_del', this.deleteSource.bind(this));
      $('body').on('click', '.addObject', this.update.bind(this));
    },

    // render the new list in the modal
    render:function(){
      object = this.objects[this.actualObject];
      this.$sourceList.find('li').empty(); //delete old list
      
      for(var i = 0; i < object[this.fieldStr]['sources'].length; i++){
        if(object[this.fieldStr]['sources'][i]){
          var confidenceString;
          var sourceInfo = object[this.fieldStr]['sources'][i];
          // create list element and add it to the list in the appropriate modal
          this.$rowTemplate = $('#source-template').find('li').clone().removeClass('hide');
          this.$rowTemplate.find('.src_name').html(sourceInfo.source);
          this.$rowTemplate.find('.src_del').attr('id', sourceInfo.id);
          this.$sourceList.append(this.$rowTemplate);  //append the row to the list
        }
      }
      if(object[this.fieldStr]['confidence']){
        this.$confLvl.val(object[this.fieldStr]['confidence']); 
        $('select').selectpicker('refresh');
      }
    },
    //this function dynamically assigns the element vars everytime a modal is triggered
    dynamicAssignments:function(event){
      $('select').selectpicker('refresh');  //refresh the select box
      this.$el_popoverTrigger = $(event.relatedTarget);
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
    setArrayIndexes:function(el_index1, el_field_id){
      //set gloabal indexes
      index1 = el_index1;
      field_id = el_field_id;
      //test and set index parameters for the modal views
      if(this.srcObjArr[index1] === undefined && this.srcObjArr[field_id] === undefined){
        this.srcObjArr[index1]=[];
        this.srcObjArr[index1][field_id] = [];
      }else if(this.srcObjArr[index1][field_id] === undefined){
        this.srcObjArr[index1][field_id] = [];
      }
    },
    getTempId:function(){
      var id = "_" + this.tempId;
      this.tempId++;
      return id;
    },
    updateConfidence: function(){
      object = this.objects[this.actualObject];
      object[field_id]['confidence'] = this.$confLvl.val();
    },
    addSources:function(){
      object = this.objects[this.actualObject];
      object[field_id]['sources'].push({source: this.$srcName.val(), id: this.getTempId()});
      this.$srcName.val("");
      this.render();
    },
    deleteSource:function(event){
      object = this.objects[this.actualObject];
      self = this;
      object[this.fieldStr]['sources'].forEach(function(source) {
        if(source.id == $(event.target).closest('p').attr('id')){
          index = object[self.fieldStr]['sources'].indexOf(source);
          object[self.fieldStr]['sources'].splice(index, 1);
        }
      });
      this.render();
    },
    update:function(){
      object = this.objects[this.actualObject];

      var objArr = [];
      var modelArr = Object.keys(this.objects);
      self = this;

      postData = {};
      for (var fieldStr in object) {
        if (object.hasOwnProperty(fieldStr)) {
          postData[fieldStr] = object[fieldStr];

          // Remove temp ids
          postData[fieldStr]['sources'].forEach( function(source) {
            if(source['id'][0] == "_"){
              source['id'] = 0;
            }
          });
        }
      }

      this.actualElement.find('.real-input').each(function(index, input){
        postData[input.id]['value'] = input.value;
      });

      console.log(postData);

      if(this.$mdObjId === 0){
        this.$mdObjId = "add";
      }

      $.ajax({
        type: "POST",
        url: window.location,
        data: {
          csrfmiddlewaretoken: window.CSRF_TOKEN,
          object: JSON.stringify(postData)
        },
        success: function(response, status){
          console.log(response);
          var err_str, err_id;
          self.actualElement.find('.error-message').each(function(index, error){
            $(error).html("");
          });
          if(response.errors !== undefined){
            for(var key in response.errors){
              err_str = response.errors[key];
              $("#" + key).siblings('.error-message').html("* " + err_str);
            }
          } else {
            url = window.location.href
            if(self.$mdObjId == "add"){
              url = url.replace('add', response.id);
            } else {
              url = url.replace(response.id + '/', '')
            }
            window.location.href = url;
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
