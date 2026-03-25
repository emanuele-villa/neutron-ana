#!/usr/bin/env python3
import json

notebook_path = "/Users/virgolaema/Software/3det/neutron-ana/two_channel_neutron_gamma_analysis.ipynb"

with open(notebook_path, 'r') as f:
    notebook = json.load(f)

# Fix the imports cell (cell 1)
for i, cell in enumerate(notebook['cells']):
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'from lib import' in source and 'create_analysis_report' not in source:
            # Update imports
            cell['source'] = [
                "from __future__ import annotations\n",
                "\n",
                "import logging\n",
                "import re\n",
                "from dataclasses import dataclass\n",
                "from pathlib import Path\n",
                "from typing import Dict, List, Optional, Tuple\n",
                "\n",
                "import matplotlib.pyplot as plt\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "from scipy.signal import savgol_filter\n",
                "\n",
                "try:\n",
                "    import lecroyparser\n",
                "except ImportError as exc:\n",
                "    raise ImportError(\"lecroyparser required. Install: pip install lecroyparser\") from exc\n",
                "\n",
                "logging.basicConfig(level=logging.INFO, format=\"%(asctime)s [%(levelname)s] %(message)s\")\n",
                "logger = logging.getLogger(\"two_channel\")\n",
                "\n",
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
            print(f"✓ Fixed imports in cell {i}")
            break

# Save
with open(notebook_path, 'w') as f:
    json.dump(notebook, f, indent=1)

print("✓ Notebook updated")
