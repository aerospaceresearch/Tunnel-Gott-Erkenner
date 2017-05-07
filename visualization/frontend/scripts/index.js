var data = [];
var markers = [];
var map;
$(document).ready(function() {
    map = L.map('map').setView([48.777113, 9.235659], 13);
    var mapLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>';
    L.tileLayer(
        'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; ' + mapLink + ' Contributors',
            maxZoom: 18,
        }).addTo(map);

    start();
});

function start() {
    var wsServer = 'ws://localhost:1337/';
    var ws = new WebSocket(wsServer);

    ws.onmessage = function(event) {
        // TODO: differentiate between earthquake event and new sensor data
        var data = $.parseJSON(event.data);
        updateMap(data);
    };

    ws.onclose = function() {
        console.log("Socket connection closed");
    };

    ws.onopen = function() {
        console.log("Connected");
    };

    $('button').click(function(e) {
        ws.send();
    });
}

function updateMap(newData) {
    console.log('Updating map with: ', newData);

    newData.forEach(function(d) {
        data.push(d);
    });

    while(data.length > 10) {
        data.shift();
    }

    markers.forEach(function(marker) {
        marker.remove();
    });

    data.forEach(function(dataPoint) {
        // TODO: Use custom icon for earthquake events
        markers.push(L.marker([dataPoint.lat, dataPoint.lng]).addTo(map));
    });
}
