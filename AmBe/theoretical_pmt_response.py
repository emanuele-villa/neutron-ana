#!/usr/bin/env python3
"""
Theoretical PMT Response Calculation

Estimates expected charge output from a typical 10cm PMT
for neutron capture gamma detection.
"""

def theoretical_pmt_response():
    print("=== Theoretical 10cm PMT Response ===\n")

    # Typical 10cm PMT parameters (e.g., Hamamatsu R7081)
    quantum_efficiency = 0.25      # 25% at peak wavelength
    collection_efficiency = 0.80   # 80% light collection
    pmt_gain = 1e6                 # 10^6 typical gain
    scintillator_light_yield = 10  # photons/keV (organic scintillator)

    # Neutron capture physics
    gamma_energy = 478  # keV
    compton_edge = 311  # keV (calculated earlier)

    print("Typical 10cm PMT parameters:")
    print(f"  Quantum efficiency: {quantum_efficiency*100:.0f}%")
    print(f"  Collection efficiency: {collection_efficiency*100:.0f}%")
    print(f"  PMT gain: {pmt_gain:.0e}")
    print(f"  Scintillator light yield: {scintillator_light_yield} photons/keV")
    print()

    # Calculation for Compton edge (maximum energy deposition)
    print("For Compton edge energy deposition:")
    print(f"  Energy deposited: {compton_edge} keV")

    photons_produced = compton_edge * scintillator_light_yield
    print(f"  Scintillation photons: {photons_produced:.0f}")

    photoelectrons = photons_produced * quantum_efficiency * collection_efficiency
    print(f"  Photoelectrons at photocathode: {photoelectrons:.0f}")

    total_electrons = photoelectrons * pmt_gain
    print(f"  Total electrons after multiplication: {total_electrons:.2e}")

    # Convert to charge
    e = 1.602e-19  # Elementary charge
    charge_coulombs = total_electrons * e
    print(f"  Output charge: {charge_coulombs*1e12:.1f} pC")

    # Convert to V·s at 50Ω
    R = 50  # Ohms
    charge_vs = charge_coulombs * R
    print(f"  At 50Ω input: {charge_vs*1e9:.1f} nV·s")

    print(f"\nComparison with your data:")
    measured_99th = 3.13  # nV·s from user's data
    print(f"  Theoretical prediction: {charge_vs*1e9:.1f} nV·s")
    print(f"  Your measured 99th %ile: {measured_99th:.1f} nV·s")
    print(f"  Ratio (measured/theory): {measured_99th/(charge_vs*1e9):.1f}")

    if 0.5 <= measured_99th/(charge_vs*1e9) <= 2.0:
        print("  ✓ Excellent agreement! PMT assumptions are reasonable.")
    else:
        print("  ⚠ Significant difference - PMT parameters may differ.")

    return charge_vs * 1e9  # Return in nV·s

if __name__ == "__main__":
    theoretical_pmt_response()