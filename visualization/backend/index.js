var WebSocketServer = require('websocket').server;
var http = require('http');
var clients = [];
var serverPort = 1337;
var data;

var server = http.createServer(function(request, response) {
  // We don't need no HTTP server.
});

server.listen(serverPort, function() {
    console.log(new Date() + " Server is listening on port " + serverPort);
});

var wsServer = new WebSocketServer({
    httpServer: server
});

function sendCallback(err) {
    if (err) console.error("send() error: " + err);
}

wsServer.on('request', function(request) {
    console.log(new Date() + " Connection from origin " + request.origin);

    var connection = request.accept(null, request.origin);
    clients.push(connection);

    connection.send(JSON.stringify(data), sendCallback);

    connection.on('close', function(connection) {
        clients.splice(clients.indexOf(connection), 1);
    });
});

setInterval(function() {
    generateData();
    clients.forEach(function(outputConnection) {
        outputConnection.send(JSON.stringify(data), sendCallback);
    });
}, 1000);

function generateData() {
    var newData = [];
    for(var i = 0; i < 10; i++) {
        newData.push(randomGeo());
    }
    data = newData;
}

function randomGeo() {
    var radius = 2000;
    var y0 = 48.777113;
    var x0 = 9.235659;

    var u = Math.random();
    var v = Math.random();

    var rd = radius / 111300; //about 111300 meters in one degree
    var w = rd * Math.sqrt(u);
    var t = 2 * Math.PI * v;
    var x = w * Math.cos(t);
    var y = w * Math.sin(t);


    var newlat = y + y0;
    var newlon = x + x0;

    return {
        'lat': newlat.toFixed(5),
        'lng': newlon.toFixed(5)
    };
}

