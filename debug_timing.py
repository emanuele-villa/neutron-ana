#!/usr/bin/env python3
"""
Investigate time differences in paired waveforms.
"""
import sys
sys.path.insert(0, '/Users/virgolaema/Software/3det/neutron-ana')

from pathlib import Path
import numpy as np
from lib import TwoChannelConfig, find_channel_pairs, load_waveform, analyze_pair

# Setup config
WAVEFORM_DIR = Path("~/Software/3det/Osc_Data/AmBe_therma_coincidence_1750V_3x3_sample").expanduser()
RESULTS_DIR = Path("~/Software/3det/Osc_Data/Analysis_results/debug").expanduser()

config = TwoChannelConfig(
    waveform_dir=WAVEFORM_DIR,
    results_dir=RESULTS_DIR,
    ch1_pattern="C1_",
    ch2_pattern="C2_",
    file_extension=".trc",
    baseline_window_ns=100.0,
    charge_window_ns=(20.0, 40.0),
    t0_threshold_fraction=0.5,
    t0_search_window_ns=100.0,
    pulse_polarity="negative",
    saturation_flatness_window_ns=10.0,
    saturation_tolerance_v=0.0015,
    saturation_fraction=0.3,
    saturation_min_consecutive=5,
    stack_plot_limit=50,
    stack_alpha=0.3,
    show_plots=False,
    max_pairs=10,
)

# Find pairs
pairs = find_channel_pairs(config)
print(f"Found {len(pairs)} pairs\n")

# Analyze first few pairs
print("Analyzing first 5 pairs:")
print("-" * 80)

for i, (ch1_path, ch2_path) in enumerate(pairs[:5]):
    print(f"\nPair {i}: {ch1_path.name} + {ch2_path.name}")

    # Load waveforms
    ch1_wf = load_waveform(ch1_path)
    ch2_wf = load_waveform(ch2_path)

    if ch1_wf is None or ch2_wf is None:
        print("  ERROR: Failed to load")
        continue

    # Check time ranges
    ch1_start = ch1_wf.time_ns[0]
    ch1_end = ch1_wf.time_ns[-1]
    ch2_start = ch2_wf.time_ns[0]
    ch2_end = ch2_wf.time_ns[-1]

    print(f"  CH1 time range: {ch1_start:.2f} ns to {ch1_end:.2f} ns")
    print(f"  CH2 time range: {ch2_start:.2f} ns to {ch2_end:.2f} ns")
    print(f"  Time offset between channels: {ch2_start - ch1_start:.2f} ns")

    # Analyze the pair
    try:
        event = analyze_pair(ch1_wf, ch2_wf, config, neutron_channel="ch2")
        print(f"  CH1 T0: {event.ch1_t0_ns:.2f} ns")
        print(f"  CH2 T0: {event.ch2_t0_ns:.2f} ns")
        print(f"  Delta T (CH2-CH1): {event.delta_t_ns:.2f} ns")
        print(f"  CH1 peak time: {event.ch1_peak_time_ns:.2f} ns")
        print(f"  CH2 peak time: {event.ch2_peak_time_ns:.2f} ns")
    except Exception as e:
        print(f"  ERROR during analysis: {e}")

print("\n" + "=" * 80)
print("Checking if files are actually from the same trigger...")
