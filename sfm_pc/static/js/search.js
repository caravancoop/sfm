var moduleController = (function(){
    this.params = {};

    this.init = function(){
        this.loadPage();
        this.refreshResults();
        this.bindInputs();
        this.bindPopstate();
        this.bindOrderby();
    }

    /**
     * Call the endpoint to get the results list
     */
    this.refreshResults = function(){
        self = this;
        $.ajax({
            type: 'get',
            url: window.location.origin + window.location.pathname + "search/",
            data: this.params,
            dataType: 'json',
            success: function(data) {
                if(data.success == true){
                    self.populateResults(data);
                }
            }
        });
    }

    /**
     * @param {object} data
     * @return void
     * Populate the results list
     */
    this.populateResults = function(data){ 
        if(data){
            $('#object-linked-table').html("");
            $.each(data.objects, function(index, object){
                row = "<tr data-object-id='" + object['id'] + "'>";
                len = data.keys.length;
                $.each(data.keys, function(i, key){
                    if(i == len - 1){
                      row += "<td><a href='" + object['id'] + "'></a>" + object[key] + "<a href='delete/" + object['id'] + "/'><i class='fa fa-trash fa-lg pull-right'></i></a></td>";
                    } else {
                      row += "<td><a href='" + object['id'] + "'></a>" + object[key] + "</td>";
                    }
                })
                row += "</tr>";
                $('#object-linked-table').append(row);
            });
            $("#object-linked-table tr").click( function() {
                window.location = $(this).find('a').attr('href');
            });

            $("#paginator-content").html(data.paginator);
            this.bindPaginator();
            $("#result-number").html(data.result_number);
        }
    }

    /*
     * Load the page from the current url and set the form values
     */
    this.loadPage = function(){
        this.paramsExtract();

        for(field in this.params){
            $("[ID='"+field+"']").not("[type=radio]").val(decodeURIComponent(this.params[field]));
        }
        if(typeof this.params['orderby'] !== 'undefined'){
            col = $("#result-table").find('[data-orderby="'+this.params['orderby']+'"]');
            if( this.params['order'] == 'ASC' ){
                col.addClass('dropup');
            }
        }
    }

    /*
     * @return {{ object }}
     * Extract parameters from url
     */
    this.paramsExtract = function(){
        var qstring = window.location.hash;
        this.params = {}

        if(qstring){
            var qsplit = qstring.substr(1).split('&');

            for (var params in qsplit) {
                if(params != "clean"){
                    var pair = qsplit[params].split('=');
                    this.params[pair[0]] = decodeURIComponent(pair[1]);
                }
            }
        }
    }

    /*
     * @param {{ key, value }}
     * Update the page with the new search parameter
     */
    this.updateParameter = function(key, value){
        this.params[key] = value;
        refreshResults(this.params);
        history.pushState({}, "",
            window.location.origin +
            window.location.pathname +
            "?#" + $.param(this.params));
    }

    /*
     * Bind input fields
     */
    this.bindInputs = function(){
        update = this.updateParameter;
        $("select, input").on("change", function(e) {
            elem = $(e.target);
            update(elem.attr('id'), elem.val());
        }).keyup(function(event){
            if(event.keyCode == 13){
                $(this).trigger("change");
            }
        }); 
    }

    /*
     * Bind popstate event
     */
    this.bindPopstate = function(){
        self = this;
        window.onpopstate = function(e){
        e.preventDefault();
            this.loadPage();
            this.refreshResults();
        }
    }


    /*
     *
     */
    this.bindOrderby = function(){
        self = this;
        cols = $("#result-table th")
        $.each(cols, function(index, col){
            $(col).on('click', function(){
                orderby = $(this).data('orderby');
                if( self.params['orderby'] == orderby ){
                    if( self.params['order'] == "DESC" ){
                        $(this).addClass('dropup');
                        self.updateParameter('order', 'ASC');
                    } else {
                        self.updateParameter('order', 'DESC');
                    }
                } else {
                    old_col = $("#result-table").find('[data-orderby="'+self.params['orderby']+'"]');
                    old_col.removeClass('dropup');
                    self.params['orderby'] = orderby;
                    self.updateParameter('order', 'DESC');
                }
            });
        });
    }

    /*
     *
     */
    this.bindPaginator = function(){
        self = this;
        $('#paginator-content li a').on('click', function(){
            self.updateParameter('page', $(this).data('page-id'));
        });
    }
    this.init();
})();

