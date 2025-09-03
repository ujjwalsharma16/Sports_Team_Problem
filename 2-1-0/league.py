from dataclasses import dataclass
from typing import Dict, List
import json

@dataclass
class Team:
    name: str
    wins: int
    draws: int
    losses: int
    points: int
    remaining_games: Dict[str, int]  # opponent -> games left

    @property
    def max_wins(self) -> int:
        """Current wins + all remaining games"""
        return self.wins + sum(self.remaining_games.values())
    
    @property
    def max_points_3point(self) -> int:
        """Maximum possible points under 3-1-0 system"""
        return self.points + 3 * sum(self.remaining_games.values())
    
    @property
    def max_points_2point(self) -> int:
        """Maximum possible points under 2-1-0 system"""
        return self.points + 2 * sum(self.remaining_games.values())


def load_teams_from_json(path: str) -> List[Team]:
    """
    Load league data from a JSON file.
    """
    with open(path) as f:
        data = json.load(f)
    teams: List[Team] = []
    for entry in data.get('teams', []):
        # Handle backward compatibility - if only wins provided, assume draws/losses = 0
        wins = entry.get('wins', 0)
        draws = entry.get('draws', 0)
        losses = entry.get('losses', 0)
        points = entry.get('points', wins * 3 + draws * 1)  # Default to 3-1-0 system
        
        teams.append(Team(
            name=entry['name'],
            wins=wins,
            draws=draws,
            losses=losses,
            points=points,
            remaining_games=entry['remaining']
        ))
    return teams
