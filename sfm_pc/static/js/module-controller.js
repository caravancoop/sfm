var moduleController = (function(){
  var modCtrl = {
    init:function(){
      this.cacheDom();
      this.getModules();
      // this.bindEvents();
    },
    cacheDom:function(){
      this.$el_modal =  $('#complexFieldModal');
      this._srcModule = null;
      this._versModule = null;
      this._langModule = null;
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      // $('body').on('click', '.addPerson', this.update.bind(this));
    },
    getModules:function(){
      this._srcModule = source.publicAPI();
      this._langModule = language.publicAPI();
    }
  };
  modCtrl.init();
  return {
    dispModObjs: function(){
      console.log(modCtrl._srcModule);
      console.log(modCtrl._langModule);
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

  Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
