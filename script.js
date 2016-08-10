//Some gobals - at least for now
/*
Ok, so overall process: I have my old python script which will still fetch data for me. When D3 page is requested (or perhaps a button click even), D3 uses the bit of code below. URL points to whatever URL flask is running, now on local host. Eventually will have to be set to my server's IP.

Better yet, have that setup in my environment.csv file.

When Flask is called, he runs the kobod3.py script. That fetches the data, then refreshes the data.csv file that actually constains the data. Maybe I'll switch to a JSON file structure if that's better. Will see. But then I could probably just alter the python script so it fetches CSV instead of JSON? arggg... TBD.

Once that's done, I would like Flask to return a error/success code to D3. Not working for now. 

Then, the DB for D3 is updated - that's the data.csv
*/

//##TODO: have the URL for Flask be setup in a variables.csv file instead of hardcoded.
//##TODO: get the error/success response from Flask to D3 to work


//################## WORKING SNIPPET BELOW FOR FLASK CALLS
/*
Flask must be up & running @ URL. kobod3.py returns an error/success code (TBD), which flask returns as well to D3. It is shown & as "answer". Will allow error controls in case update requests fails, could try X times.
*/
// var URL = "http://127.0.0.1:5000/test"
// d3.text(URL, "text/plain", function(error, answer){
//     d3.select("body")
//         .append("div")
//         .text(answer);
// })
//################## WORKING SNIPPET  FOR FLASK CALLS - THE RESPONSE FROM FLASK CAN'T YET BE READ

//############# WORKING SNIPPET FOR DYNAMICALLY POPULATED DROPDOWN
/*
Populates the dropdown according to whatever values are listed in dropdown.csv
*/
d3.csv("dropdowns.csv", function(error, d){
    var options = [];
    if (error) throw error;
    d.forEach( function(x) {
        if (x["id"] == "sample") {
            options.push(x["value"]);
        }
    });
    d3.select("body").select("select.dropdown")
        .selectAll("option")
        .data(options)
        .enter()
        .append("option")
        .text(function(d){return d;})
    });
//############# WORKING SNIPPET FOR DYNAMICALLY POPULATED DROPDOWN


