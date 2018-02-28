$.getJSON('http://127.0.0.1:8000/getdata.json',
 function(data){
  //Retrieve all data to be inputted into the graphs, Needs to be parsed.
  var line_data = data['0'];
  var pieX = data['1'];
  var pieY = data['2'];

  var line_temp = [];
  for(i in line_data){
    tweet_date = Date.parse(line_data[i][0]);
    line_temp.push([(tweet_date), line_data[i][1]]);
  }

  Highcharts.chart('highCharts-line', {
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
      Highcharts.chart('highCharts-pie', {
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
