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
    Fixed greedy heuristic for EST(3,1,0) using professor's formula:
    P_target + 3k >= min max{P1*,...,Pi*}
    where Pi* = realistic maximum points for team i considering game constraints
    """
    # Trivial elimination check
    for team in teams:
        if team.name != target.name and team.points > target.max_points_3point:
            return True
    
    # Calculate target's maximum possible points: P_target + 3k
    k = sum(target.remaining_games.values())  # remaining matches for target
    target_max_points = target.points + 3 * k
    
    # Calculate realistic Pi* values using constraint-aware approach
    other_teams_max_points = calculate_realistic_max_points(target, teams)
    
    # Check formula: P_target + 3k >= min max{P1*,...,Pi*}
    # Target is eliminated if they can't reach the minimum of other teams' maximums
    if other_teams_max_points:
        min_of_other_max = min(other_teams_max_points)
        return target_max_points < min_of_other_max
    
    return False


def calculate_realistic_max_points(target: Team, teams: List[Team]) -> List[int]:
    """
    Calculate realistic maximum points Pi* for each team using constraint optimization.
    Uses greedy allocation to find achievable maximum points considering:
    1. Games vs target (worst case: target loses all)
    2. Games between other teams (zero-sum constraint aware)
    3. Simultaneous achievability of all Pi* values
    """
    other_teams = [t for t in teams if t.name != target.name]
    
    # Step 1: Calculate base points (current + wins vs target)
    team_base_points = {}
    for team in other_teams:
        games_vs_target = target.remaining_games.get(team.name, 0)
        team_base_points[team.name] = team.points + 3 * games_vs_target
    
    # Step 2: Collect all games between non-target teams
    inter_team_games = []
    for i, team1 in enumerate(other_teams):
        for j, team2 in enumerate(other_teams[i+1:], i+1):
            games = team1.remaining_games.get(team2.name, 0)
            if games > 0:
                inter_team_games.append({
                    'team1': team1.name,
                    'team2': team2.name, 
                    'games': games,
                    'points_available': games * 3  # Total points from these games
                })
    
    # Step 3: Greedy allocation to maximize minimum team's maximum
    # Start with base points and allocate inter-team game points
    team_max_points = team_base_points.copy()
    
    # Sort teams by current standing (lowest first) to be conservative
    sorted_teams = sorted(other_teams, key=lambda t: team_base_points[t.name])
    
    # Allocate inter-team game points using greedy strategy
    for game in inter_team_games:
        team1, team2 = game['team1'], game['team2']
        points_available = game['points_available']
        games_count = game['games']
        
        # Get current points for both teams
        points1 = team_max_points[team1]
        points2 = team_max_points[team2]
        
        # Greedy strategy: give more points to the team that's currently behind
        # This creates a more realistic distribution than assuming all teams win everything
        if points1 <= points2:
            # Team1 is behind or tied, give them advantage
            team1_wins = min(games_count, max(1, int(games_count * 0.7)))  # 70% of games
            team2_wins = games_count - team1_wins
        else:
            # Team2 is behind, give them advantage  
            team2_wins = min(games_count, max(1, int(games_count * 0.7)))  # 70% of games
            team1_wins = games_count - team2_wins
        
        # Allocate points (3 for win, 1 for draw, but simplified to wins/losses)
        draws = 0  # Simplified: assume no draws for cleaner calculation
        team_max_points[team1] += 3 * team1_wins + 1 * draws
        team_max_points[team2] += 3 * team2_wins + 1 * draws
    
    # Step 4: Return as list in original team order
    max_points = []
    for team in other_teams:
        max_points.append(team_max_points[team.name])
    
    return max_points


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
