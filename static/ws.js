//Establish a new WebSocket, Remember to change local address accordingly!
var ws = new WebSocket("ws://127.0.0.1:8000/websocket");

ws.onopen = function(){
  alert("Sucessfully connected");
};

ws.onmessage = function(event) {
  /**We use this function to update the graphs and other updating information**/
  var chart = $('#highCharts').highcharts();
  data = JSON.parse(event.data);
  tweet_date = Date.parse(data['Created_at']);
  chart.series[0].addPoint([(tweet_date),data['Polarity']], true);
  $("#tweet").empty().append(data['Tweet']);

};

ws.onerror = function(){
  alert("Can not establish WebSocket.");
};
