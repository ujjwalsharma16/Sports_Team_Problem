# Testing Guide - EST(3,1,0) Updated Implementation

This guide covers testing the **3-1-0updated** implementation, which contains the professor's updated heuristic formula and comprehensive real Premier League data.

## Quick Start

### Navigate to Implementation Directory
```bash
cd 3-1-0updated
```

### Basic Test Command
```bash
python3 elimination.py Tests/final_test_1.json 3-1-0
```

## Environment Setup

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (pure Python implementation)

### Optional Dependencies (for data scraping)
```bash
pip install requests beautifulsoup4
```

## Test Data Overview

The **3-1-0updated** implementation includes two types of test data:

### 1. Final Test Cases (`Tests/final_test_*.json`)
Comprehensive test scenarios created from real Premier League data:

| Test File | Season | Gameweek | Description |
|-----------|--------|----------|-------------|
| `final_test_1.json` | 2019-20 | 3 | Early season form |
| `final_test_2.json` | 2019-20 | 28 | Mid-season battles |
| `final_test_3.json` | 2019-20 | 35 | Title race climax |
| `final_test_4.json` | 2021-22 | 15 | Winter form guide |
| `final_test_5.json` | 2021-22 | 25 | Spring momentum |
| `final_test_6.json` | 2021-22 | 28 | Spring run-in begins |
| `final_test_7.json` | 2021-22 | 36 | Championship race final weeks |
| `final_test_8.json` | 2022-23 | 10 | Autumn form taking shape |
| `final_test_9.json` | 2022-23 | 22 | Winter transfer window impact |
| `final_test_10.json` | 2022-23 | 32 | Final sprint to title |

### 2. Full Season Data (`Data/scraped_*.json`)
Complete gameweek-by-gameweek data for three Premier League seasons:
- **2019-20 Season**: `scraped_2019_20_gameweek_01.json` to `scraped_2019_20_gameweek_38.json`
- **2021-22 Season**: `scraped_2021_22_gameweek_01.json` to `scraped_2021_22_gameweek_38.json`  
- **2022-23 Season**: `scraped_2022_23_gameweek_01.json` to `scraped_2022_23_gameweek_38.json`

## Running Tests

### Individual Test Examples

#### Early Season Test (Most Teams in Contention)
```bash
python3 elimination.py Tests/final_test_1.json 3-1-0
```
**Expected**: 19/20 teams in contention (only Norwich eliminated)

#### Championship Race Test (Few Teams Left)
```bash
python3 elimination.py Tests/final_test_7.json 3-1-0
```
**Expected**: Only Manchester City and Liverpool in contention

#### Final Sprint Test (Title Decider)
```bash
python3 elimination.py Tests/final_test_10.json 3-1-0
```
**Expected**: Arsenal, Manchester City, Newcastle United, Manchester United in contention

### Batch Testing All Final Tests
```bash
# Test all final test cases
for i in {1..10}; do
    echo "=== Testing final_test_$i.json ==="
    python3 elimination.py Tests/final_test_$i.json 3-1-0
    echo ""
done
```

### Testing Full Season Data
```bash
# Test specific gameweek from 2021-22 season
python3 elimination.py Data/scraped_2021_22_gameweek_15.json 3-1-0

# Test championship-deciding gameweek
python3 elimination.py Data/scraped_2021_22_gameweek_36.json 3-1-0
```

## Understanding the Output

### Sample Output Analysis
```
=== Elimination Analysis (3-1-0 scoring system) ===
Arsenal FC: IN CONTENTION
Manchester City: IN CONTENTION
Newcastle United: IN CONTENTION
Manchester United: IN CONTENTION
Liverpool FC: ELIMINATED by Arsenal FC, Manchester City
Brighton & Hove Albion: ELIMINATED by Arsenal FC, Manchester City
Tottenham Hotspur: ELIMINATED by Arsenal FC, Manchester City
```

### Output Interpretation
- **IN CONTENTION**: Team can still mathematically achieve first place
- **ELIMINATED**: Team cannot win the title even if they win all remaining games
- **ELIMINATED by [teams]**: Shows which teams make elimination mathematically certain

## Algorithm Details

### Updated Heuristic Formula
The implementation uses the exact formula specified by the professor:

**P₂₀ + 3k ≥ min max{P₁*,...,Pᵢ*}**

Where:
- **P₂₀** = Target team's current points
- **k** = Target team's remaining games
- **Pᵢ*** = Maximum possible points for other team i

### Implementation Location
The updated heuristic is implemented in `flow_model.py` at function `is_eliminated_3point_heuristic()`.

## Historical Validation

### Key Historical Results Validated
- **2021-22 GW36**: Correctly identifies only Man City and Liverpool as title contenders (City won the title)
- **2022-23 Season**: Shows Arsenal's early dominance and Manchester City's sustained challenge
- **Progressive Elimination**: Teams eliminated in realistic order based on points gaps

## Troubleshooting

### Common Issues

#### File Not Found Error
```bash
# Make sure you're in the 3-1-0updated directory
cd 3-1-0updated
pwd  # Should show: .../edmond-karps/3-1-0updated
```

#### Import Errors
```bash
# Verify all core files are present
ls *.py
# Should show: elimination.py, flow_model.py, league.py, ...
```

#### Testing Different Scoring Systems
```bash
# The 3-1-0updated implementation supports all systems
python3 elimination.py Tests/final_test_1.json 1-0    # Win/Loss only
python3 elimination.py Tests/final_test_1.json 2-1-0  # 2-1-0 scoring
python3 elimination.py Tests/final_test_1.json 3-1-0  # 3-1-0 scoring (recommended)
```

## Performance Notes

- **Fast Execution**: Most tests complete in under 1 second
- **Memory Efficient**: Handles 20-team leagues with 114 datasets efficiently
- **No External Dependencies**: Pure Python implementation of Edmonds-Karp algorithm

## File Structure Reference

```
3-1-0updated/
├── elimination.py           # Main algorithm entry point
├── flow_model.py           # Edmonds-Karp + professor's heuristic
├── league.py               # Team data structures
├── Data/                   # Full season datasets (114 files)
├── Tests/                  # Curated test cases (20 files)
├── scraper.py             # Data collection utility
├── advanced_fixture_calculator.py  # Fixture calculations
└── *.py                   # Additional utilities
```

---
