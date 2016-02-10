var moduleController = (function(){
  var modCtrl = {
    objects:{},
    actualObject:"",
    actualObjectId:"",
    
    init:function(){
      this.cacheDom();
    },
    cacheDom:function(){
      this.objects['object-1'] = {"element": $('.content'), "data":{}}
      this.actualObject = "object-1";
      this.actualObjectElement = this.objects[this.actualObject]['element']
      this.actualObjectId = this.actualObjectElement.find('#fields-container').data('model-object-id');
      if(this.actualObjectId == "" || this.actualObjectId == "None"){
        this.actualObjectId = 0;
      }
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
    },
  };
  modCtrl.init();
  return {
    getActualObject: function(){
        return modCtrl.objects[modCtrl.actualObject];
    },
    getActualObjectName: function(){
        return modCtrl.actualObject;
    },
    getActualObjectId: function(){
        return modCtrl.actualObjectId;
    },
  };
})();

  //this Appends a clean function to the Array prototype
  Array.prototype.clean = function(deleteValue) {
    for (var i = 0; i < this.length; i++) {
      if (this[i] == deleteValue) {
        this.splice(i, 1);
        i--;
      }
    }
    return this;
  };
