"""
=============================================================================
OPEN ADS COMPLEXITY & TOPOLOGY TOOLKIT - INTERACTIVE CLI EDITION
=============================================================================
Top-Tier 1 Open Science Tool for NASA ADS Interfacing.
Integrates Spectral Graph Theory, Bayesian Epistemology, and Live Plotting.
=============================================================================
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from itertools import combinations
from pathlib import Path

sns.set_theme(style="whitegrid", context="paper")
plt.rcParams.update({"font.family": "serif", "figure.dpi": 300, "axes.titlesize": 12})

try:
    import ads
except ImportError:
    print("[CRITICAL ERROR] Module 'ads' not found. Please execute: pip install ads networkx pandas seaborn")
    sys.exit(1)

class ADSTopologyCLI:
    def __init__(self):
        self.api_token = "L8Gl2fryv5uIGYvXuCZrhHZYlt9A3IfgBrhUvghT"
        self.query = 'keyword:"astrobiology" AND year:2020-2024'
        self.max_records = 300
        self.out_dir = Path("outputs/ads_complexity_cli")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.df_ads = None
        self.G = None
        self.df_cent = pd.DataFrame()
        self.pmi_results = []
        ads.config.token = self.api_token

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def header(self):
        self.clear()
        print("="*75)
        print(" 🌌 OPEN ADS COMPLEXITY & TOPOLOGY TOOLKIT ".center(75))
        print("="*75)
        print(" Advanced Interactive Engine | NASA ADS | Graph Theory | Bayesian Nodes")
        print("="*75 + "\n")

    def run(self):
        while True:
            self.header()
            print(" [ MAIN MENU ]")
            print(" 1. Environment Configuration (API Key & Paths)")
            print(" 2. NASA ADS Data Ingestion (Custom Query & Limits)")
            print(" 3. [Post-Processing] Graph Topology & Nodal Complexity")
            print(" 4. [Post-Processing] Bayesian Inference (Epistemic Missing Links)")
            print(" 5. Export Database, Visualizations, and Markdown Report")
            print(" 0. Exit Framework")
            
            c = input("\n >>> Select an option (0-5): ").strip()
            if c == '1': self.menu_config()
            elif c == '2': self.menu_extract()
            elif c == '3': self.menu_topology()
            elif c == '4': self.menu_bayesian()
            elif c == '5': self.menu_export()
            elif c == '0':
                print("\nExiting the Framework... Open Science endures!")
                break
            else:
                input(" Invalid option. [Press ENTER to continue]")

    def menu_config(self):
        self.header()
        print(f" [*] Current API Token: {self.api_token[:5]}...{self.api_token[-5:]}")
        print(f" [*] Output Directory: {self.out_dir}")
        print("\n Options:")
        print(" 1. Modify API Token")
        print(" 2. Modify Output Directory")
        print(" 0. Return to Main Menu")
        c = input("\n >>> Option: ").strip()
        if c == '1':
            t = input(" Enter new NASA ADS Token: ").strip()
            if t: 
                self.api_token = t
                ads.config.token = t
                print(" Token updated dynamically.")
        elif c == '2':
            d = input(" Enter new path (e.g., 'data/ads_results/'): ").strip()
            if d:
                self.out_dir = Path(d)
                self.out_dir.mkdir(parents=True, exist_ok=True)
                print(" Directory routed and created.")
        if c in ['1','2']: input("\n [Press ENTER to continue]")

    def menu_extract(self):
        self.header()
        print(f" [*] Current Query : {self.query}")
        print(f" [*] Record Limit  : {self.max_records}")
        print("\n Options:")
        print(" 1. Execute Extraction with current parameters")
        print(" 2. Modify Query (ADS Syntax)")
        print(" 3. Modify Maximum Record Volume")
        print(" 0. Return to Main Menu")
        c = input("\n >>> Option: ").strip()
        if c == '1':
            print("\n [!] Interfacing with NASA ADS Servers...")
            try:
                papers = list(ads.SearchQuery(q=self.query, fl=['bibcode', 'title', 'abstract', 'keyword'], rows=self.max_records))
                data = [{'bibcode': p.bibcode, 'title': p.title[0] if p.title else 'No Title', 'abstract': p.abstract or '', 'keywords': getattr(p, 'keyword', []) or []} for p in papers]
                self.df_ads = pd.DataFrame(data)
                print(f"\n [SUCCESS] Captured {len(self.df_ads)} multidisciplinary records.")
            except Exception as e:
                print(f"\n [ERROR] Connection Exception: {e}")
            input("\n [Press ENTER to continue]")
        elif c == '2':
            q = input(" Enter Search Query (e.g., keyword:\"exoplanet\"): ").strip()
            if q: self.query = q
        elif c == '3':
            try:
                self.max_records = int(input(" Enter maximum record limit (integer): ").strip())
            except:
                pass

    def menu_topology(self):
        self.header()
        if self.df_ads is None or self.df_ads.empty:
            print(" [X] Error: No corpus loaded. Please execute Module 2 first.")
            input("\n [Press ENTER to return]")
            return
            
        print(" Assembling Multi-layer Lexical Graph Vector...")
        self.G = nx.Graph()
        for kws in self.df_ads['keywords'].dropna():
            if len(kws) > 1:
                clean = [k.lower() for k in kws[:6]]
                for p1, p2 in combinations(clean, 2):
                    if self.G.has_edge(p1, p2): self.G[p1][p2]['weight'] += 1
                    else: self.G.add_edge(p1, p2, weight=1)
                    
        print(f" [*] Ramanujan-Proxy Graph: {self.G.number_of_nodes()} Nodes, {self.G.number_of_edges()} Edges.")
        
        prune_w = input("\n >>> Prune edges with weight below X? (Leave blank for None): ").strip()
        if prune_w.isdigit():
            w = int(prune_w)
            rem = [(u, v) for u, v, d in self.G.edges(data=True) if d['weight'] < w]
            self.G.remove_edges_from(rem)
            self.G.remove_nodes_from(list(nx.isolates(self.G)))
            print(f" [*] Post-Pruning: {self.G.number_of_nodes()} Nodes, {self.G.number_of_edges()} Edges.")
            
        if self.G.number_of_nodes() > 0:
            print(" Computing Eigenvector Centrality...")
            try:
                cent = nx.eigenvector_centrality_numpy(self.G, max_iter=1000)
                self.df_cent = pd.DataFrame(list(cent.items()), columns=["Node", "Centrality"]).sort_values(by="Centrality", ascending=False)
                print("\n Top 5 Nodes of Maximum Hidden Centrality:")
                print(self.df_cent.head(5).to_string(index=False))
                
                if input("\n >>> Plot Nodal Density and Save to PDF? (y/n): ").strip().lower() == 'y':
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.barplot(data=self.df_cent.head(15), y="Node", x="Centrality", palette="mako", ax=ax, hue="Node", legend=False)
                    ax.set_title("Lexical Eigenvector Centrality (Top 15 Nodes)")
                    sns.despine(trim=True)
                    plt.tight_layout()
                    plt.savefig(self.out_dir / "eigen_centrality_plot.pdf")
                    plt.close()
                    print(f" Plot saved successfully to {self.out_dir}")
            except Exception as e:
                print(f" [!] Matrix convergence failure: {e}")
        input("\n [Press ENTER to continue]")

    def menu_bayesian(self):
        self.header()
        if self.df_ads is None or self.df_ads.empty:
            print(" [X] Error: No corpus in memory. Extract using Module 2.")
            input("\n [Press ENTER to return]")
            return
            
        print(" [ BAYESIAN INFERENCE OF EPISTEMIC VOIDS (MISSING LINKS) ]")
        print(" Analyzes Pointwise Mutual Information (PMI) between concepts.\n")
        
        while True:
            t1 = input(" > Term A (or '0' to return): ").strip().lower()
            if t1 == '0': break
            t2 = input(" > Term B: ").strip().lower()
            
            docs_a = self.df_ads['abstract'].str.contains(t1, case=False, na=False)
            docs_b = self.df_ads['abstract'].str.contains(t2, case=False, na=False)
            
            p_a, p_b = docs_a.mean(), docs_b.mean()
            p_ab = (docs_a & docs_b).mean()
            
            pmi = np.log2(p_ab / (p_a * p_b)) if p_a > 0 and p_b > 0 and p_ab > 0 else (-np.inf if p_a > 0 and p_b > 0 else 0)
            
            stat = "Epistemic Missing Link (Highly Suggested Fusion)" if pmi == -np.inf else ("Latent Synergy" if pmi > 0 else "Sterile Base")
            
            print(f"\n [+] Mathematical Diagnostics for '{t1}' <-> '{t2}':")
            print(f"     N(A): {docs_a.sum()} | N(B): {docs_b.sum()} | N(A∩B): {(docs_a & docs_b).sum()}")
            print(f"     PMI : {pmi:.4f} bits")
            print(f"     Status: {stat}\n")
            
            self.pmi_results.append({"TermA": t1, "TermB": t2, "PMI": pmi, "Status": stat})

    def menu_export(self):
        self.header()
        if self.df_ads is None:
            print(" [X] Null Datasets. Please extract data first.")
            input("\n [Return]")
            return
        
        print(" Writing Raw Database (CSV)...")
        self.df_ads.to_csv(self.out_dir / "ADS_Raw_Matrix.csv", index=False)
        
        print(" Exporting Integrating Scientific Report (Top Tier 1 Markdown)...")
        with open(self.out_dir / "Investigative_Report_Tier1.md", "w", encoding="utf-8") as f:
            f.write("# Analytical Report: Topological Mining from NASA ADS\n\n")
            f.write(f"**Computed Query:** `{self.query}`\n")
            f.write(f"**Indexed Nodes:** {len(self.df_ads)} multidimensional records.\n\n")
            if not self.df_cent.empty:
                f.write("## 1. Lexical Graph Centrality Metric (Dominant Ramanujan Topology)\n\n")
                f.write(self.df_cent.head(20).to_markdown(index=False) + "\n\n")
            if self.pmi_results:
                f.write("## 2. Bayesian Inference: Hypothesis Void Detection (Missing Links)\n\n")
                f.write(pd.DataFrame(self.pmi_results).to_markdown(index=False) + "\n\n")
            f.write("\n---\n*Compiled algorithmically via Open ADS Complexity CLI*")
            
        print(f"\n [SUCCESS] All objects successfully saved in '{self.out_dir}'.")
        input("\n [Press ENTER to return]")

if __name__ == "__main__":
    ADSTopologyCLI().run()
