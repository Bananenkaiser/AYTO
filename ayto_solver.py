import json
import sys
import time
from itertools import permutations, combinations

# ------------------------------
# Hilfsfunktionen
# ------------------------------
def build_double_match_dicts(data):
    """Returns (man_doubles, woman_doubles) for participants with two perfect matches.
    man_doubles:   {man:   [woman1, woman2]}  — man with multiple female matches
    woman_doubles: {woman: [man1,   man2  ]}  — woman with multiple male matches
    """
    man_doubles = {}
    woman_doubles = {}
    for dm in data.get("double_matches", []):
        if "man" in dm:
            man_doubles[dm["man"]] = dm["women"]
        elif "woman" in dm:
            woman_doubles[dm["woman"]] = dm["men"]
    return man_doubles, woman_doubles

def is_valid_truth_booth(pairing, truth_booths, man_doubles=None, woman_doubles=None):
    if man_doubles is None:
        man_doubles = {}
    if woman_doubles is None:
        woman_doubles = {}
    for tb in truth_booths:
        man, woman, is_match = tb["man"], tb["woman"], tb["is_match"]
        if man in man_doubles:
            actual = woman in man_doubles[man]
        elif woman in woman_doubles:
            actual = man in woman_doubles[woman]
        else:
            actual = man in pairing and pairing[man] == woman
        if actual != is_match:
            return False
    return True

def respects_perfect_matches(pairing, truth_booths, man_doubles=None, woman_doubles=None):
    if man_doubles is None:
        man_doubles = {}
    if woman_doubles is None:
        woman_doubles = {}
    for tb in truth_booths:
        if not tb["is_match"]:
            continue
        man, woman = tb["man"], tb["woman"]
        if man in man_doubles:
            if pairing.get(man) not in man_doubles[man]:
                return False
        elif woman in woman_doubles:
            # Either of the woman's valid men must be paired with her
            if not any(pairing.get(m) == woman for m in woman_doubles[woman]):
                return False
        else:
            if pairing.get(man) != woman:
                return False
    return True

def match_score(pairing, ceremony, man_doubles=None, woman_doubles=None):
    if man_doubles is None:
        man_doubles = {}
    if woman_doubles is None:
        woman_doubles = {}
    no_pair = ceremony.get("no_pair", None)
    score = 0
    for p in ceremony["pairs"]:
        man, woman = p["man"], p["woman"]
        if woman == no_pair:
            continue
        if man in man_doubles:
            if woman in man_doubles[man]:
                score += 1
        elif woman in woman_doubles:
            if man in woman_doubles[woman]:
                score += 1
        else:
            if pairing.get(man) == woman:
                score += 1
    return score

def is_valid_ceremonies(pairing, ceremonies, man_doubles=None, woman_doubles=None):
    if man_doubles is None:
        man_doubles = {}
    if woman_doubles is None:
        woman_doubles = {}
    for ceremony in ceremonies:
        if match_score(pairing, ceremony, man_doubles, woman_doubles) != ceremony["score"]:
            return False
    return True

def evaluate_pairing(pairing, truth_booths, ceremonies, man_doubles=None, woman_doubles=None):
    if man_doubles is None:
        man_doubles = {}
    if woman_doubles is None:
        woman_doubles = {}
    score = 0
    for tb in truth_booths:
        man, woman, is_match = tb["man"], tb["woman"], tb["is_match"]
        if man in man_doubles:
            actual = woman in man_doubles[man]
        elif woman in woman_doubles:
            actual = man in woman_doubles[woman]
        else:
            actual = man in pairing and pairing[man] == woman
        if actual == is_match:
            score += 1
    for ceremony in ceremonies:
        if match_score(pairing, ceremony, man_doubles, woman_doubles) == ceremony["score"]:
            score += 1
    return score

# ------------------------------
# Hauptfunktion: Suche der gültigen Lösung
# ------------------------------
def find_valid_ayto_solutions(data, limit=1, patience=1000):
    men = data["participants"]["men"]
    women = data["participants"]["women"]
    truth_booths = data["truth_booths"]
    ceremonies = data["match_ceremonies"]
    man_doubles, woman_doubles = build_double_match_dicts(data)

    valid_solutions = []
    best_solution = None
    best_score = -1
    iterations_without_improvement = 0

    # 1–2. Finde heraus, welche Gruppe kleiner ist
    if len(men) <= len(women):
        small, large = men, women
        small_is_men = True
    else:
        small, large = women, men
        small_is_men = False

    # Determine the smaller group size to handle unmatched participants
    min_size = len(small)

    # 3. Aus der größeren Gruppe alle Teilmengen der Größe min_size wählen
    for subset in combinations(large, min_size):
        # 4. Und dann jede Permutation dieser Teilmenge durchprobieren
        for perm in permutations(subset):
            # 5. Baue ein Dict man → frau
            if small_is_men:
                # small ist men, perm enthält women
                pairing = dict(zip(small, perm))
            else:
                # small ist women, perm enthält men → invertieren
                pairing = {man: woman for man, woman in zip(perm, small)}

    
            # … hier deine Validierungs-Checks …
            if is_valid_truth_booth(pairing, truth_booths, man_doubles, woman_doubles) \
            and respects_perfect_matches(pairing, truth_booths, man_doubles, woman_doubles) \
            and is_valid_ceremonies(pairing, ceremonies, man_doubles, woman_doubles):
                valid_solutions.append(pairing)
                if len(valid_solutions) >= limit:
                    return valid_solutions

            # Evaluate the pairing if not fully valid
            score = evaluate_pairing(pairing, truth_booths, ceremonies, man_doubles, woman_doubles)
            if score > best_score:
                best_score = score
                best_solution = pairing
                iterations_without_improvement = 0  # Reset counter
                # Print feedback on the current best score and pairing
                print(f"Neue beste Lösung gefunden mit Score {best_score}:")
                for man, woman in best_solution.items():
                    print(f"{man} ↔ {woman}")
                print()
            else:
                iterations_without_improvement += 1

            # Check if patience has been exceeded
            if iterations_without_improvement >= patience:
                print("Keine Verbesserung seit längerer Zeit. Suche beendet.")
                return valid_solutions if valid_solutions else [best_solution]

    return valid_solutions if valid_solutions else [best_solution]
def find_min_ceremonies_for_solution(data, start=5, limit=1, patience=100000):
    men = data["participants"]["men"]
    women = data["participants"]["women"]
    truth_booths = data["truth_booths"]
    all_ceremonies = data["match_ceremonies"]
    man_doubles, woman_doubles = build_double_match_dicts(data)

    # Bestimme universal small/large grouping wie besprochen:
    if len(men) <= len(women):
        small, large, small_is_men = men, women, True
    else:
        small, large, small_is_men = women, men, False

    min_size = len(small)

    # Iteriere n von start bis Gesamtzahl der ceremonies
    for n in range(start, len(all_ceremonies) + 1):
        ceremonies = all_ceremonies[:n]
        print(f"Teste mit {n} Ceremonies…")

        valid = []
        best = None
        best_score = -1
        no_improve = 0

        # generiere alle möglichen Pairings
        for subset in combinations(large, min_size):
            for perm in permutations(subset):
                # Baue immer ein man→woman Dict
                if small_is_men:
                    pairing = dict(zip(small, perm))
                else:
                    pairing = {man: woman for man, woman in zip(perm, small)}

                # Prüfe auf Truth Booths + perfekte Matches
                if not (is_valid_truth_booth(pairing, truth_booths, man_doubles, woman_doubles) and
                        respects_perfect_matches(pairing, truth_booths, man_doubles, woman_doubles)):
                    continue

                # Prüfe auf alle bisherigen Ceremonies
                if is_valid_ceremonies(pairing, ceremonies, man_doubles, woman_doubles):
                    valid.append(pairing)
                    if len(valid) >= limit:
                        print(f"✅ Lösung gefunden mit {n} Ceremonies!")
                        return n, valid

                # Optional: Track best Näherung
                score = evaluate_pairing(pairing, truth_booths, ceremonies, man_doubles, woman_doubles)
                if score > best_score:
                    best_score, best, no_improve = score, pairing, 0
                else:
                    no_improve += 1
                if no_improve >= patience:
                    break
            if valid or no_improve >= patience:
                break

        print(f"→ Keine perfekte Lösung bei n={n}")

    print("❌ Selbst mit allen Ceremonies keine perfekte Lösung gefunden.")
    return None, None

def find_unique_solution(data, start=5, patience=1000000):
    men = data["participants"]["men"]
    women = data["participants"]["women"]
    truth_booths = data["truth_booths"]
    all_ceremonies = data["match_ceremonies"]
    man_doubles, woman_doubles = build_double_match_dicts(data)

    # 1. Small/large-Gruppen bestimmen
    if len(men) <= len(women):
        small, large, small_is_men = men, women, True
    else:
        small, large, small_is_men = women, men, False

    min_size = len(small)

    # 2. Nacheinander immer eine Ceremony mehr nutzen
    for n in range(start, len(all_ceremonies) + 1):
        current_ceremonies = all_ceremonies[:n]
        valid_solutions = []
        no_improve = 0
        best_score = -1

        print(f"Teste mit den ersten {n} Matching Nights…")

        # 3. Alle möglichen Pairings durchprobieren
        for subset in combinations(large, min_size):
            for perm in permutations(subset):
                # immer man→frau dict bauen
                if small_is_men:
                    pairing = dict(zip(small, perm))
                else:
                    pairing = {man: woman for man, woman in zip(perm, small)}

                # Truth Booths + perfekte Matches prüfen
                if not (is_valid_truth_booth(pairing, truth_booths, man_doubles, woman_doubles) and
                        respects_perfect_matches(pairing, truth_booths, man_doubles, woman_doubles)):
                    continue

                # Ceremonies prüfen
                if is_valid_ceremonies(pairing, current_ceremonies, man_doubles, woman_doubles):
                    valid_solutions.append(pairing)
                    # wenn mehr als 1 Lösung gefunden, abbrechen—wir brauchen noch mehr Info
                    if len(valid_solutions) > 1:
                        break
                else:
                    # Optional: Track beste Näherung, um früh abzubrechen
                    score = evaluate_pairing(pairing, truth_booths, current_ceremonies, man_doubles, woman_doubles)
                    if score > best_score:
                        best_score, no_improve = score, 0
                    else:
                        no_improve += 1
                    if no_improve >= patience:
                        break
            if len(valid_solutions) > 1 or no_improve >= patience:
                break

        # 4. Prüfen, ob genau eine Lösung übrig ist
        if len(valid_solutions) == 1:
            print(f"✅ Einzig gültige Lösung bei n={n} gefunden.")
            return n, valid_solutions[0]
        else:
            print(f"→ {len(valid_solutions)} Lösungen bei n={n}. Füge nächste Ceremony hinzu.")

    print("❌ Selbst mit allen Matching Nights konnte nicht auf eine eindeutige Lösung eingegrenzt werden.")
    return None, None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python3 ayto_solver.py <pfad-zur-json>")
        print("Beispiel:   python3 ayto_solver.py src/germany/normal/season_1.json")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        data = json.load(f)

    start_time = time.time()
    n_unique, unique_solution = find_unique_solution(data, start=1)
    elapsed = time.time() - start_time

    if n_unique:
        print(f"\n✅ Eindeutige Lösung nach {n_unique} Matching Nights ({elapsed:.1f}s):")
        for man, woman in sorted(unique_solution.items()):
            print(f"  {man} ↔ {woman}")
    else:
        print(f"\n❌ Keine eindeutige Lösung gefunden ({elapsed:.1f}s).")