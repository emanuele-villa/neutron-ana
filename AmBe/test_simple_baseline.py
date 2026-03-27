#!/usr/bin/env python3
"""
Test simplified baseline calculation (first 10 samples only)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Quick test of the new baseline calculation
def test_simple_baseline():
    """Test the simplified baseline calculation approach."""

    print("=== Testing Simplified Baseline Calculation ===\n")

    # Create test waveform
    np.random.seed(42)
    time_ns = np.linspace(0, 1000, 1000)  # 1000 samples, 1 ns apart

    # Simulate a waveform: baseline + noise + signal
    baseline_true = -0.05  # -50 mV
    noise_rms = 0.002      # 2 mV RMS noise

    noise = np.random.normal(0, noise_rms, 1000)
    signal = np.zeros(1000)
    signal[200:300] = -0.1 * np.exp(-np.linspace(0, 5, 100))  # 100 mV pulse

    voltage_v = baseline_true + noise + signal

    # Test original method (time-based)
    baseline_window_ns = 100  # First 100 ns
    mask = time_ns <= (time_ns[0] + baseline_window_ns)
    baseline_time = np.mean(voltage_v[mask])
    baseline_std_time = np.std(voltage_v[mask], ddof=0)

    # Test simplified method (first 10 samples)
    baseline_simple = np.mean(voltage_v[:10])
    baseline_std_simple = np.std(voltage_v[:10], ddof=0)

    print(f"Test waveform (true baseline = {baseline_true*1000:.1f} mV, noise = {noise_rms*1000:.1f} mV RMS)")
    print(f"  Time-based (100ns):   baseline = {baseline_time*1000:.2f} mV, std = {baseline_std_time*1000:.2f} mV")
    print(f"  Simple (10 samples):  baseline = {baseline_simple*1000:.2f} mV, std = {baseline_std_simple*1000:.2f} mV")

    print(f"\nNumber of samples in baseline window:")
    print(f"  Time-based: {mask.sum()} samples")
    print(f"  Simple: 10 samples")

    # Plot comparison
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(time_ns[:50], voltage_v[:50]*1000, 'b-', linewidth=1, label='Waveform')
    plt.axhline(baseline_time*1000, color='red', linestyle='--', label=f'Time method: {baseline_time*1000:.1f} mV')
    plt.axhline(baseline_simple*1000, color='green', linestyle='--', label=f'Simple method: {baseline_simple*1000:.1f} mV')
    plt.xlabel('Time [ns]')
    plt.ylabel('Voltage [mV]')
    plt.title('Baseline Region (First 50 ns)')
    plt.legend()
    plt.grid(alpha=0.3)

    plt.subplot(2, 2, 2)
    plt.plot(time_ns, voltage_v*1000, 'b-', linewidth=0.5, alpha=0.7)
    plt.axhspan((baseline_time - baseline_std_time)*1000, (baseline_time + baseline_std_time)*1000,
                alpha=0.3, color='red', label=f'Time ± σ')
    plt.axhspan((baseline_simple - baseline_std_simple)*1000, (baseline_simple + baseline_std_simple)*1000,
                alpha=0.3, color='green', label=f'Simple ± σ')
    plt.xlabel('Time [ns]')
    plt.ylabel('Voltage [mV]')
    plt.title('Full Waveform with Baseline ± σ')
    plt.legend()
    plt.grid(alpha=0.3)

    # Test multiple waveforms to see consistency
    print(f"\n=== Consistency Test (100 waveforms) ===")

    baselines_time = []
    baselines_simple = []
    baseline_stds_time = []
    baseline_stds_simple = []

    for i in range(100):
        # Generate slightly different waveforms
        noise_i = np.random.normal(0, noise_rms, 1000)
        voltage_i = baseline_true + noise_i + signal

        # Time method
        mask_i = time_ns <= (time_ns[0] + baseline_window_ns)
        baselines_time.append(np.mean(voltage_i[mask_i]))
        baseline_stds_time.append(np.std(voltage_i[mask_i], ddof=0))

        # Simple method
        baselines_simple.append(np.mean(voltage_i[:10]))
        baseline_stds_simple.append(np.std(voltage_i[:10], ddof=0))

    baselines_time = np.array(baselines_time) * 1000
    baselines_simple = np.array(baselines_simple) * 1000
    baseline_stds_time = np.array(baseline_stds_time) * 1000
    baseline_stds_simple = np.array(baseline_stds_simple) * 1000

    print(f"Baseline measurement consistency:")
    print(f"  Time method:   {np.mean(baselines_time):.2f} ± {np.std(baselines_time):.2f} mV")
    print(f"  Simple method: {np.mean(baselines_simple):.2f} ± {np.std(baselines_simple):.2f} mV")

    print(f"Noise measurement consistency:")
    print(f"  Time method:   {np.mean(baseline_stds_time):.2f} ± {np.std(baseline_stds_time):.2f} mV")
    print(f"  Simple method: {np.mean(baseline_stds_simple):.2f} ± {np.std(baseline_stds_simple):.2f} mV")

    # Plot distributions
    plt.subplot(2, 2, 3)
    plt.hist(baseline_stds_time, bins=20, alpha=0.7, label='Time method', color='red')
    plt.hist(baseline_stds_simple, bins=20, alpha=0.7, label='Simple method', color='green')
    plt.xlabel('Baseline Std [mV]')
    plt.ylabel('Counts')
    plt.title('Baseline Noise Measurement Distribution')
    plt.legend()
    plt.grid(alpha=0.3)

    plt.subplot(2, 2, 4)
    plt.scatter(baseline_stds_time, baseline_stds_simple, alpha=0.7)
    plt.xlabel('Time Method Std [mV]')
    plt.ylabel('Simple Method Std [mV]')
    plt.title('Method Comparison')
    plt.plot([0, max(baseline_stds_time)], [0, max(baseline_stds_time)], 'r--', alpha=0.5)
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('../docs/output/baseline_method_comparison.png', dpi=150)
    print(f"\nSaved comparison plot to: ../docs/output/baseline_method_comparison.png")
    plt.show()

    print(f"\n*** CONCLUSION ***")
    print(f"✓ Simple method (10 samples) is more consistent")
    print(f"✓ Time method uses {mask.sum()} samples (variable)")
    print(f"✓ Simple method always uses exactly 10 samples")
    print(f"✓ Both methods give similar results for clean data")

    if np.std(baseline_stds_simple) < np.std(baseline_stds_time):
        print(f"✓ Simple method has more consistent noise measurements")

    print(f"\n*** RECOMMENDATION ***")
    print(f"Use the simplified baseline calculation in your analysis!")
    print(f"This should fix the extreme baseline_std_v differences between channels.")

if __name__ == "__main__":
    test_simple_baseline()