var language = (function(){
  var langModule = {
    langObjArr:[],
    fieldStrArr : [],
    modelArr : [],
    init:function(){
      this.cacheDom();
      this.bindEvents();
      this.getAll();
    },
    getAll:function(){
      // var self = this;
      // $('.modalBox').each(function(){
      //   var languages = $(this).data('remote').replace('/modal', "");
      //   var model = $(this).data('model-id');
      //   var fieldStr = $(this).data('field-str');
      //   if (self.$mdObjId === null || self.$mdObjId === undefined || self.$mdObjId === ""){
      //     self.$mdObjId =  $(this).data('model-object-id');
      //   }
      //   //if the fieldStr is not in array push it
      //   if ($.inArray(fieldStr, self.fieldStrArr) === -1){
      //     self.fieldStrArr.push(fieldStr);
      //   }
      //   //if the model is not in array push it
      //   if ($.inArray(model, self.modelArr) === -1){
      //     self.modelArr.push(fieldStr);
      //   }
      //   //set the source object array indexes
      //   self.setArrayIndexes(model, fieldStr);
      //   patt = new RegExp("/source");  //filter out the sources path
      //   $.ajax({
      //     async: false,
      //     context:self,
      //     type: "GET",
      //     url: sources,
      //     dataType: "json",
      //     // success callback function
      //     success: function (response) {
      //       for (var i in response) {
      //         if(patt.test(sources)){ //test if path contains sources
      //           this.sourceObjArr[index1][index2][this.sourceObjArr[index1][index2].length] = response[i];
      //         }
      //       }
      //     },
      //     error: function (request, status, error) {
      //       console.log(error);
      //     }
      //   });
      // });
    },
    cacheDom:function(){

    },
    bindEvents:function(){

    },
    render:function(){

    },
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
  };
  langModule.init();
  return {
    publicAPI: function(){
      return langModule.langObjArr;
    }
  };
}());
