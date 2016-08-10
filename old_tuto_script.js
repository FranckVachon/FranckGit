/* Script to go with the Basic tuto pages
All of the code below goes with Alignedleft.com/tutorials/d3. The capped titles in the comments refer to section of that tutorials. I have deviated in some way to experiment further with & better understand, but the basic principles are the same.
*/
// ######## GLOBAL CONSTANTS ############
h = 300 //Height
w = 700 //Width



//ADDING ELEMENTS
//d3.select("body").append("p").text("New paragraph!");
//Note that the above is exactly the same as:
/*
d3.select("body")
    .append("p")
    .text("New paragraph!");
*/

//CHAINING METHODS SCRIPT
d3.select("body").text("Text set directly on the body - whips out any existing element without the seletion on which .text() is called");
d3.select("body").append("p").text("New paragraph! Because this one is appended after the body.text(), it still works");

// Equivalent of the above, without using chaining methods - yields exactly the same results
//var body = d3.select("body");
//body.text("Text set directly on the body - whips out any existing element without the seletion on which .text() is called");
//var p = body.append("p");
//p.text("New paragraph! Because this one is appended after the body.text(), it still works");

//BINDING DATA
//The data - could be JSON, csv etc but for now let's just hard-code stuff

/*Below I had to append div element before doing the P thing - because I already appended a P element above. So when D3 looked up the data, it saw there already was 1 p element, so I considered it only needed to append one element to have as many p as data point. Because I appended a div element, the selection/reference changed and was thus set on that new div, which had no P element. So it added 5 p to that div, unaffected by the above body p element I appeneded earlier. I then used the css selector in style.css to make them smaller font-size*/


//################ The dataset below is used throughout the code #####################
var dataset1 = [1,2,4,8,16];



d3.select("body").append("div")
    .selectAll("p")
    .data(dataset1)
    .enter()
    .append("p")
    .text("Added P elements based on dataset")

//USING YOUR DATA
/*
Similar to the previous one - but using an JS anonymous function, which function somewhat like lampda functions in Python. I could also use ca regural function (e.g. named). Nothinga  special about "d" in the anonymous function, it's just a placeholder you define. Convention in D3 examples seems to be to use d for that purpose, like i-j-k for loops etc

Likewise, you can use functions to determine other attribute, either based on the data or not. In that case I set the color based on the value
*/

d3.select("body").append("div")
    .selectAll("p")
    .data(dataset1)
    .enter()
    .append("p")
    .text(function(d) {return d;})
    .style("color", function(d) {
        if (d<7){
            return "red";
        } else {
            return "blue";
        }
        });
//DRAWING DIV
/*
NOTE: next section. SVG PRIMER, will highlight a much better approach to grouping things - an svg. So typcally you wouldn't introduce random divs like below.

Other than that, I basically used a similar syntax to what is above. I used the .classed() method to assig a "bar" class to my divs in the graph, then I used the div.bar CSS selector to assign it a global style. I've also classed the wrapper DIV for the whole graph, in case I want later to use CSS to style all my graphs in some ways.
*/
d3.select("body").append("div").classed("graph", true)
d3.select("body").select("div.graph")
    .selectAll("div")
    .data(dataset1)
    .enter()
    .append("div")
    .classed("bar",true)
    .style("height", function(d) { return 5*d + "px";});

// AN SVG PRIMER
/*
The SVG is basically the canvas for all our graphic representation. Generating random data (more interesting), and using that as a dataset
*/

// new_circle = [cx, cy, r]
var dataset_svg = []
for (var i=0; i<20; i++) {
    var new_circle = [Math.round(Math.random()*w), Math.round(Math.random()*h), Math.round(Math.random()*25)]
    dataset_svg.push(new_circle);
}

var svg = d3.select("body") //We create our SVG canvas, then we'll set its properties with attr()
    .append("svg")  
    .attr("width", w)
    .attr("height", h);

//We'll create a bunch of circles for our new data. Assigning the svg.selectAll() method to a variable will allow us to iterate through all the circles created. I assign a class to those circles when I create them, so I can use CSS to batch-style them
var circles =  svg.selectAll("circle")
                .data(dataset_svg)
                .enter()
                .append("circle")
                .classed("pts", true);
var circle_text = svg.selectAll("text")
    .data(dataset_svg)
    .enter()
    .append("text")
    .text(function(d,i) {return i})
    .classed("pts_labels", true)

// Awesomeness: we don't NEED to create a loop to iterate through each members of our circles variable - D3 understands that's what we want to do and he does it for us. Setting each circle's attribute based on the dataset randomly generated
svg.selectAll("circle")
    .attr("cx", function(d){return d[0]})
    .attr("cy", function(d){return d[1]})
    .attr("r", function(d) {return d[2]}) 
svg.selectAll("text")
    .attr("x", function(d) {return d[0]})
    .attr("y", function(d) {return d[1]})

//SCALES
/*
Now, we'll set the above scatter-plot on some decent scale
*/

var xscale = d3.scale.linear();
var yscale = d3.scale.linear();
var rscale = d3.scale.linear();
var padding = 30;

xscale.domain([0, d3.max(dataset_svg, function(d) {return (d[0] + d[2]);})])     //We want to take the diameter into consideration
    .range([padding,w-padding]);
yscale.domain([0, d3.max(dataset_svg, function(d) {return (d[1] + d[2]);})])     //We want to take the diameter into consideration
    .range([h-padding,padding]);
rscale.domain([d3.min(dataset_svg, function(d) {return d[2]}), d3.max(dataset_svg, function(d) {return d[2]})])
    .range([1,20]);

//Because I don't want to destroy the previous tutorial where I create the circles, I'll just re-edit their attr here using the scales I have created

svg.selectAll("circle")
    .attr("cx", function(d){return xscale(d[0])})
    .attr("cy", function(d){return yscale(d[1])})
    .attr("r", function(d){return rscale(d[2])});

svg.selectAll("text")
    .attr("x", function(d) {return xscale(d[0])})
    .attr("y", function(d) {return yscale(d[1])});

//AXES

/*
Setting some axes for that scatterplot.
*/

var xaxis = d3.svg.axis()
    .scale(xscale)
    .orient("bottom")
    .ticks(5);
var yaxis = d3.svg.axis()
    .scale(yscale)
    .orient("left")
    .ticks(5);

svg.append("g")
    .classed("axis", true)
    .attr("transform", "translate(0," + (h-padding) + ")")
    .call(xaxis);
svg.append("g")
    .classed("axis", true)
    .attr("transform", "translate(" + padding + ",0)")
    .call(yaxis);
