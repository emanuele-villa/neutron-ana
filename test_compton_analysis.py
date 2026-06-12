#!/usr/bin/env python3
"""Test Compton analysis functions."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import lecroyparser
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
from scipy.special import erf

WORKDIR = Path("/Users/virgolaema/Software/3det/Osc_Data")
WAVEFORM_DIR = WORKDIR / "AmBe_therma_coincidence_1750V_3x3_sample"

def load_waveform(path, channel_idx):
    scope = lecroyparser.ScopeData(str(path), parseAll=True)
    time_s = np.asarray(scope.x, dtype=np.float64)
    time_ns = time_s * 1e9
    if isinstance(scope.y, list) and len(scope.y) > channel_idx:
        voltage_v = np.asarray(scope.y[channel_idx], dtype=np.float64)
    else:
        voltage_v = np.asarray(scope.y[0] if isinstance(scope.y, list) else scope.y, dtype=np.float64)
    return time_ns, voltage_v

def compute_total_energy(time_ns, voltage_v):
    baseline = np.mean(voltage_v[:10])
    signal = voltage_v - baseline
    signal_abs = np.abs(signal)
    try:
        energy = np.trapezoid(signal_abs, time_ns)
    except AttributeError:
        energy = np.trapz(signal_abs, time_ns)
    return energy

def compton_continuum(x, A, B, C, edge):
    return A * np.exp(-B * x) * (1 - 0.5 * (1 + erf((x - edge) / C)))

def find_compton_edge(energies, counts, energy_range=(2, 15)):
    mask = (energies >= energy_range[0]) & (energies <= energy_range[1])
    e_fit = energies[mask]
    c_fit = counts[mask]
    edge_guess = energy_range[0] + 0.65 * (energy_range[1] - energy_range[0])
    try:
        p0 = [np.max(c_fit), 0.3, 1.0, edge_guess]
        popt, _ = curve_fit(compton_continuum, e_fit, c_fit, p0=p0, maxfev=5000)
        return popt[3], popt
    except:
        derivative = np.gradient(c_fit, e_fit)
        edge_idx = np.argmin(derivative)
        return e_fit[edge_idx], None

def find_photopeak(energies, counts, energy_range=(8, 20)):
    mask = (energies >= energy_range[0]) & (energies <= energy_range[1])
    e_fit = energies[mask]
    c_fit = counts[mask]
    if len(c_fit) > 10:
        window = min(11, len(c_fit) if len(c_fit) % 2 == 1 else len(c_fit) - 1)
        c_smooth = savgol_filter(c_fit, window, 3)
    else:
        c_smooth = c_fit
    peaks, _ = find_peaks(c_smooth, prominence=np.max(c_smooth)*0.1, width=2)
    if len(peaks) > 0:
        highest_peak_idx = peaks[np.argmax(c_smooth[peaks])]
        return e_fit[highest_peak_idx], c_smooth[highest_peak_idx], None
    else:
        max_idx = np.argmax(c_fit)
        return e_fit[max_idx], c_fit[max_idx], None

if __name__ == "__main__":
    print("Testing Compton analysis with 100 CH1 files...")
    
    # Load CH1 data
    ch1_files = sorted(WAVEFORM_DIR.glob("C1_*.trc"))[:100]
    energies = []
    
    for f in ch1_files:
        time_ns, voltage_v = load_waveform(f, channel_idx=0)
        if time_ns is not None:
            energy = compute_total_energy(time_ns, voltage_v)
            energies.append(energy)
    
    energies = np.array(energies)
    print(f"Loaded {len(energies)} events")
    print(f"Energy range: {energies.min():.2f} - {energies.max():.2f} V·ns")
    
    # Create histogram
    counts, bin_edges = np.histogram(energies, bins=200, range=(0, 30))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Find Compton edge
    print("\nFinding Compton edge...")
    compton_edge, compton_params = find_compton_edge(bin_centers, counts, energy_range=(2, 12))
    print(f"✓ Compton edge: {compton_edge:.3f} V·ns")
    
    # Find photopeak
    print("\nFinding photoelectric peak...")
    photopeak_pos, photopeak_height, _ = find_photopeak(bin_centers, counts, energy_range=(8, 25))
    print(f"✓ Photopeak: {photopeak_pos:.3f} V·ns")
    print(f"✓ Peak height: {photopeak_height:.1f} counts")
    
    # Calculate ratio
    ratio = compton_edge / photopeak_pos
    print(f"\n✓ Compton/Photopeak ratio: {ratio:.3f}")
    
    print("\n✅ Compton analysis test complete!")
