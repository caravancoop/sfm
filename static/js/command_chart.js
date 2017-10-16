var CommandChart = CommandChart || {};

var CommandChart = {

    container: '#org-chart-container',
    edgelists: [],

    initCarousel: function() {

        // Add divs to carousel
        $.each(CommandChart.edgelists, function(index, value) {

            var carouselID = "command-chart-" + index;
            var carouselYearID = "command-chart-year-" + index;
            $('#org-chart-container').append('<div class="carousel-cell"><div class="chart-cell" id="' + carouselID + '"></div><div class="chart-date text-center" id="' + carouselYearID + '"></div></div>');

        });

        var org_count = CommandChart.edgelists.length;

        // Initialize carousel
        if (org_count > 1) {
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

    show: function() {

        // Build charts and add year
        $.each(CommandChart.edgelists, function(index, org_data) {

            $("#command-chart-" + index).spin()

            var command_chain_url = org_data['url'];
            var when = org_data['when'];

            $.getJSON(command_chain_url, {index: index}, function(obj) {

                var idx = obj['index'];
                var cellID = "command-chart-" + idx;
                var cellYearID = "command-chart-year-" + idx;
                $('#' + cellID).spin(false);

                var node_list = CommandChart.addMultiFont(obj['nodes']);
                var edge_list = (obj['edges']);

                var nodes = new vis.DataSet(node_list);
                var edges = new vis.DataSet(edge_list);

                var container = document.getElementById(cellID);
                var data = {
                    nodes: nodes,
                    edges: edges,
                };

                var options = {
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
                            direction: 'UD', // Inverts chart
                            sortMethod: 'directed',
                        }
                    },
                    interaction: {
                        zoomView: true,
                        dragView: true,
                        hover:true,
                    },
                };

                var network = new vis.Network(container, data, options);

                if (typeof when != 'undefined') {
                    $('#' + cellYearID).append(when);
                } else {
                    $('#' + cellYearID).append('No known end date');
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

            });

        });
    }
}
