//route from app.py (where the json data comes from)
const pythonUrl = "/shots";

//reads the json data from the route and then process the function
d3.json(pythonUrl).then(function(data) {

    //convert the json data into an array that can be iterated over
    pythonData = data[0];

    var game_shot_dict = {};
    var game_shot_list = [];

    //create dictionary from json data
    for (var i = 0; i < pythonData['GAME_ID'].length; i++){   
        game_shot_dict = {game_id: pythonData['GAME_ID'][i],
                                Shot_Made_Flag: pythonData['SHOT_MADE_FLAG'][i],
                                LOC_X: pythonData['LOC_X'][i],
                                LOC_Y: pythonData['LOC_Y'][i]
                              };
       
          game_shot_list.push(game_shot_dict);
    }
      
    //converts the game_data into a unique list of games
    let game_list = [...new Set(pythonData['GAME_ID'])]; 
    
    //element for drop down box
    var select = document.getElementById("example-select");
    
    //creates drop down list
    for(i in game_list) {
          select.options[select.options.length] = new Option(game_list[i],i);
    }

    // Select the submit button
    var filter_button = d3.select("#filter-btn");
    filter_button.on("click", function () {
       
      // Prevent the page from refreshing
      d3.event.preventDefault();

      // grabs the text from the input selection and
      // filters the data the game entered in the form once button is clicked
      var gameInput_value = d3.select("#example-select option:checked").text();
      var filteredInput = game_shot_list.filter(game_shot_list => game_shot_list.game_id === gameInput_value);
      
       //loops throug the filtered data to place in each array for assinging to html td's
      var game_output = []
      for (i in filteredInput) {
              game_output.push(filteredInput[i]);
      }
      console.log("game output",game_output);

      var selection = d3.select(".shots")
                        .selectAll("div")
                        .data(game_output)
                        .text(function(d){
                                return 'game ' + d['game_id'] + ' x loc ' + d['LOC_X'] + ' y loc ' + d['LOC_Y'];
                            });
           selection.enter()
                    .append("div")
                    .text(function(d){
                            return 'game ' + d['game_id'] + ' x loc ' + d['LOC_X'] + ' y loc ' + d['LOC_Y'];
                        });         
            
            selection.exit().remove();
        //filter to made shots, put xaxis into list
        var x_make_data = game_output.filter(game_output => game_output['Shot_Made_Flag'] === 1);
        var x_make=[];
        x_make_data.forEach(x_make_data => {
            x_make.push(x_make_data['LOC_X']);
        });
        //filter to made shots, put yaxis into list
        var y_make_data = game_output.filter(game_output => game_output['Shot_Made_Flag'] === 1);
        var y_make=[];
        y_make_data.forEach(y_make_data => {
            y_make.push(y_make_data['LOC_Y']);
        });
        
        var trace_make = {
            x: x_make,
            y: y_make,
            mode: 'markers',
            type: 'scatter',
            marker: {'color':'blue','size':5}
            };
        //filter to miss shots, put xaxis into list
        var x_miss_data = game_output.filter(game_output => game_output['Shot_Made_Flag'] === 0);
        var x_miss=[];
        x_miss_data.forEach(x_miss_data => {
            x_miss.push(x_miss_data['LOC_X']);
        });
        
        //filter to miss shots, put yaxis into list
        var y_miss_data = game_output.filter(game_output => game_output['Shot_Made_Flag'] === 0);
        var y_miss=[];
        y_miss_data.forEach(y_miss_data => {
            y_miss.push(y_miss_data['LOC_Y']);
        });

        var trace_miss = {
            x: x_miss,
            y: y_miss,
            mode: 'markers',
            type: 'scatter',
            marker: {'color':'red','size':5}
            };
        
        // court_shapes comes from plotly_shapes.js
        var layout = {title:'Shots by Kemba Walker in 2018-19',
                        showlegend:true,
                        xaxis:{showgrid:true,range:[-300,300]},
                        yaxis:{showgrid:true,range:[-100,600]},
                        height:600,
                        width:650,
                        shapes:court_shapes};

        plot_data = [trace_make,trace_miss]
        
        //'myScatter' is the html id
        Plotly.newPlot('myScatter', plot_data, layout);
   });

});

