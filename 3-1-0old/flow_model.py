from typing import List, Dict, Tuple, Set
from collections import deque
from league import Team


class FlowNetwork:
    def __init__(self):
        self.graph: Dict[str, Dict[str, int]] = {}
        self.nodes: Set[str] = set()
    
    def add_node(self, node: str):
        if node not in self.graph:
            self.graph[node] = {}
            self.nodes.add(node)
    
    def add_edge(self, u: str, v: str, capacity: int):
        self.add_node(u)
        self.add_node(v)
        self.graph[u][v] = capacity
        if v not in self.graph or u not in self.graph[v]:
            if v not in self.graph:
                self.graph[v] = {}
            self.graph[v][u] = 0


def build_flow_network(target: Team, teams: List[Team]) -> FlowNetwork:
    """
    Build a flow network to test whether `target` can avoid elimination.
    Original win/loss system (EST(1,0)).
    """
    G = FlowNetwork()
    source, sink = 's', 't'
    G.add_node(source)
    G.add_node(sink)

    # Team -> sink
    for team in teams:
        if team.name == target.name:
            continue
        cap = max(target.max_wins - team.wins, 0)
        G.add_edge(team.name, sink, cap)

    # Source -> game nodes -> team nodes
    n = len(teams)
    for i in range(n):
        A = teams[i]
        if A.name == target.name:
            continue
        for j in range(i+1, n):
            B = teams[j]
            if B.name == target.name:
                continue
            games = A.remaining_games.get(B.name, 0)
            if games <= 0:
                continue
            game_node = f"game_{A.name}_{B.name}"
            G.add_edge(source, game_node, games)
            G.add_edge(game_node, A.name, float('inf'))
            G.add_edge(game_node, B.name, float('inf'))

    return G


def build_flow_network_2point(target: Team, teams: List[Team]) -> FlowNetwork:
    """
    Build a flow network for EST(2,1,0) - 2 points for win, 1 for draw, 0 for loss.
    This is polynomial time solvable (equivalent to EST(1,0) with doubled capacity).
    """
    G = FlowNetwork()
    source, sink = 's', 't'
    G.add_node(source)
    G.add_node(sink)

    # Team -> sink (capacity = max possible points - current points)
    for team in teams:
        if team.name == target.name:
            continue
        cap = max(target.max_points_2point - team.points, 0)
        G.add_edge(team.name, sink, cap)

    # Source -> game nodes -> team nodes
    # Each game can contribute maximum 2 points (win for one team)
    n = len(teams)
    for i in range(n):
        A = teams[i]
        if A.name == target.name:
            continue
        for j in range(i+1, n):
            B = teams[j]
            if B.name == target.name:
                continue
            games = A.remaining_games.get(B.name, 0)
            if games <= 0:
                continue
            game_node = f"game_{A.name}_{B.name}"
            # Each game can contribute max 2 points
            G.add_edge(source, game_node, 2 * games)
            G.add_edge(game_node, A.name, float('inf'))
            G.add_edge(game_node, B.name, float('inf'))

    return G


def bfs_find_path(graph: Dict[str, Dict[str, int]], source: str, sink: str) -> List[str]:
    """
    Find an augmenting path using BFS (Breadth-First Search).
    Returns the path if found, empty list otherwise.
    """
    visited = set()
    queue = deque([(source, [source])])
    visited.add(source)
    
    while queue:
        node, path = queue.popleft()
        
        if node == sink:
            return path
            
        for neighbor in graph.get(node, {}):
            if neighbor not in visited and graph[node][neighbor] > 0:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return []


def edmonds_karp(G: FlowNetwork, source: str, sink: str) -> Tuple[int, Dict[str, Dict[str, int]]]:
    """
    Manual implementation of Edmonds-Karp algorithm for maximum flow.
    Returns (max_flow_value, flow_dict).
    """
    # Create residual graph
    residual = {}
    flow = {}
    
    # Initialize residual graph and flow
    for u in G.graph:
        residual[u] = {}
        flow[u] = {}
        for v in G.graph[u]:
            residual[u][v] = G.graph[u][v]
            flow[u][v] = 0
    
    max_flow_value = 0
    
    # Find augmenting paths until no more exist
    while True:
        path = bfs_find_path(residual, source, sink)
        if not path:
            break
            
        # Find minimum capacity along the path
        path_flow = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            path_flow = min(path_flow, residual[u][v])
        
        # Update residual capacities and flow
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            flow[u][v] += path_flow
            flow[v][u] -= path_flow
        
        max_flow_value += path_flow
    
    return max_flow_value, flow


def run_max_flow(G: FlowNetwork) -> int:
    """
    Compute max flow using manual Edmonds-Karp implementation.
    """
    flow_value, _ = edmonds_karp(G, 's', 't')
    return flow_value


def is_eliminated_3point_heuristic(target: Team, teams: List[Team]) -> bool:
    """
    Greedy heuristic for EST(3,1,0) using professor's formula:
    P_target + 3k >= min max{P1*,...,Pi*}
    where Pi* = points of team i after target's matches are decided
    """
    # Trivial elimination check
    for team in teams:
        if team.name != target.name and team.points > target.max_points_3point:
            return True
    
    # Calculate target's maximum possible points: P_target + 3k
    k = sum(target.remaining_games.values())  # remaining matches for target
    target_max_points = target.points + 3 * k
    
    # Get games between target and other teams
    target_vs_others = target.remaining_games.copy()
    
    # Greedy approach: for each team, calculate their maximum possible points
    # considering the worst case scenario for target (target loses all matches)
    other_teams_max_points = []
    
    for team in teams:
        if team.name == target.name:
            continue
            
        # Pi* = current points + points from remaining games
        # In greedy approach, assume each team gets maximum possible points
        # from games not involving target, and wins against target
        
        games_vs_target = target_vs_others.get(team.name, 0)
        other_remaining = sum(team.remaining_games.values()) - games_vs_target
        
        # Team's points if they win all games including vs target
        team_max_points = team.points + 3 * games_vs_target + 3 * other_remaining
        other_teams_max_points.append(team_max_points)
    
    # Check formula: P_target + 3k >= min max{P1*,...,Pi*}
    # Target is eliminated if they can't reach the minimum of other teams' maximums
    if other_teams_max_points:
        min_of_other_max = min(other_teams_max_points)
        return target_max_points < min_of_other_max
    
    return False


def find_min_cut(G: FlowNetwork, source: str, sink: str) -> Tuple[Set[str], Set[str]]:
    """
    Find minimum cut after running max flow.
    Returns (reachable_from_source, unreachable_from_source).
    """
    # Run max flow first to get residual graph
    _, flow = edmonds_karp(G, source, sink)
    
    # Create residual graph
    residual = {}
    for u in G.graph:
        residual[u] = {}
        for v in G.graph[u]:
            residual[u][v] = G.graph[u][v] - flow[u][v]
    
    # Find all nodes reachable from source in residual graph
    visited = set()
    queue = deque([source])
    visited.add(source)
    
    while queue:
        node = queue.popleft()
        for neighbor in residual.get(node, {}):
            if neighbor not in visited and residual[node][neighbor] > 0:
                visited.add(neighbor)
                queue.append(neighbor)
    
    all_nodes = G.nodes
    reachable = visited
    unreachable = all_nodes - reachable
    
    return reachable, unreachable
