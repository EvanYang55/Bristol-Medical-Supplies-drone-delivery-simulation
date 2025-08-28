from Strategy_Choose import interactive_path_planner
from Distance_calculate import calculate_distance
from Astart import optimize_paths as optimize_path_Astart
from Dijkstra import optimize_paths as optimize_path_Dijkstra
from Charge import charge_simulation
from temdecrease import battery_degradation



# Maximum allowed payload weight (kg)
MAX_PAYLOAD = 45.03
# Location name mapping
LOCATION_NAMES = {
    # Target points
    'target': {
        1: "NHS Blood Centre (Filton)",
        2: "South Bristol NHS Community Hospital",
        3: "UWE Health Tech Hub"
    },
    # Task points
    'task': {
        1: "Southmead Hospital",
        2: "Bristol Royal Infirmary (BRI)",
        3: "St Michael's Hospital",
        4: "Eastville Medical Centre",
        5: "Fishponds Primary Care Centre",
        6: "Bristol Haematology and Oncology Centre (BHOC)",
        7: "Emersons Green NHS Treatment Centre",
        8: "Lawrence Hill Health Centre",
        9: "Montpelier Health Centre"
    }
}


def main():
    print("=== Medical Resource Path Planning System ===")
    print("Loading path planning selection interface...")

    # Call the interactive path planning selection function
    targets, tasks, strategy, charge_strategy, temperature = interactive_path_planner()

    # Check if the user made a selection
    if not targets or not tasks:
        print("User canceled selection or did not select any points. Program exiting.")
        return

    print("\n=== User Selection Results ===")
    print("Target Points and Payload Weights:")
    total_target_weight = 0.0
    target_names = []
    for target_id, weight in targets:
        name = LOCATION_NAMES['target'][target_id]
        print(f"  Target Point {target_id}: {name} - {weight} kg")
        total_target_weight += weight
        target_names.append(name)

    print("\nTask Points and Payload Weights:")
    total_task_weight = 0.0
    task_names = []
    for task_id, weight in tasks:
        name = LOCATION_NAMES['task'][task_id]
        print(f"  Task Point {task_id}: {name} - {weight} kg")
        total_task_weight += weight
        task_names.append(name)

    strategy_id = strategy[0]
    strategy_names = {
        1: "A* Path Planning Algorithm",
        2: "Dijkstra Algorithm"
    }
    print(f"\nSelected Path Optimization Strategy: {strategy_id} - {strategy_names[strategy_id]}")
    charge_strategy_id = charge_strategy[0]
    charge_strategy_names = {
        1: "Strategy A: Return to charge after each mission, then depart with a full battery.",
        2: "Strategy B: Return to charge after completing two missions, then depart with a full battery."
    }
    print(f"\nSelected Charge Strategy: {charge_strategy_id} - {charge_strategy_names[charge_strategy_id]}")


    # Check if total target payload weight exceeds limit
    if total_target_weight > MAX_PAYLOAD:
        print(
            f"\nError: Total target payload weight {total_target_weight:.2f} kg exceeds maximum allowed {MAX_PAYLOAD} kg!")
        print("Please reduce target payload weights and try again.")
        return

    # Check if total task payload weight exceeds limit
    if total_task_weight > MAX_PAYLOAD:
        print(
            f"\nWarning: Total task payload weight {total_task_weight:.2f} kg exceeds maximum allowed {MAX_PAYLOAD} kg!")
        print("This may affect path planning results.")

    print("\n=== Calculating Distances Between Points ===")
    all_points = target_names + task_names
    distance_matrix = {}

    # Calculate and store distances between all point pairs
    for i, loc1 in enumerate(all_points):
        for j, loc2 in enumerate(all_points):
            if i < j:  # Avoid duplicate calculations and self-distance
                distance = calculate_distance(loc1, loc2)
                distance_matrix[(loc1, loc2)] = distance
                distance_matrix[(loc2, loc1)] = distance  # Symmetric storage
                print(f"  {loc1} -> {loc2}: {distance:.2f} km")


    # Execute path planning

    # 在策略选择后添加以下代码
    if strategy_id == 1:  # A* Algorithm
        print("\n=== Using A* Algorithm for Path Planning ===")
        # Pass the correct distance_data dictionary
        paths, total_distances, segment_distances_list = optimize_path_Astart(target_names, task_names, distance_matrix)

        # 初始化 flight_missions 数组
        flight_missions = []

        # Process results for each start point
        for i, start in enumerate(target_names):
            print(f"\nPath for start point: {start}")
            print("Optimal Path:")
            print(" -> ".join(paths[i]))
            print(f"Total Distance: {total_distances[i]:.2f} km")

            print("Path Segment Distances:")
            for loc1, loc2, distance in segment_distances_list[i]:
                mission_str = f"{loc1} -> {loc2}: {distance:.2f} km"
                flight_missions.append(mission_str)
                print(f"  {mission_str}")
        temperature_D = battery_degradation(temperature)
        charged_missions, total_time, total_energy, total_segments = charge_simulation(
            flight_missions, charge_strategy_names[charge_strategy_id], temperature_D, targets, tasks)

        # 打印返回值
        print("\n=== Charge Simulation Results ===")
        print("Return Value 1 (Charged Missions):")
        for mission in charged_missions:
            print(f"  {mission}")

        print(f"\nReturn Value 2 (Total Flight Time): {total_time:.2f} minutes")
        print(f"Return Value 3 (Total Energy Consumed): {total_energy:.2f} Ah")
        print(f"Return Value 4 (Total Segments): {total_segments}")




    if strategy_id == 2:  # Dijkstra Algorithm
        print("\n=== Using Dijkstra Algorithm for Path Planning ===")
        # Pass the correct distance_data dictionary
        paths, total_distances, segment_distances_list = optimize_path_Dijkstra(target_names, task_names,distance_matrix)

        # 初始化 flight_missions 数组
        flight_missions = []

        # Process results for each start point
        for i, start in enumerate(target_names):
            print(f"\nPath for start point: {start}")
            print("Optimal Path:")
            print(" -> ".join(paths[i]))
            print(f"Total Distance: {total_distances[i]:.2f} km")

            print("Path Segment Distances:")
            for loc1, loc2, distance in segment_distances_list[i]:
                mission_str = f"{loc1} -> {loc2}: {distance:.2f} km"
                flight_missions.append(mission_str)
                print(f"  {mission_str}")
        temperature_D = battery_degradation(temperature)
        charged_missions, total_time, total_energy, total_segments = charge_simulation(
            flight_missions, charge_strategy_names[charge_strategy_id], temperature_D, targets, tasks)
        # 打印返回值
        print("\n=== Charge Simulation Results ===")
        print("Return Value 1 (Charged Missions):")
        for mission in charged_missions:
            print(f"  {mission}")

        print(f"\nReturn Value 2 (Total Flight Time): {total_time:.2f} minutes")
        print(f"Return Value 3 (Total Energy Consumed): {total_energy:.2f} Ah")
        print(f"Return Value 4 (Total Segments): {total_segments}")

if __name__ == "__main__":

    main()
