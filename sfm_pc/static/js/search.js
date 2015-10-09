var moduleController = (function(){
    this.params = {};

    this.init = function(){
        this.loadPage();
        this.refreshResults();
        this.bindInputs();
        this.bindPopstate();
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
                $.each(data.keys, function(i, key){
                    row += "<td>" + object[key] + "</td>";
                })
                row += "</tr>";
                $('#object-linked-table').append(row);
            });
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
     * @param {{ element }}
     * Update the page with the new search parameter
     */
    this.updateParameter = function(elem){
        this.params[elem.attr('id')] = elem.val();
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
            update(elem);
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

    this.init();
})();

