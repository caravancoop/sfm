var CommandChart = CommandChart || {};

var CommandChart = {

    container: '#org-chart-container',
    dateMissingString: '',
    edgelists: [],
    options: {
        nodes: {
            shape: 'box',
            fixed: {
                x:true,
                y:true,
            },
            shapeProperties: {
                borderRadius: 2,
            },
            color: {
                background: '#f4f4f4',
                border: '#D6D6D6',
                highlight: { // Change color of node on click
                    background: '#EBEBEB',
                    border: '#D6D6D6',
                },
                hover: {
                    background:'#e0e0e0',
                    border:'#D6D6D6',
                },
            },
            font: {
                color: '#777777',
                face: 'Open Sans',
            },
        },
        layout: {
            hierarchical: {
                levelSeparation: 100, // Distance between levels
                nodeSpacing: 300, // Distance between nodes
                direction: 'DU', // Inverts chart
                sortMethod: 'directed',
            }
        },
        interaction: {
            zoomView: true,
            dragView: true,
            hover:true,
        },
    },

    initCarousel: function() {

        // Add divs to carousel
        $.each(CommandChart.edgelists, function(index, value) {

            var carouselID = "command-chart-" + index;
            var carouselYearID = "command-chart-year-" + index;
            $('#org-chart-container').append('<div class="carousel-cell"><div class="chart-cell" id="' + carouselID + '"></div><div class="chart-date text-center" id="' + carouselYearID + '"></div></div>');

        });

        var org_count = CommandChart.edgelists.length;

        // Initialize carousel
        if (org_count > 0) {
            var orgCarousel = $('#org-chart-container').flickity({
                initialIndex: org_count - 1,
                wrapAround: true,
                draggable: true,
            });
        };
    },

    addMultiFont: function(node_list) {
        var new_list = node_list.map(function(item) {
            item['font'] = {multi: true};
            return item
        });

        return new_list
    },

    getCommandChain: function(edgeList) {
        var index = CommandChart.edgelists.indexOf(edgeList);
        $("#command-chart-" + index).spin();
        return $.getJSON(edgeList.url, {index: index});
    },

    show: function() {

        // Build charts and add year
        var display_charts = false;

        $.when.apply(
            $, CommandChart.edgelists.map(CommandChart.getCommandChain)
        ).then(function () {
            var commandChains = CommandChart.edgelists.length === 1
                ? [arguments]
                : arguments;

            $.each(CommandChart.edgelists, function(index, org_data) {
                var when = org_data['display_date'];
                var obj = commandChains[index][0];

                var idx = obj['index'];
                var cellID = "command-chart-" + idx;
                var cellYearID = "command-chart-year-" + idx;
                $('#' + cellID).spin(false);

                if (obj['nodes'].length > 0){
                    display_charts = true;
                    var node_list = CommandChart.addMultiFont(obj['nodes']);
                    var edge_list = (obj['edges']);

                    var nodes = new vis.DataSet(node_list);
                    var edges = new vis.DataSet(edge_list);

                    var container = document.getElementById(cellID);
                    var data = {
                        nodes: nodes,
                        edges: edges,
                    };

                    var network = new vis.Network(container, data, CommandChart.options);

                    if (typeof when != 'undefined' && when !== '') {
                        $('#' + cellYearID).append(when);
                    } else {
                        $('#' + cellYearID).append(CommandChart.dateMissingString);
                    }

                    // Bind click event to individual nodes
                    network.on("selectNode", function (params) {
                        if (params.nodes.length === 1) {
                            node = nodes.get(params.nodes[0]);
                            window.location = node.url;
                        }
                    });

                    // Transform cursor (from hand into pointed finger and back again)
                    network.on("hoverNode", function (params) {
                        network.canvas.body.container.style.cursor = 'pointer'
                    });

                    network.on("blurNode", function (params) {
                        network.canvas.body.container.style.cursor = 'default'
                    });
                } else {
                    $('#org-chart-container').flickity('remove', $('#' + cellID).parent())
                }

            })

            if (!display_charts) {
                // Hide the sidebar links and the command chain section
                $('a[href="#chain-of-command"],#command-chain').hide();
            } else {
                var $cells = $('.carousel-cell');
                if ($cells.length > 1) {
                    // Select the last cell, representing the latest command chart
                    $('#org-chart-container').flickity('selectCell', $cells.length - 1);
                } else {
                    console.log('Skipping cell selection...');
                }
            }

        })
    }
}
