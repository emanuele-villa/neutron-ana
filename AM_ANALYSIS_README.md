# Americium-241 (Am-241) Waveform Analysis

## Overview
The notebook `Am.ipynb` (also saved as `Am_analysis.ipynb`) analyzes waveforms from Am-241 measurements.

## What Was Fixed

### Original Issues:
1. ❌ Used `lecroyparser.TRC` (doesn't exist)
2. ❌ Incorrect API calls
3. ❌ No waveform plotting functionality
4. ❌ Baseline calculation used full waveform mean (incorrect)

### Fixed Version:
1. ✅ Uses correct `lecroyparser.ScopeData` with `parseAll=True`
2. ✅ Proper time conversion (seconds → nanoseconds)
3. ✅ Baseline from first 10 samples only
4. ✅ Complete waveform plotting with multiple views

## Notebook Structure

### 1. Configuration
- Data directory: `/Users/virgolaema/Software/3det/Osc_Data/Am24_251212`
- Configurable max events and sample plot count

### 2. File Loading
- Finds all `.trc` files in the specified directory
- Shows file count and examples

### 3. Energy Calculation
- Loads waveforms using proper lecroyparser API
- Computes baseline from first 10 samples
- Integrates baseline-subtracted absolute signal
- Returns energy in V·ns (volt-nanoseconds)

### 4. Energy Distribution Plot
- Histogram of all energy values
- Log scale y-axis for better visibility
- Statistics box (mean, std, median)
- Green color scheme for Am-241

### 5. Sample Waveform Plots
- Individual plots for N sample waveforms (default: 10)
- Shows evenly spaced samples across dataset
- Displays:
  - Full waveform trace
  - Baseline (red dashed line)
  - Peak location (red dot)
  - Energy and peak voltage in title

### 6. Overlaid Waveforms
- Up to 50 waveforms overlaid with transparency
- Visualizes pulse shape consistency
- Good for identifying anomalies

### 7. Data Export
- Saves all energies to CSV file
- Includes filename and energy for each event

## Output Files

1. `am241_energy_distribution.png` - Energy histogram
2. `am241_sample_waveforms.png` - Individual waveform plots
3. `am241_overlaid_waveforms.png` - Overlaid waveforms
4. `am241_energy_data.csv` - Energy data table

## Usage

1. Open `Am.ipynb` in Jupyter
2. Adjust configuration in first cell if needed:
   - `max_analyzed_events`: Limit number of files (-1 = all)
   - `n_sample_plots`: Number of waveforms to plot individually
3. Run all cells in order

## Am-241 Physics Notes

Americium-241 is an alpha emitter:
- Primary alpha: 5.486 MeV (84.8%)
- Secondary alpha: 5.443 MeV (13.1%)
- Also emits 59.5 keV gamma rays

The waveforms show the detector response to these emissions.

## Requirements
- Python 3.8+
- lecroyparser
- numpy
- pandas
- matplotlib
