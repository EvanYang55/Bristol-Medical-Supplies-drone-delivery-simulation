import heapq
from collections import defaultdict
import math


class AStarPathPlanner:
    def __init__(self, distance_data):
        """
        初始化A*路径规划器

        参数:
        distance_data: 字典，包含所有点对之间的距离
        """
        self.distance_data = distance_data
        self.graph = self.build_graph(distance_data)
        self.coordinates = self.estimate_coordinates()

    def build_graph(self, distance_data):
        """
        构建图结构

        参数:
        distance_data: 字典，包含所有点对之间的距离

        返回:
        graph: 字典，表示图的邻接表
        """
        graph = defaultdict(dict)
        for (loc1, loc2), distance in distance_data.items():
            graph[loc1][loc2] = distance
            graph[loc2][loc1] = distance
        return graph

    def estimate_coordinates(self):
        """
        估计位置坐标（用于启发式函数）

        返回:
        coordinates: 字典，包含每个位置的估计坐标
        """
        # 使用简单的估计方法：将位置映射到二维平面
        # 在实际应用中，应该使用真实的地理坐标
        coordinates = {}
        all_locations = set()
        for (loc1, loc2) in self.distance_data.keys():
            all_locations.add(loc1)
            all_locations.add(loc2)

        # 为每个位置分配一个角度（模拟圆形分布）
        angle_step = 2 * math.pi / len(all_locations)
        radius = 10.0  # 假设所有位置在一个半径为10的圆上

        for i, location in enumerate(all_locations):
            angle = i * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            coordinates[location] = (x, y)

        return coordinates

    def heuristic(self, loc1, loc2):
        """
        启发式函数 - 使用欧几里得距离作为启发值

        参数:
        loc1: 起点位置
        loc2: 终点位置

        返回:
        欧几里得距离
        """
        x1, y1 = self.coordinates[loc1]
        x2, y2 = self.coordinates[loc2]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def a_star(self, start, goal):
        """
        A*算法实现

        参数:
        start: 起点位置
        goal: 终点位置

        返回:
        path: 从起点到终点的路径列表
        distance: 路径总距离
        """
        # 初始化数据结构
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {location: float('inf') for location in self.graph}
        g_score[start] = 0
        f_score = {location: float('inf') for location in self.graph}
        f_score[start] = self.heuristic(start, goal)

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current), g_score[current]

            for neighbor, distance in self.graph[current].items():
                tentative_g_score = g_score[current] + distance

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float('inf')  # 没有找到路径

    def reconstruct_path(self, came_from, current):
        """
        重构路径

        参数:
        came_from: 字典，记录每个节点的前驱节点
        current: 当前节点

        返回:
        路径列表
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def tsp_a_star(self, start_points, task_points):
        """
        解决旅行商问题(TSP)的近似算法

        参数:
        start_points: 起点列表
        task_points: 任务点列表

        返回:
        paths: 每个起点的最优路径列表
        total_distances: 每个起点的总距离列表
        segment_distances_list: 每个起点的路径段距离列表
        """
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
                # 找到最近的未访问点
                next_point = None
                min_distance = float('inf')

                for point in unvisited:
                    # 使用A*算法计算从当前点到该点的最短路径
                    _, distance = self.a_star(current, point)
                    if distance < min_distance:
                        min_distance = distance
                        next_point = point

                if next_point is None:
                    break  # 没有可达的点

                # 使用A*算法获取完整路径
                segment_path, segment_distance = self.a_star(current, next_point)

                # 计算路径段距离
                for i in range(len(segment_path) - 1):
                    loc1 = segment_path[i]
                    loc2 = segment_path[i + 1]
                    distance_val = self.graph[loc1][loc2]
                    segment_distances.append((loc1, loc2, distance_val))

                # 更新路径和当前点
                path.extend(segment_path[1:])  # 避免重复添加当前点
                total_distance += segment_distance
                current = next_point
                unvisited.remove(current)

            paths.append(path)
            total_distances.append(total_distance)
            segment_distances_list.append(segment_distances)

        return paths, total_distances, segment_distances_list


def optimize_paths(start_points, task_points, distance_data):
    """
    使用A*算法优化多个起点的路径

    参数:
    start_points: 起点列表
    task_points: 任务点列表
    distance_data: 距离数据字典

    返回:
    paths: 每个起点的最优路径列表
    total_distances: 每个起点的总距离列表
    segment_distances_list: 每个起点的路径段距离列表
    """
    planner = AStarPathPlanner(distance_data)
    return planner.tsp_a_star(start_points, task_points)