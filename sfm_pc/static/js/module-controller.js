var moduleController = (function(){
  var modCtrl = {
    objects:{},
    actualObject:"",
    
    init:function(){
      this.cacheDom();
      //this.setDates();
      //this.setRadios();
      //this.bindEvents();
    },
    cacheDom:function(){
      this.objects['object-1'] = {"element": $('.content'), "data":{}}
      this.actualObject = "object-1";
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
    },
  };
  modCtrl.init();
  return {
    getActualObject: function(){
        return modCtrl.objects[modCtrl.actualObject];
    }
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
