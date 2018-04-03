/**Establish a new WebSocket, Remember to change local address accordingly!**/
var ws = new WebSocket("ws://127.0.0.1:8080/websocket");

ws.onopen = function(){

};

ws.onmessage = function(event){
  /**We use this function to update the graphs and other updating information**/
  var line_chart = $('#highChartsLine').highcharts();
  var pie_chart = $('#highChartsPie').highcharts();
  data = JSON.parse(event.data);
  tweet_date = Date.parse(data['Created_at']);
  pie_val = data['Pie_val'];
  //Set the word values.
  posWords = data['Positive'];
  negWords = data['Negative'];
  posTweets = data['PositiveTweets'];
  negTweets = data['NegativeTweets'];

  line_chart.series[0].addPoint([(tweet_date),data['Polarity']], true);
  $("#tweet").empty().append(data['Tweet']);

  //Gather previous values from chart
  posData = pie_chart.series[0].data[0].y;
  negData = pie_chart.series[0].data[1].y;
  if(pie_val == 1){
    pie_chart.series[0].setData([['Positive', posData+1],['Negative', negData]], true);
  }
  else if (pie_val == -1){
      pie_chart.series[0].setData([['Positive', posData],['Negative', negData+1]], true);
  } else { return }

  updateWords();
  if(selectedWord != null){
    getWordData(selectedWord);
  }
};

ws.onerror = function(){
  alert("Can not establish WebSocket, your Browser may not be compatible.");
};

ws.onclose = function(){

};
