import json
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
    no_pair = ceremony.get("no_pair:", None)
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

# ------------------------------
# Hauptfunktion: Suche der gültigen Lösung
# ------------------------------
def find_valid_ayto_solutions(data, limit=1):
    men = data["participants"]["men"]
    women = data["participants"]["women"]
    truth_booths = data["truth_booths"]
    ceremonies = data["match_ceremonies"]

    valid_solutions = []

    for selected_women in combinations(women, len(men)):
        for perm in permutations(selected_women):
            pairing = dict(zip(men, perm))

            if not is_valid_truth_booth(pairing, truth_booths):
                continue
            if not respects_perfect_matches(pairing, truth_booths):
                continue
            if not is_valid_ceremonies(pairing, ceremonies):
                continue

            valid_solutions.append(pairing)
            if len(valid_solutions) >= limit:
                return valid_solutions

    return valid_solutions

# ------------------------------
# Ausführung
# ------------------------------
if __name__ == "__main__":
    path = f".\\src\\vip\\"
    #path = f".\\src\\normal\\"
    season = "Season_4.json"

    with open(path + season, "r") as f:
        data = json.load(f)

    solutions = find_valid_ayto_solutions(data, limit=1)

    if solutions:
        print("✅ Gültige Lösung gefunden:\n")
        for man, woman in solutions[0].items():
            print(f"{man} ↔ {woman}")
    else:
        print("❌ Keine gültige Lösung gefunden.")
