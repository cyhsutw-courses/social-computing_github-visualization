onload = function(){

    var width = 1440,
        height = 900;

    var force = d3.layout.force()
        //.linkDistance(function(d){return 400*(36-d.value)/36.0;})
        .linkDistance(function(d){ return 250;})
        //.linkStrength(function(d){ console.log(d);return (36.0-d.value)/36.0;})
        .charge(function(d){ return -1000;})
        .size([width, height]);

    var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

    d3.json("../json/star.json", function(error, graph) {

        force.nodes(graph.nodes)
             .links(graph.links)
             .start();


        // build the arrow.
        svg.append("svg:defs").selectAll("marker")
            .data(["end"])      // Different link/path types can be defined here
            .enter().append("svg:marker")    // This section adds in the arrows
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", function(d) { return 60; })
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .style("fill", function(d) { return '#ccc'; })
            .append("svg:path")
            .attr("d", "M0,-5L10,0L0,5");

        // add the links and the arrows
        var path = svg.append("svg:g").selectAll("path")
                    .data(force.links())
                    .enter().append("svg:path")
                    .attr("class", "link")
                    .attr("marker-end", "url(#end)");


        var gnodes = svg.selectAll('g.gnode')
                        .data(graph.nodes)
                        .enter()
                        .append('g')
                        .classed('gnode', true);

        var node = gnodes.append("circle")
                        .attr("r", function(d){ return Math.sqrt(d.weight+1)*4.0+10.0; })
                        .attr('class', 'node')
                        .style("fill", function(d) { return '#F49B6C'; })
                        .call(force.drag);


        gnodes.append("text").attr('class', 'label no-selection')
                             .text(function(d) {return d.name;})
                             .attr('x', function(d) {return -0.8*(Math.sqrt(d.weight+1)*4.0+10.0);})
                             .attr('y', 5);

        force.on("tick", function() {

            path.attr("d", function(d) {
                var x1 = d.source.x;
                var y1 = d.source.y;
                var x2 = d.target.x;
                var y2 = d.target.y;

                return "M" +
                    x1 + " " + y1 +
                    " L " + x2 + " " + y2;
            }).style('stroke-width', function(d){
                return Math.sqrt(d.value+1)/2.0;
            });

            gnodes.attr("transform", function(d) {
                return 'translate(' + [d.x, d.y] + ')';
            });

        });

    });
};
