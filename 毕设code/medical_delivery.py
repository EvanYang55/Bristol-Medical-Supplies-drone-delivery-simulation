import folium
import math
import numpy as np
import pandas as pd
import random
import heapq
import itertools
from folium.plugins import MarkerCluster, AntPath
import matplotlib.pyplot as plt
import time
import networkx as nx
from collections import defaultdict
import json
import os
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import sys

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

FLIGHT_DATA = [
    # (Flight time (min), Payload (lb), Payload (kg), Total weight (lb), Thrust-to-weight ratio)
    (50.0, 0, 0.0, 43.28, 3.5),
    (41.7, 5, 2.3, 48.28, 3.1),
    (33.3, 10, 4.5, 53.28, 2.8),
    (26.6, 15, 6.8, 58.28, 2.6),
    (22.0, 20, 9.1, 63.28, 2.4),
    (18.0, 25, 11.3, 68.28, 2.2),
    (12.5, 30, 13.6, 73.28, 2.0),
    (10.75, 35, 15.9, 78.28, 1.9)
]


class MedicalDroneDelivery:
    def __init__(self):
        self.cruise_speed = 40  # km/h
        self.max_payload_kg = 15.9  # kg
        self.battery_capacity = 10000  # mAh
        self.power_consumption = 150  # W (cruising)
        self.takeoff_power = 250  # W (takeoff)
        self.landing_power = 100  # W (landing)
        self.max_range = 30  # km
        self.safe_battery_threshold = 20  # %

        self.energy_strategy = 'A'  # Default strategy

        self.flight_data = pd.DataFrame(FLIGHT_DATA,
                                        columns=['flight_time', 'payload_lbs', 'payload_kg',
                                                 'total_weight', 'thrust_ratio'])

        self.distribution_centers = []

        # Hospitals
        self.hospitals = []

        # Delivery tasks
        self.delivery_tasks = []

        # Path planning results
        self.delivery_routes = []

        # Obstacles (simulate buildings, no-fly zones)
        self.obstacles = []

        # Road network (simulate flyable paths)
        self.road_network = nx.Graph()

        # Drone fleet
        self.drones = []

        # Charging stations
        self.charging_stations = []

        # Performance metrics
        self.performance_metrics = {
            'total_time': 0,
            'total_energy': 0,
            'battery_cycles': 0,
            'battery_swaps': 0,
            'safe_margin_violations': 0,
            'success_rate': 0,
            'abort_rate': 0,
            'transfer_count': 0
        }

        # Task scheduling queue
        self.task_queue = []

        # Current time
        self.current_time = datetime.now()

        # Log records
        self.log = []

    def import_data(self, centers_file=None, hospitals_file=None, tasks_file=None):
        """Import data (use default if no files provided)"""
        if centers_file and os.path.exists(centers_file):
            self.import_centers_from_file(centers_file)
        else:
            self.add_default_centers()

        if hospitals_file and os.path.exists(hospitals_file):
            self.import_hospitals_from_file(hospitals_file)
        else:
            self.add_default_hospitals()

        if tasks_file and os.path.exists(tasks_file):
            self.import_tasks_from_file(tasks_file)
        else:
            self.add_default_tasks()

    def calculate_energy_consumption(self, distance_km, payload_kg, flight_time_min):
        # Takeoff energy (assume 1 min takeoff)
        takeoff_time = 1
        takeoff_energy = (takeoff_time / 60) * self.takeoff_power

        # Landing energy (assume 1 min landing)
        landing_time = 1
        landing_energy = (landing_time / 60) * self.landing_power

        # Cruise time
        cruise_time = flight_time_min - takeoff_time - landing_time
        if cruise_time < 0:
            cruise_time = 0

        # Cruise energy
        cruise_energy = (cruise_time / 60) * self.power_consumption

        # Payload impact factor (5% increase per kg)
        payload_factor = 1 + (payload_kg / 10) * 0.05

        # Total energy
        total_energy = (takeoff_energy + landing_energy + cruise_energy) * payload_factor

        return total_energy

    def import_centers_from_file(self, file_path):
        """Import distribution centers from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for center in data:
                    self.add_distribution_center(
                        center['name'],
                        center['lat'],
                        center['lon'],
                        center.get('service_time', 5)
                    )
            print(f"Successfully imported {len(data)} distribution centers")
        except Exception as e:
            print(f"Failed to import centers: {str(e)}")
            self.add_default_centers()

    def import_hospitals_from_file(self, file_path):
        """Import hospitals from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for hospital in data:
                    self.add_hospital(
                        hospital['name'],
                        hospital['lat'],
                        hospital['lon'],
                        hospital.get('service_time', 5)
                    )
            print(f"Successfully imported {len(data)} hospitals")
        except Exception as e:
            print(f"Failed to import hospitals: {str(e)}")
            self.add_default_hospitals()

    def import_tasks_from_file(self, file_path):
        """Import tasks from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                for task in data:
                    # Find center and hospital indices
                    from_idx = next((i for i, c in enumerate(self.distribution_centers)
                                     if c['name'] == task['from']), -1)
                    to_idx = next((i for i, h in enumerate(self.hospitals)
                                   if h['name'] == task['to']), -1)

                    if from_idx >= 0 and to_idx >= 0:
                        self.add_delivery_task(
                            from_idx,
                            to_idx,
                            task['payload_kg'],
                            task.get('material_type', 'medical'),
                            task.get('priority', 'normal')
                        )
                print(f"Successfully imported {len(data)} tasks")
        except Exception as e:
            print(f"Failed to import tasks: {str(e)}")
            self.add_default_tasks()

    def add_default_centers(self):
        """Add default distribution centers"""
        centers = [
            {'name': 'NHS Blood Centre (Filton)', 'lat': 51.518333, 'lon': -2.565278, 'service_time': 5},
            {'name': 'South Bristol NHS Community Hospital', 'lat': 51.4125, 'lon': -2.583056, 'service_time': 5},
            {'name': 'UWE Health Tech Hub', 'lat': 51.500833, 'lon': -2.551944, 'service_time': 5}
        ]
        for center in centers:
            self.add_distribution_center(center['name'], center['lat'], center['lon'], center['service_time'])

    def add_default_hospitals(self):
        """Add default hospitals"""
        hospitals = [
            {'name': 'Southmead Hospital', 'lat': 51.495833, 'lon': -2.591389, 'service_time': 5},
            {'name': 'Bristol Royal Infirmary (BRI)', 'lat': 51.458056, 'lon': -2.596944, 'service_time': 5},
            {'name': 'St Michael\'s Hospital', 'lat': 51.458889, 'lon': -2.599444, 'service_time': 5},
            {'name': 'Eastville Medical Centre', 'lat': 51.470278, 'lon': -2.562222, 'service_time': 5},
            {'name': 'Fishponds Primary Care Centre', 'lat': 51.479722, 'lon': -2.526667, 'service_time': 5},
            {'name': 'Bristol Haematology and Oncology Centre (BHOC)', 'lat': 51.458333, 'lon': -2.5975,
             'service_time': 5},
            {'name': 'Emersons Green NHS Treatment Centre', 'lat': 51.503333, 'lon': -2.496389, 'service_time': 5},
            {'name': 'Lawrence Hill Health Centre', 'lat': 51.4575, 'lon': -2.571944, 'service_time': 5},
            {'name': 'Montpelier Health Centre', 'lat': 51.466944, 'lon': -2.589167, 'service_time': 5}
        ]
        for hospital in hospitals:
            self.add_hospital(hospital['name'], hospital['lat'], hospital['lon'], hospital['service_time'])

    def add_default_tasks(self):
        """Add default tasks"""
        tasks = [
            {'from': 'NHS Blood Centre (Filton)', 'to': 'Southmead Hospital', 'payload_kg': 5, 'material_type': 'blood',
             'priority': 'high'},
            {'from': 'NHS Blood Centre (Filton)', 'to': 'Bristol Royal Infirmary (BRI)', 'payload_kg': 3,
             'material_type': 'medicine', 'priority': 'high'},
            {'from': 'South Bristol NHS Community Hospital', 'to': 'St Michael\'s Hospital', 'payload_kg': 8,
             'material_type': 'equipment', 'priority': 'normal'},
            {'from': 'UWE Health Tech Hub', 'to': 'Eastville Medical Centre', 'payload_kg': 4,
             'material_type': 'medicine', 'priority': 'normal'},
            {'from': 'NHS Blood Centre (Filton)', 'to': 'Fishponds Primary Care Centre', 'payload_kg': 6,
             'material_type': 'medicine', 'priority': 'normal'},
            {'from': 'South Bristol NHS Community Hospital', 'to': 'Bristol Haematology and Oncology Centre (BHOC)',
             'payload_kg': 7, 'material_type': 'medicine', 'priority': 'high'},
            {'from': 'UWE Health Tech Hub', 'to': 'Emersons Green NHS Treatment Centre', 'payload_kg': 5,
             'material_type': 'equipment', 'priority': 'normal'},
            {'from': 'NHS Blood Centre (Filton)', 'to': 'Lawrence Hill Health Centre', 'payload_kg': 4,
             'material_type': 'medicine', 'priority': 'normal'},
            {'from': 'South Bristol NHS Community Hospital', 'to': 'Montpelier Health Centre', 'payload_kg': 3,
             'material_type': 'medicine', 'priority': 'normal'}
        ]

        for task in tasks:
            # Find center and hospital indices
            from_idx = next((i for i, c in enumerate(self.distribution_centers)
                             if c['name'] == task['from']), -1)
            to_idx = next((i for i, h in enumerate(self.hospitals)
                           if h['name'] == task['to']), -1)

            if from_idx >= 0 and to_idx >= 0:
                self.add_delivery_task(
                    from_idx,
                    to_idx,
                    task['payload_kg'],
                    task['material_type'],
                    task['priority']
                )

    def add_distribution_center(self, name, lat, lon, service_time=5):
        """Add distribution center"""
        self.distribution_centers.append({
            'name': name,
            'position': (lat, lon),
            'type': 'distribution',
            'service_time': service_time
        })
        # Add to road network
        self.road_network.add_node(name, pos=(lat, lon), type='center')

    def add_hospital(self, name, lat, lon, service_time=5):
        """Add hospital"""
        self.hospitals.append({
            'name': name,
            'position': (lat, lon),
            'type': 'hospital',
            'service_time': service_time
        })
        # Add to road network
        self.road_network.add_node(name, pos=(lat, lon), type='hospital')

    def add_charging_station(self, name, lat, lon, capacity=4):
        """Add charging station"""
        self.charging_stations.append({
            'name': name,
            'position': (lat, lon),
            'capacity': capacity,
            'available': capacity
        })
        # Add to road network
        self.road_network.add_node(name, pos=(lat, lon), type='charging')

    def add_obstacle(self, lat, lon, radius=0.1):
        """Add obstacle (circular area)"""
        self.obstacles.append({
            'position': (lat, lon),
            'radius': radius  # km
        })

    def add_road(self, from_name, to_name):
        """Add road connection"""
        if from_name not in self.road_network.nodes or to_name not in self.road_network.nodes:
            raise ValueError("Node does not exist")

        # Get positions
        pos1 = self.road_network.nodes[from_name]['pos']
        pos2 = self.road_network.nodes[to_name]['pos']

        # Calculate distance
        distance = self.calculate_distance(pos1, pos2)

        # Add to network
        self.road_network.add_edge(from_name, to_name, weight=distance)

    def calculate_distance(self, point1, point2):
        """
        Calculate distance between two points (km)
        :param point1: (lat, lon)
        :param point2: (lat, lon)
        :return: Distance (km)
        """
        lat1, lon1 = point1
        lat2, lon2 = point2

        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius (km)
        r = 6371
        return c * r

    def calculate_flight_time(self, payload_kg):
        """
        Calculate flight time based on payload (linear interpolation)
        :param payload_kg: Payload weight (kg)
        :return: Flight time (minutes)
        """
        # Validate payload range
        if payload_kg < 0:
            raise ValueError("Payload cannot be negative")

        if payload_kg > self.max_payload_kg:
            raise ValueError(f"Payload exceeds limit {self.max_payload_kg} kg")

        # Get and sort data points
        points = self.flight_data.sort_values('payload_kg')

        # Handle below min payload
        if payload_kg <= points['payload_kg'].min():
            return points.iloc[0]['flight_time']

        # Handle above max payload
        if payload_kg >= points['payload_kg'].max():
            return points.iloc[-1]['flight_time']

        # Find nearest points for interpolation
        for i in range(1, len(points)):
            low_data = points.iloc[i - 1]
            high_data = points.iloc[i]

            if low_data['payload_kg'] <= payload_kg <= high_data['payload_kg']:
                # Calculate interpolation factor
                factor = (payload_kg - low_data['payload_kg']) / (high_data['payload_kg'] - low_data['payload_kg'])

                # Linear interpolation
                flight_time = low_data['flight_time'] + (high_data['flight_time'] - low_data['flight_time']) * factor
                return flight_time

        return points.iloc[-1]['flight_time']

    def calculate_battery_usage(self, payload_kg, flight_time_min):
        """
        Calculate battery usage
        :param payload_kg: Payload (kg)
        :param flight_time_min: Flight time (minutes)
        :return: Battery usage percentage
        """
        # Base energy (without payload)
        base_energy = (flight_time_min / 60) * self.power_consumption  # Wh

        # Payload impact factor (5% per kg)
        payload_factor = 1 + (payload_kg / 10) * 0.05

        # Total energy
        total_energy = base_energy * payload_factor  # Wh

        # Convert capacity to Wh
        battery_wh = self.battery_capacity / 1000 * 14.8  # 14.8V battery

        # Usage percentage
        battery_usage = (total_energy / battery_wh) * 100

        return min(100, battery_usage)

    def calculate_flight_time_from_distance(self, distance_km, payload_kg):
        """
        Calculate flight time based on distance and payload
        :param distance_km: Distance (km)
        :param payload_kg: Payload (kg)
        :return: Flight time (minutes)
        """
        # Base time (without payload)
        base_time = (distance_km / self.cruise_speed) * 60  # min

        # Payload adjustment
        payload_factor = 1 + (payload_kg / self.max_payload_kg) * 0.3
        adjusted_time = base_time * payload_factor

        return adjusted_time

    def add_delivery_task(self, from_index, to_index, payload_kg, material_type='medical', priority='normal'):
        """Add delivery task"""
        if not self.distribution_centers or not self.hospitals:
            raise ValueError("Add centers and hospitals first")

        if from_index < 0 or from_index >= len(self.distribution_centers):
            raise ValueError("Invalid center index")

        if to_index < 0 or to_index >= len(self.hospitals):
            raise ValueError("Invalid hospital index")

        # Get start and end
        start = self.distribution_centers[from_index]
        end = self.hospitals[to_index]

        # Save task
        task = {
            'from': start,
            'to': end,
            'payload_kg': payload_kg,
            'material_type': material_type,
            'priority': priority,
            'status': 'pending',  # pending, in_progress, completed, failed
            'assigned_drone': None,
            'start_time': None,
            'end_time': None
        }

        self.delivery_tasks.append(task)
        self.task_queue.append(task)
        return task

    def direct_path(self, start, end):
        """Direct path planning"""
        return [start['position'], end['position']]

    def a_star_path(self, start, end):
        """A* path planning (consider obstacles)"""
        # Simplified implementation
        if not self.obstacles:
            return [start['position'], end['position']]

        # Calculate midpoint
        mid_lat = (start['position'][0] + end['position'][0]) / 2
        mid_lon = (start['position'][1] + end['position'][1]) / 2

        # Random offset to avoid obstacles
        offset_lat = random.uniform(-0.01, 0.01)
        offset_lon = random.uniform(-0.01, 0.01)

        waypoint = (mid_lat + offset_lat, mid_lon + offset_lon)

        return [start['position'], waypoint, end['position']]

    def dijkstra_path(self, start, end):
        """Dijkstra path planning (road network)"""
        if len(self.road_network.nodes) == 0:
            return [start['position'], end['position']]

        try:
            path_nodes = nx.shortest_path(self.road_network, start['name'], end['name'], weight='weight')
        except nx.NetworkXNoPath:
            return [start['position'], end['position']]

        # Get positions
        path = [self.road_network.nodes[node]['pos'] for node in path_nodes]

        return path

    def genetic_algorithm_path(self, start, end):
        """Genetic algorithm path planning (multi-objective)"""
        # Simplified implementation
        path = [start['position']]

        # Add 1-3 random waypoints
        num_waypoints = random.randint(1, 3)
        for _ in range(num_waypoints):
            lat = random.uniform(min(start['position'][0], end['position'][0]),
                                 max(start['position'][0], end['position'][0]))
            lon = random.uniform(min(start['position'][1], end['position'][1]),
                                 max(start['position'][1], end['position'][1]))
            path.append((lat, lon))

        path.append(end['position'])

        return path

    def plan_delivery(self, algorithm='direct', task_index=0):
        """
        Plan delivery task
        :param algorithm: Path algorithm ('direct', 'a_star', 'dijkstra', 'genetic')
        :param task_index: Task index
        :return: Delivery path
        """
        if task_index < 0 or task_index >= len(self.delivery_tasks):
            raise ValueError("Invalid task index")

        task = self.delivery_tasks[task_index]
        start = task['from']
        end = task['to']

        # Select path method
        if algorithm == 'direct':
            path = self.direct_path(start, end)
        elif algorithm == 'a_star':
            path = self.a_star_path(start, end)
        elif algorithm == 'dijkstra':
            path = self.dijkstra_path(start, end)
        elif algorithm == 'genetic':
            path = self.genetic_algorithm_path(start, end)
        else:
            path = [start['position'], end['position']]  # Default direct

        # Calculate total distance
        total_distance = 0
        for i in range(1, len(path)):
            total_distance += self.calculate_distance(path[i - 1], path[i])

        # Return delivery path
        return {
            'algorithm': algorithm,
            'path': path,
            'distance_km': total_distance,
            'transfer_needed': self.check_transfer_needed(total_distance)
        }

    def initialize_drones(self, num_drones_per_center=2):
        """Initialize drone fleet"""
        self.drones = []
        for center in self.distribution_centers:
            for i in range(num_drones_per_center):
                drone = {
                    'id': f"{center['name']}_Drone_{i + 1}",
                    'home_base': center['name'],  # Add home_base
                    'position': center['position'],
                    'battery_level': 100,  # %
                    'battery_cycles': 0,
                    'status': 'idle',  # idle, charging, flying, delivering
                    'current_task': None,
                    'total_distance': 0,  # km
                    'total_flight_time': 0,  # min
                    'battery_swaps': 0
                }
                self.drones.append(drone)

    def set_energy_strategy(self, strategy):
        """Set energy replenishment strategy"""
        valid_strategies = ['A', 'B', 'C', 'D']
        if strategy in valid_strategies:
            self.energy_strategy = strategy
            print(f"Energy strategy set to: {strategy}")
        else:
            print(f"Invalid strategy: {strategy}. Valid options: {valid_strategies}")

    def check_transfer_needed(self, distance_km):
        """
        Check if transfer needed
        :param distance_km: Distance (km)
        :return: Transfer required
        """
        return distance_km > self.max_range

    def plan_transfer(self, start, end, payload_kg):
        """
        Plan transfer route
        :param start: Start point
        :param end: End point
        :param payload_kg: Payload
        :return: Transfer points
        """
        # Simplified implementation
        start_pos = start['position']
        end_pos = end['position']

        mid_lat = (start_pos[0] + end_pos[0]) / 2
        mid_lon = (start_pos[1] + end_pos[1]) / 2

        # Find nearest transfer point
        transfer_point = None
        min_distance = float('inf')

        # Check all centers and hospitals
        all_points = self.distribution_centers + self.hospitals
        for point in all_points:
            distance = self.calculate_distance((mid_lat, mid_lon), point['position'])
            if distance < min_distance:
                min_distance = distance
                transfer_point = point

        return [transfer_point] if transfer_point else []

    def apply_energy_strategy(self, drone, task):
        """
        Apply energy strategy
        :param drone: Drone
        :param task: Task
        :return: Charge/swap required
        """
        # Calculate required energy
        distance = self.calculate_distance(drone['position'], task['from']['position'])
        distance += self.calculate_distance(task['from']['position'], task['to']['position'])
        flight_time = self.calculate_flight_time_from_distance(distance, task['payload_kg'])
        energy_needed = self.calculate_energy_consumption(distance, task['payload_kg'], flight_time)

        # Convert capacity to Wh
        battery_wh = self.battery_capacity / 1000 * 14.8

        # Available energy
        available_energy = (drone['battery_level'] / 100) * battery_wh

        # Strategy A: Charge after every task
        if self.energy_strategy == 'A':
            return True  # Always charge

        # Strategy B: Charge every two tasks
        elif self.energy_strategy == 'B':
            if drone['battery_cycles'] % 2 == 0:
                return True
            return available_energy < energy_needed * 1.2  # 20% safety margin

        # Strategy C: Dynamic judgment
        elif self.energy_strategy == 'C':
            # 20% safety margin
            if available_energy < energy_needed * 1.2:
                return True
            return False

        # Strategy D: Hot-swap batteries
        elif self.energy_strategy == 'D':
            # Always swap
            self.performance_metrics['battery_swaps'] += 1
            drone['battery_swaps'] += 1
            return True

        return False

    def charge_battery(self, drone, to_full=True):
        """Charge operation"""
        if to_full:
            drone['battery_level'] = 100
        else:
            # Fast charge to 80%
            drone['battery_level'] = min(100, drone['battery_level'] + 80)

        drone['battery_cycles'] += 1
        self.performance_metrics['battery_cycles'] += 1
        drone['status'] = 'charging'

        # Log
        self.log.append({
            'time': self.current_time,
            'event': 'charging',
            'drone': drone['id'],
            'battery_level': drone['battery_level']
        })

    def schedule_tasks(self):
        """Task scheduling"""
        # Sort tasks by priority
        priority_order = {'high': 1, 'normal': 2, 'low': 3}
        self.task_queue.sort(key=lambda t: priority_order[t['priority']])

        # Assign to drones
        for task in self.task_queue:
            if task['status'] != 'pending':
                continue

            # Find available drones
            available_drones = [d for d in self.drones if
                                d['status'] == 'idle' and d['home_base'] == task['from']['name']]

            if not available_drones:
                print(f"No drones available for: {task['from']['name']} -> {task['to']['name']}")
                continue

            # Select highest battery drone
            available_drones.sort(key=lambda d: d['battery_level'], reverse=True)
            drone = available_drones[0]

            # Check energy need
            if self.apply_energy_strategy(drone, task):
                if self.energy_strategy == 'D':
                    # Hot-swap battery
                    drone['battery_level'] = 100
                    drone['battery_swaps'] += 1
                    self.performance_metrics['battery_swaps'] += 1

                    # Log
                    self.log.append({
                        'time': self.current_time,
                        'event': 'battery_swap',
                        'drone': drone['id'],
                        'battery_level': 100
                    })
                else:
                    # Charge
                    self.charge_battery(drone)
                    # Charge time (assume 10 min)
                    self.current_time += timedelta(minutes=10)

            # Assign task
            task['status'] = 'in_progress'
            task['assigned_drone'] = drone['id']
            task['start_time'] = self.current_time
            drone['status'] = 'flying'
            drone['current_task'] = task

            # Log
            self.log.append({
                'time': self.current_time,
                'event': 'task_start',
                'drone': drone['id'],
                'task': f"{task['from']['name']} -> {task['to']['name']}",
                'payload': task['payload_kg'],
                'battery_level': drone['battery_level']
            })

            # Execute task
            self.execute_task(drone, task)

            # Update time
            self.current_time += timedelta(minutes=task['flight_time_min'])

            # Add service time
            self.current_time += timedelta(minutes=task['to']['service_time'])

            # Complete task
            task['status'] = 'completed'
            task['end_time'] = self.current_time
            drone['status'] = 'idle'
            drone['current_task'] = None

            # Log
            self.log.append({
                'time': self.current_time,
                'event': 'task_complete',
                'drone': drone['id'],
                'task': f"{task['from']['name']} -> {task['to']['name']}",
                'battery_level': drone['battery_level']
            })

    def execute_task(self, drone, task):
        """Execute delivery task"""
        # Calculate distances
        distance_to_start = self.calculate_distance(drone['position'], task['from']['position'])
        distance_to_end = self.calculate_distance(task['from']['position'], task['to']['position'])
        total_distance = distance_to_start + distance_to_end

        # Check if transfer needed
        if self.check_transfer_needed(total_distance):
            transfer_points = self.plan_transfer(task['from'], task['to'], task['payload_kg'])
            if transfer_points:
                self.performance_metrics['transfer_count'] += 1

                # Execute in segments
                segments = []
                current_pos = drone['position']

                # Start to transfer point
                segments.append({
                    'from': task['from'],
                    'to': transfer_points[0],
                    'distance': self.calculate_distance(current_pos, transfer_points[0]['position'])
                })
                current_pos = transfer_points[0]['position']

                # Transfer to destination
                segments.append({
                    'from': transfer_points[0],
                    'to': task['to'],
                    'distance': self.calculate_distance(current_pos, task['to']['position'])
                })

                # Execute segments
                for segment in segments:
                    flight_time = self.calculate_flight_time_from_distance(segment['distance'], task['payload_kg'])
                    energy_used = self.calculate_energy_consumption(segment['distance'], task['payload_kg'],
                                                                    flight_time)

                    # Update drone
                    battery_wh = self.battery_capacity / 1000 * 14.8
                    energy_used_percent = (energy_used / battery_wh) * 100
                    drone['battery_level'] = max(0, drone['battery_level'] - energy_used_percent)
                    drone['total_distance'] += segment['distance']
                    drone['total_flight_time'] += flight_time

                    # Log
                    self.log.append({
                        'time': self.current_time,
                        'event': 'transfer_segment',
                        'drone': drone['id'],
                        'from': segment['from']['name'],
                        'to': segment['to']['name'],
                        'distance': segment['distance'],
                        'energy_used': energy_used,
                        'battery_level': drone['battery_level']
                    })

                    # Update time
                    self.current_time += timedelta(minutes=flight_time)

                    # Transfer service time
                    if segment['to'] != task['to']:
                        self.current_time += timedelta(minutes=5)
            else:
                # No transfer found, fail task
                task['status'] = 'failed'
                drone['status'] = 'idle'
                drone['current_task'] = None
                self.performance_metrics['abort_rate'] += 1

                # Log
                self.log.append({
                    'time': self.current_time,
                    'event': 'task_failed',
                    'drone': drone['id'],
                    'task': f"{task['from']['name']} -> {task['to']['name']}",
                    'reason': 'No transfer point found'
                })
                return
        else:
            # Direct flight
            flight_time = self.calculate_flight_time_from_distance(total_distance, task['payload_kg'])
            energy_used = self.calculate_energy_consumption(total_distance, task['payload_kg'], flight_time)

            # Update drone
            battery_wh = self.battery_capacity / 1000 * 14.8
            energy_used_percent = (energy_used / battery_wh) * 100
            drone['battery_level'] = max(0, drone['battery_level'] - energy_used_percent)
            drone['total_distance'] += total_distance
            drone['total_flight_time'] += flight_time

            # Log
            self.log.append({
                'time': self.current_time,
                'event': 'direct_flight',
                'drone': drone['id'],
                'from': task['from']['name'],
                'to': task['to']['name'],
                'distance': total_distance,
                'energy_used': energy_used,
                'battery_level': drone['battery_level']
            })

        # Update task
        task['flight_time_min'] = flight_time
        task['distance_km'] = total_distance
        task['energy_used'] = energy_used

        # Update metrics
        self.performance_metrics['total_time'] += flight_time
        self.performance_metrics['total_energy'] += energy_used

        # Check safety margin
        if drone['battery_level'] < 20:
            self.performance_metrics['safe_margin_violations'] += 1

    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        total_tasks = len(self.delivery_tasks)
        completed_tasks = sum(1 for t in self.delivery_tasks if t['status'] == 'completed')
        failed_tasks = sum(1 for t in self.delivery_tasks if t['status'] == 'failed')

        self.performance_metrics['success_rate'] = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        self.performance_metrics['abort_rate'] = (failed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        return self.performance_metrics

    def create_delivery_map(self, algorithm='direct'):
        """Create delivery map"""
        if not self.distribution_centers and not self.hospitals:
            return None

        # Calculate center point
        all_points = [center['position'] for center in self.distribution_centers] + \
                     [hospital['position'] for hospital in self.hospitals]

        avg_lat = sum(p[0] for p in all_points) / len(all_points)
        avg_lon = sum(p[1] for p in all_points) / len(all_points)

        # Create map
        m = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=12,
            tiles='OpenStreetMap',
            control_scale=True
        )

        # Add centers
        for center in self.distribution_centers:
            folium.Marker(
                location=center['position'],
                popup=f"<b>{center['name']}</b><br>Distribution Center",
                icon=folium.Icon(color='green', icon='warehouse', prefix='fa')
            ).add_to(m)

        # Add hospitals
        for hospital in self.hospitals:
            folium.Marker(
                location=hospital['position'],
                popup=f"<b>{hospital['name']}</b><br>Hospital",
                icon=folium.Icon(color='red', icon='hospital', prefix='fa')
            ).add_to(m)

        # Add obstacles
        for obstacle in self.obstacles:
            folium.Circle(
                location=obstacle['position'],
                radius=obstacle['radius'] * 1000,  # Convert to meters
                color='gray',
                fill=True,
                fill_color='gray',
                fill_opacity=0.3,
                popup=f"Obstacle (radius: {obstacle['radius']}km)"
            ).add_to(m)

        # Add road network
        for edge in self.road_network.edges:
            node1 = self.road_network.nodes[edge[0]]
            node2 = self.road_network.nodes[edge[1]]

            folium.PolyLine(
                locations=[node1['pos'], node2['pos']],
                color='gray',
                weight=2,
                opacity=0.5
            ).add_to(m)

        # Add delivery paths
        colors = {
            'direct': 'blue',
            'a_star': 'green',
            'dijkstra': 'red',
            'genetic': 'purple'
        }

        for i, task in enumerate(self.delivery_tasks):
            if task['status'] != 'completed':
                continue

            # Plan path
            route = self.plan_delivery(algorithm, i)

            # Create path
            AntPath(
                locations=route['path'],
                color=colors[algorithm],
                weight=4,
                dash_array=[10, 20],
                delay=800,
                pulse_color='#00FFFF'
            ).add_to(m)

            # Add transfer marker if needed
            if route.get('transfer_needed', False):
                mid_idx = len(route['path']) // 2
                mid_point = route['path'][mid_idx]
                folium.Marker(
                    location=mid_point,
                    icon=folium.Icon(color='orange', icon='exchange', prefix='fa'),
                    popup="Transfer Point"
                ).add_to(m)

        return m

    def plot_energy_consumption(self):
        """Plot energy consumption comparison"""
        plt.figure(figsize=(12, 6))

        # Group energy by material type
        energy_by_type = {}
        for task in self.delivery_tasks:
            if task['status'] != 'completed':
                continue
            if 'energy_used' not in task or pd.isna(task['energy_used']):
                continue

            material_type = task.get('material_type', 'unknown')
            if material_type not in energy_by_type:
                energy_by_type[material_type] = []
            energy_by_type[material_type].append(task['energy_used'])

        # Calculate averages
        avg_energy = {}
        for material, energies in energy_by_type.items():
            if energies:
                avg_energy[material] = sum(energies) / len(energies)

        # Plot bars
        if avg_energy:
            materials = list(avg_energy.keys())
            energies = list(avg_energy.values())

            plt.bar(materials, energies, color=['blue', 'green', 'red', 'purple', 'orange'])
            plt.title('Average Energy by Material Type', fontsize=14)
            plt.xlabel('Material Type', fontsize=12)
            plt.ylabel('Energy (Wh)', fontsize=12)

            # Add labels
            for i, energy in enumerate(energies):
                plt.text(i, energy + 5, f"{energy:.1f}", ha='center')
        else:
            plt.text(0.5, 0.5, 'No energy data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            plt.title('Energy Comparison', fontsize=14)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save image
        plt.savefig('energy_consumption.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'energy_consumption.png'

    def plot_time_statistics(self):
        """Plot time statistics"""
        plt.figure(figsize=(12, 6))

        # Extract task times
        flight_times = []
        service_times = []
        for task in self.delivery_tasks:
            if task['status'] != 'completed':
                continue
            if 'flight_time_min' in task and not pd.isna(task['flight_time_min']):
                flight_times.append(task['flight_time_min'])
            if 'to' in task and 'service_time' in task['to'] and not pd.isna(task['to']['service_time']):
                service_times.append(task['to']['service_time'])

        # Plot
        if flight_times or service_times:
            if flight_times:
                plt.plot(range(len(flight_times)), flight_times, 'o-', label='Flight Time')
            if service_times:
                plt.plot(range(len(service_times)), service_times, 'o-', label='Service Time')

            plt.title('Task Time Statistics', fontsize=14)
            plt.xlabel('Task Index', fontsize=12)
            plt.ylabel('Time (min)', fontsize=12)
            plt.legend()
        else:
            plt.text(0.5, 0.5, 'No time data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            plt.title('Time Statistics', fontsize=14)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save image
        plt.savefig('time_statistics.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'time_statistics.png'

    def plot_battery_cycles(self):
        """Plot battery cycles"""
        plt.figure(figsize=(8, 8))

        # Collect cycles per drone
        cycles_by_drone = {}
        for drone in self.drones:
            if 'battery_cycles' in drone and not pd.isna(drone['battery_cycles']) and drone['battery_cycles'] > 0:
                cycles_by_drone[drone['id']] = drone['battery_cycles']

        # Check data
        if not cycles_by_drone:
            plt.text(0.5, 0.5, 'No battery cycle data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            plt.title('Battery Cycle Distribution', fontsize=14)
        else:
            # Create pie chart
            plt.pie(cycles_by_drone.values(),
                    labels=cycles_by_drone.keys(),
                    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                    startangle=90)
            plt.title('Battery Cycle Distribution', fontsize=14)

        # Save image
        plt.savefig('battery_cycles.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'battery_cycles.png'

    def plot_performance_metrics(self):
        """Plot performance metrics"""
        # Calculate metrics
        metrics = self.calculate_performance_metrics()

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Metric names
        metric_names = ['Total Time(min)', 'Total Energy(Wh)', 'Battery Cycles', 'Battery Swaps', 'Safety Violations',
                        'Success Rate(%)',
                        'Abort Rate(%)', 'Transfers']
        metric_values = [
            metrics.get('total_time', 0),
            metrics.get('total_energy', 0),
            metrics.get('battery_cycles', 0),
            metrics.get('battery_swaps', 0),
            metrics.get('safe_margin_violations', 0),
            metrics.get('success_rate', 0),
            metrics.get('abort_rate', 0),
            metrics.get('transfer_count', 0)
        ]

        # Plot bars
        if any(metric_values):
            bars = ax.bar(metric_names, metric_values, color='skyblue')

            # Add values
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')

            ax.set_title('System Performance Metrics', fontsize=16)
            ax.set_ylabel('Value', fontsize=12)
        else:
            plt.text(0.5, 0.5, 'No performance data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            ax.set_title('Performance Metrics', fontsize=14)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save image
        plt.savefig('performance_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'performance_metrics.png'

    def plot_flight_time_vs_payload(self):
        """Plot flight time vs payload"""
        plt.figure(figsize=(10, 6))

        # Extract data
        payloads = []
        flight_times = []
        for task in self.delivery_tasks:
            if task['status'] != 'completed':
                continue
            if 'payload_kg' in task and not pd.isna(task['payload_kg']):
                payloads.append(task['payload_kg'])
            if 'flight_time_min' in task and not pd.isna(task['flight_time_min']):
                flight_times.append(task['flight_time_min'])

        # Plot
        if payloads and flight_times and len(payloads) == len(flight_times):
            plt.plot(payloads, flight_times, 'o-', color='#1f77b4', label='Flight Time')

            plt.title('Flight Time vs Payload', fontsize=14)
            plt.xlabel('Payload (kg)', fontsize=12)
            plt.ylabel('Flight Time (min)', fontsize=12)

            # Add labels
            for i, (x, y) in enumerate(zip(payloads, flight_times)):
                plt.annotate(f"{y:.1f} min", (x, y),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center')

            plt.legend()
        else:
            plt.text(0.5, 0.5, 'No flight time/payload data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            plt.title('Flight Time vs Payload', fontsize=14)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save image
        plt.savefig('flight_time_vs_payload.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'flight_time_vs_payload.png'

    def plot_thrust_ratio_vs_payload(self):
        """Plot thrust ratio vs payload"""
        plt.figure(figsize=(10, 6))

        # Extract data
        payloads = []
        thrust_ratios = []
        for task in self.delivery_tasks:
            if task['status'] != 'completed':
                continue
            if 'payload_kg' in task and not pd.isna(task['payload_kg']):
                payloads.append(task['payload_kg'])
            if 'thrust_ratio' in task and not pd.isna(task['thrust_ratio']):
                thrust_ratios.append(task['thrust_ratio'])

        # Plot
        if payloads and thrust_ratios and len(payloads) == len(thrust_ratios):
            plt.plot(payloads, thrust_ratios, 'o-', color='#ff7f0e', label='Thrust Ratio')

            plt.title('Thrust Ratio vs Payload', fontsize=14)
            plt.xlabel('Payload (kg)', fontsize=12)
            plt.ylabel('Thrust Ratio', fontsize=12)

            # Add labels
            for i, (x, y) in enumerate(zip(payloads, thrust_ratios)):
                plt.annotate(f"{y:.1f}", (x, y),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center')

            plt.legend()
        else:
            plt.text(0.5, 0.5, 'No thrust ratio/payload data',
                     horizontalalignment='center',
                     verticalalignment='center',
                     fontsize=16)
            plt.title('Thrust Ratio vs Payload', fontsize=14)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save image
        plt.savefig('thrust_ratio_vs_payload.png', dpi=300, bbox_inches='tight')
        plt.close()

        return 'thrust_ratio_vs_payload.png'

    def export_logs(self, file_path='delivery_logs.json'):
        """Export logs to file"""
        try:
            # Convert datetime
            log_data = []
            for entry in self.log:
                entry_copy = entry.copy()
                entry_copy['time'] = entry_copy['time'].isoformat()
                log_data.append(entry_copy)

            with open(file_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"Logs exported to: {file_path}")
            return True
        except Exception as e:
            print(f"Log export failed: {str(e)}")
            return False

    def run_simulation(self):
        """Run entire simulation"""
        print("Starting simulation...")
        self.current_time = datetime.now()

        # Initialize drones
        self.initialize_drones(num_drones_per_center=2)

        # Schedule tasks
        self.schedule_tasks()

        # Calculate metrics
        self.calculate_performance_metrics()

        print("Simulation complete!")

        # Print metrics
        print("\nPerformance metrics:")
        for k, v in self.performance_metrics.items():
            print(f"{k}: {v}")

        # Generate visuals
        print("\nGenerating visualizations...")
        self.create_delivery_map().save('delivery_map.html')
        self.plot_energy_consumption()
        self.plot_time_statistics()
        self.plot_battery_cycles()
        self.plot_performance_metrics()
        self.plot_flight_time_vs_payload()
        self.plot_thrust_ratio_vs_payload()

        # Export logs
        self.export_logs()

        print("\nAll outputs generated!")


# Create Bristol medical delivery system
def create_bristol_medical_delivery():
    # Create instance
    delivery_system = MedicalDroneDelivery()

    # Import data
    delivery_system.import_data()

    # Set energy strategy
    delivery_system.set_energy_strategy('C')  # Dynamic strategy

    delivery_system.run_simulation()
if __name__ == "__main__":
    try:
        create_bristol_medical_delivery()
        print("Simulation completed successfully!")
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)