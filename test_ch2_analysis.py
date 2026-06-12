#!/usr/bin/env python3
"""
Test script for CH2 energy analysis.
"""

from pathlib import Path
import numpy as np
import lecroyparser

# Configuration
WORKDIR = Path("/Users/virgolaema/Software/3det/Osc_Data")
WAVEFORM_DIR = WORKDIR / "AmBe_therma_coincidence_1750V_3x3_sample"

def load_ch2_waveform(path: Path):
    """Load a single CH2 waveform."""
    try:
        scope = lecroyparser.ScopeData(str(path), parseAll=True)
        time_s = np.asarray(scope.x, dtype=np.float64)
        time_ns = time_s * 1e9
        
        # CH2 files use channel 1 (index 1)
        if isinstance(scope.y, list) and len(scope.y) > 1:
            voltage_v = np.asarray(scope.y[1], dtype=np.float64)
        else:
            voltage_v = np.asarray(scope.y[0] if isinstance(scope.y, list) else scope.y, dtype=np.float64)
        
        return time_ns, voltage_v
    except Exception as exc:
        print(f"Failed to load {path}: {exc}")
        return None, None


def compute_total_energy(time_ns: np.ndarray, voltage_v: np.ndarray):
    """Compute total energy as integral."""
    baseline = np.mean(voltage_v[:10])
    signal = voltage_v - baseline
    signal_abs = np.abs(signal)
    # Use np.trapezoid (trapz is deprecated in newer numpy)
    try:
        energy = np.trapezoid(signal_abs, time_ns)
    except AttributeError:
        energy = np.trapz(signal_abs, time_ns)
    return energy


if __name__ == "__main__":
    # Find first 5 CH2 files
    ch2_files = sorted(WAVEFORM_DIR.glob("C2_*.trc"))[:5]
    print(f"Testing with {len(ch2_files)} CH2 files\n")
    
    for ch2_file in ch2_files:
        time_ns, voltage_v = load_ch2_waveform(ch2_file)
        
        if time_ns is None:
            print(f"❌ {ch2_file.name}: FAILED")
            continue
        
        energy = compute_total_energy(time_ns, voltage_v)
        print(f"✓ {ch2_file.name}: Energy = {energy:.6f} V·ns")
    
    print("\n✅ Test complete!")
