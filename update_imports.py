#!/usr/bin/env python3
"""
Update imports in notebook to include create_analysis_report.
"""
import json

notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Find the import cell (should be cell 1)
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code' and 'from lib import' in ''.join(cell['source']):
        # Update the imports
        cell['source'] = [
            "# Import analysis functions from lib\n",
            "from lib import (\n",
            "    TwoChannelConfig, Waveform, TwoChannelEvent,\n",
            "    find_channel_pairs, load_waveform,\n",
            "    analyze_channel, analyze_pair,\n",
            "    plot_stacked_waveforms, plot_pair_comparison,\n",
            "    plot_waveform_with_features, extract_waveform_shape_features,\n",
            "    create_analysis_report\n",
            ")\n"
        ]
        print(f"✓ Updated imports in cell {i}")
        break

# Save
with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print("✓ Notebook imports updated to include create_analysis_report")
