"""
=============================================================================
OPEN DECADAL NLP & EXTRACTION TOOLKIT - INTERACTIVE CLI EDITION
=============================================================================
Top-Tier 1 Open Science Tool for Semantic Deep Parsing of PDF Documents.
Proactive Regex/NLP search, stratigraphy histograms, and Machine-Driven Truth.
=============================================================================
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="ticks", context="paper")
plt.rcParams.update({"font.family": "serif", "figure.dpi": 300, "axes.titlesize": 12})

try:
    import pdfplumber
except ImportError:
    print("[CRITICAL ERROR] Module 'pdfplumber' not detected. Execute: pip install pdfplumber pandas matplotlib seaborn")
    sys.exit(1)

class DecadalNLPCLI:
    def __init__(self):
        self.pdf_path = "data/external/decadal_survey_2022.pdf"
        self.out_dir = Path("outputs/decadal_nlp_cli")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.df_text = None
        self.search_logs = []
        self.df_tc = pd.DataFrame()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def header(self):
        self.clear()
        print("="*75)
        print(" 🛰️ OPEN DECADAL SURVEY NLP TOOLKIT ".center(75))
        print("="*75)
        print(" Machine-Driven Deep Parsing | Heuristic NLP | Semantic Stratigraphy")
        print("="*75 + "\n")

    def run(self):
        while True:
            self.header()
            print(" [ INTERACTIVE MAIN MENU ]")
            print(" 1. Environment Configuration (Input PDF Path)")
            print(" 2. Ingest and Ontologically Parse PDF")
            print(" 3. [Analysis] Dynamic Frequency Index (Concept Hunting / Citability)")
            print(" 4. [Analysis] Deep Scanner for Parametric Targets (Dense Chapters)")
            print(" 5. Export Visual Plots (Matplotlib) and Markdown Report")
            print(" 0. Abort Framework")
            
            c = input("\n >>> Enter a command (0-5): ").strip()
            if c == '1': self.menu_config()
            elif c == '2': self.menu_ingest()
            elif c == '3': self.menu_lexical()
            elif c == '4': self.menu_targets()
            elif c == '5': self.menu_export()
            elif c == '0':
                print("\nClosing terminal... Ecosystem secured.")
                break
            else:
                input(" Invalid operator. [Press ENTER to iterate]")

    def menu_config(self):
        self.header()
        print(f" [*] Current PDF Target Path: {self.pdf_path}")
        print(f" [*] Results Directory      : {self.out_dir}")
        print("\n 1. Change PDF Path")
        print(" 2. Change Results Directory")
        print(" 0. Return to Main Menu")
        c = input("\n >>> Option: ").strip()
        if c == '1':
            n = input(" Exact path (e.g., docs/my_file.pdf): ").strip()
            if n: self.pdf_path = n
        elif c == '2':
            n = input(" Export folder (e.g., outputs/my_scan/): ").strip()
            if n:
                self.out_dir = Path(n)
                self.out_dir.mkdir(parents=True, exist_ok=True)
        if c in ['1','2']: input("\n [Press ENTER to continue]")

    def menu_ingest(self):
        self.header()
        print(" Initiating Stratigraphic Phagocytosis of the PDF File...")
        if not os.path.exists(self.pdf_path):
            print(f"\n [ERROR] File does not exist at {self.pdf_path}")
            input(" [Press ENTER to abort subroutine]")
            return
            
        print(" Extracting and segmenting corpus. Please wait... (may take >30s)")
        try:
            data = []
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    t = page.extract_text()
                    if t: data.append({"page": i+1, "text": t})
            self.df_text = pd.DataFrame(data)
            print(f"\n [SUCCESS] Organically ingested {len(self.df_text)} semantic text blocks/pages.")
        except Exception as e:
            print(f"\n [FATAL ERROR] Parser exception: {e}")
            
        input("\n [Press ENTER to continue]")

    def menu_lexical(self):
        self.header()
        if self.df_text is None:
            print(" [X] PDF not ingested. Please operate Module 2.")
            input("\n [Press ENTER to return]")
            return
            
        print(" [ CONCEPTUAL HUNTING AND STRATIGRAPHIC DISTRIBUTION ]\n")
        term = input(" Enter Token/Regex for Mining (e.g., 'Habitability|Ocean Worlds'): ").strip()
        if term:
            mask = self.df_text['text'].str.contains(term, case=False, regex=True)
            hits = self.df_text[mask]
            print(f"\n [+] Search '{term}' impacts -> {len(hits)} pages.")
            if not hits.empty:
                print(f" [+] Density Mode (Peak Pages): {hits['page'].mode().tolist()}")
                self.search_logs.append({"Term": term, "Pages_Affected": len(hits), "Mode_Page": hits['page'].mode()[0]})
                
                if input("\n >>> Automatically Render Density Histogram to PDF? (y/n): ").strip().lower() == 'y':
                    fig, ax = plt.subplots(figsize=(10, 4))
                    sns.histplot(data=hits, x="page", bins=50, color='indigo', kde=True, ax=ax)
                    ax.set_title(f"Lexical Density: '{term}' ")
                    ax.set_xlabel("PDF Page Number")
                    sns.despine()
                    plt.tight_layout()
                    plt.savefig(self.out_dir / f"density_{term.replace(' ', '')[:15]}.pdf")
                    plt.close()
                    print(f" [SUCCESS] PDF Vector saved in the output directory.")
        input("\n [Press ENTER to return]")

    def menu_targets(self):
        self.header()
        if self.df_text is None: return
        print(" [ PARAMETRIC PROMINENCE MATRIX (TARGETS) ]\n")
        t_input = input(" Enter comma-separated Targets (e.g., Mars,Europa,Titan,Enceladus): ").strip()
        if t_input:
            targets = [x.strip() for x in t_input.split(",")]
            print(" Computing prominence spectrum...\n")
            counts = {t: self.df_text['text'].str.contains(t, case=False).sum() for t in targets}
            self.df_tc = pd.DataFrame(list(counts.items()), columns=["Target", "Mentions"]).sort_values("Mentions", ascending=False)
            
            print(self.df_tc.to_string(index=False))
            
            # --- NEW: Spearman Rho Validation Logic ---
            print("\n" + "-"*40)
            print(" [ CROSS-VALIDATION WITH BIBLIOMETRIC EVIDENCE ]")
            print(" Do you want to correlate these mentions with E(T) scores?")
            if input(" >>> Correlate with custom Evidence scores? (y/n): ").strip().lower() == 'y':
                ev_data = {}
                for t in targets:
                    try:
                        ev_data[t] = float(input(f" Enter Evidence Score E({t}) [0-1]: "))
                    except: ev_data[t] = 0.0
                
                self.df_tc['Evidence'] = self.df_tc['Target'].map(ev_data)
                from scipy.stats import spearmanr
                rho, p = spearmanr(self.df_tc['Mentions'], self.df_tc['Evidence'])
                print(f"\n [+] Spearman's Rho: {rho:.4f} (p-value: {p:.4f})")
                stat = "Strong Alignment" if rho > 0.7 else ("Decoupled Priorities" if rho < 0.3 else "Moderate Tracking")
                print(f" [+] Diagnostic: {stat}")
            # ------------------------------------------

            if input("\n >>> Export Corporative Graphical Plots? (y/n): ").strip().lower() == 'y':
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(data=self.df_tc, x="Target", y="Mentions", palette="magma", ax=ax, hue="Target", legend=False)
                ax.set_title("Parametric Prevalence of the Base Target Environment")
                sns.despine()
                plt.tight_layout()
                plt.savefig(self.out_dir / "target_prominence.pdf")
                plt.close()
                print(" [SUCCESS] Matrix rendering complete.")
        input("\n [Press ENTER to return]")

    def menu_export(self):
        self.header()
        print(" Assembling Markdown Master Report...")
        with open(self.out_dir / "Decadal_NLP_Master_Report.md", "w", encoding="utf-8") as f:
            f.write("# Analytical Extract and Automatic Document Processing (PDF NLP)\n\n")
            f.write("Underlying Tool: **Open Decadal Machine-Driven Framework**\n\n")
            if self.search_logs:
                f.write("## 1. Conceptual Saturation Log\n\n")
                f.write(pd.DataFrame(self.search_logs).to_markdown(index=False) + "\n\n")
            if not self.df_tc.empty:
                f.write("## 2. Empirical Astrobiological Weighting / Target Density\n\n")
                f.write(self.df_tc.to_markdown(index=False) + "\n\n")
            f.write("---\n*Top Tier 1 Astro-Architect | Open Science*")
        
        print("\n [SUCCESS] Static MD reports generated successfully.")
        input("\n [Press ENTER to continue]")

if __name__ == "__main__":
    DecadalNLPCLI().run()
