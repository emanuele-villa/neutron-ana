# Two-Channel Neutron-Gamma Coincidence Analysis

## Overview

This analysis processes paired waveforms from a two-channel neutron-gamma coincidence detection system using an AmBe (Americium-Beryllium) neutron source with thermal neutron detection via boron-10 capture.

### Experimental Setup

| Channel | Detector | Signal Type | Purpose |
|---------|----------|-------------|---------|
| CH1 | Standard scintillator | Gamma | Prompt signal from AmBe source |
| CH2 | Borated scintillator | Neutron | Delayed signal from thermal neutron capture |

**Detection Mechanism:**
1. AmBe source emits neutrons + 4.4 MeV gamma (prompt)
2. Neutrons thermalize in moderator material
3. Thermal neutrons captured by B-10 in borated scintillator
4. Capture reaction: n + ¹⁰B → ⁷Li + α + γ (478 keV)

The **time-of-flight (Δt = T₀_CH2 - T₀_CH1)** between gamma and neutron signals is the primary discriminator.

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total waveform pairs** | 2000 |
| **After saturation filter** | 1655 |
| **Saturation rate** | 17.2% |
| **Files per channel** | 11,099 available |

### Data Source
- **Directory:** `/Users/virgolaema/Software/3det/Osc_Data/AmBe_therma_coincidence_1750V_3x3_sample/`
- **File format:** LeCroy oscilloscope .trc files
- **Naming convention:** `C1_XXXXX.trc` (gamma), `C2_XXXXX.trc` (neutron)

---

## Time-of-Flight Analysis

### Delta-t Distribution (All Non-Saturated Events)

| Statistic | Value |
|-----------|-------|
| Mean | -1.39 ns |
| Std Dev | 37.79 ns |
| Median | 2.10 ns |
| Range | [-123.54, 94.65] ns |

### Sign Convention
- **Δt > 0:** CH2 (neutron) arrives AFTER CH1 (gamma) → Expected for neutron capture
- **Δt < 0:** CH2 arrives BEFORE CH1 → Accidental coincidence

### Neutron Capture Selection (Δt > 20 ns)

| Metric | Value |
|--------|-------|
| **Events selected** | 349 |
| **Fraction of total** | 21.1% |
| **Mean Δt** | 48.58 ns |
| **Median Δt** | 46.93 ns |

The 20 ns threshold effectively separates thermal neutron capture events from prompt gamma coincidences.

![Delta-t Histogram](../Osc_Data/two_channel_neutron_gamma/delta_t_histogram.png)

---

## Charge Analysis

### CH2 (Neutron Channel) Charge Distribution

| Population | Median Charge |
|------------|---------------|
| All events | 0.679 nV·s |
| Neutron capture (Δt > 20 ns) | 0.542 nV·s |

**Observation:** Neutron capture events have slightly lower charge, consistent with the lower energy deposition from thermal neutron capture (~2.3 MeV total from Li + α) compared to higher-energy gamma interactions.

![Charge Distributions](../Osc_Data/two_channel_neutron_gamma/charge_distributions.png)

![Thermal Neutron Charge Spectrum](../Osc_Data/two_channel_neutron_gamma/thermal_neutron_charge_spectrum.png)

---

## Pulse Shape Discrimination (PSD) Analysis

### Shape Parameters Extracted

For each CH2 waveform, the following features were extracted:

1. **Rise time (10-90%)** - Time from 10% to 90% of peak amplitude
2. **Fall time (90-10%)** - Time from 90% to 10% after peak
3. **FWHM** - Full width at half maximum
4. **Peak amplitude** - Maximum signal height
5. **Charge asymmetry** - (Q_pre - Q_post) / Q_total
6. **Tail-to-peak ratio** - Charge in tail region / peak amplitude

### Shape Parameter Comparison: Neutron vs Gamma

| Parameter | Neutron Median | Gamma Median | Separation* |
|-----------|---------------|--------------|-------------|
| Rise time | 4.20 ns | 3.80 ns | 0.39 |
| Peak amplitude | 54.5 mV | 86.7 mV | 0.35 |
| Fall time | 11.0 ns | 10.2 ns | 0.28 |
| FWHM | 7.40 ns | 7.20 ns | 0.13 |
| Charge asymmetry | 0.375 | 0.384 | 0.07 |
| Tail-to-peak ratio | 0.0096 | 0.0077 | 0.01 |

*Separation = |median_diff| / pooled_std (higher = better discrimination)

![Shape Parameter Distributions](../Osc_Data/two_channel_neutron_gamma/ch2_shape_parameter_distributions.png)

![Shape Parameter Correlations](../Osc_Data/two_channel_neutron_gamma/ch2_shape_parameter_correlations.png)

### Discrimination Power (ROC-AUC Analysis)

| Parameter | AUC Score | Rating |
|-----------|-----------|--------|
| Rise time | 0.648 | Poor |
| Peak amplitude | 0.604 | Poor |
| Tail-to-peak ratio | 0.570 | None |
| FWHM | 0.565 | None |
| Fall time | 0.562 | None |
| Charge asymmetry | 0.543 | None |

**AUC Interpretation:**
- 0.5 = Random (no discrimination)
- 0.6-0.7 = Poor
- 0.7-0.8 = Fair
- 0.8-0.9 = Good
- \> 0.9 = Excellent

---

## Key Findings

### 1. Time-of-Flight is the Primary Discriminator

The Δt > 20 ns cut successfully identifies 349 neutron capture events (21.1% of non-saturated data). This leverages the fundamental physics:
- Prompt gamma → immediate CH1 signal
- Thermal neutron moderation (tens of ns) → delayed CH2 signal

### 2. Pulse Shape Discrimination is Weak

**All PSD parameters show AUC < 0.65, indicating poor standalone discrimination capability.**

Possible reasons:
- Both neutrons and gammas produce scintillation in CH2
- Pulse shapes are dominated by PMT/electronics response
- Thermal neutron capture signals overlap significantly with gamma signals in shape

### 3. Best PSD Indicators

If PSD is needed as supplementary discrimination:
1. **Rise time** (AUC = 0.648) - Neutrons have ~10% longer rise times
2. **Peak amplitude** (AUC = 0.604) - Neutrons tend to produce smaller pulses

### 4. Saturation Handling

17.2% of events show saturation in the neutron channel, properly filtered from analysis.

---

## Waveform Examples

### Stacked Waveforms

**CH1 (Gamma) - 2000 overlaid waveforms:**
![CH1 Stacked](../Osc_Data/two_channel_neutron_gamma/ch1_gamma_stacked.png)

**CH2 (Neutron) - 2000 overlaid waveforms:**
![CH2 Stacked](../Osc_Data/two_channel_neutron_gamma/ch2_neutron_stacked.png)

### Individual Pair Examples

![Pair Example 0](../Osc_Data/two_channel_neutron_gamma/pair_example_000.png)
![Pair Example 1](../Osc_Data/two_channel_neutron_gamma/pair_example_001.png)

### Feature Extraction Detail

![Feature Extraction](../Osc_Data/two_channel_neutron_gamma/ch2_shape_feature_extraction_details.png)

---

## Conclusions

1. **Time-of-flight analysis successfully identifies thermal neutron capture events** using a Δt > 20 ns cut, yielding 21.1% neutron capture fraction.

2. **Pulse shape discrimination provides minimal additional separation** (best AUC = 0.65). PSD alone cannot reliably distinguish neutrons from gammas in this borated scintillator system.

3. **Recommended analysis strategy:**
   - Primary selection: Δt > 20 ns time-of-flight cut
   - Secondary (optional): Rise time > 4 ns may slightly improve purity
   - Saturation filter: Exclude saturated events (17% of data)

4. **For improved PSD**, consider:
   - Higher sampling rate acquisition
   - Different scintillator materials with distinct n/γ pulse shapes
   - Longer integration windows for tail analysis

---

## Output Files

| File | Description |
|------|-------------|
| `two_channel_all_events.csv` | All 2000 analyzed event pairs |
| `two_channel_no_saturation.csv` | 1655 non-saturated events |
| `ch2_waveform_shape_features.csv` | Shape parameters for all events |
| `neutron_capture_events.csv` | Events passing Δt > 20 ns cut |
| `neutron_gamma_analysis_report.pdf` | PDF summary report |

---

## Code Structure

```
neutron-ana/
├── lib.py                                    # Analysis library
├── two_channel_neutron_gamma_analysis.ipynb  # Main analysis notebook
└── Summary.md                                # This file
```

### Key Functions in lib.py

- `find_channel_pairs()` - Match C1/C2 file pairs
- `load_waveform()` - Parse LeCroy .trc files (auto-detects channel)
- `analyze_pair()` - Extract timing and charge for a pair
- `extract_waveform_shape_features()` - PSD parameter extraction
- `create_analysis_report()` - Generate PDF report

---

*Analysis performed: March 2026*
*Data: AmBe thermal coincidence, 1750V, 3x3 sample*
