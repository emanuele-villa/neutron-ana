#!/usr/bin/env python3
"""
Clean up notebook by removing function definitions that are now in lib.py
"""
import json
import re

def clean_notebook(notebook_path):
    """Remove function definitions and add import statement."""

    with open(notebook_path, 'r') as f:
        notebook = json.load(f)

    # Functions to remove (they're now in lib.py)
    functions_to_remove = [
        'find_channel_pairs',
        'load_waveform',
        'compute_baseline',
        'find_peak',
        'find_threshold_crossing',
        'integrate_charge',
        'detect_saturation',
        '_max_consecutive_true',
        'analyze_channel',
        'analyze_pair',
        'plot_stacked_waveforms',
        'plot_pair_comparison',
        'extract_waveform_shape_features',
        'plot_waveform_with_features',
    ]

    # Classes to remove (they're now in lib.py)
    classes_to_remove = [
        'TwoChannelConfig',
        'Waveform',
        'TwoChannelEvent',
    ]

    cells_to_remove = []
    import_cell_added = False

    for idx, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            source_text = ''.join(cell['source'])

            # Check if this cell contains a function or class definition to remove
            should_remove = False

            # Check for function definitions
            for func_name in functions_to_remove:
                if re.search(rf'^\s*def\s+{func_name}\s*\(', source_text, re.MULTILINE):
                    should_remove = True
                    print(f"Marking cell {idx} for removal: contains function '{func_name}'")
                    break

            # Check for class definitions
            if not should_remove:
                for class_name in classes_to_remove:
                    if re.search(rf'^\s*@dataclass.*?\nclass\s+{class_name}', source_text, re.DOTALL | re.MULTILINE):
                        should_remove = True
                        print(f"Marking cell {idx} for removal: contains class '{class_name}'")
                        break
                    elif re.search(rf'^\s*class\s+{class_name}\s*[:\(]', source_text, re.MULTILINE):
                        should_remove = True
                        print(f"Marking cell {idx} for removal: contains class '{class_name}'")
                        break

            if should_remove:
                cells_to_remove.append(idx)

            # Add import statement after the first imports cell
            elif not import_cell_added and 'import' in source_text and 'numpy' in source_text:
                # This looks like the imports cell - add our lib import
                if 'from lib import' not in source_text and 'import lib' not in source_text:
                    # Add import at the end of this cell
                    cell['source'].append('\n')
                    cell['source'].append('# Import analysis functions from lib\n')
                    cell['source'].append('from lib import (\n')
                    cell['source'].append('    TwoChannelConfig, Waveform, TwoChannelEvent,\n')
                    cell['source'].append('    find_channel_pairs, load_waveform,\n')
                    cell['source'].append('    analyze_channel, analyze_pair,\n')
                    cell['source'].append('    plot_stacked_waveforms, plot_pair_comparison,\n')
                    cell['source'].append('    plot_waveform_with_features, extract_waveform_shape_features\n')
                    cell['source'].append(')\n')
                    import_cell_added = True
                    print(f"Added import statement to cell {idx}")

    # Remove cells in reverse order to maintain indices
    for idx in reversed(cells_to_remove):
        del notebook['cells'][idx]
        print(f"Removed cell {idx}")

    # Write back
    with open(notebook_path, 'w') as f:
        json.dump(notebook, f, indent=1)

    print(f"\n✓ Cleaned notebook: removed {len(cells_to_remove)} cells with function/class definitions")
    print(f"✓ Added import statement from lib.py")

if __name__ == "__main__":
    notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"
    clean_notebook(notebook_path)
