# Are You The One — Solver & Analyzer

A combinatorial solver and probabilistic analyzer for the TV show *Are You The One (AYTO)*, covering multiple German and US seasons. Given the show's game mechanics — Truth Booth results and Matching Night scores — the system deduces the unique valid pairing or narrows down the solution space.

## Problem

Each season of AYTO consists of ~10–11 participants per gender. The goal of the show (and this project) is to identify the one correct perfect matching. Two types of clues are revealed episode by episode:

- **Truth Booth:** confirms or rules out a specific pair
- **Matching Night:** n pairs are formed; the score reveals how many are correct (without revealing which ones)

The challenge is to use these constraints to find — or approximate — the one valid assignment.

## Approach

### Exact Solver (`ayto_solver.py`)
- Iterates over all permutations of possible pairings using `itertools.combinations` and `permutations`
- Filters candidates against all accumulated constraints (Truth Booths + Matching Night scores)
- Three modes:
  - **`find_valid_ayto_solutions`** — returns all pairings consistent with the current data
  - **`find_min_ceremonies_for_solution`** — finds the minimum number of Matching Nights required to produce at least one valid solution
  - **`find_unique_solution`** — incrementally adds Matching Nights until exactly one solution remains

### Probabilistic Analyzer (`Split/`)
- **Data Preprocessing** (`data_preprocessing.ipynb`): initializes match probabilities at 0.5 per pair, updates them based on Truth Booth results, and normalizes across remaining candidates after each ceremony
- **Monte Carlo Simulation** (`monte_carlo.py`): runs 10,000 random-assignment iterations weighted by the current probability distribution; outputs empirical match frequencies
- **Visualization**: probability matrices and pair-frequency bar charts rendered as heatmaps via Matplotlib

## Skills Demonstrated

| Area | Details |
|---|---|
| Algorithm Design | Constraint satisfaction, combinatorial search with early pruning, incremental filtering |
| Probabilistic Modeling | Bayesian-style probability updates, Monte Carlo simulation |
| Data Engineering | Structured JSON schema design for multi-season, multi-format data |
| Scientific Python | NumPy, Matplotlib (heatmaps, bar charts, matrix visualizations) |
| Jupyter Notebooks | Exploratory data analysis, step-by-step preprocessing pipeline |
| Software Design | Separation of exact solver, probabilistic layer, and data layer |

## Tech Stack

- **Language:** Python 3
- **Libraries:** NumPy, Matplotlib
- **Data Format:** JSON
- **Environment:** Jupyter Notebook + standalone scripts

## Project Structure

```
AYTO/
├── ayto_solver.py              # Exact constraint-based solver (3 modes)
├── ayto_solver_codiert.ipynb   # Interactive notebook version of the solver
├── Split/
│   ├── data_preprocessing.ipynb  # Probability initialization & update pipeline
│   └── monte_carlo.py            # Monte Carlo simulation + heatmap visualization
└── src/
    ├── germany/
    │   ├── normal/               # Seasons 1–6 + test seasons
    │   └── vip/                  # VIP seasons 1–5
    └── us/
        └── normal/               # US seasons 1–2 + test seasons
```

## Data Model

Each season is stored as a JSON file with three sections:

```json
{
  "participants": { "men": [...], "women": [...] },
  "truth_booths": [{ "man": "...", "woman": "...", "is_match": true }],
  "match_ceremonies": [{ "score": 3, "pairs": [...] }]
}
```

This schema handles asymmetric group sizes (more women than men) and missing participants (no-pair episodes) generically.

## Example Output

Running `find_unique_solution` on Season 6 (Germany):

```
Teste mit den ersten 7 Matching Nights…
✅ Einzig gültige Lösung bei n=7 gefunden.

Danish ↔ Nadja
Dino   ↔ Deisy
Dion   ↔ Anna
Enes   ↔ Nasti
Josh   ↔ Camelia
Joshua ↔ Chiara
Kaan   ↔ Selina
Levin  ↔ Ina
Sinan  ↔ Joanna
Tano   ↔ Sophia
```

The solver determined the unique solution after just 7 of 8 available Matching Nights.
