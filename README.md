# League Team Elimination Project

## Overview
This project implements algorithms to determine if sports teams can be mathematically eliminated from first place in a league. It supports multiple scoring systems and uses real Premier League data for validation.

## Implemented Systems
- **EST(1,0)**: Win/Loss only - Polynomial time solvable
- **EST(2,1,0)**: 2 points for win, 1 for draw, 0 for loss - Polynomial time solvable  
- **EST(3,1,0)**: 3 points for win, 1 for draw, 0 for loss - NP-complete (uses heuristic)

## Files Structure
```
edmond-karps/
├── elimination.py          # Main elimination algorithms
├── flow_model.py          # Flow network and Edmonds-Karp implementation
├── league.py              # Team data structures and JSON loading
├── TESTING_GUIDE.md       # Comprehensive testing instructions
├── README.md              # This file
├── venv/                  # Python virtual environment
├── league_*.json          # Original test cases (4, 6, 8, 10 teams)
├── premier_league_*.json  # Real Premier League final tables
├── test_*.json           # 10 mid-season test scenarios
└── readme                # Original readme (outdated)
```

## Quick Start

### Setup
```bash
# Navigate to project directory
cd edmond-karps

# Activate virtual environment
source venv/bin/activate

# (Dependencies already installed in venv)
```

### Basic Usage
```bash
# Test with 3-point system (modern football)
python elimination.py test_2023_24_gameweek_8.json 3-1-0

# Test with all scoring systems
python elimination.py league_4.json

# Test on real Premier League data
python elimination.py premier_league_2023_2024_final.json 3-1-0
```

## Key Features
- **Custom Edmonds-Karp Algorithm**: No external graph libraries required
- **Real Data Testing**: Uses actual Premier League results from 2021-2024
- **Multiple Scoring Systems**: Supports all three elimination problem variants
- **Comprehensive Test Suite**: 10 realistic mid-season scenarios
- **Min-Cut Analysis**: Identifies teams responsible for elimination

## Algorithm Complexity
- **EST(1,0)**: O(V²E) using max-flow reduction
- **EST(2,1,0)**: O(V²E) polynomial time solvable
- **EST(3,1,0)**: NP-complete, uses polynomial-time heuristic

## Testing
See `TESTING_GUIDE.md` for detailed instructions on running all test scenarios.

## Dependencies
- Python 3.7+
- requests, beautifulsoup4 (for data extraction, already installed in venv)
- No NetworkX or external graph libraries required# Sports_Team_Problem
