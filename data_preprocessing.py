import json
import matplotlib.pyplot as plt
import numpy as np


DUMMY_PENALTY = 0




def balance_participants(participants):
    """
    Gleicht die Teilnehmerzahlen aus, indem Dummy-Einträge hinzugefügt werden.
    Beispiel: Wenn mehr Männer als Frauen vorhanden sind, werden Dummy-Frauen hinzugefügt.
    
    Rückgabe:
      Ein Dictionary mit ausgeglichenen Listen für "men" und "women".
    """
    men = [m.lower() for m in participants['men']]
    women = [w.lower() for w in participants['women']]
    if len(men) > len(women):
        diff = len(men) - len(women)
        for i in range(diff):
            dummy = f"dummy_woman_{i+1}"
            women.append(dummy)
    elif len(women) > len(men):
        diff = len(women) - len(men)
        for i in range(diff):
            dummy = f"dummy_man_{i+1}"
            men.append(dummy)
    return {"men": men, "women": women}

def load_data(filename):
    """
    Lädt JSON-Daten aus der angegebenen Datei.
    """
    with open(filename, 'r') as f:
        return json.load(f)

def initialize_probabilities(participants):
    """
    Initialisiert:
      - probabilities[(man, woman)] startet mit 0.5
      - fixed[(man, woman)] startet mit False
    """
    probabilities = {}
    fixed = {}
    men = [man.lower() for man in participants['men']]
    women = [woman.lower() for woman in participants['women']]
    for man in men:
        for woman in women:
            probabilities[(man, woman)] = 0.5
            fixed[(man, woman)] = False
    return probabilities, fixed

def update_truth_booths(probabilities, fixed, truth_booths):
    """
    Aktualisiert Wahrscheinlichkeiten und Fixed-Status anhand der Truth-Booth-Ergebnisse.
    Bei bestätigten Matches wird der Wert auf 1.0 gesetzt und der betreffende Mann und/oder
    die Frau von allen weiteren Kombinationen ausgeschlossen.
    """
    for booth in truth_booths:
        man = booth['man'].lower()
        woman = booth['woman'].lower()
        pair = (man, woman)

        if booth['is_match']:
            # Bestätige das Paar
            probabilities[pair] = 1.0
            fixed[pair] = True
            # Schließe diesen Mann aus allen anderen Paaren aus
            for other_pair in list(probabilities.keys()):
                if other_pair[0] == man and other_pair != pair:
                    probabilities[other_pair] = 0.0
                    fixed[other_pair] = True
            # Schließe diese Frau aus allen anderen Paaren aus
            for other_pair in list(probabilities.keys()):
                if other_pair[1] == woman and other_pair != pair:
                    probabilities[other_pair] = 0.0
                    fixed[other_pair] = True
        else:
            # Bestätige, dass es kein Match ist
            probabilities[pair] = 0.0
            fixed[pair] = True

    return probabilities, fixed

def normalize_possible_pairs(probabilities, fixed, participants):
    """
    Normalisiert für jeden Mann die Wahrscheinlichkeiten, sofern noch kein perfektes (festes) Match vorliegt.
    """
    men = [m.lower() for m in participants['men']]
    women = [w.lower() for w in participants['women']]

    for man in men:
        # Prüfe, ob bereits ein festes Match vorliegt
        has_fixed_match = any(
            fixed[(man, woman)] and probabilities[(man, woman)] == 1.0
            for woman in women
        )
        if has_fixed_match:
            continue

        # Andernfalls verteile die Wahrscheinlichkeit gleichmäßig auf alle noch möglichen Frauen
        possible_women = [woman for woman in women if not fixed[(man, woman)]]
        if possible_women:
            new_prob = 1.0 / len(possible_women)
            for woman in possible_women:
                probabilities[(man, woman)] = new_prob

    return probabilities

def plot_probability_matrix(probabilities, participants):
    """
    Zeichnet eine Heatmap (Wärmekarte) der Wahrscheinlichkeiten (Männer vs. Frauen).
    """
    men = [m.lower() for m in participants['men']]
    women = [w.lower() for w in participants['women']]

    matrix = np.zeros((len(men), len(women)))
    for i, man in enumerate(men):
        for j, woman in enumerate(women):
            matrix[i, j] = probabilities.get((man, woman), 0)

    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(matrix, cmap='coolwarm', vmin=0, vmax=1)
    plt.xticks(ticks=np.arange(len(women)), labels=[w.capitalize() for w in women], rotation=90)
    plt.yticks(ticks=np.arange(len(men)), labels=[m.capitalize() for m in men])

    for i in range(len(men)):
        for j in range(len(women)):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha='center', va='center', color='black')

    plt.colorbar(cax, label="Wahrscheinlichkeit")
    plt.xlabel("Frauen")
    plt.ylabel("Männer")
    plt.title("Probability Matrix for Matches")
    plt.tight_layout()
    plt.show()

def count_pair_occurrences(data):
    """
    Zählt, wie oft jedes Paar in den Match Ceremonies ausgewählt wurde.
    """
    pair_counts = {}
    for ceremony in data.get('match_ceremonies', []):
        for p in ceremony['pairs']:
            man = p['man'].lower()
            woman = p['woman'].lower()
            key = (man, woman)
            pair_counts[key] = pair_counts.get(key, 0) + 1
    return pair_counts

def plot_pair_counts(pair_counts):
    """
    Zeichnet ein Balkendiagramm, das die Häufigkeit der in den Match Ceremonies gebildeten Paare zeigt.
    """
    pairs = list(pair_counts.keys())
    counts = [pair_counts[p] for p in pairs]
    labels = [f"{man.capitalize()} - {woman.capitalize()}" for man, woman in pairs]

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(labels, counts)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Paare")
    plt.ylabel("Häufigkeit")
    plt.title("Häufigkeit der in den Match Ceremonies gebildeten Paare")
    plt.tight_layout()
    plt.show()

def preprocessing(season):
    """
    Führt folgende Schritte durch:
      1) Laden der Daten
      2) Ausbalancieren der Teilnehmer
      3) Initialisieren der Wahrscheinlichkeiten
      4) Verarbeiten der Truth Booths und Match Ceremonies
      5) Normalisieren der Wahrscheinlichkeiten
      6) Visualisierung der Ergebnisse
    Rückgabe:
      probabilities, fixed, participants, ceremonies
    """
    # Dateipfad anpassen
    
    path = f".\\src\\normal\\"
    data = load_data(path + season)
    
    # 1) Teilnehmer ausbalancieren
    participants = balance_participants(data['participants'])
    
    # 2) Wahrscheinlichkeiten initialisieren (mit den ausgeglichenen Teilnehmern)
    probabilities, fixed = initialize_probabilities(participants)
    
    # 3) Truth Booths verarbeiten
    if 'truth_booths' in data and data['truth_booths']:
        probabilities, fixed = update_truth_booths(probabilities, fixed, data['truth_booths'])
    
    # 4) Match Ceremonies verarbeiten
    if 'match_ceremonies' in data and data['match_ceremonies']:
        for i, ceremony in enumerate(data['match_ceremonies'], start=1):
            confirmed_match_count = 0
            for p in ceremony['pairs']:
                key = (p['man'].lower(), p['woman'].lower())
                if fixed.get(key, False) and probabilities.get(key, 0) == 1.0:
                    confirmed_match_count += 1
            if confirmed_match_count > 0:
                #print(f"[Ceremony {i}] Found {confirmed_match_count} confirmed perfect match(es).")
                ceremony['score'] = max(ceremony['score'] - confirmed_match_count, 0)
                #print(f"[Ceremony {i}] New Score: {ceremony['score']}")
                if ceremony['score'] == 0:
                    print(f"[Ceremony {i}] Blackout triggered!")
                    for p in ceremony['pairs']:
                        key = (p['man'].lower(), p['woman'].lower())
                        if not (fixed.get(key, False) and probabilities.get(key, 0) == 1.0):
                            probabilities[key] = 0.0
                            fixed[key] = True
    
    # 5) Normalisieren der Wahrscheinlichkeiten
    probabilities = normalize_possible_pairs(probabilities, fixed, participants)
    
    # 6) Visualisierung (optional)
    #plot_probability_matrix(probabilities, participants)
    #pair_counts = count_pair_occurrences(data)
    #print("\nHäufigkeit der Paare (über alle Match Ceremonies):")
    #for pair, count in sorted(pair_counts.items(), key=lambda x: x[1], reverse=True):
    #    print(f"{pair[0].capitalize()} - {pair[1].capitalize()}: {count} mal")
    #plot_pair_counts(pair_counts)
    
    # Zusätzlich: Übergabe der Ceremonies
    return probabilities, fixed, participants, data.get('match_ceremonies', [])


if __name__ == "__main__":
    preprocessing()
