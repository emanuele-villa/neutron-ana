#!/usr/bin/env python3
"""Verify that waveforms are being loaded correctly."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import lecroyparser

WORKDIR = Path("/Users/virgolaema/Software/3det/Osc_Data")
WAVEFORM_DIR = WORKDIR / "Am24_251212"

def load_waveform(file_path):
    """Load waveform data."""
    scope = lecroyparser.ScopeData(str(file_path), parseAll=True)
    time_s = np.asarray(scope.x, dtype=np.float64)
    time_ns = time_s * 1e9
    
    if isinstance(scope.y, list) and len(scope.y) > 0:
        voltage_v = np.asarray(scope.y[0], dtype=np.float64)
    else:
        voltage_v = np.asarray(scope.y, dtype=np.float64)
    
    return time_ns, voltage_v

if __name__ == "__main__":
    # Load one file and inspect it
    files = sorted(WAVEFORM_DIR.glob("*.trc"))
    if not files:
        print("No files found!")
        exit(1)
    
    test_file = files[0]
    print(f"Testing file: {test_file.name}")
    print(f"Full path: {test_file}\n")
    
    time_ns, voltage_v = load_waveform(test_file)
    
    # Print detailed information
    print("=" * 60)
    print("WAVEFORM DATA VERIFICATION")
    print("=" * 60)
    print(f"\nTime array:")
    print(f"  Length: {len(time_ns)} samples")
    print(f"  Min: {time_ns.min():.3f} ns")
    print(f"  Max: {time_ns.max():.3f} ns")
    print(f"  Duration: {time_ns.max() - time_ns.min():.3f} ns")
    print(f"  Sampling interval: {np.mean(np.diff(time_ns)):.6f} ns")
    print(f"  First 5 values: {time_ns[:5]}")
    
    print(f"\nVoltage array:")
    print(f"  Length: {len(voltage_v)} samples")
    print(f"  Min: {voltage_v.min():.6f} V")
    print(f"  Max: {voltage_v.max():.6f} V")
    print(f"  Mean: {voltage_v.mean():.6f} V")
    print(f"  Std: {voltage_v.std():.6f} V")
    print(f"  First 10 values (baseline region): {voltage_v[:10]}")
    
    # Check if this looks like a real waveform
    baseline = np.mean(voltage_v[:10])
    peak_idx = np.argmin(np.abs(voltage_v - baseline))
    peak_deviation = voltage_v[peak_idx] - baseline
    
    print(f"\nWaveform characteristics:")
    print(f"  Baseline (first 10 samples): {baseline:.6f} V")
    print(f"  Peak index: {peak_idx}")
    print(f"  Peak value: {voltage_v[peak_idx]:.6f} V")
    print(f"  Peak deviation from baseline: {peak_deviation:.6f} V")
    
    # Look for a pulse
    signal = voltage_v - baseline
    max_positive = np.max(signal)
    max_negative = np.min(signal)
    
    print(f"\nSignal analysis (baseline subtracted):")
    print(f"  Max positive deviation: {max_positive:.6f} V")
    print(f"  Max negative deviation: {max_negative:.6f} V")
    
    if abs(max_negative) > abs(max_positive):
        print(f"  → NEGATIVE pulse detected (typical for PMT)")
    elif abs(max_positive) > abs(max_negative):
        print(f"  → POSITIVE pulse detected")
    else:
        print(f"  ⚠️  No clear pulse detected!")
    
    print("\n" + "=" * 60)
    print("VERDICT: ", end="")
    if abs(max_negative) > 0.001 or abs(max_positive) > 0.001:
        print("✅ This looks like REAL waveform data!")
    else:
        print("❌ This might be empty/flat data")
    print("=" * 60)
    
    # Create a quick plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Full waveform
    ax1.plot(time_ns, voltage_v, 'b-', linewidth=1, alpha=0.7)
    ax1.axhline(baseline, color='r', linestyle='--', label='Baseline')
    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title(f'Full Waveform: {test_file.name}')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Baseline-subtracted
    ax2.plot(time_ns, signal, 'g-', linewidth=1, alpha=0.7)
    ax2.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('Time (ns)')
    ax2.set_ylabel('Voltage - Baseline (V)')
    ax2.set_title('Baseline-Subtracted Signal')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('waveform_verification.png', dpi=150)
    print(f"\n📊 Verification plot saved to: waveform_verification.png")
    
    # Test multiple files
    print("\n" + "=" * 60)
    print("Testing first 5 files:")
    print("=" * 60)
    for i, f in enumerate(files[:5]):
        t, v = load_waveform(f)
        bl = np.mean(v[:10])
        sig = v - bl
        peak_neg = np.min(sig)
        peak_pos = np.max(sig)
        pulse_type = "NEG" if abs(peak_neg) > abs(peak_pos) else "POS"
        print(f"{i+1}. {f.name}: Baseline={bl:.6f}V, Peak={peak_neg if pulse_type=='NEG' else peak_pos:.6f}V [{pulse_type}]")
    
    print("\n✅ Waveform verification complete!")
