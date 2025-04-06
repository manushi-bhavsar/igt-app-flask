import random
import time
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
class Deck:
    def __init__(self, name, reward, penalty, quadrant=None, last_gain=0, last_penalty=0):
        self.name = name
        self.reward = reward
        self.penalty = penalty
        self.quadrant = quadrant
        self.last_gain = last_gain
        self.last_penalty = last_penalty

    def play(self):
        self.last_gain = self.reward
        # Apply penalty 50% of the time
        self.last_penalty = self.penalty if random.random() < 0.5 else 0
        return self.last_gain + self.last_penalty  # penalty is negative
    
class IowaGamblingTask:
    def __init__(self):
        self.bank = 2000
        self.deck_properties = [
            {"reward": 150, "penalty": -200, "quadrant": "Reckless Gambler"},
            {"reward": 100, "penalty": -50, "quadrant": "Calculated Risk-Taker"},
            {"reward": 100, "penalty": -100, "quadrant": "Fearful-Spender"},
            {"reward": 75, "penalty": -50, "quadrant": "Risk-Averse Analyst"}
        ]
        self.decks = self._assign_random_decks()
        self.deck_choices = defaultdict(int)
        self.reaction_times = []
        self.results = []

    def _assign_random_decks(self):
        shuffled = random.sample(self.deck_properties, len(self.deck_properties))
        return {deck: Deck(deck, prop["reward"], prop["penalty"], prop["quadrant"])
                for deck, prop in zip(["A", "B", "C", "D"], shuffled)}

    def get_user_choice(self):
        while True:
            choice = input("Choose a deck (A, B, C, or D): ").strip().upper()
            if choice in self.decks:
                return choice
            print("Invalid choice! Please select A, B, C, or D.")

    def compute_entropy(self):
        N = sum(self.deck_choices.values())
        probabilities = np.array([count / N for count in self.deck_choices.values()])
        return -np.sum(probabilities * np.log2(probabilities + 1e-10))

    def compute_std_dev(self):
        net_gains = [result["Net Gain"] for result in self.results]
        return np.std(net_gains)  # Sample SD (ddof=1 by default)

    def run(self):
        print(f"Starting bank: ${self.bank}")
        for round_number in range(1, 101):
            print(f"\nRound {round_number}: Bank = ${self.bank}")
            start_time = time.time()
            deck_choice = self.get_user_choice()
            end_time = time.time()

            reaction_time = end_time - start_time
            self.reaction_times.append(reaction_time)

            net_gain = self.decks[deck_choice].play()
            self.bank += net_gain
            self.deck_choices[deck_choice] += 1

            print(f"You chose Deck {deck_choice} ({self.decks[deck_choice].quadrant})")
            print(f"Net gain: ${net_gain}, New bank: ${self.bank}")

            self.results.append({
                "Round": round_number,
                "Deck Chosen": deck_choice,
                "Quadrant": self.decks[deck_choice].quadrant,
                "Net Gain": net_gain,
                "Bank Balance": self.bank,
                "Reaction Time (s)": reaction_time
            })

        # Analysis
        entropy = self.compute_entropy()
        std_dev = self.compute_std_dev()
        print(f"\n--- Analysis ---")
        print(f"Shannon Entropy: {entropy:.4f} (Exploration vs. Exploitation)")
        print(f"Standard Deviation of Net Gain: {std_dev:.2f} (Impulsivity vs. Strategic Thinking)")

        # Export results
        self._export_results(entropy, std_dev)

    def _export_results(self, entropy, std_dev):
        with pd.ExcelWriter("Iowa_Gambling_Task_Results.xlsx", engine="openpyxl") as writer:
            pd.DataFrame(self.results).to_excel(writer, sheet_name="Round Data", index=False)
            pd.DataFrame({"Final Bank": [self.bank]}).to_excel(writer, sheet_name="Final Bank", index=False)
            pd.DataFrame({"Reaction Time (s)": self.reaction_times}).to_excel(writer, sheet_name="Reaction Times", index=False)
            pd.DataFrame(list(self.deck_choices.items()), columns=["Deck", "Times Chosen"]).to_excel(writer, sheet_name="Deck Choices", index=False)
            pd.DataFrame({"Metric": ["Shannon Entropy", "Std Dev Net Gain"], "Value": [entropy, std_dev]}).to_excel(writer, sheet_name="Analysis", index=False)
        print("\nResults exported to 'Iowa_Gambling_Task_Results.xlsx'.")

if __name__ == "__main__":
    igt = IowaGamblingTask()
    igt.run()