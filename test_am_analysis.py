#!/usr/bin/env python3
"""Test Am-241 analysis."""

from pathlib import Path
import numpy as np
import lecroyparser

WORKDIR = Path("/Users/virgolaema/Software/3det/Osc_Data")
WAVEFORM_DIR = WORKDIR / "Am24_251212"

def load_waveform(file_path):
    try:
        scope = lecroyparser.ScopeData(str(file_path), parseAll=True)
        time_s = np.asarray(scope.x, dtype=np.float64)
        time_ns = time_s * 1e9
        if isinstance(scope.y, list) and len(scope.y) > 0:
            voltage_v = np.asarray(scope.y[0], dtype=np.float64)
        else:
            voltage_v = np.asarray(scope.y, dtype=np.float64)
        return time_ns, voltage_v
    except Exception as exc:
        print(f"Failed: {exc}")
        return None, None

def compute_total_energy(time_ns, voltage_v):
    baseline = np.mean(voltage_v[:10])
    signal = voltage_v - baseline
    signal_abs = np.abs(signal)
    try:
        energy = np.trapezoid(signal_abs, time_ns)
    except AttributeError:
        energy = np.trapz(signal_abs, time_ns)
    return energy

if __name__ == "__main__":
    print(f"Testing Am-241 analysis...")
    print(f"Data directory: {WAVEFORM_DIR}")
    
    # Find files
    files = sorted(WAVEFORM_DIR.glob("*.trc"))[:5]
    print(f"Found {len(files)} test files\n")
    
    for f in files:
        time_ns, voltage_v = load_waveform(f)
        if time_ns is not None:
            energy = compute_total_energy(time_ns, voltage_v)
            peak_v = voltage_v.min() if voltage_v.min() < voltage_v[0] else voltage_v.max()
            print(f"✓ {f.name}")
            print(f"  Energy: {energy:.6f} V·ns")
            print(f"  Peak: {peak_v:.6f} V")
            print(f"  Samples: {len(voltage_v)}")
    
    print("\n✅ Test complete!")
