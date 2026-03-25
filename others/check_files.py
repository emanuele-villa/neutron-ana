#!/usr/bin/env python3
"""
Check what's actually in the LeCroy files.
"""
import lecroyparser
from pathlib import Path

# Load a sample file pair
ch1_file = Path("~/Software/3det/Osc_Data/AmBe_therma_coincidence_1750V_3x3_sample/C1_00000.trc").expanduser()
ch2_file = Path("~/Software/3det/Osc_Data/AmBe_therma_coincidence_1750V_3x3_sample/C2_00000.trc").expanduser()

print("Investigating C1_00000.trc:")
print("-" * 60)
scope1 = lecroyparser.ScopeData(str(ch1_file), parseAll=True)
print(f"  Type of scope.y: {type(scope1.y)}")
print(f"  Length of scope.y: {len(scope1.y)}")
if isinstance(scope1.y, list):
    print(f"  Number of channels in file: {len(scope1.y)}")
    for i, ch in enumerate(scope1.y):
        print(f"    Channel {i}: {len(ch)} samples, first 5 values: {ch[:5]}")

print("\nInvestigating C2_00000.trc:")
print("-" * 60)
scope2 = lecroyparser.ScopeData(str(ch2_file), parseAll=True)
print(f"  Type of scope.y: {type(scope2.y)}")
print(f"  Length of scope.y: {len(scope2.y)}")
if isinstance(scope2.y, list):
    print(f"  Number of channels in file: {len(scope2.y)}")
    for i, ch in enumerate(scope2.y):
        print(f"    Channel {i}: {len(ch)} samples, first 5 values: {ch[:5]}")

# Check if they're different
if isinstance(scope1.y, list) and isinstance(scope2.y, list):
    if len(scope1.y[0]) == len(scope2.y[0]):
        import numpy as np
        ch1_data = np.array(scope1.y[0])
        ch2_data = np.array(scope2.y[0])

        if np.allclose(ch1_data, ch2_data):
            print("\n❌ ERROR: C1 and C2 files contain IDENTICAL data!")
        else:
            print("\n✓ C1 and C2 files contain DIFFERENT data")
            print(f"  Max difference: {np.max(np.abs(ch1_data - ch2_data))}")
