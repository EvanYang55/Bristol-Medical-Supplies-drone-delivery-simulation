from AltaX import simulate_flight
from battery import calculate_battery_attenuation


def calculate_average_payload(target):
    """
    计算目标数组中 payload 的平均值

    参数:
        target: 包含 (id, payload) 元组的列表或数组

    返回:
        float: payload 的平均值
    """
    # 提取所有 payload 值
    payloads = [item[1] for item in target]

    # 计算平均值
    average = sum(payloads) / len(payloads)

    return average
def charge_simulation(flight_missions, charge_strategy,temperature_D, targets, tasks):

    """
    充电模拟函数

    参数:
    flight_missions: 飞行任务列表，格式为 ["起点 -> 终点: 距离 km", ...]
    charge_strategy: 充电策略字符串

    返回:
    new_missions: 添加充电点后的飞行任务列表
    total_time_flown: 总飞行时间 (分钟)
    total_energy_consumed: 总能量消耗 (Ah)
    total_segments: 总航段数 (原始任务数 + 截断次数)
    """
    # 解析飞行任务
    average_payload = calculate_average_payload(targets)
    payload_D = calculate_battery_attenuation(average_payload)
    parsed_missions = []
    for mission in flight_missions:
        # 分割起点和终点
        parts = mission.split(" -> ")
        start = parts[0].strip()
        end_part = parts[1].split(":")
        end = end_part[0].strip()
        distance = float(end_part[1].split("km")[0].strip())
        parsed_missions.append((start, end, distance))

    # 处理长距离航段 (大于3.6km)
    processed_missions = []
    truncate_count = 0
    charge_spot_counter = 1

    for start, end, distance in parsed_missions:
        if distance > 3.6:
            # 需要截断
            truncate_count += 1
            # 第一段
            processed_missions.append((start, f"Charge spot {charge_spot_counter}", 3.6))
            # 第二段
            processed_missions.append((f"Charge spot {charge_spot_counter}", end, distance - 3.6))
            charge_spot_counter += 1
        else:
            processed_missions.append((start, end, distance))

    # 初始化结果
    new_missions = []
    total_time_flown = 0.0
    total_energy_consumed = 0.0
    battery_capacity = 18.0  # 电池容量
    payload = 1.0  # 有效载荷重量

    # 根据充电策略进行模拟
    if "Strategy A" in charge_strategy:
        # 策略A: 每次任务后返回充电
        for i, (start, end, distance) in enumerate(processed_missions):
            # 模拟飞行
            time_flown, time_remaining, energy_remaining = simulate_flight(
                payload, distance, battery_capacity, payload_D,temperature_D
            )

            # 添加任务
            new_missions.append(f"{start} -> {end}: {distance:.2f} km")

            # 累加时间和能量消耗
            total_time_flown += time_flown
            total_energy_consumed += (battery_capacity - energy_remaining)

            # 如果不是最后一个任务，添加返回充电和重新出发的任务
            if i < len(processed_missions) - 1:
                # 返回充电站
                return_distance = distance / 2  # 简化：假设返回距离为当前距离的一半
                new_missions.append(f"{end} -> Charge station: {return_distance:.2f} km")

                # 重新出发
                next_start = processed_missions[i + 1][0]
                depart_distance = return_distance  # 简化：假设出发距离与返回距离相同
                new_missions.append(f"Charge station -> {next_start}: {depart_distance:.2f} km")

                # 累加返回和出发的时间和能量消耗
                return_time, _, return_energy_remaining = simulate_flight(
                    payload, return_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += return_time
                total_energy_consumed += (battery_capacity - return_energy_remaining)

                depart_time, _, depart_energy_remaining = simulate_flight(
                    payload, depart_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += depart_time
                total_energy_consumed += (battery_capacity - depart_energy_remaining)

        # 计算总航段数
        total_segments = len(processed_missions) + truncate_count + 2 * (len(processed_missions) - 1)

    elif "Strategy B" in charge_strategy:
        # 策略B: 每完成两个任务后返回充电
        mission_count = 0
        current_energy = battery_capacity

        for i, (start, end, distance) in enumerate(processed_missions):
            # 模拟飞行以获取实际所需时间
            time_flown, time_remaining, energy_remaining = simulate_flight(
                payload, distance, current_energy, payload_D,temperature_D
            )

            # 估算所需能量（使用模拟飞行结果）
            required_energy = distance * (5.68 / 60) * time_flown

            # 检查当前能量是否足够
            if current_energy < required_energy:
                # 能量不足，需要提前充电
                return_distance = distance / 2
                new_missions.append(f"{end} -> Charge station: {return_distance:.2f} km")
                new_missions.append(f"Charge station -> {end}: {return_distance:.2f} km")

                # 充电后重置能量
                current_energy = battery_capacity
                mission_count = 0  # 重置任务计数

                # 累加返回和出发的时间和能量消耗
                return_time, _, return_energy_remaining = simulate_flight(
                    payload, return_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += return_time
                total_energy_consumed += (battery_capacity - return_energy_remaining)

                depart_time, _, depart_energy_remaining = simulate_flight(
                    payload, return_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += depart_time
                total_energy_consumed += (battery_capacity - depart_energy_remaining)

                # 重新模拟飞行（充电后）
                time_flown, time_remaining, energy_remaining = simulate_flight(
                    payload, distance, current_energy, payload_D,temperature_D
                )

            # 添加任务
            new_missions.append(f"{start} -> {end}: {distance:.2f} km")

            # 累加时间和能量消耗
            total_time_flown += time_flown
            energy_used = current_energy - energy_remaining
            total_energy_consumed += energy_used
            current_energy = energy_remaining

            # 更新任务计数
            mission_count += 1

            # 每完成两个任务后返回充电
            if mission_count >= 2 and i < len(processed_missions) - 1:
                # 返回充电站
                return_distance = distance / 2  # 简化：假设返回距离为当前距离的一半
                new_missions.append(f"{end} -> Charge station: {return_distance:.2f} km")

                # 重新出发
                next_start = processed_missions[i + 1][0]
                depart_distance = return_distance  # 简化：假设出发距离与返回距离相同
                new_missions.append(f"Charge station -> {next_start}: {depart_distance:.2f} km")

                # 累加返回和出发的时间和能量消耗
                return_time, _, return_energy_remaining = simulate_flight(
                    payload, return_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += return_time
                total_energy_consumed += (battery_capacity - return_energy_remaining)

                depart_time, _, depart_energy_remaining = simulate_flight(
                    payload, depart_distance, battery_capacity, payload_D,temperature_D
                )
                total_time_flown += depart_time
                total_energy_consumed += (battery_capacity - depart_energy_remaining)

                # 重置任务计数和能量
                mission_count = 0
                current_energy = battery_capacity

        # 计算总航段数
        total_segments = len(new_missions)

    else:
        # 未知策略
        raise ValueError(f"Unknown charge strategy: {charge_strategy}")

    return new_missions, total_time_flown, total_energy_consumed, total_segments