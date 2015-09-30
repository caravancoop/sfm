var moduleController = (function(){
  var modCtrl = {
    init:function(){
      this.cacheDom();
      this.getModules();
      this.setDates();
      // this.bindEvents();
    },
    cacheDom:function(){
      this.$el_modal =  $('#complexFieldModal');
      this.dateWrapper = $('.date-wrapper');
      // this._srcModule = null;
      // this._versModule = null;
      // this._langModule = null;

    },
    setDates:function(){

      var d = new Date();
      var day, month, year, currYear, currMonth, currDay;
      var firstYear = 1950;
      currYear = d.getFullYear();
      var self = this;
      this.dateWrapper.each(function(){

        year = self.dateWrapper.find('.-sfm-year'); // set the year
        month = self.dateWrapper.find('.-sfm-month'); // set the month
        day = self.dateWrapper.find('.-sfm-day'); // set the date
        for(var y = firstYear; y <= currYear; ++y){
          $(year).append('<option value=' + y + '>' + y + '</option>');
        }
      });
      $('select').selectpicker('refresh');

    },

    // this function binds all the initial events to the selectors
    bindEvents:function(){
      // $('body').on('click', '.addPerson', this.update.bind(this));
    },
    getModules:function(){
      this._srcModule = source.publicAPI();
      this._langModule = language.publicAPI();
    },
    daysInMonth:function (month,year) {
      return new Date(year, month, 0).getDate();
    },
  };
  modCtrl.init();
  return {
    dispModObjs: function(){
      // console.log(modCtrl._srcModule);
      // console.log(modCtrl._langModule);
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
