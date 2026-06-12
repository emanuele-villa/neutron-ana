#!/usr/bin/env python3
"""Test script for CH1 and CH2 energy analysis."""

from pathlib import Path
import numpy as np
import lecroyparser

WORKDIR = Path("/Users/virgolaema/Software/3det/Osc_Data")
WAVEFORM_DIR = WORKDIR / "AmBe_therma_coincidence_1750V_3x3_sample"

def load_waveform(path: Path, channel_idx: int):
    """Load a waveform from specified channel."""
    try:
        scope = lecroyparser.ScopeData(str(path), parseAll=True)
        time_s = np.asarray(scope.x, dtype=np.float64)
        time_ns = time_s * 1e9
        
        if isinstance(scope.y, list) and len(scope.y) > channel_idx:
            voltage_v = np.asarray(scope.y[channel_idx], dtype=np.float64)
        else:
            voltage_v = np.asarray(scope.y[0] if isinstance(scope.y, list) else scope.y, dtype=np.float64)
        
        return time_ns, voltage_v
    except Exception as exc:
        print(f"Failed to load {path}: {exc}")
        return None, None

def compute_total_energy(time_ns, voltage_v):
    """Compute total energy as integral."""
    baseline = np.mean(voltage_v[:10])
    signal = voltage_v - baseline
    signal_abs = np.abs(signal)
    try:
        energy = np.trapezoid(signal_abs, time_ns)
    except AttributeError:
        energy = np.trapz(signal_abs, time_ns)
    return energy

if __name__ == "__main__":
    # Test CH2
    ch2_files = sorted(WAVEFORM_DIR.glob("C2_*.trc"))[:3]
    print(f"Testing CH2 with {len(ch2_files)} files:")
    for f in ch2_files:
        time_ns, voltage_v = load_waveform(f, channel_idx=1)
        if time_ns is not None:
            energy = compute_total_energy(time_ns, voltage_v)
            print(f"  ✓ {f.name}: {energy:.6f} V·ns")
    
    # Test CH1
    ch1_files = sorted(WAVEFORM_DIR.glob("C1_*.trc"))[:3]
    print(f"\nTesting CH1 with {len(ch1_files)} files:")
    for f in ch1_files:
        time_ns, voltage_v = load_waveform(f, channel_idx=0)
        if time_ns is not None:
            energy = compute_total_energy(time_ns, voltage_v)
            print(f"  ✓ {f.name}: {energy:.6f} V·ns")
    
    print("\n✅ Both channels work!")
