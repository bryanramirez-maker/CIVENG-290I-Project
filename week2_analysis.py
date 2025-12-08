import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIGURATION ===
CSV_FILE = "week2_api_path_impact.csv"

def analyze_impact():
    # 1. Load Data
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find {CSV_FILE}. Run the impact script first!")
        return

    # 2. Filter out infinite values (disconnected paths) for plotting
    # We keep them for the "Top 10" list but exclude them from histograms
    df_clean = df[df['delta_m'] != float('inf')].copy()
    
    # 3. Find the "Top 10 Critical Edges" (Bottlenecks)
    # We sort by delta_m descending
    top_bottlenecks = df.sort_values(by='delta_m', ascending=False).head(10)
    
    print("\n=== TOP 10 CRITICAL EDGES (BOTTLENECKS) ===")
    print(top_bottlenecks[['s', 't', 'u', 'v', 'scenario', 'delta_m']])

    # 4. Compare Closure vs. Reversal
    # We pivot the table to compare scenarios side-by-side
    df_pivot = df.pivot_table(index=['u', 'v', 's', 't'], columns='scenario', values='delta_m').reset_index()
    
    if 'closure' in df_pivot.columns and 'reversal' in df_pivot.columns:
        df_pivot['diff'] = df_pivot['closure'] - df_pivot['reversal']
        better_reversals = df_pivot[df_pivot['diff'] > 0.1] # Tolerance for float math
        
        print("\n=== REVERSAL ANALYSIS ===")
        if len(better_reversals) == 0:
            print("Finding: 'Reversal' impact was IDENTICAL to 'Closure' impact for all tested edges.")
            print("Interpretation: Reversing the street direction provided NO relief compared to closing it.")
        else:
            print(f"Finding: In {len(better_reversals)} cases, Reversal was better than Closure.")
            print(better_reversals.head())

    # 5. Visualizations
    plt.figure(figsize=(14, 6))

    # Plot A: Histogram of Delays
    plt.subplot(1, 2, 1)
    sns.histplot(data=df_clean, x='delta_m', hue='scenario', kde=True, bins=20)
    plt.title('Distribution of Delays (Impact of Disruption)')
    plt.xlabel('Added Distance (meters)')
    plt.ylabel('Count of Edges')

    # Plot B: Impact by Baseline Path Length
    # Does disrupting a long trip cause more delay than a short trip?
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df_clean, x='baseline_m', y='delta_m', hue='scenario', style='scenario')
    plt.title('Baseline Trip Length vs. Impact Severity')
    plt.xlabel('Original Trip Length (m)')
    plt.ylabel('Added Delay (m)')

    plt.tight_layout()
    plt.savefig("week2_impact_analysis.png")
    print("\nAnalysis Complete! Plot saved as 'week2_impact_analysis.png'")
    plt.show()

if __name__ == "__main__":
    analyze_impact()
