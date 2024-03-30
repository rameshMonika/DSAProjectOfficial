if (data[0].direct_flight_data.length > 0) {
    var htmlContent = "";
    for (var y = 0; y < data[0].direct_flight_data.length; y++) {
        var directEstTime = data[0].direct_flight_data[y][4][0] + " Hours " + data[0].indirect_flight_data[y][4][1] + " Mins";
        var route = data[0].direct_flight_data[y];
        var routeInfo = "";
        for (let j = 0; j < route[0].length; j++) {
            routeInfo += route[0][j];
            if (j < route[0].length - 1) {
                routeInfo += ' > ';
            }
        }
        if (!encounteredClasses[route[1]]) {
            // If not encountered, add it to the encountered classes set
            encounteredClasses[route[1]] = true;
            htmlContent += `
                                                    <div class="card w-50 mb-2 ${route[1]}">
                                                        <form action="/OneMap" method="post">
                                                            <div class="card-body">
                                                                <h5 class="card-title">Source Airport: ${route[0][0]}</h5>
                                                                <h5 class="card-title">Destination Airport: ${route[0][route[0].length - 1]}</h5>
                                                                <p class="card-text">Distance: ${route[1]} km</p>
                                                                <p class="card-text">Airline: ${route[2]} </p>
                                                                <p class="card-text">Price: $${route[3]} </p>
                                                                <p class="card-text FlightRoutes"  name="FlightRoutes">Route: ${routeInfo}</p>
                                                                <button type="submit" class="btn btn-primary">View More</button>
                                                            </div>
                                                            <input type="text" style="visibility: hidden;" id="Dest" name="Dest" value="${flightCoordinates[1]}" readonly>
                                                            <input type="text" style="hidden: visible;" id="Source" name="Source" value="${flightCoordinates[0]}" readonly>


                                                            <p>
                                                                <label for="ETA">Estimated Time of Arrival</label>
                                                                <input type="text" style="visibility: visible;" id="ETA" name="ETA" value="${directEstTime}" readonly>
                                                            </p>
                                                            <input type="text" style="visibility: visible;" name="FlightRoutes" value="${routeInfo}" readonly>
                                                            <input type="text" style="visibility: visible;" name="totalDistance" value="${route[1]}" readonly>
                                                            <input type="text" style="visibility: visible;" name="allCoordinate" value="${route_Coordinate[y + 1]}" readonly>
                                                        </form>
                                                    </div>`;
        }
    }
    output.innerHTML += htmlContent; // Append the HTML content
}