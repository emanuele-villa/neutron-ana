#!/usr/bin/env python3
"""
BDT Feature Separation Analysis

Create comprehensive plots showing how well each feature separates
neutron vs gamma events for visual inspection.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import roc_curve, auc
import seaborn as sns

def create_feature_separation_plots():
    """Create grid of plots showing BDT feature separation."""

    # Load the neutron capture events (these are the "neutron" class)
    neutron_file = Path("../docs/output/neutron_capture_events.csv")
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

    # Extract features from CH2 (neutron detector) - the key discriminating features
    feature_map = {
        'ch2_baseline_std_v': 'Baseline Noise [mV]',
        'ch2_amplitude_v': 'Amplitude [mV]',
        'ch2_charge_v_s': 'Charge [nV·s]',
        'delta_t_ns': 'Time-of-Flight [ns]',
        'ch2_baseline_v': 'Baseline Level [mV]',
        'ch1_amplitude_v': 'CH1 Amplitude [mV]',
        'ch1_charge_v_s': 'CH1 Charge [nV·s]',
        'ch1_baseline_std_v': 'CH1 Baseline Noise [mV]'
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

        # Calculate separation metric (Cohen's d)
        pooled_std = np.sqrt(((len(neutron_vals)-1)*neutron_std**2 +
                             (len(gamma_vals)-1)*gamma_std**2) /
                            (len(neutron_vals) + len(gamma_vals) - 2))
        cohens_d = abs(neutron_mean - gamma_mean) / pooled_std

        # Calculate ROC AUC for this feature
        try:
            fpr, tpr, _ = roc_curve(df_all['is_neutron'], feature_values)
            roc_auc = auc(fpr, tpr)
        except:
            roc_auc = 0.5

        separation_stats.append({
            'Feature': feature_name,
            'Cohens_d': cohens_d,
            'ROC_AUC': roc_auc,
            'Neutron_mean': neutron_mean,
            'Gamma_mean': gamma_mean,
            'Separation': 'Good' if cohens_d > 0.5 else 'Poor'
        })

        # Create overlaid histograms
        bins = 50
        alpha = 0.6

        ax.hist(gamma_vals, bins=bins, alpha=alpha, color=colors[0],
               label=f'{labels[0]} (n={len(gamma_vals)})', density=True)
        ax.hist(neutron_vals, bins=bins, alpha=alpha, color=colors[1],
               label=f'{labels[1]} (n={len(neutron_vals)})', density=True)

        # Add mean lines
        ax.axvline(gamma_mean, color=colors[0], linestyle='--', linewidth=2, alpha=0.8)
        ax.axvline(neutron_mean, color=colors[1], linestyle='--', linewidth=2, alpha=0.8)

        # Formatting
        ax.set_xlabel(feature_name)
        ax.set_ylabel('Density')
        ax.set_title(f'{feature_name}\nCohen\'s d = {cohens_d:.2f}, ROC AUC = {roc_auc:.3f}')
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)

        # Color-code title based on separation quality
        if cohens_d > 0.8:
            ax.title.set_color('green')  # Excellent separation
        elif cohens_d > 0.5:
            ax.title.set_color('orange')  # Good separation
        else:
            ax.title.set_color('red')     # Poor separation

    # Remove empty subplots
    for i in range(n_features, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    plt.savefig('../docs/output/bdt_feature_separation_grid.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved feature separation grid to: ../docs/output/bdt_feature_separation_grid.png")
    plt.show()

    # Create summary table
    separation_df = pd.DataFrame(separation_stats)
    separation_df = separation_df.sort_values('Cohens_d', ascending=False)

    print(f"\n=== Feature Separation Analysis ===")
    print(f"{'Feature':<25} {'Cohen d':<10} {'ROC AUC':<10} {'Quality':<10}")
    print("-" * 60)

    for _, row in separation_df.iterrows():
        quality = "★★★" if row['Cohens_d'] > 0.8 else "★★☆" if row['Cohens_d'] > 0.5 else "★☆☆"
        print(f"{row['Feature']:<25} {row['Cohens_d']:<10.2f} {row['ROC_AUC']:<10.3f} {quality:<10}")

    # Create correlation matrix
    print(f"\n=== Feature Correlation Analysis ===")

    feature_matrix = pd.DataFrame(feature_data)
    feature_matrix['is_neutron'] = df_all['is_neutron']

    corr_matrix = feature_matrix.corr()

    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": .8})
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig('../docs/output/feature_correlation_matrix.png', dpi=150, bbox_inches='tight')
    print(f"Saved correlation matrix to: ../docs/output/feature_correlation_matrix.png")
    plt.show()

    # Highlight key findings
    print(f"\n=== Key Findings ===")

    best_feature = separation_df.iloc[0]
    worst_feature = separation_df.iloc[-1]

    print(f"🏆 Best discriminating feature: {best_feature['Feature']} (d={best_feature['Cohens_d']:.2f})")
    print(f"❌ Worst discriminating feature: {worst_feature['Feature']} (d={worst_feature['Cohens_d']:.2f})")

    # Check if ToF is the best (as expected)
    tof_row = separation_df[separation_df['Feature'] == 'Time-of-Flight [ns]']
    if len(tof_row) > 0:
        tof_cohen = tof_row.iloc[0]['Cohens_d']
        if tof_cohen > 2.0:
            print(f"✓ Time-of-Flight has excellent separation (d={tof_cohen:.2f}) - as expected!")
        else:
            print(f"⚠ Time-of-Flight separation lower than expected (d={tof_cohen:.2f})")

    # Check baseline noise issue
    baseline_features = separation_df[separation_df['Feature'].str.contains('Baseline Noise')]
    if len(baseline_features) > 0:
        for _, row in baseline_features.iterrows():
            if row['Cohens_d'] > 1.0:
                print(f"⚠ {row['Feature']} is highly discriminative (d={row['Cohens_d']:.2f}) - hardware issue!")

    return separation_df

if __name__ == "__main__":
    create_feature_separation_plots()