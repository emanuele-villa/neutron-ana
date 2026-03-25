# Neutron-Gamma Coincidence Analysis

Two-channel neutron-gamma coincidence analysis using AmBe source and borated scintillator detectors.

## Quick Start

1. **Environment setup:**
   ```bash
   source ~/Software/neutron-env/bin/activate  # Or your preferred virtual env
   ```

2. **Run analysis notebooks in order:**
   - `01_basic_analysis.ipynb` - Time-of-flight and charge analysis
   - `02_pulse_shape_analysis.ipynb` - PSD feature extraction
   - `03_physics_background.ipynb` - Background investigation
   - `04_machine_learning.ipynb` - BDT and supervised learning
   - `05_unsupervised_analysis.ipynb` - Clustering and dimensionality reduction

## Analysis Overview

### Key Results
- **Primary discriminator:** Time-of-flight (Δt > 20 ns) → 21.1% neutron capture efficiency
- **Pulse shape discrimination:** Limited (AUC ~0.65) due to physics constraints
- **Background source:** Pair production from 4.4 MeV gammas creates 511 keV background
- **Machine learning:** BDT provides marginal improvement (AUC ~0.68)
- **Unsupervised learning:** No natural n/γ clustering found

### Physics Understanding
- **Signal:** 478 keV γ from thermal neutron capture (n + ¹⁰B → ⁷Li + α + γ)
- **Background:** 511 keV γ from e⁺ annihilation (4.4 MeV γ → pair production)
- **Challenge:** Similar energies (478 vs 511 keV) make discrimination difficult

## File Structure

```
neutron-ana/
├── 01_basic_analysis.ipynb           # TOF, charge, basic characterization
├── 02_pulse_shape_analysis.ipynb     # PSD feature extraction, ROC analysis
├── 03_physics_background.ipynb       # Amplitude analysis, pair production
├── 04_machine_learning.ipynb         # BDT, feature importance, supervised learning
├── 05_unsupervised_analysis.ipynb    # PCA, t-SNE, clustering
├── lib.py                            # Analysis functions library
├── output/                           # Generated plots and results
├── Summary.md                        # Comprehensive analysis summary
└── README.md                         # This file
```

## Dependencies

```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
scikit-learn>=1.0.0
scipy>=1.7.0
lecroyparser
```

Install with: `pip install -r requirements.txt`

## Data

- **Source:** AmBe neutron source (4.4 MeV γ + neutrons)
- **Detectors:** CH1 (standard scintillator), CH2 (borated scintillator)
- **Format:** LeCroy .trc oscilloscope files
- **Dataset:** 2000 waveform pairs, 1655 after saturation filtering

## Analysis Methods

1. **Time-of-Flight:** Δt = T₀_CH2 - T₀_CH1 (primary neutron ID)
2. **Pulse Shape Discrimination:** 6 shape parameters extracted per waveform
3. **Machine Learning:** Gradient boosting with 8 features
4. **Physics Analysis:** Energy spectrum analysis for background identification
5. **Unsupervised Learning:** PCA, t-SNE, clustering for natural separation

## Key Findings

- **TOF cut (Δt > 20 ns) is essential and sufficient** for neutron identification
- **Pair production background** explains why PSD discrimination is weak
- **Machine learning confirms** rather than improves upon traditional methods
- **Physics understanding** more valuable than complex algorithms

See `Summary.md` for complete analysis details and interpretation.

---

## Legacy Information

Original 3DET project data is in `/eos/user/e/evilla/3det/` (contact `emanuele.villa@cern.ch` for access).
Current analysis focuses on AmBe coincidence measurements with borated scintillator detectors.