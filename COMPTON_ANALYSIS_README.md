# CH1 and CH2 Energy Analysis with Compton Fitting

## Overview
The notebook `ch1_ch2_energy_analysis.ipynb` performs energy analysis on both CH1 and CH2 channels from coincidence measurements.

## Structure

### 1. Channel 2 (CH2) Analysis
- Loads all C2_*.trc files
- Computes total energy integrals (V·ns)
- Creates energy distribution histogram (log scale, blue)
- Saves results to `ch2_energy_data.csv`

### 2. Channel 1 (CH1) Analysis
- Loads all C1_*.trc files  
- Computes total energy integrals (V·ns)
- Creates energy distribution histogram (log scale, red)
- **Compton Edge and Photoelectric Peak Analysis:**
  - **Compton continuum fitting**: Fits exponential decay with error function edge
  - **Compton edge detection**: Identifies the maximum energy from Compton scattering
  - **Photoelectric peak identification**: Finds the full-energy absorption peak
  - **Gaussian fitting**: Fits Gaussian to photopeak for precise position
  - **Ratio calculation**: Computes Compton edge / Photopeak ratio
    - Theoretical range for single Compton scatter: ~0.66-0.75
- Saves results to `ch1_energy_data.csv` and `ch1_compton_analysis.json`

## Compton Analysis Details

### Physical Interpretation
For gamma-ray spectroscopy:
- **Compton Edge**: Maximum energy transfer in Compton scattering events
- **Photoelectric Peak**: Full energy deposition from photoelectric absorption
- The ratio provides information about the scattering characteristics

### Fitting Functions

1. **Compton Continuum Model**:
   ```
   f(E) = A * exp(-B*E) * [1 - 0.5*(1 + erf((E - E_edge)/C))]
   ```
   - A: Amplitude
   - B: Decay constant
   - C: Edge width
   - E_edge: Compton edge position

2. **Gaussian Photopeak Model**:
   ```
   f(E) = A * exp(-0.5*((E - μ)/σ)²)
   ```
   - A: Peak amplitude
   - μ: Peak position (energy)
   - σ: Peak width (energy resolution)

## Output Files

1. `ch2_energy_distribution.png` - CH2 histogram
2. `ch2_energy_data.csv` - CH2 energy values
3. `ch1_energy_distribution.png` - CH1 histogram
4. `ch1_compton_analysis.png` - CH1 with Compton edge and photopeak marked
5. `ch1_energy_data.csv` - CH1 energy values
6. `ch1_compton_analysis.json` - Compton analysis results (edge, peak, ratio)

## Usage

1. Set the data directory in the first cell:
   ```python
   WAVEFORM_DIR = WORKDIR / "AmBe_therma_coincidence_1750V_3x3_sample"
   ```

2. Set max_analyzed_events (-1 for all files, or a number to limit)

3. Run all cells in order

## Requirements
- lecroyparser
- numpy
- pandas
- matplotlib
- scipy
