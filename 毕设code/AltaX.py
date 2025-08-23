import sys
import numpy as np


def simulate_flight(payload, distance_desired, battery_capacity, payload_battery_attenuation,
                    tem_battery_degradation):
    """
    Simulate the flight process of Alta X drone with battery degradation factors

    Parameters:
    payload (float): Payload weight (kg) [must be <= 15.06 kg]
    distance_desired (float): Desired flight distance (km) [must be <= 3.6 km]
    battery_capacity (float): Battery capacity (Ah) [must be <= 18.0 Ah]
    temperature (float): Operating temperature (°C) [0-50°C]
    payload_battery_attenuation (float): Payload-induced battery attenuation (optional)
    tem_battery_degradation (float): Temperature-induced battery degradation (optional)

    Returns:
    tuple: (time_flown, time_remaining_battery, energy_remaining) for the final state
    """
    # Drone specifications
    MAX_PAYLOAD = 15.06  # kg
    MAX_DISTANCE = 3.6  # km
    MAX_BATTERY = 18.0  # Ah

    # Input validation
    if payload > MAX_PAYLOAD:
        return "Error: Payload cannot exceed maximum payload (15.06 kg)"

    if distance_desired > MAX_DISTANCE:
        return "Error: Flight distance cannot exceed maximum range (3.6 km)"

    if battery_capacity > MAX_BATTERY:
        return "Error: Battery capacity cannot exceed maximum capacity (18.0 Ah)"

    if payload < 0 or distance_desired < 0 or battery_capacity < 0:
        return "Error: Payload, distance and battery capacity cannot be negative"

    # Drone performance parameters
    BATTERY_CAPACITY = battery_capacity
    DISCHARGE_CURRENT = 5.68  # A
    SPEED_KM_PER_MIN = 10.8 / 60  # km/min

    # Calculate total degradation factor
    degradation_factor = 1 + tem_battery_degradation + payload_battery_attenuation
    print(f"Battery degradation factor: {degradation_factor:.3f}")

    # Calculate required flight time (minutes)
    time_required = distance_desired / SPEED_KM_PER_MIN
    total_minutes = int(time_required) + (1 if time_required % 1 > 0 else 0)

    # Initialize state
    time_flown = 0
    energy_used = 0.0
    energy_remaining = BATTERY_CAPACITY
    distance_flown = 0.0
    distance_remaining = distance_desired

    # Final state variables to return
    final_time_flown = 0
    final_time_remaining = 0
    final_energy_remaining = BATTERY_CAPACITY

    # Simulate flight minute by minute
    for t in range(total_minutes + 1):
        # Calculate current flight state with degradation applied
        base_energy = (DISCHARGE_CURRENT * t) / 60.0
        energy_used = base_energy * degradation_factor
        energy_remaining = max(0.0, BATTERY_CAPACITY - energy_used)

        # Calculate remaining flight time (based on battery)
        if energy_remaining > 0 and DISCHARGE_CURRENT > 0:
            time_remaining_battery = (energy_remaining * 60) / DISCHARGE_CURRENT
        else:
            time_remaining_battery = 0.0

        # Calculate distance
        if t == total_minutes:
            distance_flown = distance_desired  # Ensure reaching target
        else:
            distance_flown = min(SPEED_KM_PER_MIN * t, distance_desired)
        distance_remaining = max(0.0, distance_desired - distance_flown)

        # Update final state for the last minute
        final_time_flown = t
        final_time_remaining = time_remaining_battery
        final_energy_remaining = energy_remaining

        # Break conditions: target reached or no energy left
        if distance_flown >= distance_desired or energy_remaining <= 0:
            break

    return final_time_flown, final_time_remaining, final_energy_remaining
