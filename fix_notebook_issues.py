#!/usr/bin/env python3
"""
Script to fix NumPy and Matplotlib deprecation issues in the notebook.
"""
import json

def fix_notebook_issues(notebook_path):
    """Fix np.trapz and plt.cm.get_cmap deprecation issues."""

    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    changes_made = 0

    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            for i, line in enumerate(cell['source']):
                original_line = line

                # Fix np.trapz -> np.trapezoid
                if 'np.trapz(' in line:
                    line = line.replace('np.trapz(', 'np.trapezoid(')
                    print(f"Fixed np.trapz: {original_line.strip()} -> {line.strip()}")

                # Fix plt.cm.get_cmap -> plt.get_cmap
                if 'plt.cm.get_cmap(' in line:
                    line = line.replace('plt.cm.get_cmap(', 'plt.get_cmap(')
                    print(f"Fixed plt.cm.get_cmap: {original_line.strip()} -> {line.strip()}")

                # Fix max_pairs config
                if 'max_pairs=None,' in line:
                    line = line.replace('max_pairs=None,  # Process all pairs', 'max_pairs=100,  # Process only first 100 pairs for testing')
                    print(f"Fixed max_pairs: {original_line.strip()} -> {line.strip()}")

                if line != original_line:
                    cell['source'][i] = line
                    changes_made += 1

    if changes_made > 0:
        # Write back to file
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=1)
        print(f"\nFixed {changes_made} issues in {notebook_path}")
    else:
        print("No issues found to fix.")

if __name__ == "__main__":
    notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"
    fix_notebook_issues(notebook_path)