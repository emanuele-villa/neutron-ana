#!/usr/bin/env python3
"""
BDT Feature Separation Analysis - Simple version without sklearn

Create comprehensive plots showing how well each feature separates
neutron vs gamma events for visual inspection.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def create_feature_separation_plots():
    """Create grid of plots showing BDT feature separation."""

    # Load all events
    all_events_file = Path("../docs/output/two_channel_no_saturation.csv")

    if not all_events_file.exists():
        print(f"Error: {all_events_file} not found")
        print("Run the basic analysis notebook first to generate the data")
        return

    # Load all events
    df_all = pd.read_csv(all_events_file)

    # Create binary classification: neutron (delta_t > 20) vs gamma (delta_t <= 20)
    df_all['is_neutron'] = (df_all['delta_t_ns'] > 20).astype(int)

    neutron_events = df_all[df_all['is_neutron'] == 1]
    gamma_events = df_all[df_all['is_neutron'] == 0]

    print(f"Loaded {len(df_all)} total events:")
    print(f"  Neutron events (Δt > 20 ns): {len(neutron_events)} ({100*len(neutron_events)/len(df_all):.1f}%)")
    print(f"  Gamma events (Δt ≤ 20 ns): {len(gamma_events)} ({100*len(gamma_events)/len(df_all):.1f}%)")

    # Define BDT features (the ones typically used in machine learning)
    feature_map = {
        'delta_t_ns': 'Time-of-Flight [ns]',
        'ch2_baseline_std_v': 'CH2 Baseline Noise [mV]',
        'ch2_amplitude_v': 'CH2 Amplitude [mV]',
        'ch2_charge_v_s': 'CH2 Charge [nV·s]',
        'ch1_baseline_std_v': 'CH1 Baseline Noise [mV]',
        'ch1_amplitude_v': 'CH1 Amplitude [mV]',
        'ch1_charge_v_s': 'CH1 Charge [nV·s]',
        'ch2_baseline_v': 'CH2 Baseline Level [mV]'
    }

    # Convert units for better visualization
    feature_data = {}
    for col, label in feature_map.items():
        if 'baseline_std_v' in col or 'amplitude_v' in col or 'baseline_v' in col:
            feature_data[label] = df_all[col] * 1000  # Convert to mV
        elif 'charge_v_s' in col:
            feature_data[label] = df_all[col] * 1e9   # Convert to nV·s
        else:
            feature_data[label] = df_all[col]         # Keep as is (ns)

    # Create comprehensive separation plots
    n_features = len(feature_data)
    n_cols = 3
    n_rows = int(np.ceil(n_features / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes

    colors = ['red', 'green']
    labels = ['Gamma (Δt ≤ 20ns)', 'Neutron (Δt > 20ns)']

    separation_stats = []

    for i, (feature_name, feature_values) in enumerate(feature_data.items()):
        ax = axes[i]

        # Get values for each class
        neutron_vals = feature_values[df_all['is_neutron'] == 1]
        gamma_vals = feature_values[df_all['is_neutron'] == 0]

        # Calculate statistics
        neutron_mean = neutron_vals.mean()
        neutron_std = neutron_vals.std()
        gamma_mean = gamma_vals.mean()
        gamma_std = gamma_vals.std()

        # Calculate separation metrics
        # Cohen's d (effect size)
        pooled_std = np.sqrt(((len(neutron_vals)-1)*neutron_std**2 +
                             (len(gamma_vals)-1)*gamma_std**2) /
                            (len(neutron_vals) + len(gamma_vals) - 2))
        cohens_d = abs(neutron_mean - gamma_mean) / pooled_std if pooled_std > 0 else 0

        # Simple separation ratio
        separation_ratio = abs(neutron_mean - gamma_mean) / (neutron_std + gamma_std) if (neutron_std + gamma_std) > 0 else 0

        # Overlap percentage (rough estimate)
        min_max_gamma = gamma_vals.min(), gamma_vals.max()
        min_max_neutron = neutron_vals.min(), neutron_vals.max()
        overlap_start = max(min_max_gamma[0], min_max_neutron[0])
        overlap_end = min(min_max_gamma[1], min_max_neutron[1])
        overlap_pct = max(0, overlap_end - overlap_start) / (max(min_max_gamma[1], min_max_neutron[1]) - min(min_max_gamma[0], min_max_neutron[0])) * 100

        separation_stats.append({
            'Feature': feature_name,
            'Cohens_d': cohens_d,
            'Separation_ratio': separation_ratio,
            'Overlap_pct': overlap_pct,
            'Neutron_mean': neutron_mean,
            'Gamma_mean': gamma_mean,
            'Quality': 'Excellent' if cohens_d > 1.0 else 'Good' if cohens_d > 0.5 else 'Poor'
        })

        # Create overlaid histograms
        bins = 50
        alpha = 0.6

        # Calculate proper bin range
        all_vals = np.concatenate([gamma_vals, neutron_vals])
        bins_range = (np.percentile(all_vals, 1), np.percentile(all_vals, 99))

        ax.hist(gamma_vals, bins=bins, alpha=alpha, color=colors[0],
               label=f'{labels[0]} (n={len(gamma_vals)})', density=True, range=bins_range)
        ax.hist(neutron_vals, bins=bins, alpha=alpha, color=colors[1],
               label=f'{labels[1]} (n={len(neutron_vals)})', density=True, range=bins_range)

        # Add mean lines
        ax.axvline(gamma_mean, color=colors[0], linestyle='--', linewidth=2, alpha=0.8)
        ax.axvline(neutron_mean, color=colors[1], linestyle='--', linewidth=2, alpha=0.8)

        # Formatting
        ax.set_xlabel(feature_name)
        ax.set_ylabel('Density')
        ax.set_title(f'{feature_name}\nCohen\'s d = {cohens_d:.2f}, Overlap = {overlap_pct:.1f}%')
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)

        # Color-code title based on separation quality
        if cohens_d > 1.0:
            ax.title.set_color('darkgreen')   # Excellent separation
        elif cohens_d > 0.5:
            ax.title.set_color('orange')      # Good separation
        else:
            ax.title.set_color('red')         # Poor separation

        # Add statistics text box
        stats_text = f'γ: {gamma_mean:.1f} ± {gamma_std:.1f}\nn: {neutron_mean:.1f} ± {neutron_std:.1f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=8,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Remove empty subplots
    for i in range(n_features, len(axes)):
        fig.delaxes(axes[i])

    plt.suptitle('BDT Feature Separation Analysis\n(Mouse vs Neutron-Gamma Discrimination)', fontsize=16)
    plt.tight_layout()
    plt.savefig('../docs/output/bdt_feature_separation_grid.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved feature separation grid to: ../docs/output/bdt_feature_separation_grid.png")
    plt.show()

    # Create summary table
    separation_df = pd.DataFrame(separation_stats)
    separation_df = separation_df.sort_values('Cohens_d', ascending=False)

    print(f"\n=== Feature Discrimination Power Ranking ===")
    print(f"{'Rank':<4} {'Feature':<25} {'Cohen d':<8} {'Quality':<12} {'Overlap %':<10}")
    print("-" * 70)

    for rank, (_, row) in enumerate(separation_df.iterrows(), 1):
        quality_symbol = "★★★" if row['Cohens_d'] > 1.0 else "★★☆" if row['Cohens_d'] > 0.5 else "★☆☆"
        print(f"{rank:<4} {row['Feature']:<25} {row['Cohens_d']:<8.2f} {quality_symbol:<12} {row['Overlap_pct']:<10.1f}")

    # Create simple correlation matrix (without seaborn)
    print(f"\n=== Feature Correlations ===")

    feature_matrix = pd.DataFrame(feature_data)
    feature_matrix['is_neutron'] = df_all['is_neutron']
    corr_matrix = feature_matrix.corr()

    # Simple correlation heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)

    # Add text annotations
    for i in range(len(corr_matrix.columns)):
        for j in range(len(corr_matrix.columns)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)

    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(corr_matrix.columns)
    ax.set_title('Feature Correlation Matrix')

    plt.colorbar(im, ax=ax, label='Correlation Coefficient')
    plt.tight_layout()
    plt.savefig('../docs/output/feature_correlation_matrix.png', dpi=150, bbox_inches='tight')
    print(f"Saved correlation matrix to: ../docs/output/feature_correlation_matrix.png")
    plt.show()

    # Key findings
    print(f"\n=== 🔍 Key Findings ===")

    best_feature = separation_df.iloc[0]
    worst_feature = separation_df.iloc[-1]

    print(f"🏆 Best discriminator: {best_feature['Feature']}")
    print(f"   Cohen's d = {best_feature['Cohens_d']:.2f}, Overlap = {best_feature['Overlap_pct']:.1f}%")

    print(f"❌ Worst discriminator: {worst_feature['Feature']}")
    print(f"   Cohen's d = {worst_feature['Cohens_d']:.2f}, Overlap = {worst_feature['Overlap_pct']:.1f}%")

    # Physics insights
    tof_row = separation_df[separation_df['Feature'] == 'Time-of-Flight [ns]']
    if len(tof_row) > 0:
        tof_cohen = tof_row.iloc[0]['Cohens_d']
        print(f"\n⚡ Time-of-Flight Analysis:")
        if tof_cohen > 2.0:
            print(f"   ✓ Excellent separation (d={tof_cohen:.2f}) - TOF is golden standard!")
        else:
            print(f"   ⚠ Lower separation than expected (d={tof_cohen:.2f})")

    # Baseline noise analysis
    baseline_features = separation_df[separation_df['Feature'].str.contains('Baseline Noise')]
    if len(baseline_features) > 0:
        print(f"\n🔊 Baseline Noise Analysis:")
        for _, row in baseline_features.iterrows():
            if row['Cohens_d'] > 1.0:
                print(f"   ⚠ {row['Feature']}: d={row['Cohens_d']:.2f} - Hardware discriminator!")
            else:
                print(f"   ✓ {row['Feature']}: d={row['Cohens_d']:.2f} - Normal noise level")

    print(f"\n💡 Interpretation Guide:")
    print(f"   Cohen's d > 1.0 = Large effect (excellent discrimination)")
    print(f"   Cohen's d > 0.5 = Medium effect (good discrimination)")
    print(f"   Cohen's d < 0.5 = Small effect (poor discrimination)")
    print(f"   Overlap % = How much the distributions overlap")

    return separation_df

if __name__ == "__main__":
    create_feature_separation_plots()