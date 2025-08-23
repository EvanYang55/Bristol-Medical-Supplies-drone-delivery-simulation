import heapq
from collections import defaultdict


def dijkstra_shortest_path(graph, start):
    """
    Dijkstra算法计算从起点到所有其他点的最短路径

    参数:
    graph: 图的邻接表表示
    start: 起点

    返回:
    distances: 从起点到所有点的最短距离
    previous: 路径重建字典
    """
    # 初始化距离字典
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # 前驱节点字典
    previous = {node: None for node in graph}

    # 优先队列
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # 如果当前距离大于已知距离，跳过
        if current_distance > distances[current_node]:
            continue

        # 遍历邻居
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            # 如果找到更短路径
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous


def reconstruct_path(previous, start, end):
    """
    重构从起点到终点的路径

    参数:
    previous: 前驱节点字典
    start: 起点
    end: 终点

    返回:
    path: 路径列表
    """
    path = []
    current = end

    while current != start:
        path.append(current)
        current = previous[current]
        if current is None:  # 没有路径
            return []

    path.append(start)
    path.reverse()
    return path


def dijkstra_tsp(start_points, task_points, distance_data):
    """
    使用Dijkstra算法解决旅行商问题(TSP)的近似算法

    参数:
    start_points: 起点列表
    task_points: 任务点列表
    distance_data: 距离数据字典

    返回:
    paths: 每个起点的最优路径列表
    total_distances: 每个起点的总距离列表
    segment_distances_list: 每个起点的路径段距离列表
    """
    # 构建图
    graph = defaultdict(dict)
    for (loc1, loc2), distance in distance_data.items():
        graph[loc1][loc2] = distance
        graph[loc2][loc1] = distance

    # 所有需要访问的点
    all_points = start_points + task_points

    # 如果没有点需要访问
    if not all_points:
        return [], [], []

    paths = []
    total_distances = []
    segment_distances_list = []

    # 对每个起点分别计算路径
    for start in start_points:
        # 初始化
        unvisited = set(task_points)
        path = [start]
        segment_distances = []
        total_distance = 0
        current = start

        # 逐步访问所有点
        while unvisited:
            # 计算从当前点到所有未访问点的最短路径
            distances, previous = dijkstra_shortest_path(graph, current)

            # 找到最近的未访问点
            next_point = None
            min_distance = float('inf')

            for point in unvisited:
                if distances[point] < min_distance:
                    min_distance = distances[point]
                    next_point = point

            if next_point is None:
                break  # 没有可达的点

            # 重构路径
            segment_path = reconstruct_path(previous, current, next_point)

            # 计算路径段距离
            for i in range(len(segment_path) - 1):
                loc1 = segment_path[i]
                loc2 = segment_path[i + 1]
                distance_val = graph[loc1][loc2]
                segment_distances.append((loc1, loc2, distance_val))
                total_distance += distance_val

            # 更新路径和当前点
            path.extend(segment_path[1:])  # 避免重复添加当前点
            current = next_point
            unvisited.remove(current)

        paths.append(path)
        total_distances.append(total_distance)
        segment_distances_list.append(segment_distances)

    return paths, total_distances, segment_distances_list


def optimize_paths(start_points, task_points, distance_data):
    """
    使用Dijkstra算法优化多个起点的路径

    参数:
    start_points: 起点列表
    task_points: 任务点列表
    distance_data: 距离数据字典

    返回:
    paths: 每个起点的最优路径列表
    total_distances: 每个起点的总距离列表
    segment_distances_list: 每个起点的路径段距离列表
    """
    return dijkstra_tsp(start_points, task_points, distance_data)