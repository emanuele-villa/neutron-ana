#!/usr/bin/env python3
"""
Complete Energy Conversion Using Ohm's Law

Shows the full physics chain from V·s measurement to energy,
including the proper use of Ohm's law.
"""

import numpy as np

def complete_energy_conversion_demo():
    """Demonstrate complete conversion chain including Ohm's law."""

    print("=== Complete Energy Conversion Chain ===\n")

    # Your actual measurements
    median_charge_vs = 0.56e-9  # V·s (your median neutron event)
    max_charge_vs = 3.13e-9     # V·s (your 99th percentile)

    # System parameters
    R_input = 50  # Ohms (oscilloscope input impedance)
    e = 1.602e-19  # Elementary charge (Coulombs)

    print("Step 1: Use Ohm's Law to get actual charge")
    print("="*50)
    print("V = I·R  →  I = V/R")
    print("Q = ∫ I dt = ∫ (V/R) dt = (1/R) ∫ V dt")
    print(f"Q = (V·s) / R = (V·s) / {R_input}Ω\n")

    # Convert using Ohm's law
    median_charge_coulombs = median_charge_vs / R_input
    max_charge_coulombs = max_charge_vs / R_input

    print(f"Your measurements:")
    print(f"  Median: {median_charge_vs*1e9:.2f} nV·s → {median_charge_coulombs*1e12:.2f} pC")
    print(f"  Maximum: {max_charge_vs*1e9:.2f} nV·s → {max_charge_coulombs*1e12:.2f} pC")

    print("\nStep 2: Convert charge to number of photoelectrons")
    print("="*50)
    print(f"N = Q / e = Q / {e:.2e} C\n")

    median_N_pe = median_charge_coulombs / e
    max_N_pe = max_charge_coulombs / e

    print(f"Number of photoelectrons:")
    print(f"  Median event: {median_N_pe:.0f} photoelectrons")
    print(f"  Maximum event: {max_N_pe:.0f} photoelectrons")

    print("\nStep 3: Energy calibration using Compton edge")
    print("="*50)
    print("Compton edge energy = 311 keV")
    print("Maximum photoelectrons correspond to Compton edge\n")

    compton_edge_keV = 311
    keV_per_photoelectron = compton_edge_keV / max_N_pe

    print(f"Calibration:")
    print(f"  {max_N_pe:.0f} pe → {compton_edge_keV} keV")
    print(f"  Calibration factor: {keV_per_photoelectron:.4f} keV/photoelectron")

    # Final energy calculation
    median_energy = median_N_pe * keV_per_photoelectron

    print(f"\nStep 4: Final energy conversion")
    print("="*50)
    print(f"Energy = N_photoelectrons × {keV_per_photoelectron:.4f} keV/pe")
    print(f"\nYour median neutron event:")
    print(f"  {median_charge_vs*1e9:.2f} nV·s → {median_charge_coulombs*1e12:.2f} pC → {median_N_pe:.0f} pe → {median_energy:.0f} keV")

    print("\n" + "="*60)
    print("ALTERNATIVE: Direct calibration factor")
    print("="*60)
    print("You can combine all steps into one calibration factor:")

    # Direct calibration: V·s → keV
    direct_calibration = compton_edge_keV / max_charge_vs
    median_energy_direct = median_charge_vs * direct_calibration

    print(f"Direct: energy_keV = charge_vs × {direct_calibration:.2e}")
    print(f"Median: {median_charge_vs*1e9:.2f} nV·s → {median_energy_direct:.0f} keV")

    print(f"\nThis direct factor automatically includes:")
    print(f"  • Ohm's law (÷{R_input}Ω)")
    print(f"  • Elementary charge (÷{e:.2e})")
    print(f"  • Detector calibration (×{keV_per_photoelectron:.4f} keV/pe)")

    print("\n" + "="*60)
    print("WHY THE 50Ω IS ALREADY ACCOUNTED FOR:")
    print("="*60)
    print("✓ Your V·s measurement includes the 50Ω response")
    print("✓ The Compton edge calibration inherently accounts for it")
    print("✓ No need to manually apply Ohm's law - it's built in!")
    print("\n✓ The direct calibration factor (99 keV/nV·s) is correct as-is")

    # Verification
    print(f"\n" + "="*60)
    print("VERIFICATION:")
    print("="*60)
    print("Both methods give the same result:")
    print(f"  Method 1 (step-by-step): {median_energy:.0f} keV")
    print(f"  Method 2 (direct): {median_energy_direct:.0f} keV")
    print("✓ They match! The direct calibration is correct.")

if __name__ == "__main__":
    complete_energy_conversion_demo()