var moduleController = (function(){
  var modCtrl = {
    init:function(){
      this.cacheDom();
      this.getModules();
      this.setDates();
      this.bindEvents();
    },
    cacheDom:function(){
      this.$el_modal =  $('#complexFieldModal');
      this.dateWrapper = $('.date-wrapper');
      this.month = null;
      this.year = null;
      this.datePickerArr = [];
      this.dPickerId = null;
      this.dt_id_index = null;
      this.dt_date_index = null;
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
      //for each date on the page
      this.dateWrapper.each(function(){
        self.dPickerId = $(this).data('date-target');
        year = self.dateWrapper.find('.-sfm-year'); // set the year
        month = self.dateWrapper.find('.-sfm-month'); // set the month
        day = self.dateWrapper.find('.-sfm-day'); // set the date
        //set the year
        self.setYear(firstYear,currYear,year);
        self.setMonth(currMonth,month);
      });
      $('select').selectpicker('refresh');

    },
    setYear:function(firstYear,currYear,year){
      for(var y = firstYear; y <= currYear; ++y){
        $(year).append('<option value=' + y + '>' + y + '</option>');
      }
    },
    setMonth:function(currMonth,month){
      var monthArr = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
      for(var m = 0; m < monthArr.length; ++m){
        $(month).append('<option value=' + (m+1) + '>' + monthArr[m] + '</option>');
      }
    },
    setDay:function(hiddenInputId){
      var year = this.datePickerArr[hiddenInputId]['year'];
      var month = this.datePickerArr[hiddenInputId]['month'];
      var $day = $('.date-wrapper[data-date-target='+ hiddenInputId ).find('.-sfm-day');
      // clear out day select
      $($day[0]).empty();
      var daysInMonth = this.daysInMonth(month, year);
      for(var d = 1; d <= daysInMonth; ++d){
        $($day[0]).append('<option value=' + d + '>' + d + '</option>');
      }
      $($day[0]).prop('disabled', false);
      $('select').selectpicker('refresh');
    },
    daysInMonth:function (month,year) {
      return new Date(year, month, 0).getDate();
    },
    setDateArrayIndexes:function(id_index, date_index){
      //set gloabal indexes
      this.dt_id_index = id_index;
      this.dt_date_index = date_index;
      //test and set index parameters for the modal views
      if(this.datePickerArr[this.dt_id_index] === undefined && this.datePickerArr[this.dt_date_index] === undefined){
        this.datePickerArr[this.dt_id_index]=[];
        this.datePickerArr[this.dt_id_index][this.dt_date_index] = [];
      }else if(this.datePickerArr[this.dt_id_index][this.dt_date_index] === undefined){
        this.datePickerArr[this.dt_id_index][this.dt_date_index] = [];
      }
    },
    // this function binds all the initial events to the selectors
    bindEvents:function(){
      $('.death-date.-sfm-year').on('change', this.changeYear.bind(this));
      $('.death-date.-sfm-month').on('change',this.changeMonth.bind(this)) ;
      $('.death-date.-sfm-day').on('change', this.changeDay.bind(this));
    },
    changeDay:function(event){
      var $hiddenInputId  = $(event.target).closest('.date-wrapper').data('date-target');
      var $input = $('#' + $hiddenInputId);
      var $tempDate = $input.val();
      var $newValue = $(event.target).val();
      this.setDateArrayIndexes($hiddenInputId, 'day');
      // store month in datePickerArr array
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = $newValue;
    },
    changeMonth:function(event){
      var $dateWrapper = $(event.target).closest('.date-wrapper');
      var $hiddenInputId  = $dateWrapper.data('date-target');
      var $input = $('#' + $hiddenInputId);
      var $tempDate = $input.val();
      var $newValue = $(event.target).val();
      this.setDateArrayIndexes($hiddenInputId, 'month');
      // store month in datePickerArr array
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = $newValue;
      this.setDay($hiddenInputId);

    },
    changeYear:function(event){
      var $dateWrapper = $(event.target).closest('.date-wrapper');
      var $hiddenInputId  = $dateWrapper.data('date-target');
      var $input = $('#' + $hiddenInputId);
      var $tempDate = $input.val();
      var $newValue = $(event.target).val();
      this.setDateArrayIndexes($hiddenInputId, 'year');
      // store month in datePickerArr array
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = $newValue;
      $dateWrapper.find('.-sfm-month').prop('disabled', false);
      $('select').selectpicker('refresh');
    },
    getModules:function(){
      this._srcModule = source.publicAPI();
      this._langModule = language.publicAPI();
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
