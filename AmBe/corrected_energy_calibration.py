#!/usr/bin/env python3
"""
CORRECTED Energy Calibration - Compton Edge Method

Demonstrates the CORRECT physics-based calibration for gamma detection
in scintillators using Compton scattering theory.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def compton_edge_keV(gamma_energy_keV):
    """Calculate Compton edge for given gamma energy."""
    E_gamma = gamma_energy_keV
    m_e_c2 = 511.0  # keV

    E_max = E_gamma * (2 * E_gamma / m_e_c2) / (1 + 2 * E_gamma / m_e_c2)
    return E_max

def corrected_calibration_demo():
    """Demonstrate the correct energy calibration using Compton edge."""

    print("=== CORRECTED Energy Calibration: Compton Edge Method ===\n")

    # Load your actual neutron data
    csv_path = Path("../docs/output/neutron_capture_events.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        neutron_charges_vs = df['ch2_charge_v_s'].values  # Already in V⋅s
        neutron_charges_nVs = neutron_charges_vs * 1e9    # Convert to nV⋅s for display

        print("Loaded your actual neutron capture data:")
        print(f"  Number of events: {len(neutron_charges_vs)}")
        print(f"  Charge range: {np.min(neutron_charges_nVs):.2f} - {np.max(neutron_charges_nVs):.2f} nV·s")
        print(f"  Median: {np.median(neutron_charges_nVs):.2f} nV·s")
        print(f"  95th percentile: {np.percentile(neutron_charges_nVs, 95):.2f} nV·s")
        print(f"  99th percentile: {np.percentile(neutron_charges_nVs, 99):.2f} nV·s\n")
    else:
        print("Could not find neutron data CSV. Using simulated data.\n")
        # Simulate realistic Compton spectrum
        np.random.seed(42)
        # Exponential-like distribution (typical for Compton)
        neutron_charges_nVs = np.random.exponential(0.4, 2000)
        neutron_charges_nVs = neutron_charges_nVs[neutron_charges_nVs < 3.0]  # Cut high tail
        neutron_charges_vs = neutron_charges_nVs * 1e-9

    # Physics calculation
    gamma_energy = 478  # keV
    compton_edge = compton_edge_keV(gamma_energy)

    print(f"Physics of {gamma_energy} keV gamma in scintillator:")
    print(f"  Compton edge (max energy): {compton_edge:.0f} keV")
    print(f"  Expected spectrum: 0 to {compton_edge:.0f} keV continuum")
    print(f"  Shape: Exponential falloff (most events low energy)\n")

    # CORRECT calibration using Compton edge
    max_charge_nVs = np.percentile(neutron_charges_nVs, 99)  # 99th percentile
    corrected_calibration = compton_edge / max_charge_nVs

    print(f"CORRECT Calibration (Compton Edge Method):")
    print(f"  99th percentile charge: {max_charge_nVs:.2f} nV·s")
    print(f"  Compton edge energy: {compton_edge:.0f} keV")
    print(f"  Calibration factor: {corrected_calibration:.0f} keV/nV·s")

    # WRONG calibration for comparison
    median_charge_nVs = np.median(neutron_charges_nVs)
    wrong_calibration = gamma_energy / median_charge_nVs

    print(f"\nWRONG Calibration (Previous Method):")
    print(f"  Median charge: {median_charge_nVs:.2f} nV·s")
    print(f"  Assumed full energy: {gamma_energy} keV")
    print(f"  Wrong calibration: {wrong_calibration:.0f} keV/nV·s\n")

    # Energy interpretation with correct calibration
    median_energy_correct = median_charge_nVs * corrected_calibration
    mean_energy_correct = np.mean(neutron_charges_nVs) * corrected_calibration
    max_energy_correct = max_charge_nVs * corrected_calibration

    print(f"Energy interpretation (CORRECT):")
    print(f"  Median event: {median_charge_nVs:.2f} nV·s → {median_energy_correct:.0f} keV")
    print(f"  Mean event: {np.mean(neutron_charges_nVs):.2f} nV·s → {mean_energy_correct:.0f} keV")
    print(f"  Max events: {max_charge_nVs:.2f} nV·s → {max_energy_correct:.0f} keV (Compton edge)")

    # Create comparison plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Your charge distribution
    ax1.hist(neutron_charges_nVs, bins=50, alpha=0.7, edgecolor='black', color='green')
    ax1.axvline(median_charge_nVs, color='blue', linestyle='--', linewidth=2,
                label=f'Median: {median_charge_nVs:.2f} nV·s')
    ax1.axvline(max_charge_nVs, color='red', linestyle='--', linewidth=2,
                label=f'99th %ile: {max_charge_nVs:.2f} nV·s')
    ax1.set_xlabel('Charge [nV·s]')
    ax1.set_ylabel('Counts')
    ax1.set_title('Your Neutron Capture Data\n(Raw Charge Distribution)')
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 2. Correct energy spectrum
    energies_correct = neutron_charges_nVs * corrected_calibration
    ax2.hist(energies_correct, bins=50, alpha=0.7, edgecolor='black', color='green')
    ax2.axvline(median_energy_correct, color='blue', linestyle='--', linewidth=2,
                label=f'Median: {median_energy_correct:.0f} keV')
    ax2.axvline(compton_edge, color='red', linestyle='--', linewidth=2,
                label=f'Compton edge: {compton_edge:.0f} keV')
    ax2.set_xlabel('Energy [keV]')
    ax2.set_ylabel('Counts')
    ax2.set_title('CORRECT Energy Spectrum\n(Compton Edge Calibration)')
    ax2.legend()
    ax2.grid(alpha=0.3)

    # 3. Wrong energy spectrum (for comparison)
    energies_wrong = neutron_charges_nVs * wrong_calibration
    ax3.hist(energies_wrong, bins=50, alpha=0.5, edgecolor='black', color='red')
    ax3.axvline(gamma_energy, color='red', linestyle='--', linewidth=2,
                label=f'Wrong "peak": {gamma_energy} keV')
    ax3.set_xlabel('Energy [keV]')
    ax3.set_ylabel('Counts')
    ax3.set_title('WRONG Energy Spectrum\n(Median = 478 keV Method)')
    ax3.legend()
    ax3.grid(alpha=0.3)

    # 4. Theoretical Compton spectrum
    theory_energies = np.linspace(0, 400, 1000)
    # Simplified Klein-Nishina cross-section shape
    compton_theory = np.where(theory_energies <= compton_edge,
                             np.exp(-theory_energies/80), 0)  # Exponential falloff
    compton_theory = compton_theory / np.max(compton_theory)

    ax4.plot(theory_energies, compton_theory, 'b-', linewidth=2, label='Theory')
    ax4.axvline(compton_edge, color='red', linestyle='--', linewidth=2,
                label=f'Compton edge: {compton_edge:.0f} keV')
    ax4.fill_between(theory_energies, compton_theory, alpha=0.3, color='blue')
    ax4.set_xlabel('Energy [keV]')
    ax4.set_ylabel('Relative probability')
    ax4.set_title('Theoretical Compton Spectrum\n(478 keV gamma)')
    ax4.legend()
    ax4.grid(alpha=0.3)
    ax4.set_xlim(0, 400)

    plt.tight_layout()

    # Save plot
    output_path = Path("../docs/output/corrected_energy_calibration.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved comparison plots to: {output_path}")
    plt.close()

    print("\n" + "="*70)
    print("KEY PHYSICS INSIGHTS:")
    print("="*70)
    print("✓ Median energy should be MUCH LESS than photon energy")
    print("✓ Maximum energy should equal Compton edge (~312 keV)")
    print("✓ Most events are forward scattering (low energy)")
    print("✓ Few events are backscattering (high energy)")
    print("✓ NO events should exceed Compton edge")
    print("\n✓ Your observation that median ≠ 478 keV was CORRECT!")
    print("✓ The endpoint (99th percentile) should be used for calibration")

    return corrected_calibration, compton_edge

if __name__ == "__main__":
    corrected_calibration_demo()