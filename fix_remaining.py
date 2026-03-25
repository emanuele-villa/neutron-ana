#!/usr/bin/env python3
"""
Script to fix remaining matplotlib issues.
"""
import json

def fix_remaining_matplotlib(notebook_path):
    """Fix remaining plt.cm.get_cmap issues."""

    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    changes_made = 0

    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            for i, line in enumerate(cell['source']):
                original_line = line

                # Fix plt.cm.get_cmap -> plt.get_cmap (more thorough)
                if 'plt.cm.get_cmap(' in line:
                    line = line.replace('plt.cm.get_cmap(', 'plt.get_cmap(')
                    print(f"Fixed matplotlib: {original_line.strip()} -> {line.strip()}")
                    cell['source'][i] = line
                    changes_made += 1

    if changes_made > 0:
        # Write back to file
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=1)
        print(f"\nFixed {changes_made} remaining matplotlib issues.")
    else:
        print("No remaining matplotlib issues found.")

if __name__ == "__main__":
    notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"
    fix_remaining_matplotlib(notebook_path)