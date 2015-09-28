var version = (function(){
  var index1, index2;
  var verModule = {
    verObjArr:[],
    fieldStrArr : [],
    modelArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      this.getAll();
    },
    getAll:function(){
      var self = this;
      $('.modalBox').each(function(){
        var versions = $(this).data('remote').replace('/modal', "");
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
        //set the version object array indexes
        self.setArrayIndexes(model, fieldStr);
        patt = new RegExp("/version");  //filter out the translate path
        $.ajax({
          async: false,
          context:self,
          type: "GET",
          url: versions,
          dataType: "json",
          // success callback function
          success: function (response) {
            for (var i in response) {
              if(patt.test(versions)){ //test if path contains versions
                this.verObjArr[index1][index2][this.verObjArr[index1][index2].length] = response[i];
              }
            }
          },
          error: function (request, status, error) {
            console.log(error);
          }
        });
      });
    },
    cacheDom:function(){
      this.$el_modal =  $('#complexFieldModal');
      this.$el_popoverTrigger = null; //get the btn trigger for the modal
      this.$txtInput = null; //get the input field that corresponds to the current modal

      this.fieldStr = null;
      this.dataModId = null;
      this.$rowTemplate = null;
      this.$versionList = null;
      this.$verLanguage = null;
      this.$verTrans = null;

    },
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
    },
    render:function(){
      this.$versionList.find('li').empty();//delete old list
      this.verObjArr[this.dataModId][this.fieldStr].clean();
      for(var i = 0; i < this.verObjArr[this.dataModId][this.fieldStr].length; i++){

        var versionInfo = this.verObjArr[this.dataModId][this.fieldStr][i];
          // create list element and add it to the list in the appropriate modal
        this.$rowTemplate = $('#version-template').find('li').clone().removeClass('hide');
        this.$rowTemplate.find('.ver_vers').html(versionInfo.value);
        this.$rowTemplate.find('.ver_src-conf').html(versionInfo.sources);
        this.$rowTemplate.find('.ver_rev').attr('id', versionInfo.id);

        this.$versionList.append(this.$rowTemplate);  //append the row to the list
      }
    },
    dynamicAssignments:function(event){
      $('select').selectpicker('refresh');  //refresh the select box
      this.$el_popoverTrigger = $(event.relatedTarget);
      // console.log(this.$el_popoverTrigger[0]);
      this.$verLanguage = this.$el_modal.find('.--ver-lang');   //version language name
      this.$txtInput = $('#' + this.$el_popoverTrigger[0].dataset.fieldStr);
      this.$versionList = $('.versions_list');
      this.fieldStr = this.$el_popoverTrigger[0].dataset.fieldStr;
      this.dataModId = this.$el_popoverTrigger[0].dataset.modelId;
      this.render();
      this.setArrayIndexes(this.$el_popoverTrigger[0].dataset.modelId, this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    setArrayIndexes:function(el_index1, el_index2){
      //set gloabal indexes
      index1 = el_index1;
      index2 = el_index2;
      //test and set index parameters for the modal views
      if(this.verObjArr[index1] === undefined && this.verObjArr[index2] === undefined){
        this.verObjArr[index1]=[];
        this.verObjArr[index1][index2] = [];
      }else if(this.verObjArr[index1][index2] === undefined){
        this.verObjArr[index1][index2] = [];
      }
    },
  };
  verModule.init();
  return {
    publicAPI: function(){
      return verModule.verObjArr;
    }
  };
}());
