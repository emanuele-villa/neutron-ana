#!/usr/bin/env python3
"""
Energy Calibration Example for Neutron-Gamma Coincidence Analysis

Demonstrates how to convert charge measurements (nV·s) to energy (keV) using:
1. 50Ω oscilloscope impedance
2. Neutron capture peak calibration (478 keV)
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import calibration functions
from lib import charge_to_energy_keV, calibrate_energy_from_neutron_peak

def main():
    """Demonstrate energy calibration using your neutron data."""

    # Example: Using your actual neutron measurements
    # From your analysis: Neutron capture events have median charge = 0.56 nV·s

    # Simulate example neutron capture charges (in V·s, not nV·s)
    example_neutron_charges_vs = np.array([
        0.56e-9,  # Median from your data
        0.86e-9,  # Mean from your data
        0.45e-9, 0.67e-9, 0.78e-9, 0.34e-9, 0.89e-9, 0.23e-9
    ])

    print("=== Energy Calibration for Neutron-Gamma Coincidence Analysis ===\n")

    # Step 1: Calculate calibration factor using neutron capture peak
    print("Step 1: Calculate calibration factor from neutron capture peak")
    print(f"Known neutron capture energy: 478 keV (B-10 capture)")

    calibration_factor = calibrate_energy_from_neutron_peak(
        neutron_charges_vs=example_neutron_charges_vs,
        neutron_peak_energy_keV=478.0
    )

    print(f"Average neutron charge: {np.mean(example_neutron_charges_vs)*1e9:.2f} nV·s")
    print(f"Calibration factor: {calibration_factor:.2e} keV per V·s")
    print(f"Calibration factor: {calibration_factor*1e-9:.2f} keV per nV·s\n")

    # Step 2: Convert charges to energies
    print("Step 2: Convert charge measurements to energy")
    print("Input impedance: 50Ω (standard oscilloscope)")

    energies_keV = [charge_to_energy_keV(charge, calibration_factor)
                   for charge in example_neutron_charges_vs]

    print("\nCharge → Energy conversion:")
    print("Charge [nV·s]  →  Energy [keV]")
    print("─────────────────────────────")
    for charge_vs, energy in zip(example_neutron_charges_vs, energies_keV):
        print(f"{charge_vs*1e9:8.2f}     →    {energy:6.1f}")

    print(f"\nMean energy: {np.mean(energies_keV):.1f} keV (should be ~478 keV)")

    # Step 3: Apply to your actual data
    print("\n" + "="*60)
    print("Step 3: Applying to your neutron capture data")
    print("="*60)

    # Using your actual statistics
    your_median_charge_nVs = 0.56  # nV·s from your analysis
    your_mean_charge_nVs = 0.86    # nV·s from your analysis

    # Convert to V·s for the function
    your_median_charge_vs = your_median_charge_nVs * 1e-9
    your_mean_charge_vs = your_mean_charge_nVs * 1e-9

    median_energy = charge_to_energy_keV(your_median_charge_vs, calibration_factor)
    mean_energy = charge_to_energy_keV(your_mean_charge_vs, calibration_factor)

    print(f"Your neutron capture data (Δt > 20 ns, n=2058 events):")
    print(f"  Median charge: {your_median_charge_nVs:.2f} nV·s → {median_energy:.1f} keV")
    print(f"  Mean charge:   {your_mean_charge_nVs:.2f} nV·s → {mean_energy:.1f} keV")

    # Step 4: Physics discussion
    print("\n" + "="*60)
    print("Physics Discussion")
    print("="*60)
    print("• Neutron capture: n + ¹⁰B → ⁷Li* + α + 2.31 MeV")
    print("• Gamma emission: ⁷Li* → ⁷Li + γ (478 keV)")
    print("• PMT detects scintillation light from Compton electrons")
    print("• Energy calibration accounts for:")
    print("  - Scintillator light yield (photons/keV)")
    print("  - PMT quantum efficiency")
    print("  - Collection efficiency")
    print("  - Electronic chain gain")
    print("\n• Typical energy resolution: 10-20% FWHM for organic scintillators")
    print(f"• Your calibration: {calibration_factor*1e-9:.2f} keV/nV·s")

    # Step 5: Create calibration plot
    print("\nCreating calibration plot...")

    # Generate charge range for plotting
    charge_range_nVs = np.linspace(0.1, 2.0, 100)  # nV·s
    charge_range_vs = charge_range_nVs * 1e-9       # V·s

    energy_range_keV = [charge_to_energy_keV(charge, calibration_factor)
                       for charge in charge_range_vs]

    plt.figure(figsize=(10, 6))
    plt.plot(charge_range_nVs, energy_range_keV, 'b-', linewidth=2,
             label='Calibration curve')

    # Mark your data points
    plt.scatter([your_median_charge_nVs], [median_energy],
               color='red', s=100, zorder=5,
               label=f'Your median: {your_median_charge_nVs:.2f} nV·s → {median_energy:.0f} keV')
    plt.scatter([your_mean_charge_nVs], [mean_energy],
               color='orange', s=100, zorder=5,
               label=f'Your mean: {your_mean_charge_nVs:.2f} nV·s → {mean_energy:.0f} keV')

    # Mark 478 keV line
    plt.axhline(478, color='green', linestyle='--', alpha=0.7,
                label='Expected neutron capture (478 keV)')

    plt.xlabel('Charge [nV·s]', fontsize=12)
    plt.ylabel('Energy [keV]', fontsize=12)
    plt.title('Energy Calibration for Borated Scintillator\n(50Ω impedance, 478 keV neutron capture)', fontsize=13)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Save plot
    output_dir = Path("../docs/output")
    output_dir.mkdir(exist_ok=True)
    plot_path = output_dir / "energy_calibration_example.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"Saved calibration plot to: {plot_path}")

    # plt.show()  # Uncomment to display
    plt.close()

    print("\n" + "="*60)
    print("Summary: How to use in your analysis")
    print("="*60)
    print("1. Import functions:")
    print("   from lib import charge_to_energy_keV, calibrate_energy_from_neutron_peak")
    print()
    print("2. Calculate calibration factor once:")
    print("   cal_factor = calibrate_energy_from_neutron_peak(neutron_charges_vs)")
    print()
    print("3. Convert any charge measurement:")
    print("   energy_keV = charge_to_energy_keV(charge_vs, cal_factor)")
    print()
    print("4. For your data (nV·s → keV):")
    print(f"   energy = charge_nVs * {calibration_factor*1e-9:.2f}")


if __name__ == "__main__":
    main()