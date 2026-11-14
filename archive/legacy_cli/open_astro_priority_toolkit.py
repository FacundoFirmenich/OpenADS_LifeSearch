"""
=============================================================================
OPEN ASTRO-PRIORITY TOOLKIT - INTERACTIVE SMAA-2 ENGINE
=============================================================================
Operationalizing Paradigmatic Inertia & Stochastic MCDA.
Top-Tier 1 Open Science Framework for Planetary Science Policy.
=============================================================================
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="white", context="paper")

class AstroPriorityCLI:
    def __init__(self):
        self.targets = ["Enceladus", "Europa", "Mars", "Titan", "Venus", "Ganymede"]
        self.criteria = ["Evidence (E)", "Feasibility (F)"]
        self.evidence = np.array([0.600, 0.533, 0.467, 0.400, 0.733, 0.267])
        self.feasibility = np.array([0.45, 0.65, 0.95, 0.55, 0.35, 0.50])
        self.out_dir = Path("outputs/astro_priority_cli")
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*75)
        print(" 🌌 OPEN ASTRO-PRIORITY TOOLKIT (SMAA-2) ".center(75))
        print("="*75)
        print(" Stochastic Multi-Criteria Design | Policy Simulation | SROI Analysis")
        print("="*75 + "\n")

    def run_simulation(self, n_iter=10000):
        self.header()
        print(f" Initiating Stochastic Simulation ({n_iter} iterations)...")
        
        # Simple SMAA-2 Implementation for the Toolkit
        n_targets = len(self.targets)
        rank_counts = np.zeros((n_targets, n_targets))
        
        for _ in range(n_iter):
            # Sample w_E from [0, 1], w_F = 1 - w_E
            we = np.random.rand()
            wf = 1 - we
            
            # Utility (Hybrid Multiplicative-Additive approximation)
            u = we * self.evidence + wf * self.feasibility
            
            # Sorting to get ranks
            ranks = n_targets - np.argsort(np.argsort(u)) 
            for i in range(n_targets):
                rank_counts[i, int(ranks[i]-1)] += 1
                
        b1 = rank_counts[:, 0] / n_iter
        df_res = pd.DataFrame({
            "Target": self.targets,
            "Acceptability (b1)": b1
        }).sort_values("Acceptability (b1)", ascending=False)
        
        print("\n [ SIMULATION RESULTS ]")
        print(df_res.to_string(index=False))
        
        if input("\n >>> Plot Priority Distribution (b1 Dashboard)? (y/n): ").strip().lower() == 'y':
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.barplot(data=df_res, x="Target", y="Acceptability (b1)", palette="viridis", ax=ax, hue="Target", legend=False)
            ax.set_title("First-Rank Acceptability (b1) - Stochastic Priorities")
            ax.set_ylim(0, 1)
            sns.despine()
            plt.tight_layout()
            plt.savefig(self.out_dir / "priority_dashboard.pdf")
            plt.close()
            print(f" [SUCCESS] Dashboard saved in {self.out_dir}")
            
        input("\n [Press ENTER to return]")

    def run(self):
        while True:
            self.header()
            print(" 1. Run Stochastic Prioritization (SMAA-2)")
            print(" 2. Configure Target Metrics (Evidence / Feasibility)")
            print(" 0. Exit")
            c = input("\n >>> Command: ").strip()
            if c == '1': self.run_simulation()
            elif c == '0': break

if __name__ == "__main__":
    AstroPriorityCLI().run()
