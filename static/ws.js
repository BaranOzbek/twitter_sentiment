//Establish a new WebSocket, Remember to change local address accordingly!
var ws = new WebSocket("ws://127.0.0.1:8000/websocket");
var status = document.getElementById("status");

ws.onopen = function(){
  alert("Sucessfully connected");
};

ws.onmessage = function(event) {
  /**We use this function to update the graphs and other updating information**/
  data = JSON.parse(event.data);
  $("#tweet").append(data['Tweet']);

};

ws.onerror = function(){
  alert("Can not establish WebSocket.");
};
