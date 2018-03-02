//Function processing line graph data for input.
function parseData(data){
  var line_temp = [];
  for(i in data){
    tweet_date = Date.parse(data[i][0]);
    line_temp.push([(tweet_date), data[i][1]]);
  }
  return line_temp;
}

$.getJSON('http://127.0.0.1:8080/getdata',
 function(data){
  //Retrieve all data to be inputted into the graphs
  var line_temp = parseData(data['0']);
  var pieX = data['1'];
  var pieY = data['2'];
  var posWord = data['3'];
  var negWord = data['4'];
  console.log(line_temp);
  //Button f or each positive and negative word.
  for(i in posWord){
    $("#posWord").append('<button id='+ '"' + posWord[i] + '"' + 'class="button posWord"  onclick="updateChart(this.id)">' + posWord[i] + '</button>');
    $("#negWord").append('<button id='+ '"' + negWord[i] + '"' +  'class="button negWord"  onclick="updateChart(this.id)">' + negWord[i] + '</button>');
  }

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
                  {name: 'Positive', y: pieX[0][0], color:  '#C7BCA8'},
                  {name: 'Negative', y: pieY[0][0], color:  'red'},
              ]
          }]
      });
  });

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

function getWordData(btn_id){


}
