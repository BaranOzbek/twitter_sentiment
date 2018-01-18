//Establish a new WebSocket
var ws = new WebSocket("ws://127.0.0.1:8000/websocket");
var status = document.getElementById("status");

ws.onopen = function(){
  print("Sucessfully connected")
};

ws.onmessage = function(event) {
  /**We use this function to update the graphs and other updating information**/
  $("#tweet").empty().append(event.data);
};

ws.onerror = function(){
  alert("Can not establish WebSocket.");
};
