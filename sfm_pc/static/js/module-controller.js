var moduleController = (function(){
  var modCtrl = {
    init:function(){
      this.cacheDom();
      this.getModules();
      // this.bindEvents();
    },
    cacheDom:function(){
      this._srcModule = null;
      this._versModule = null;
      this._langModule = null;
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      // this.$el_modal.on('shown.bs.modal', this.dynamicAssignments.bind(this));
      // this.$el_modal.on('click', '.--src-add-btn', this.addSources.bind(this));
      // this.$el_modal.on('click', '.src_del', this.deleteSource.bind(this));
      // $('body').on('click', '.addPerson', this.update.bind(this));
    },
    getModules:function(){
      this._srcModule = source.publicAPI();
    }
  };
  modCtrl.init();
  return {
    dispModObjs: function(){
      console.log(modCtrl._srcModule);
    }
  };
})();

(function(){
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
}());
