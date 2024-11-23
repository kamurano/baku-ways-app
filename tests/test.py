import googlemaps
from datetime import datetime
from typing import List, Dict, Tuple

# Initialize Google Maps client
gmaps = googlemaps.Client(key='AIzaSyD1VIIdnbjMB5d6iqkkpItlH74RJniI1i4')

def get_nearby_pickup_points(origin: str, radius: int = 200) -> List[Dict]:
    """
    Get nearby potential pick-up points by first converting the user address to coordinates.
    :param origin: The current location of the user as an address string.
    :param radius: Radius to search for nearby points (in meters).
    :return: List of nearby potential pick-up points.
    """
    # Geocode the origin address to get latitude and longitude
    geocode_result = gmaps.geocode(origin)
    
    if not geocode_result:
        raise ValueError("Could not geocode the origin address.")
    
    # Extract latitude and longitude
    origin_coordinates = geocode_result[0]['geometry']['location']
    origin_latlng = f"{origin_coordinates['lat']},{origin_coordinates['lng']}"
    
    # Use the coordinates in places_nearby
    places_result = gmaps.places_nearby(location=origin_latlng, radius=radius)
    pickup_points = [place['geometry']['location'] for place in places_result['results']]
    return pickup_points


def calculate_best_pickup_point(user_location: str, destination: str, taxi_location: str, radius: int = 200) -> Tuple[str, float]:
    """
    Calculates the best pickup point for a taxi considering taxi's real-time location.
    :param user_location: User's original location.
    :param destination: Destination location.
    :param taxi_location: Taxi's real-time location.
    :param radius: Search radius for nearby pick-up points.
    :return: Optimal pick-up point and total estimated time.
    """
    # Get nearby points around the user's location
    nearby_points = get_nearby_pickup_points(user_location, radius)
    print(nearby_points)
    
    optimal_point = None
    minimal_time = float('inf')

    for point in nearby_points:
        print(point)
        # Get coordinates of point
        point_location = f"{point['lat']},{point['lng']}"

        # Calculate time for taxi to reach the pick-up point
        taxi_to_pickup_result = gmaps.directions(origin=taxi_location,
                                                 destination=point_location,
                                                 mode="driving",
                                                 departure_time=datetime.now())
        
        # Calculate travel time from pickup point to destination
        pickup_to_dest_result = gmaps.directions(origin=point_location,
                                                 destination=destination,
                                                 mode="driving",
                                                 departure_time=datetime.now())
        
        if taxi_to_pickup_result and pickup_to_dest_result:
            # Extract travel times
            taxi_to_pickup_time = taxi_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
            pickup_to_dest_time = pickup_to_dest_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
            total_time = taxi_to_pickup_time + pickup_to_dest_time

            # Update optimal point if this point has the minimal time
            if total_time < minimal_time:
                minimal_time = total_time
                optimal_point = point_location

    return optimal_point, minimal_time
    

def get_route_from_pickup_to_destination(pickup_point: str, destination: str) -> List[Dict]:
    """
    Get the best route from the pickup point to the destination, including directions and distance.
    :param pickup_point: Optimal pickup point as coordinates.
    :param destination: Destination as coordinates.
    :return: List of step-by-step directions.
    """
    route_result = gmaps.directions(origin=pickup_point,
                                    destination=destination,
                                    mode="driving",
                                    departure_time=datetime.now())
    
    route_coordinates = []
    
    if route_result:
        # Extract the encoded polyline for the route
        polyline = route_result[0]['overview_polyline']['points']

        steps = route_result[0]['legs'][0]['steps']
        
        for step in steps:
            # Start and end coordinates of each step
            start_location = step['start_location']
            end_location = step['end_location']
            
            # Add both start and end coordinates to the list
            route_coordinates.append((start_location['lat'], start_location['lng']))
            route_coordinates.append((end_location['lat'], end_location['lng']))
            
        # Extract directions, distance, and duration
        steps = route_result[0]['legs'][0]['steps']
        directions = []
        
        for step in steps:
            instructions = step['html_instructions']  # HTML-formatted directions
            distance = step['distance']['text']
            duration = step['duration']['text']
            directions.append({
                'instruction': instructions,
                'distance': distance,
                'duration': duration
            })
        
        return directions , polyline, route_coordinates
    else:
        return [], "", []
    
    
def calculate_estimated_time(origin: str, destination: str, mode: str = "driving") -> float:
    """
    Calculates the estimated travel time between two points.
    
    :param origin: The starting point as a string in "latitude,longitude" format.
    :param destination: The destination point as a string in "latitude,longitude" format.
    :param mode: The mode of transportation (e.g., "driving", "walking", "bicycling", "transit").
    :return: Estimated travel time in minutes.
    """
    try:
        directions_result = gmaps.directions(origin=origin,
                                             destination=destination,
                                             mode=mode,
                                             departure_time=datetime.now())
        
        if directions_result:
            # Get the duration in seconds and convert to minutes
            duration_seconds = directions_result[0]['legs'][0]['duration']['value']
            duration_minutes = duration_seconds / 60
            return duration_minutes
        else:
            print("No route found between the specified locations.")
            return None
    except googlemaps.exceptions.ApiError as e:
        print(f"API error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None    

def calculate_taxi_polyline_and_wait_time_and_distance(taxi_location: str, pickup_point: str) -> Tuple[float, float]:
    """
    Calculates the estimated time and distance for a taxi to reach the pickup point.
    :param taxi_location: Current location of the taxi.
    :param pickup_point: Optimal pickup point as coordinates.
    :return: Tuple of estimated time and distance.
    """
    taxi_to_pickup_result = gmaps.directions(origin=taxi_location,
                                             destination=pickup_point,
                                             mode="driving",
                                             departure_time=datetime.now())
    
    if taxi_to_pickup_result:
        # Extract the encoded polyline for the route
        polyline = taxi_to_pickup_result[0]['overview_polyline']['points']
        
        # Extract the coordinates for the route
        steps = taxi_to_pickup_result[0]['legs'][0]['steps']
        route_coordinates = []
        
        for step in steps:
            # Start and end coordinates of each step
            start_location = step['start_location']
            end_location = step['end_location']
            
            # Add both start and end coordinates to the list
            route_coordinates.append((start_location['lat'], start_location['lng']))
            route_coordinates.append((end_location['lat'], end_location['lng']))

        # Extract travel time and distance
        taxi_to_pickup_time = taxi_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
        taxi_to_pickup_distance = taxi_to_pickup_result[0]['legs'][0]['distance']['value'] / 1000  # in kilometers
        return polyline, route_coordinates, taxi_to_pickup_time, taxi_to_pickup_distance
    else:
        return "", [], None, None
    
    

def calculate_taxi_wait_polyline(taxi_location: str, pickup_point: str) -> Tuple[str, List[Tuple[float, float]]]:
    """
    Calculates the polyline and coordinates for the route from the taxi location to the pickup point.
    :param taxi_location: Current location of the taxi.
    :param pickup_point: Optimal pickup point as coordinates.
    :return: Tuple of polyline string and list of (latitude, longitude) tuples representing the route.
    """
    route_result = gmaps.directions(origin=taxi_location,
                                    destination=pickup_point,
                                    mode="driving",
                                    departure_time=datetime.now())
    
    if route_result:
        # Extract the encoded polyline for the route
        polyline = route_result[0]['overview_polyline']['points']
        
        # Extract the coordinates for the route
        steps = route_result[0]['legs'][0]['steps']
        route_coordinates = []
        
        for step in steps:
            # Start and end coordinates of each step
            start_location = step['start_location']
            end_location = step['end_location']
            
            # Add both start and end coordinates to the list
            route_coordinates.append((start_location['lat'], start_location['lng']))
            route_coordinates.append((end_location['lat'], end_location['lng']))
        
        return polyline, route_coordinates
    else:
        return "", []

def taxi_coordinates_generator(user_longitude: str, user_latitude: str):
    """
    Generates taxi coordinates around the user's location.
    :param user_longitude: User's longitude.
    :param user_latitude: User's latitude.
    :return: List of taxi coordinates.
    """
    # Generate taxi coordinates around the user's location
    taxi_longitude = float(user_longitude) + (3 * 0.001)
    taxi_latitude = float(user_latitude) + (3 * 0.001)
    return (taxi_longitude, taxi_latitude)

# user_location = "40.3777,49.8541"        # Coordinates for 28 May St, Baku
# destination = "40.3725,49.8373"          # Coordinates for Fountain Square, Baku
# taxi_location = "40.3764,49.8327"        # Coordinates for Nizami St, Baku

# # Calculate optimal pickup point
# optimal_pickup_point, total_estimated_time = calculate_best_pickup_point(user_location, destination, taxi_location)
# print(f"Optimal pickup point: {optimal_pickup_point}, Total estimated time: {total_estimated_time:.2f} minutes")

# # Get the best route from the pickup point to the destination
# route_directions = get_route_from_pickup_to_destination(optimal_pickup_point, destination)

# # Display route
# print("Route from pickup to destination:")
# for idx, step in enumerate(route_directions, 1):
#     print(f"Step {idx}: {step['instruction']} - {step['distance']} ({step['duration']})")



# Example usage
user_location = "40.3777,49.8541"        # Coordinates for 28 May St, Baku
destination = "40.3725,49.8373"          # Coordinates for Fountain Square, Baku
taxi_location = "40.3764,49.8327"        # Coordinates for Nizami St, Baku
taxi_location = taxi_coordinates_generator(user_location.split(",")[0], user_location.split(",")[1])

optimal_pickup_point, total_estimated_time = calculate_best_pickup_point(user_location, destination, taxi_location)
print(f"Optimal pickup point: {optimal_pickup_point}, Total estimated time: {total_estimated_time:.2f} minutes")


# Get the best route from the pickup point to the destination
route_directions = get_route_from_pickup_to_destination(optimal_pickup_point, destination)
print(route_directions)

# Display route
print("Route from pickup to destination:")
for idx, step in enumerate(route_directions, 1):
    print(f"Step {idx}: {step['instruction']} - {step['distance']} ({step['duration']})")

# Get the route as a list of coordinates
polyline, route_coordinates = get_route_coordinates(optimal_pickup_point, destination)
print("Route coordinates:")
for coord in route_coordinates:
    print(coord)

print("Polyline:", polyline)

# taxi wait time and distance
taxi_coming_polyline, taxi_coming_coordinates, taxi_wait_time, taxi_wait_distance = calculate_taxi_polyline_and_wait_time_and_distance(taxi_location, optimal_pickup_point)
print(f"Estimated taxi wait time: {taxi_wait_time:.2f} minutes, Estimated taxi wait distance: {taxi_wait_distance:.2f} km")
print("Taxi polyline:", taxi_coming_polyline)
print("Taxi coordinates:", taxi_coming_coordinates)

# Generate taxi coordinates around the user's location
taxi_coordinates = taxi_coordinates_generator("49.8541", "40.3777")
print("Taxi coordinates:")
print(taxi_coordinates)