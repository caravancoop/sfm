var dateController = (function(){
  var dateCtrl = {
    monthArr:["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    dateIsSet:false,
    oldYear:null,
    oldMonth:null,
    oldDay:null,
    init:function(){
      this.cacheDom();
      this.setDates();
      this.setRadios();
      this.bindEvents();
    },
    cacheDom:function(){
      this.$el_modal =  $('#complexFieldModal');
      this.dateWrapper = $('.date-wrapper');
      this.datePickerArr = [];
      this.dPickerId = null;
      this.dt_id_index = null;
      this.dt_date_index = null;

      // this._srcModule = null;
      // this._versModule = null;
      // this._langModule = null;

    },
    setRadios:function(){
      $.each($('input[type="radio"]:checked'), function(index, element){
        id = $(element).attr('name');
        $('#' + id).val($(element).val());
      });
    },
    changeRadio:function(e){
      elem = $(e.target);
      $('#' + elem.attr('name')).val(elem.val());
    },
    setDates:function(){
      var d = new Date();
      var day, month, year, currYear, currMonth, currDay;
      var firstYear = 1950;
      var $input;
      currYear = d.getFullYear();
      var self = this;
      //for each date on the page
      this.dateWrapper.each(function(){

        self.dPickerId = $(this).data('date-target');
        year = $(this).find('.-sfm-year'); // set the year
        month = $(this).find('select.-sfm-month'); // set the month
        day = $(this).find('select.-sfm-day'); // set the date
        $input = $('.date-wrapper[data-date-target='+ self.dPickerId +']').find('input');
        var currentDate = $input.val();
        if( currentDate == undefined ){
          var tempArray = ['Year', '00', '00'];
        } else {
          var tempArray = currentDate.split("-");
        }
        self.oldYear = tempArray[0];
        self.oldMonth = tempArray[1];
        self.oldDay = tempArray[2];
        //set the year
        if($input.val() === ""){
          self.setYear(firstYear,currYear,year);
          self.setMonth(currMonth,month);
        }else{
          self.dateIsSet = true;
          self.setYear(firstYear,currYear,year);
          self.setMonth(currMonth,month);
        }

      });
      $('select').selectpicker('refresh');
    },
    setYear:function(firstYear,currYear,year){
      for(var y = firstYear; y <= currYear; ++y){
        $(year).append('<option value=' + y + '>' + y + '</option>');
      }
      if(this.dateIsSet){
        $(year).attr("title", this.oldYear);
      }
    },
    setMonth:function(currMonth,month){
      $(month).append('<option value="00">None</option>');
      for(var m = 0; m < this.monthArr.length; ++m){
        if(m < 9){
          $(month).append('<option value="0' + (m+1) + '">' + this.monthArr[m] + '</option>');
        } else {
          $(month).append('<option value=' + (m+1) + '>' + this.monthArr[m] + '</option>');
        }
      }
      if(this.dateIsSet){
        $(month).attr("title", this.monthArr[parseInt(this.oldMonth-1)]);
        $(month).prop('disabled', false);
        this.setOldDay(this.dPickerId);
      }
    },
    setOldDay:function(hiddenInputId){

      var $input = $('.date-wrapper[data-date-target='+ hiddenInputId  +']').find('input');
      var currentDate = $input.val();
      if( currentDate == undefined ){
        var tempArray = ['Year', '00', '00'];
      } else {
        var tempArray = currentDate.split("-");
      }
      var year = tempArray[0];
      var month = tempArray[1];
      var $day = $('.date-wrapper[data-date-target='+ hiddenInputId  +']').find('.-sfm-day');
      // clear out day select
      $($day[0]).empty();
      var daysInMonth = this.daysInMonth(month, year);
      for(var d = 0; d <= daysInMonth; ++d){
        if( d < 10 ){
          $($day[0]).append('<option value="0' + d + '">0' + d + '</option>');
        } else {
          $($day[0]).append('<option value=' + d + '>' + d + '</option>');
        }
      }
      this.setDateArrayIndexes(hiddenInputId, 'year');
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = year;
      this.setDateArrayIndexes(hiddenInputId, 'month');
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = month;
      this.setDateArrayIndexes(hiddenInputId, 'day');

      if(this.dateIsSet){
        if( this.oldDay != 0){
          $($day[0]).attr("title", this.oldDay);
        }
        this.datePickerArr[this.dt_id_index][this.dt_date_index] = this.oldDay;
      }
      $($day[0]).prop('disabled', false);
    },
    setDay:function(hiddenInputId){
      var year = this.datePickerArr[hiddenInputId]['year'];
      var month = this.datePickerArr[hiddenInputId]['month'];
      var $day = $('.date-wrapper[data-date-target='+ hiddenInputId  +']').find('.-sfm-day');
      // clear out day select
      $($day[0]).empty();
      var daysInMonth = this.daysInMonth(month, year);
      for(var d = 0; d <= daysInMonth; ++d){
        if( d < 10 ){
          $($day[0]).append('<option value="0' + d + '">0' + d + '</option>');
        } else {
          $($day[0]).append('<option value=' + d + '>' + d + '</option>');
        }
      }
      $($day[0]).prop('disabled', false);
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
      $('.approx-date.-sfm-year').on('change', this.changeYear.bind(this));
      $('.approx-date.-sfm-month').on('change',this.changeMonth.bind(this)) ;
      $('.approx-date.-sfm-day').on('change', this.changeDay.bind(this));
      $('input[type="radio"]').on('change', this.changeRadio.bind(this));
    },
    changeDay:function(event){
      var $hiddenInputId  = $(event.target).closest('.date-wrapper').data('date-target');
      var $input = $('#' + $hiddenInputId);
      var $tempDate = $input.val();
      var $newValue = $(event.target).val();
      this.setDateArrayIndexes($hiddenInputId, 'day');
      // store month in datePickerArr array
      this.datePickerArr[this.dt_id_index][this.dt_date_index] = $newValue;
      this.updateDates($hiddenInputId);
      $('select').selectpicker('refresh');
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
      this.updateDates($hiddenInputId);
      $('select').selectpicker('refresh');

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
      this.updateDates($hiddenInputId);
      $('select').selectpicker('refresh');
    },
    updateDates:function(hiddenInputId){
      var $input = $('.date-wrapper[data-date-target='+ hiddenInputId +']' ).find('input');
      var year = this.datePickerArr[hiddenInputId]['year'];
      var month = this.datePickerArr[hiddenInputId]['month'];
      var day = this.datePickerArr[hiddenInputId]['day'];
      // if($input.val() === ""){

        if(year === undefined){
          year = 00;
        }
        if(month === undefined){
          month = 00;
        }
        if(day === undefined){
          day = 00;
        }
      // }else{
      //   var currentDate = $input.val();
      //   var tempArray = currentDate.split("-");
      //   this.datePickerArr[hiddenInputId]['year'] = tempArray[0];
      //   this.datePickerArr[hiddenInputId]['month'] = tempArray[1];
      //   this.datePickerArr[hiddenInputId]['day'] = tempArray[2];
      //
      // }

      $input.val(year + '-' + month + '-' + day);

    }

  };
  dateCtrl.init();
})();
