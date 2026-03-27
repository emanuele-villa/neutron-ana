#!/usr/bin/env python3
"""
Baseline Noise Analysis

Analyze baseline_std_v distribution and check if baseline subtraction is being applied.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_baseline_noise():
    """Analyze baseline noise characteristics and baseline subtraction."""

    # Load the data
    csv_path = Path("../docs/output/neutron_capture_events.csv")

    if not csv_path.exists():
        print("Error: neutron_capture_events.csv not found")
        return

    df = pd.read_csv(csv_path)

    print("=== Baseline Noise RMS Analysis ===\n")

    # Basic statistics
    ch1_baseline_std = df['ch1_baseline_std_v']
    ch2_baseline_std = df['ch2_baseline_std_v']

    print(f"CH1 (Gamma) Baseline Noise:")
    print(f"  Mean: {ch1_baseline_std.mean()*1000:.2f} mV")
    print(f"  Std:  {ch1_baseline_std.std()*1000:.2f} mV")
    print(f"  Min:  {ch1_baseline_std.min()*1000:.2f} mV")
    print(f"  Max:  {ch1_baseline_std.max()*1000:.2f} mV")

    print(f"\nCH2 (Neutron) Baseline Noise:")
    print(f"  Mean: {ch2_baseline_std.mean()*1000:.2f} mV")
    print(f"  Std:  {ch2_baseline_std.std()*1000:.2f} mV")
    print(f"  Min:  {ch2_baseline_std.min()*1000:.2f} mV")
    print(f"  Max:  {ch2_baseline_std.max()*1000:.2f} mV")

    # Check if there's a significant difference
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(ch1_baseline_std, ch2_baseline_std)
    print(f"\nChannel comparison (t-test):")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {p_value:.2e}")
    if p_value < 0.001:
        print("  *** HIGHLY SIGNIFICANT difference between channels! ***")
    elif p_value < 0.05:
        print("  ** Significant difference between channels")
    else:
        print("  No significant difference between channels")

    # Create comprehensive noise plots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # 1. Noise distribution comparison
    axes[0,0].hist(ch1_baseline_std * 1000, bins=50, alpha=0.7, label='CH1 (Gamma)', color='blue')
    axes[0,0].hist(ch2_baseline_std * 1000, bins=50, alpha=0.7, label='CH2 (Neutron)', color='green')
    axes[0,0].set_xlabel('Baseline RMS Noise [mV]')
    axes[0,0].set_ylabel('Counts')
    axes[0,0].set_title('Baseline Noise Distribution')
    axes[0,0].legend()
    axes[0,0].grid(alpha=0.3)

    # 2. Noise vs amplitude (check correlation)
    axes[0,1].scatter(df['ch1_peak_amplitude_v'] * 1000, ch1_baseline_std * 1000,
                     alpha=0.3, s=1, color='blue', label='CH1')
    axes[0,1].scatter(df['ch2_peak_amplitude_v'] * 1000, ch2_baseline_std * 1000,
                     alpha=0.3, s=1, color='green', label='CH2')
    axes[0,1].set_xlabel('Peak Amplitude [mV]')
    axes[0,1].set_ylabel('Baseline RMS [mV]')
    axes[0,1].set_title('Noise vs Signal Amplitude')
    axes[0,1].legend()
    axes[0,1].grid(alpha=0.3)

    # 3. Noise vs time (event order)
    df['event_number'] = range(len(df))
    axes[0,2].scatter(df['event_number'], ch1_baseline_std * 1000,
                     alpha=0.3, s=1, color='blue', label='CH1')
    axes[0,2].scatter(df['event_number'], ch2_baseline_std * 1000,
                     alpha=0.3, s=1, color='green', label='CH2')
    axes[0,2].set_xlabel('Event Number (Time Order)')
    axes[0,2].set_ylabel('Baseline RMS [mV]')
    axes[0,2].set_title('Noise vs Time')
    axes[0,2].legend()
    axes[0,2].grid(alpha=0.3)

    # 4. Baseline mean vs std (check for offset issues)
    axes[1,0].scatter(df['ch1_baseline_v'] * 1000, ch1_baseline_std * 1000,
                     alpha=0.3, s=1, color='blue', label='CH1')
    axes[1,0].scatter(df['ch2_baseline_v'] * 1000, ch2_baseline_std * 1000,
                     alpha=0.3, s=1, color='green', label='CH2')
    axes[1,0].set_xlabel('Baseline Mean [mV]')
    axes[1,0].set_ylabel('Baseline RMS [mV]')
    axes[1,0].set_title('Baseline Mean vs RMS')
    axes[1,0].legend()
    axes[1,0].grid(alpha=0.3)

    # 5. Noise vs charge (important for calibration!)
    axes[1,1].scatter(df['ch1_charge_v_s'] * 1e12, ch1_baseline_std * 1000,
                     alpha=0.3, s=1, color='blue', label='CH1')
    axes[1,1].scatter(df['ch2_charge_v_s'] * 1e12, ch2_baseline_std * 1000,
                     alpha=0.3, s=1, color='green', label='CH2')
    axes[1,1].set_xlabel('Integrated Charge [pV·s]')
    axes[1,1].set_ylabel('Baseline RMS [mV]')
    axes[1,1].set_title('Noise vs Integrated Charge')
    axes[1,1].legend()
    axes[1,1].grid(alpha=0.3)

    # 6. Box plot comparison
    data_to_plot = [ch1_baseline_std * 1000, ch2_baseline_std * 1000]
    axes[1,2].boxplot(data_to_plot, labels=['CH1 (Gamma)', 'CH2 (Neutron)'])
    axes[1,2].set_ylabel('Baseline RMS [mV]')
    axes[1,2].set_title('Channel Noise Comparison')
    axes[1,2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('../docs/output/baseline_noise_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved plot to: ../docs/output/baseline_noise_analysis.png")
    plt.show()

    # Calculate correlations
    print(f"\n=== Correlation Analysis ===")
    correlations = [
        ("CH1 noise vs amplitude", np.corrcoef(df['ch1_peak_amplitude_v'], ch1_baseline_std)[0,1]),
        ("CH2 noise vs amplitude", np.corrcoef(df['ch2_peak_amplitude_v'], ch2_baseline_std)[0,1]),
        ("CH1 noise vs charge", np.corrcoef(df['ch1_charge_v_s'], ch1_baseline_std)[0,1]),
        ("CH2 noise vs charge", np.corrcoef(df['ch2_charge_v_s'], ch2_baseline_std)[0,1]),
        ("CH1 noise vs baseline", np.corrcoef(df['ch1_baseline_v'], ch1_baseline_std)[0,1]),
        ("CH2 noise vs baseline", np.corrcoef(df['ch2_baseline_v'], ch2_baseline_std)[0,1]),
    ]

    for name, corr in correlations:
        print(f"  {name}: {corr:.3f}")
        if abs(corr) > 0.3:
            print(f"    *** STRONG CORRELATION! This suggests systematic effects ***")

    # Check baseline subtraction question
    print(f"\n" + "="*60)
    print("CRITICAL QUESTION: Is baseline subtraction being applied?")
    print("="*60)

    print("Looking at your data characteristics:")
    print(f"  CH1 baseline mean: {df['ch1_baseline_v'].mean()*1000:.2f} ± {df['ch1_baseline_v'].std()*1000:.2f} mV")
    print(f"  CH2 baseline mean: {df['ch2_baseline_v'].mean()*1000:.2f} ± {df['ch2_baseline_v'].std()*1000:.2f} mV")
    print(f"  Peak amplitudes: {df['ch1_peak_amplitude_v'].mean()*1000:.0f} mV (CH1), {df['ch2_peak_amplitude_v'].mean()*1000:.0f} mV (CH2)")

    # Check if baseline variation is large compared to noise
    baseline_variation_ch1 = df['ch1_baseline_v'].std()
    baseline_variation_ch2 = df['ch2_baseline_v'].std()
    avg_noise_ch1 = ch1_baseline_std.mean()
    avg_noise_ch2 = ch2_baseline_std.mean()

    print(f"\n  Baseline variation vs noise:")
    print(f"    CH1: baseline_std = {baseline_variation_ch1*1000:.2f} mV, noise_rms = {avg_noise_ch1*1000:.2f} mV")
    print(f"    CH2: baseline_std = {baseline_variation_ch2*1000:.2f} mV, noise_rms = {avg_noise_ch2*1000:.2f} mV")

    if baseline_variation_ch1 > 2*avg_noise_ch1 or baseline_variation_ch2 > 2*avg_noise_ch2:
        print(f"\n  *** WARNING: Baseline variation >> noise RMS ***")
        print(f"  *** This suggests baseline subtraction may NOT be applied! ***")
        print(f"  *** Baseline offsets are contaminating your measurements! ***")
    else:
        print(f"\n  ✓ Baseline variation ~ noise level (baseline subtraction likely working)")


if __name__ == "__main__":
    analyze_baseline_noise()