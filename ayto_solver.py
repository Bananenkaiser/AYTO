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

# ------------------------------
# Ausführung
# ------------------------------
if __name__ == "__main__":
    path = f".\\src\\vip\\"
    #path = f".\\src\\normal\\"
    season = "Season_3.json"

    with open(path + season, "r") as f:
        data = json.load(f)

    start_time = time.time()  # Record start time

    solutions = find_valid_ayto_solutions(data, limit=1, patience=5000000)

    end_time = time.time()  # Record end time
    elapsed_time = end_time - start_time

    if solutions:
        print("✅ Gültige Lösung gefunden:\n")
        for man, woman in solutions[0].items():
            print(f"{man} ↔ {woman}")
    else:
        print("❌ Keine gültige Lösung gefunden.")

    print(f"Zeit zum Finden der Lösung: {elapsed_time:.2f} Sekunden")
