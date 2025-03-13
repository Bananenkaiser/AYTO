import numpy as np
import matplotlib.pyplot as plt
from data_preprocessing import preprocessing  # Importiere die Preprocessing-Funktion

def monte_carlo_simulation(probabilities, fixed, participants, n_iterations=10000):
    """
    Führt eine Monte-Carlo-Simulation durch:
      - Übernimmt feste (bestätigte) Paare.
      - Erzeugt für die restlichen Männer in jeder Iteration ein vollständiges Matching anhand
        der (normalisierten) Wahrscheinlichkeiten.
    Rückgabe:
      Relative Häufigkeiten der Paare über alle Simulationen.
    """
    men = [m.lower() for m in participants['men']]
    women = [w.lower() for w in participants['women']]

    # Feste Paare übernehmen und verbleibende Männer/Frauen ermitteln
    fixed_pairs = {}
    remaining_men = []
    for man in men:
        match_found = False
        for woman in women:
            if fixed.get((man, woman), False) and probabilities.get((man, woman), 0) == 1.0:
                fixed_pairs[man] = woman
                match_found = True
                break
        if not match_found:
            remaining_men.append(man)
    remaining_women = [w for w in women if w not in fixed_pairs.values()]

    # Dictionary zum Zählen der Paare in der Simulation
    simulation_counts = { (man, woman): 0 for man in men for woman in women }

    for _ in range(n_iterations):
        matching = fixed_pairs.copy()
        available_women = remaining_women.copy()

        # Für jeden verbleibenden Mann: wähle eine Frau basierend auf den Wahrscheinlichkeiten
        for man in remaining_men:
            probs = np.array([probabilities[(man, w)] for w in available_women])
            if probs.sum() == 0:
                probs = np.ones(len(available_women))
            probs = probs / probs.sum()
            chosen = np.random.choice(available_women, p=probs)
            matching[man] = chosen
            available_women.remove(chosen)

        for man, woman in matching.items():
            simulation_counts[(man, woman)] += 1

    # Umwandlung in relative Häufigkeiten
    simulation_freq = { k: v / n_iterations for k, v in simulation_counts.items() }
    return simulation_freq

def plot_simulation_matrix(simulation_freq, participants):
    """
    Zeichnet eine Heatmap, die die relative Häufigkeit der Paare in der Monte-Carlo-Simulation zeigt.
    """
    men = [m.lower() for m in participants['men']]
    women = [w.lower() for w in participants['women']]
    matrix = np.zeros((len(men), len(women)))

    for i, man in enumerate(men):
        for j, woman in enumerate(women):
            matrix[i, j] = simulation_freq.get((man, woman), 0)

    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(matrix, cmap='viridis', vmin=0, vmax=1)
    plt.xticks(ticks=np.arange(len(women)), labels=[w.capitalize() for w in women], rotation=90)
    plt.yticks(ticks=np.arange(len(men)), labels=[m.capitalize() for m in men])

    for i in range(len(men)):
        for j in range(len(women)):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha='center', va='center', color='white')

    plt.colorbar(cax, label="Relative Häufigkeit")
    plt.xlabel("Frauen")
    plt.ylabel("Männer")
    plt.title("Monte-Carlo-Simulation: Auftretenswahrscheinlichkeiten der Paare")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Preprocessing durchführen und Daten laden
    probabilities, fixed, participants = preprocessing()
    
    # Monte-Carlo-Simulation durchführen
    simulation_freq = monte_carlo_simulation(probabilities, fixed, participants, n_iterations=10000)
    
    # Ergebnisse visualisieren
    plot_simulation_matrix(simulation_freq, participants)
