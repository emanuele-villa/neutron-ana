#!/usr/bin/env python3
import json

notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Find and fix the PDF report cell
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'create_analysis_report' in source and 'csv_results' in source:
            # Fix the cell to use correct CSV filename
            cell['source'] = [
                "# Generate comprehensive PDF report\n",
                "from lib import create_analysis_report\n",
                "\n",
                "# Define output path\n",
                "pdf_report_path = config.results_dir / \"neutron_gamma_analysis_report.pdf\"\n",
                "\n",
                "# Use the all events CSV file\n",
                "csv_results = config.results_dir / \"two_channel_all_events.csv\"\n",
                "\n",
                "if csv_results.exists():\n",
                "    print(f\"Creating PDF report from {csv_results}...\")\n",
                "    create_analysis_report(\n",
                "        csv_path=csv_results,\n",
                "        output_pdf=pdf_report_path,\n",
                "        waveform_dir=config.waveform_dir,\n",
                "        title=\"AmBe Thermal Neutron Coincidence Analysis\"\n",
                "    )\n",
                "    print(f\"\\n✓ PDF report saved to: {pdf_report_path}\")\n",
                "    print(f\"  File size: {pdf_report_path.stat().st_size / 1024:.1f} KB\")\n",
                "else:\n",
                "    print(f\"Error: CSV file not found at {csv_results}\")\n",
                "    print(\"Please run the analysis cells first (cells 8-10) to generate the CSV.\")\n"
            ]
            print(f"✓ Fixed PDF report cell {i}")
            break

# Save
with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print("✓ Notebook updated")
