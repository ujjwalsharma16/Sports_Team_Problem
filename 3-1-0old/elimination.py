from typing import List, Set, Optional, Tuple
from league import Team, load_teams_from_json
from flow_model import build_flow_network, build_flow_network_2point, run_max_flow, find_min_cut, is_eliminated_3point_heuristic


def find_elimination_teams(target: Team, teams: List[Team]) -> Set[str]:
    """
    Find teams responsible for eliminating the target team using min-cut.
    """
    G = build_flow_network(target, teams)
    reachable, unreachable = find_min_cut(G, 's', 't')
    
    # Teams that cause elimination are those connected to the sink
    # but not reachable from source in the residual graph
    eliminating_teams = set()
    for team in teams:
        if team.name != target.name and team.name in unreachable:
            eliminating_teams.add(team.name)
    
    return eliminating_teams


def is_eliminated(target: Team, teams: List[Team]) -> Tuple[bool, Optional[Set[str]]]:
    """
    Check if target team is eliminated using original win/loss system (EST(1,0)).
    Returns (is_eliminated, eliminating_teams).
    """
    # Trivial elimination - check if any team already has more wins than target's max possible
    trivial_eliminators = set()
    for team in teams:
        if team.name != target.name and team.wins > target.max_wins:
            trivial_eliminators.add(team.name)
    
    if trivial_eliminators:
        return True, trivial_eliminators

    # Non-trivial elimination using max flow
    G = build_flow_network(target, teams)
    flow_value = run_max_flow(G)
    
    # Calculate total games that need to be distributed
    total_games = 0
    for u in G.graph.get('s', {}):
        if u.startswith('game_'):
            total_games += G.graph['s'][u]
    
    if flow_value < total_games:
        eliminating_teams = find_elimination_teams(target, teams)
        return True, eliminating_teams
    
    return False, None


def is_eliminated_2point(target: Team, teams: List[Team]) -> Tuple[bool, Optional[Set[str]]]:
    """
    Check if target team is eliminated using 2-1-0 scoring system (EST(2,1,0)).
    Returns (is_eliminated, eliminating_teams).
    """
    # Trivial elimination - check if any team already has more points than target's max possible
    trivial_eliminators = set()
    for team in teams:
        if team.name != target.name and team.points > target.max_points_2point:
            trivial_eliminators.add(team.name)
    
    if trivial_eliminators:
        return True, trivial_eliminators

    # Non-trivial elimination using max flow
    G = build_flow_network_2point(target, teams)
    flow_value = run_max_flow(G)
    
    # Calculate total points that need to be distributed
    total_points = 0
    for u in G.graph.get('s', {}):
        if u.startswith('game_'):
            total_points += G.graph['s'][u]
    
    if flow_value < total_points:
        # For simplicity, return empty eliminating teams set for 2-point system
        return True, set()
    
    return False, None


def is_eliminated_3point(target: Team, teams: List[Team]) -> Tuple[bool, Optional[Set[str]]]:
    """
    Check if target team is eliminated using 3-1-0 scoring system (EST(3,1,0)).
    Since this is NP-complete, we use a heuristic approach.
    Returns (is_eliminated, eliminating_teams).
    """
    # Trivial elimination - check if any team already has more points than target's max possible
    trivial_eliminators = set()
    for team in teams:
        if team.name != target.name and team.points > target.max_points_3point:
            trivial_eliminators.add(team.name)
    
    if trivial_eliminators:
        return True, trivial_eliminators

    # Use heuristic for NP-complete case
    eliminated = is_eliminated_3point_heuristic(target, teams)
    return eliminated, set() if eliminated else None


def check_all(teams: List[Team], scoring_system: str = "1-0") -> None:
    """
    Check elimination status for all teams using specified scoring system.
    scoring_system: "1-0" for win/loss, "2-1-0" for 2-point wins, "3-1-0" for 3-point wins
    """
    print(f"\n=== Elimination Analysis ({scoring_system} scoring system) ===")
    
    for t in teams:
        if scoring_system == "1-0":
            eliminated, eliminating_teams = is_eliminated(t, teams)
        elif scoring_system == "2-1-0":
            eliminated, eliminating_teams = is_eliminated_2point(t, teams)
        elif scoring_system == "3-1-0":
            eliminated, eliminating_teams = is_eliminated_3point(t, teams)
        else:
            raise ValueError(f"Unknown scoring system: {scoring_system}")
            
        if eliminated:
            if eliminating_teams:
                eliminating_list = ", ".join(sorted(eliminating_teams))
                print(f"{t.name}: ELIMINATED by {eliminating_list}")
            else:
                print(f"{t.name}: ELIMINATED")
        else:
            print(f"{t.name}: IN CONTENTION")


if __name__ == "__main__":
    import sys
    if len(sys.argv) not in [2, 3]:
        print("Usage: python elimination.py <league.json> [scoring_system]")
        print("scoring_system: '1-0' (default), '2-1-0', or '3-1-0'")
        sys.exit(1)

    teams = load_teams_from_json(sys.argv[1])
    scoring_system = sys.argv[2] if len(sys.argv) == 3 else "1-0"
    
    # Run analysis for specified system
    check_all(teams, scoring_system)
    
    # If using default, also show comparison
    if scoring_system == "1-0" and len(sys.argv) == 2:
        check_all(teams, "2-1-0")
        check_all(teams, "3-1-0")


