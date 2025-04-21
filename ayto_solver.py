import json
import time
from itertools import permutations, combinations

# ------------------------------
# Hilfsfunktionen
# ------------------------------
def is_valid_truth_booth(pairing, truth_booths):
    for tb in truth_booths:
        man, woman, is_match = tb["man"], tb["woman"], tb["is_match"]
        if (man in pairing and pairing[man] == woman) != is_match:
            return False
    return True

def respects_perfect_matches(pairing, truth_booths):
    for tb in truth_booths:
        if tb["is_match"]:
            if pairing.get(tb["man"]) != tb["woman"]:
                return False
    return True

def match_score(pairing, ceremony):
    expected_pairs = {(p["man"], p["woman"]) for p in ceremony["pairs"]}
    no_pair = ceremony.get("no_pair", None)
    return sum(
        1 for man, woman in pairing.items()
        if (man, woman) in expected_pairs and woman != no_pair
    )

def is_valid_ceremonies(pairing, ceremonies):
    for ceremony in ceremonies:
        expected_score = ceremony["score"]
        if match_score(pairing, ceremony) != expected_score:
            return False
    return True

def evaluate_pairing(pairing, truth_booths, ceremonies):
    score = 0
    # Add points for each truth booth that is respected
    for tb in truth_booths:
        man, woman, is_match = tb["man"], tb["woman"], tb["is_match"]
        if (man in pairing and pairing[man] == woman) == is_match:
            score += 1
    # Add points for each ceremony score that matches
    for ceremony in ceremonies:
        if match_score(pairing, ceremony) == ceremony["score"]:
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
            if is_valid_truth_booth(pairing, truth_booths) \
            and respects_perfect_matches(pairing, truth_booths) \
            and is_valid_ceremonies(pairing, ceremonies):
                valid_solutions.append(pairing)
                if len(valid_solutions) >= limit:
                    return valid_solutions

            # Evaluate the pairing if not fully valid
            score = evaluate_pairing(pairing, truth_booths, ceremonies)
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
                if not (is_valid_truth_booth(pairing, truth_booths) and
                        respects_perfect_matches(pairing, truth_booths)):
                    continue

                # Prüfe auf alle bisherigen Ceremonies
                if is_valid_ceremonies(pairing, ceremonies):
                    valid.append(pairing)
                    if len(valid) >= limit:
                        print(f"✅ Lösung gefunden mit {n} Ceremonies!")
                        return n, valid

                # Optional: Track best Näherung
                score = evaluate_pairing(pairing, truth_booths, ceremonies)
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
                if not (is_valid_truth_booth(pairing, truth_booths) and
                        respects_perfect_matches(pairing, truth_booths)):
                    continue

                # Ceremonies prüfen
                if is_valid_ceremonies(pairing, current_ceremonies):
                    valid_solutions.append(pairing)
                    # wenn mehr als 1 Lösung gefunden, abbrechen—wir brauchen noch mehr Info
                    if len(valid_solutions) > 1:
                        break
                else:
                    # Optional: Track beste Näherung, um früh abzubrechen
                    score = evaluate_pairing(pairing, truth_booths, current_ceremonies)
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


# Beispiel-Aufruf im __main__-Block
if __name__ == "__main__":
    #path = f".\\src\\vip\\"
    path = f".\\src\\us\\normal\\"
    #path = f".\\src\\normal\\"
    season = "season_2.json"

    with open(path + season, "r") as f:
        data = json.load(f)

    start_time = time.time()  # Record start time
    # ... lade data wie gehabt ...
    n_unique, unique_solution = find_unique_solution(data, start=5)
    if n_unique:
        print(f"Du brauchst mindestens {n_unique} Matching Nights, um exakt eine Lösung zu erhalten.")
        for man, woman in unique_solution.items():
            print(f"{man} ↔ {woman}")
    else:
        print("Eine eindeutige Lösung ließ sich nicht finden.")