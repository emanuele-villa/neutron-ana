#!/usr/bin/env python3
"""
Add a PDF report generation cell to the notebook.
"""
import json

notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Create the new cell content
new_cell_markdown = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Generate PDF Report\n",
        "\n",
        "Create a comprehensive PDF report with all analysis results and visualizations."
    ]
}

new_cell_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Generate comprehensive PDF report\n",
        "from lib import create_analysis_report\n",
        "\n",
        "# Define output path\n",
        "pdf_report_path = config.results_dir / \"neutron_gamma_analysis_report.pdf\"\n",
        "\n",
        "# Create report from the CSV results\n",
        "csv_results = config.results_dir / \"two_channel_events.csv\"\n",
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
        "    print(\"Please run the analysis cells first to generate the CSV.\")"
    ]
}

# Find the best position to insert - after "Analysis Complete" section (around cell 13)
insert_position = 14  # After cell 13

# Insert the new cells
notebook['cells'].insert(insert_position, new_cell_markdown)
notebook['cells'].insert(insert_position + 1, new_cell_code)

# Save the modified notebook
with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print(f"✓ Added PDF report generation cells at position {insert_position} and {insert_position + 1}")
print("  - Markdown header cell")
print("  - Code cell with create_analysis_report() function call")
