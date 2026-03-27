#!/usr/bin/env python3
"""
Quick fix for machine learning notebook - use main events file instead of missing shape features file
"""

print("""
=== FIX for Machine Learning Notebook ===

The notebook is trying to load: '../docs/output/ch2_waveform_shape_features.csv'
But this file doesn't exist.

SOLUTION: Replace this in your notebook:
""")

print("CHANGE THIS:")
print("""
# Load waveform shape features
df_shape = pd.read_csv(RESULTS_DIR / 'ch2_waveform_shape_features.csv')
""")

print("TO THIS:")
print("""
# Load all events and create features
df_events = pd.read_csv(RESULTS_DIR / 'two_channel_no_saturation.csv')

# Create binary labels: neutron (delta_t > 20) vs gamma (delta_t <= 20)
df_events['is_neutron'] = (df_events['delta_t_ns'] > 20).astype(int)

print(f"Loaded {len(df_events)} events:")
print(f"  Neutron events: {df_events['is_neutron'].sum()}")
print(f"  Gamma events: {len(df_events) - df_events['is_neutron'].sum()}")

# Define features for BDT (similar to what you had)
feature_columns = [
    'ch2_baseline_std_v',    # Baseline noise
    'ch2_amplitude_v',       # Peak amplitude
    'ch2_charge_v_s',        # Integrated charge
    'delta_t_ns',            # Time-of-flight (most important!)
    'ch1_baseline_std_v',    # CH1 baseline noise
    'ch1_amplitude_v',       # CH1 amplitude
    'ch1_charge_v_s',        # CH1 charge
    'ch2_baseline_v'         # Baseline level
]

# Extract features and labels
X = df_events[feature_columns].copy()
y = df_events['is_neutron'].copy()

print(f"\\nFeature matrix shape: {X.shape}")
print(f"Feature names: {feature_columns}")
""")

print("\nThis will:")
print("✓ Use the existing events file")
print("✓ Create proper neutron/gamma labels using Δt > 20 ns cut")
print("✓ Define 8 key features for BDT analysis")
print("✓ Make your notebook work immediately")

print("\nThen the feature separation grid will show you visually which features discriminate best!")