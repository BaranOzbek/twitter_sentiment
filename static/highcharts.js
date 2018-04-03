var negWords = [];
var posWords = [];
var negTweets = [];
var posTweets = [];
//Update grid when new data gets recieved, if selected word is updated.
var selectedWord = null;

//Function processing line graph data for input
function parseData(data){
  var line_temp = [];
  for(i in data){
    tweet_date = Date.parse(data[i][0]);
    line_temp.push([(tweet_date), data[i][1]]);
  }
  return line_temp;
}

//Function loads up initially without event, populates values used in streaming live.
$.getJSON('http://127.0.0.1:8080/getdata',
 function(data){
  //Retrieve all data to be inputted into the graphs
  var line_temp = parseData(data['0']);
  posWords = data['Positive'];
  negWords = data['Negative'];
  posTweets = data['PositiveTweets'];
  negTweets = data['NegativeTweets'];

  updateWords();

  Highcharts.chart('highChartsLine', {
      chart: {
          backgroundColor: '#F4F4F4',
          zoomType: 'x',
          type: 'line'
      },
      title: {
          text: 'What do people think?'
      },
      subtitle: {
          text: document.ontouchstart === undefined ?
                  'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
      },
      xAxis: {
          type: 'datetime'
      },
      yAxis: {

          title: {
              text: 'Polarity'
          }
      },
      legend: {
          enabled: false
      },
      plotOptions: {
          series: {
            connectNulls: true
          },
          line: {
              fillColor: {
                  linearGradient: {
                      x1: 0,
                      y1: 0,
                      x2: 0,
                      y2: 1
                  },
                  stops: [
                      [0, '#b3d9ff'],
                      [1, '#ffe6e6']
                  ]
              },
              lineWidth: 3,
              states: {
                  hover: {
                      lineWidth: 2
                  }
              },
              threshold: null
          }
      },
      series: [{
          type: 'line',
          color: '#b3d9ff',
          name: 'Polarity',
          data: line_temp
      }]
    });
      //Chart for our pie semi circle
      Highcharts.chart('highChartsPie', {
          exporting: {
            enabled: false
          },
          chart: {
            backgroundColor: {
              linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
              stops: [
                 [0, '#282627']
              ]
            },
              plotBorderWidth: 0,
              plotShadow: false
          },
          title: {
            style: {
              color: '#C7BCA8',
            },
              text: 'Total <br>tweet<br>sentiment',
              align: 'center',
              verticalAlign: 'middle',
              y: 40
          },
          tooltip: {
              pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
          },
          plotOptions: {
              pie: {
                  dataLabels: {
                      enabled: true,
                      distance: -50,
                      style: {
                          fontWeight: 'bold',
                          color: 'white'
                      }
                  },
                  startAngle: -90,
                  endAngle: 90,
                  center: ['50%', '75%']
              }
          },
          series: [{
              type: 'pie',
              name: 'Polarity',
              innerSize: '50%',
              data: [
                  {name: 'Positive', y: data['1'][0][0], color:  '#C7BCA8'}, //pie data from server get_data
                  {name: 'Negative', y: data['2'][0][0], color:  'red'},
              ]
          }]
      });
  });

//Buttons for the chart to update according to a time scale.
function updateChart(btn_id) {
  var chart = $('#highChartsLine').highcharts();
  if(btn_id == "currentBtn"){
    //Remove all data within the series.
      chart.series[0].setData([], true);
  }
  else if(btn_id == "dayBtn"){
    $.getJSON('http://127.0.0.1:8080/getdata?key='+btn_id,
    function(data){
      var line_temp = parseData(data['0']);
      chart.series[0].setData(line_temp, true);
    });
  }
  else {
    $.getJSON('http://127.0.0.1:8080/getdata?key='+btn_id,
    function(data){
      var line_temp = parseData(data['0']);
      chart.series[0].setData(line_temp, true);
    });
  }
}

//Get and display information on words selected.
function getWordData(btn_id){

  $('#word-information').empty();
  $('#word-title').empty();
  temp = [];
  var position = null;

  if(btn_id != selectedWord){
    //Scroll down when updated.
    $('html, body').animate({
         scrollTop: $("#word-title").offset().top
     }, 1000);
   }

  if(btn_id.indexOf("Pos") != -1){
    string = btn_id.replace("Pos","");
    selectedWord = btn_id;
      for(var i = 0; i < posWords.length; ++i){
        if(posWords[i][0] == string){
          position = i;
          $('#word-title').append('Live word count: ' + posWords[i][2] + '<br>');
        }
      }
      temp = posTweets;
  }
  else if(btn_id.indexOf("Neg") != -1){
    string = btn_id.replace("Neg","");
    selectedWord = btn_id;
    for(var i = 0; i < negWords.length; ++i){
      if(negWords[i][0] == string){
        position = i;
        $('#word-title').append('Live word count: ' + negWords[i][2] + '<br>');
      }
    }
    temp = negTweets;
  }

  var wordText = document.getElementById(btn_id);
  $('#word-title').append('<u>' + wordText.textContent + '</u>');

  for(var i = 0; i < temp[position].length; ++i){
    //Update fields with, polarity and subjectivity
    $('#word-information').append('<tr><td class="wordInfo">\
     <span class="headings" style="float: left;">Tweet: ' + (i+1) + '</span><br>' + temp[position][i][0] + '</td>\
     <td class="wordInfo"><span class="headings">Polarity:<span style="color:#1E90FF;">\
      ' + temp[position][i][1] + '<br>' + ' <span class="headings">Subjectivity: </span>' + temp[position][i][2] + '</span></td></tr>');
  }
}

function updateWords(){
  //Button for each positive and negative word.
  $("#posWord").empty();
  $("#negWord").empty();
  for(i in posWords){
    $("#posWord").append('\
      <button id='+ '"' + posWords[i][0] + "Pos" + '"' + 'class="button posWord"  onclick="getWordData(this.id)">' + posWords[i][0] + '</button>\
    ');
  }
  for(i in negWords){
    $("#negWord").append('\
      <button id='+ '"' + negWords[i][0] + "Neg" + '"' +  'class="button negWord"  onclick="getWordData(this.id)">' + negWords[i][0] + '</button>\
    ');
  }
}
