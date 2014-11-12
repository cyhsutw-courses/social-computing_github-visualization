onload = function(){


    var langs = [
        'Java',
        'Python',
        'PHP',
        'JavaScript',
        'CoffeeScript',
        'C',
        'Objective-C',
        'CSS',
        'Ruby',
        'Haxe',
        'C++',
        'C#',
        'Emacs Lisp',
        'Objective-J',
        'Scala',
        'Go',
        'Groovy',
        'PowerShell',
        'Perl',
        'VimL',
        'Shell',
        'Dart',
        'Clojure',
        'Haskell'
    ];
    var width = 1280,
        height = 800;

    var color = d3.scale.category20();

    var force = d3.layout.force()
        .charge(-1000)
        .linkDistance(250)
        .gravity(0.1)
        .size([width, height]);

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height);

    d3.json("json/network.json", function(error, graph) {
        force
            .nodes(graph.nodes)
            .links(graph.links)
            .start();

      var link = svg
                    .selectAll(".link")
                    .data(graph.links)
                    .enter()
                    .append("line")
                .attr("class", "link")
                .style("stroke-width", function(d) {
                    return d.value;
                });

      var node = svg.selectAll(".node")
          .data(graph.nodes)
        .enter().append("circle")
          .attr("class", "node")
          .attr("r", function(d){ return 8.0; })
          .style("fill", function(d) { return color(d.group); })
          .call(force.drag);



      node.append("title")
          .text(function(d) {
               return d.name;
           });

      force.on("tick", function() {
          link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });


      });

    });
};
