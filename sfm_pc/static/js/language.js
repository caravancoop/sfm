var language = (function(){
  var index1, index2;
  var langModule = {
    langObjArr:[],
    fieldStrArr : [],
    modelArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      // this.getAll();
    },
    getAll:function(){
      this.langObjArr = [];
      this.fieldStrArr = [];
      this.modelArr = [];
      var self = this;
      $('.modalBox').each(function(){
        var languages = $(this).data('remote').replace('/modal', "");
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
        //set the language object array indexes
        self.setArrayIndexes(model, fieldStr);
        patt = new RegExp("/translate");  //filter out the translate path
        $.ajax({
          async: false,
          context:self,
          type: "GET",
          url: languages,
          dataType: "json",
          // success callback function
          success: function (response) {
            for (var i in response) {
              if(patt.test(languages) && typeof response[i] !== 'function'){ //test if path contains languages
                this.langObjArr[index1][index2][this.langObjArr[index1][index2].length] = response[i];
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
      // this.$modalHeader = null; //modal header class
      this.$addBtn = null;
      this.fieldStr = null;
      this.dataModId = null;
      this.$rowTemplate = null;
      this.$languageList = null;
      this.$langName = null;
      this.$langTrans = null;
    },
    bindEvents:function(){
      this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      this.$el_modal.on('click', '.--lang-add-btn', this.addLanguages.bind(this));
      this.$el_modal.on('change input', '.--lang-name', this.autoFill.bind(this));
    },
    render:function(){
      this.$languageList.find('li').empty();//delete old list

      this.langObjArr[this.dataModId][this.fieldStr].clean();
      for(var i = 0; i < this.langObjArr[this.dataModId][this.fieldStr].length; i++){

        var languageInfo = this.langObjArr[this.dataModId][this.fieldStr][i];
          // create list element and add it to the list in the appropriate modal
        this.$rowTemplate = $('#language-template').find('li').clone().removeClass('hide');
        this.$rowTemplate.find('.lang_name').html(languageInfo.lang);
        this.$rowTemplate.find('.lang_trans').html(languageInfo.value);

        this.$languageList.append(this.$rowTemplate);  //append the row to the list
      }
    },
    dynamicAssignments:function(event){
      $('select').selectpicker('refresh');  //refresh the select box
      this.$el_popoverTrigger = $(event.relatedTarget);
      // console.log(this.$el_popoverTrigger[0]);
      this.$langName = this.$el_modal.find('.--lang-name');   //source name
      this.$langTrans = this.$el_modal.find('.--lang-trans');   //level of confidence
      this.$addBtn = this.$el_modal.find('.--lang-add-btn')[0]; //add button
      this.$txtInput = $('#' + this.$el_popoverTrigger[0].dataset.fieldStr);
      this.$modalHeader = this.$el_modal.find('.modal-header');
      this.$mdObjName = this.$modalHeader.data('field-object-name');
      this.$mdObjId = this.$modalHeader.data('field-object-id');
      this.$mdFieldName = this.$modalHeader.data('field-attr-name');
      this.$mdModalType = this.$modalHeader.data('modal-type');
      this.$languageList = $('.languages_list');
      this.fieldStr = this.$el_popoverTrigger[0].dataset.fieldStr;
      this.dataModId = this.$el_popoverTrigger[0].dataset.modelId;
      this.getAll();
      this.render();
      this.setArrayIndexes(this.$el_popoverTrigger[0].dataset.modelId, this.$el_popoverTrigger[0].dataset.fieldStr);
    },
    setArrayIndexes:function(el_index1, el_index2){
      //set gloabal indexes
      index1 = el_index1;
      index2 = el_index2;
      //test and set index parameters for the modal views
      if(this.langObjArr[index1] === undefined && this.langObjArr[index2] === undefined){
        this.langObjArr[index1]=[];
        this.langObjArr[index1][index2] = [];
      }else if(this.langObjArr[index1][index2] === undefined){
        this.langObjArr[index1][index2] = [];
      }
    },
    addLanguages:function(){
      this.langObjArr[index1][index2][this.langObjArr[index1][index2].length] = {lang: this.$langName.val(), value: this.$langTrans.val()};
      this.update();
      this.render();
    },
    autoFill:function(){
      console.log(this.$langName);
      this.$langName.autocomplete({
        // request options from the server.
        source: "/translate/languages/autocomplete",
      });
    },
    update:function(){
      var postData = {
    		"value" : this.$langTrans.val(),
    		"lang" : this.$langName.val()
    	};
      $.ajax({
        context:langModule,
    		type: "POST",
    		url: "/" + window.LANG + "/translate/" + this.$mdObjName + "/" + this.$mdObjId + "/" + this.$mdFieldName + "/",
    		data: {
    			csrfmiddlewaretoken: window.CSRF_TOKEN,
    			translation: JSON.stringify(postData)
    		},
    		success: function (response, status) {
    			console.log(response);
    			//on success, clear fields
          this.$langName.val("");
          this.$langTrans.val("");
          this.getAll();
          this.render();
          console.log("success");
    		},
    		error: function (request, status, error) {
    			console.log(status);
    			console.log(error);
    		}
    	});
    }
  };
  langModule.init();
  return {
    publicAPI: function(){
      return langModule.langObjArr;
    }
  };
}());
