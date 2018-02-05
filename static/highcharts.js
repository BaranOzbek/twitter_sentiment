$.getJSON('http://127.0.0.1:8000/getdata.json', function(data){
  var temp = [];
  for(i in data){
    tweet_date = Date.parse(data[i][0]);
    temp.push([(tweet_date), data[i][1]]);
  }

      Highcharts.chart('highCharts', {
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
              data: temp
          }]
      });
  });
