/**Establish a new WebSocket, Remember to change local address accordingly!**/
var ws = new WebSocket("ws://127.0.0.1:8000/websocket");

ws.onopen = function(){

};

ws.onmessage = function(event){
  /**We use this function to update the graphs and other updating information**/
  var line_chart = $('#highCharts-line').highcharts();
  var pie_chart = $('#highCharts-pie').highcharts();
  data = JSON.parse(event.data);
  tweet_date = Date.parse(data['Created_at']);

  line_chart.series[0].addPoint([(tweet_date),data['Polarity']], true);
  $("#tweet").empty().append(data['Tweet']);

  pie_val = data['Pie_val'];
  //Gather previous values from chart
  posData = pie_chart.series[0].data[0].y;
  negData = pie_chart.series[0].data[1].y;

  if(pie_val == 1){
    pie_chart.series[0].setData([['Positive', posData+1],['Negative', negData]], true);
  }
  else if (pie_val == -1){
      pie_chart.series[0].setData([['Positive', posData],['Negative', negData+1]], true);
  }
};

ws.onerror = function(){
  alert("Can not establish WebSocket, your Browser may not be compatible.");
};
