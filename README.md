# Neutron-Gamma Coincidence Analysis

Comprehensive analysis repository for neutron detection studies using various detector technologies and analysis approaches.

## Repository Structure

```
neutron-ana/
├── AmBe/                              # AmBe source coincidence analysis
│   ├── 01_basic_analysis.ipynb        # TOF, charge, basic characterization
│   ├── 02_pulse_shape_analysis.ipynb  # PSD feature extraction, ROC analysis
│   ├── 03_physics_background.ipynb    # Amplitude analysis, pair production
│   ├── 04_machine_learning.ipynb      # BDT, feature importance, supervised learning
│   ├── 05_unsupervised_analysis.ipynb # PCA, t-SNE, clustering
│   └── lib.py                         # Analysis functions library
├── docs/                              # Documentation and results
│   ├── Summary.md                     # Comprehensive analysis summary
│   └── output/                        # Generated plots and results
├── others/                            # Legacy analyses and utility scripts
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Setup Instructions

### 1. Clone Repository
```bash
git clone <repository-url>
cd neutron-ana
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv neutron-env

# Activate environment (Linux/Mac)
source neutron-env/bin/activate

# Activate environment (Windows)
neutron-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Register kernel for Jupyter (so notebooks use this kernel automatically)
pip install ipykernel
python -m ipykernel install --user --name neutron-env --display-name "Neutron Analysis"
```

### 3. Run Analysis

Navigate to the AmBe analysis directory and run notebooks in order:
```bash
cd AmBe/
jupyter notebook  # or jupyter lab
```

The notebooks are **automatically configured to use the `neutron-env` kernel**. When you open a notebook, it should prompt you to use the correct kernel. If not:
- Go to `Kernel` > `Change kernel` > Select `Neutron Analysis`
- Or ensure you created the kernel with: `python -m ipykernel install --user --name neutron-env --display-name "Neutron Analysis"`

**Execution order:**
1. `01_basic_analysis.ipynb` - Time-of-flight and charge analysis
2. `02_pulse_shape_analysis.ipynb` - PSD feature extraction
3. `03_physics_background.ipynb` - Background investigation
4. `04_machine_learning.ipynb` - BDT and supervised learning
5. `05_unsupervised_analysis.ipynb` - Clustering and dimensionality reduction

## AmBe Analysis Overview

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

### Data
- **Source:** AmBe neutron source (4.4 MeV γ + neutrons)
- **Detectors:** CH1 (standard scintillator), CH2 (borated scintillator)
- **Format:** LeCroy .trc oscilloscope files
- **Dataset:** 2000 waveform pairs, 1655 after saturation filtering

### Analysis Methods
1. **Time-of-Flight:** Δt = T₀_CH2 - T₀_CH1 (primary neutron ID)
2. **Pulse Shape Discrimination:** 6 shape parameters extracted per waveform
3. **Machine Learning:** Gradient boosting with 8 features
4. **Physics Analysis:** Energy spectrum analysis for background identification
5. **Unsupervised Learning:** PCA, t-SNE, clustering for natural separation

### Key Findings
- **TOF cut (Δt > 20 ns) is essential and sufficient** for neutron identification
- **Pair production background** explains why PSD discrimination is weak
- **Machine learning confirms** rather than improves upon traditional methods
- **Physics understanding** more valuable than complex algorithms

## Dependencies

Core packages (automatically installed with setup above):
```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
scikit-learn>=1.0.0
scipy>=1.7.0
lecroyparser
```

## Documentation

- **Complete analysis details:** `docs/Summary.md`
- **Generated plots and results:** `docs/output/`
- **Legacy notebooks:** `others/` directory

## Contributing

To add new analyses:
1. Create appropriate directory structure (e.g., `NewAnalysis/`)
2. Include analysis notebooks and supporting code
3. Update this README with overview
4. Add documentation to `docs/`

---

## Legacy Information

Original 3DET project data is in `/eos/user/e/evilla/3det/` (contact `emanuele.villa@cern.ch` for access).
Current repository focuses on neutron detection studies with various source and detector combinations.