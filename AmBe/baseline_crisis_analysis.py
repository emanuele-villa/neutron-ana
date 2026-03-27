#!/usr/bin/env python3
"""
Focused Baseline Noise Analysis - The baseline_std_v issue is HUGE!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_baseline_issue():
    """Analyze the baseline noise issue that's clearly present."""

    df = pd.read_csv('../docs/output/neutron_capture_events.csv')

    print("=== BASELINE NOISE CRISIS ANALYSIS ===\n")

    # The shocking statistics
    ch1_noise = df['ch1_baseline_std_v'] * 1000  # Convert to mV
    ch2_noise = df['ch2_baseline_std_v'] * 1000  # Convert to mV

    print("*** BASELINE RMS NOISE COMPARISON ***")
    print(f"CH1 (Gamma):   {ch1_noise.mean():.1f} ± {ch1_noise.std():.1f} mV")
    print(f"CH2 (Neutron): {ch2_noise.mean():.2f} ± {ch2_noise.std():.2f} mV")
    print(f"RATIO (CH1/CH2): {ch1_noise.mean()/ch2_noise.mean():.0f}x worse!")

    # Check baseline levels
    ch1_baseline = df['ch1_baseline_v'] * 1000  # mV
    ch2_baseline = df['ch2_baseline_v'] * 1000  # mV

    print(f"\n*** BASELINE LEVELS ***")
    print(f"CH1 baseline: {ch1_baseline.mean():.1f} ± {ch1_baseline.std():.1f} mV")
    print(f"CH2 baseline: {ch2_baseline.mean():.1f} ± {ch2_baseline.std():.1f} mV")

    # Check signal levels
    ch1_amplitude = df['ch1_amplitude_v'] * 1000  # mV
    ch2_amplitude = df['ch2_amplitude_v'] * 1000  # mV

    print(f"\n*** SIGNAL AMPLITUDES ***")
    print(f"CH1 amplitude: {ch1_amplitude.mean():.0f} ± {ch1_amplitude.std():.0f} mV")
    print(f"CH2 amplitude: {ch2_amplitude.mean():.0f} ± {ch2_amplitude.std():.0f} mV")

    # Signal-to-noise ratios
    ch1_snr = ch1_amplitude.mean() / ch1_noise.mean()
    ch2_snr = ch2_amplitude.mean() / ch2_noise.mean()

    print(f"\n*** SIGNAL-TO-NOISE RATIOS ***")
    print(f"CH1 S/N: {ch1_snr:.1f}")
    print(f"CH2 S/N: {ch2_snr:.1f}")
    print(f"CH2 has {ch2_snr/ch1_snr:.0f}x better S/N ratio!")

    # Create diagnostic plots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Baseline noise comparison
    axes[0,0].hist(ch1_noise, bins=50, alpha=0.7, label=f'CH1: {ch1_noise.mean():.1f} mV', color='red')
    axes[0,0].hist(ch2_noise, bins=50, alpha=0.7, label=f'CH2: {ch2_noise.mean():.2f} mV', color='green')
    axes[0,0].set_xlabel('Baseline RMS Noise [mV]')
    axes[0,0].set_ylabel('Counts')
    axes[0,0].set_title('Baseline Noise Distribution\n*** CH1 has 100x worse noise! ***')
    axes[0,0].legend()
    axes[0,0].set_xlim(0, 20)  # Zoom in to see CH2
    axes[0,0].grid(alpha=0.3)

    # 2. Baseline levels over time
    axes[0,1].plot(ch1_baseline, 'b-', alpha=0.3, linewidth=0.5, label='CH1')
    axes[0,1].plot(ch2_baseline, 'g-', alpha=0.7, linewidth=0.5, label='CH2')
    axes[0,1].set_xlabel('Event Number')
    axes[0,1].set_ylabel('Baseline Level [mV]')
    axes[0,1].set_title('Baseline Drift Over Time')
    axes[0,1].legend()
    axes[0,1].grid(alpha=0.3)

    # 3. Noise vs signal amplitude
    axes[1,0].scatter(ch1_amplitude, ch1_noise, alpha=0.3, s=1, color='red', label='CH1')
    axes[1,0].scatter(ch2_amplitude, ch2_noise, alpha=0.7, s=2, color='green', label='CH2')
    axes[1,0].set_xlabel('Signal Amplitude [mV]')
    axes[1,0].set_ylabel('Baseline Noise [mV]')
    axes[1,0].set_title('Noise vs Signal Level')
    axes[1,0].legend()
    axes[1,0].grid(alpha=0.3)

    # 4. S/N ratio comparison
    ch1_individual_snr = ch1_amplitude / ch1_noise
    ch2_individual_snr = ch2_amplitude / ch2_noise

    axes[1,1].hist(ch1_individual_snr, bins=50, alpha=0.7, label=f'CH1: {ch1_individual_snr.mean():.1f}', color='red')
    axes[1,1].hist(ch2_individual_snr, bins=50, alpha=0.7, label=f'CH2: {ch2_individual_snr.mean():.0f}', color='green')
    axes[1,1].set_xlabel('Signal-to-Noise Ratio')
    axes[1,1].set_ylabel('Counts')
    axes[1,1].set_title('S/N Ratio Distribution')
    axes[1,1].legend()
    axes[1,1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('../docs/output/baseline_crisis_analysis.png', dpi=150, bbox_inches='tight')
    print(f"\nSaved plot to: ../docs/output/baseline_crisis_analysis.png")
    plt.show()

    # Diagnosis
    print(f"\n" + "="*60)
    print("DIAGNOSIS: Why is baseline_std_v discriminative?")
    print("="*60)

    # Check if noise correlates with baseline level (suggesting baseline subtraction issues)
    corr_ch1 = np.corrcoef(ch1_baseline, ch1_noise)[0,1]
    corr_ch2 = np.corrcoef(ch2_baseline, ch2_noise)[0,1]

    print(f"Correlation (baseline level vs noise):")
    print(f"  CH1: {corr_ch1:.3f}")
    print(f"  CH2: {corr_ch2:.3f}")

    # Check baseline variation vs noise
    baseline_var_ch1 = ch1_baseline.std()
    avg_noise_ch1 = ch1_noise.mean()
    baseline_var_ch2 = ch2_baseline.std()
    avg_noise_ch2 = ch2_noise.mean()

    print(f"\nBaseline variation vs noise level:")
    print(f"  CH1: baseline_std={baseline_var_ch1:.1f} mV, noise_rms={avg_noise_ch1:.1f} mV")
    print(f"  CH2: baseline_std={baseline_var_ch2:.2f} mV, noise_rms={avg_noise_ch2:.2f} mV")

    print(f"\n*** PROBABLE CAUSES ***")
    print(f"1. CH1 electronics have ~100x worse noise than CH2")
    print(f"2. CH1 may have grounding/shielding issues")
    print(f"3. CH1 baseline subtraction may not be working properly")
    print(f"4. CH1 detector/PMT may have different characteristics")

    print(f"\n*** WHY baseline_std_v IS DISCRIMINATIVE ***")
    print(f"✓ CH1 and CH2 have fundamentally different noise signatures")
    print(f"✓ Your ML sees the huge noise difference between channels")
    print(f"✓ This helps classify which detector fired (not physics!)")

    # Check if this affects energy calibration
    print(f"\n*** IMPACT ON ENERGY CALIBRATION ***")
    charge_precision_ch1 = ch1_noise.mean() * 1e-3 * 60e-9  # noise[V] * integration_time[s]
    charge_precision_ch2 = ch2_noise.mean() * 1e-3 * 60e-9

    print(f"Charge measurement precision:")
    print(f"  CH1: ~{charge_precision_ch1*1e12:.1f} pV·s")
    print(f"  CH2: ~{charge_precision_ch2*1e12:.2f} pV·s")
    print(f"  CH1 charge precision is {charge_precision_ch1/charge_precision_ch2:.0f}x worse!")

if __name__ == "__main__":
    analyze_baseline_issue()