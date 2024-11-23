from random import randint
from typing import List

from fastapi import HTTPException
from wireup import service

from app.schemas.coordinate import Coordinate
from app.schemas.taxi_optima import TaxiOptimaRequest, TaxiOptimaResponse

import googlemaps
from datetime import datetime
from typing import List, Dict, Tuple

@service
class TaxiOptimaService:
    def __init__(self) -> None:
        self.gmaps = googlemaps.Client(key='AIzaSyD1VIIdnbjMB5d6iqkkpItlH74RJniI1i4')
    
    def get_nearby_pickup_points(self, origin: str, radius: int = 250) -> List[Dict]:
        geocode_result = self.gmaps.geocode(origin)
        
        if not geocode_result:
            raise ValueError("Could not geocode the origin address.")
        
        origin_coordinates = geocode_result[0]['geometry']['location']
        origin_latlng = f"{origin_coordinates['lat']},{origin_coordinates['lng']}"
        
        places_result = self.gmaps.places_nearby(location=origin_latlng, radius=radius)
        pickup_points = [place['geometry']['location'] for place in places_result['results']]
        return pickup_points
    
    # def calculate_best_pickup_point(self, user_location: str, destination: str, taxi_location: str, radius: int = 200) -> Tuple[str, float]:
    #     nearby_points = self.get_nearby_pickup_points(user_location, radius)
    #     print(nearby_points)
        
    #     optimal_point = None
    #     minimal_time = float('inf')

    #     for point in nearby_points:
    #         print(point)
    #         point_location = f"{point['lat']},{point['lng']}"

    #         taxi_to_pickup_result = self.gmaps.directions(origin=taxi_location,
    #                                                 destination=point_location,
    #                                                 mode="driving",
    #                                                 departure_time=datetime.now())
            
    #         pickup_to_dest_result = self.gmaps.directions(origin=point_location,
    #                                                 destination=destination,
    #                                                 mode="driving",
    #                                                 departure_time=datetime.now())
            
    #         if taxi_to_pickup_result and pickup_to_dest_result:
    #             taxi_to_pickup_time = taxi_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
    #             pickup_to_dest_time = pickup_to_dest_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
    #             total_time = taxi_to_pickup_time + pickup_to_dest_time
    #             if total_time < minimal_time:
    #                 minimal_time = total_time
    #                 optimal_point = point_location

    #     return optimal_point, minimal_time, taxi_to_pickup_time, pickup_to_dest_time
    
    def calculate_best_pickup_point(self, user_location: str, destination: str, taxi_location: str, radius: int = 200) -> Tuple[str, float, float, float]:
        nearby_points = self.get_nearby_pickup_points(user_location, radius)
        print(nearby_points)
        
        optimal_point = None
        minimal_time = float('inf')
        taxi_to_pickup_distance = 0
        user_to_pickup_distance = 0
        pickup_to_dest_distance = 0
        taxi_to_pickup_polyline = ""
        user_to_pickup_polyline = ""
        pickup_to_dest_polyline = ""
        
        data = (optimal_point, minimal_time, taxi_to_pickup_distance, pickup_to_dest_distance, taxi_to_pickup_polyline, pickup_to_dest_polyline, user_to_pickup_distance, user_to_pickup_polyline)

        for point in nearby_points:
            print(point)
            point_location = f"{point['lat']},{point['lng']}"

            taxi_to_pickup_result = self.gmaps.directions(origin=taxi_location,
                                                    destination=point_location,
                                                    mode="driving",
                                                    departure_time=datetime.now())
            
            user_to_pickup_result = self.gmaps.directions(origin=user_location,
                                                    destination=point_location,
                                                    mode="walking",
                                                    departure_time=datetime.now())

            pickup_to_dest_result = self.gmaps.directions(origin=point_location,
                                                    destination=destination,
                                                    mode="driving",
                                                    departure_time=datetime.now())
            
            
            if taxi_to_pickup_result and pickup_to_dest_result and user_to_pickup_result:
                taxi_to_pickup_time = taxi_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
                pickup_to_dest_time = pickup_to_dest_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
                user_to_pickup_time = user_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
                total_time = taxi_to_pickup_time + pickup_to_dest_time

                taxi_to_pickup_distance = taxi_to_pickup_result[0]['legs'][0]['distance']['value'] / 1000  # in kilometers
                pickup_to_dest_distance = pickup_to_dest_result[0]['legs'][0]['distance']['value'] / 1000  # in kilometers
                user_to_pickup_distance = user_to_pickup_result[0]['legs'][0]['distance']['value'] / 1000  # in kilometers

                taxi_to_pickup_polyline = taxi_to_pickup_result[0]['overview_polyline']['points']
                pickup_to_dest_polyline = pickup_to_dest_result[0]['overview_polyline']['points']
                user_to_pickup_polyline = user_to_pickup_result[0]['overview_polyline']['points']

                if total_time < minimal_time:
                    minimal_time = total_time
                    optimal_point = point_location
                    data = (optimal_point, minimal_time, taxi_to_pickup_distance, pickup_to_dest_distance, taxi_to_pickup_polyline, pickup_to_dest_polyline, user_to_pickup_distance, user_to_pickup_polyline)

        return data
    
    def get_route_from_pickup_to_destination(self, pickup_point: str, destination: str) -> List[Dict]:
        route_result = self.gmaps.directions(origin=pickup_point,
                                        destination=destination,
                                        mode="driving",
                                        departure_time=datetime.now())
        
        route_coordinates = []
        
        if route_result:
            polyline = route_result[0]['overview_polyline']['points']

            steps = route_result[0]['legs'][0]['steps']
            
            for step in steps:
                start_location = step['start_location']
                end_location = step['end_location']
                route_coordinates.append((start_location['lat'], start_location['lng']))
                route_coordinates.append((end_location['lat'], end_location['lng']))
            steps = route_result[0]['legs'][0]['steps']
            directions = []
            
            for step in steps:
                instructions = step['html_instructions']
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
        
    def calculate_estimated_time(self, origin: str, destination: str, mode: str = "driving") -> float:
        """
        Calculates the estimated travel time between two points.
        
        :param origin: The starting point as a string in "latitude,longitude" format.
        :param destination: The destination point as a string in "latitude,longitude" format.
        :param mode: The mode of transportation (e.g., "driving", "walking", "bicycling", "transit").
        :return: Estimated travel time in minutes.
        """
        try:
            directions_result = self.gmaps.directions(origin=origin,
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
        
    def calculate_taxi_polyline_and_wait_time_and_distance(self, taxi_location: str, pickup_point: str) -> Tuple[float, float]:
        """
        Calculates the estimated time and distance for a taxi to reach the pickup point.
        :param taxi_location: Current location of the taxi.
        :param pickup_point: Optimal pickup point as coordinates.
        :return: Tuple of estimated time and distance.
        """
        taxi_to_pickup_result = self.gmaps.directions(origin=taxi_location,
                                                destination=pickup_point,
                                                mode="driving",
                                                departure_time=datetime.now())
        
        if taxi_to_pickup_result:
            polyline = taxi_to_pickup_result[0]['overview_polyline']['points']
            
            steps = taxi_to_pickup_result[0]['legs'][0]['steps']
            route_coordinates = []
            
            for step in steps:
                start_location = step['start_location']
                end_location = step['end_location']

                route_coordinates.append((start_location['lat'], start_location['lng']))
                route_coordinates.append((end_location['lat'], end_location['lng']))

            taxi_to_pickup_time = taxi_to_pickup_result[0]['legs'][0]['duration']['value'] / 60  # in minutes
            taxi_to_pickup_distance = taxi_to_pickup_result[0]['legs'][0]['distance']['value'] / 1000  # in kilometers
            return polyline, route_coordinates, taxi_to_pickup_time, taxi_to_pickup_distance
        else:
            return "", [], None, None
        
    def taxi_coordinates_generator(self, user_longitude: str, user_latitude: str):
        taxi_longitude = float(user_longitude) + (randint(-5, -5) * 0.001)
        taxi_latitude = float(user_latitude) + (randint(-5, 5) * 0.001)
        return (taxi_longitude, taxi_latitude)
    
    def request_taxi_optima(self, taxi_optima_data: TaxiOptimaRequest) -> TaxiOptimaResponse:
        user_longitude = taxi_optima_data.user_longitude
        user_latitude = taxi_optima_data.user_latitude
        destination_longitude = taxi_optima_data.destination_longitude
        destination_latitude = taxi_optima_data.destination_latitude
        
        taxi_location = self.taxi_coordinates_generator(user_longitude, user_latitude)
        taxi_location_str = f"{taxi_location[1]},{taxi_location[0]}"
        
        optimal_pickup_point, total_time, taxi_to_pickup_distance, pickup_to_dest_distance, taxi_to_pickup_polyline, pickup_to_dest_polyline, user_to_pickup_distance, user_to_pickup_polyline,  = self.calculate_best_pickup_point(
            f"{user_latitude},{user_longitude}",
            f"{destination_latitude},{destination_longitude}",
            taxi_location_str
        )
        
        if optimal_pickup_point:
            directions, polyline, route_coordinates = self.get_route_from_pickup_to_destination(optimal_pickup_point,
                                                                                               f"{destination_latitude},{destination_longitude}")
            
            optimal_start_latitude = optimal_pickup_point.split(",")[0]
            optimal_start_longitude = optimal_pickup_point.split(",")[1]
            
            taxi_wait_polyline, taxi_route_coordinates, taxi_wait_time, taxi_wait_distance = self.calculate_taxi_polyline_and_wait_time_and_distance(taxi_location_str, optimal_pickup_point)
            
            return TaxiOptimaResponse(
                optimal_start_latitude=optimal_start_latitude,
                optimal_start_longitude=optimal_start_longitude,
                destination_latitude=destination_latitude,
                destination_longitude=destination_longitude,
                trip_distance=pickup_to_dest_distance,
                trip_duration=total_time,
                user_to_pickup_distance=user_to_pickup_distance,
                user_to_pickup_polyline=user_to_pickup_polyline,
                taxi_to_pickup_distance=taxi_to_pickup_distance,
                pickup_to_dest_distance=pickup_to_dest_distance,
                coordinates=route_coordinates,
                instructions=directions,
                pickup_to_dest_polyline=pickup_to_dest_polyline,
                taxi_to_pickup_polyline=taxi_to_pickup_polyline,
                taxi_coming_coordinates=taxi_route_coordinates,
                taxi_wait_time=taxi_wait_time,
                taxi_wait_distance=taxi_wait_distance
            )
        else:
            raise HTTPException(status_code=404, detail="No optimal pickup point found.")