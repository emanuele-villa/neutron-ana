"""
Two-channel neutron-gamma coincidence analysis library.

This module contains the core analysis classes and functions for processing
two-channel waveform data, typically from neutron-gamma coincidence measurements.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import lecroyparser
import matplotlib.pyplot as plt

# Set up logger
logger = logging.getLogger("two_channel")


@dataclass(slots=True)
class TwoChannelConfig:
    """Configuration for two-channel neutron-gamma coincidence analysis."""

    # Paths
    waveform_dir: Path
    results_dir: Path
    ch1_pattern: str = "C1_"
    ch2_pattern: str = "C2_"
    file_extension: str = ".trc"

    # Analysis windows (all in nanoseconds)
    baseline_window_ns: float = 100.0  # use first 100ns for baseline
    charge_window_ns: Tuple[float, float] = (20.0, 40.0)  # left/right of peak

    # Threshold crossing for T0 extraction
    t0_threshold_fraction: float = 0.5  # fraction of peak amplitude for T0 (0.5 = 50%)
    t0_search_window_ns: float = 100.0   # search window before peak for threshold

    # Pulse characteristics
    pulse_polarity: str = "negative"  # 'negative' or 'positive'

    # Saturation detection (for neutron channel)
    saturation_flatness_window_ns: float = 10.0
    saturation_tolerance_v: float = 0.0015
    saturation_fraction: float = 0.3
    saturation_min_consecutive: int = 5

    # Plotting
    stack_plot_limit: int = 50
    stack_alpha: float = 0.3
    show_plots: bool = True

    # Processing
    max_pairs: Optional[int] = None  # limit number of pairs (None = all)

    def __post_init__(self) -> None:
        if self.pulse_polarity.lower() not in {"negative", "positive"}:
            raise ValueError("pulse_polarity must be 'negative' or 'positive'")
        self.pulse_polarity = self.pulse_polarity.lower()
        self.results_dir.mkdir(parents=True, exist_ok=True)

    @property
    def polarity_sign(self) -> int:
        return -1 if self.pulse_polarity == "negative" else 1


@dataclass(slots=True)
class Waveform:
    """Single channel waveform data."""
    path: Path
    time_s: np.ndarray
    voltage_v: np.ndarray

    @property
    def time_ns(self) -> np.ndarray:
        return self.time_s * 1e9


@dataclass(slots=True)
class TwoChannelEvent:
    """Analysis result for a two-channel coincidence event."""

    # File info
    ch1_path: Path
    ch2_path: Path

    # CH1 metrics
    ch1_baseline_v: float
    ch1_baseline_std_v: float
    ch1_peak_time_ns: float
    ch1_amplitude_v: float
    ch1_t0_ns: float
    ch1_charge_v_s: float
    ch1_saturated: bool

    # CH2 metrics
    ch2_baseline_v: float
    ch2_baseline_std_v: float
    ch2_peak_time_ns: float
    ch2_amplitude_v: float
    ch2_t0_ns: float
    ch2_charge_v_s: float
    ch2_saturated: bool

    # Time-of-flight
    delta_t_ns: float  # ch2_t0 - ch1_t0

    def to_dict(self) -> Dict:
        return {
            "ch1_path": str(self.ch1_path),
            "ch2_path": str(self.ch2_path),
            "ch1_baseline_v": self.ch1_baseline_v,
            "ch1_baseline_std_v": self.ch1_baseline_std_v,
            "ch1_peak_time_ns": self.ch1_peak_time_ns,
            "ch1_amplitude_v": self.ch1_amplitude_v,
            "ch1_t0_ns": self.ch1_t0_ns,
            "ch1_charge_v_s": self.ch1_charge_v_s,
            "ch1_saturated": self.ch1_saturated,
            "ch2_baseline_v": self.ch2_baseline_v,
            "ch2_baseline_std_v": self.ch2_baseline_std_v,
            "ch2_peak_time_ns": self.ch2_peak_time_ns,
            "ch2_amplitude_v": self.ch2_amplitude_v,
            "ch2_t0_ns": self.ch2_t0_ns,
            "ch2_charge_v_s": self.ch2_charge_v_s,
            "ch2_saturated": self.ch2_saturated,
            "delta_t_ns": self.delta_t_ns,
        }


def find_channel_pairs(config: TwoChannelConfig) -> List[Tuple[Path, Path]]:
    """Find matching pairs of C1/C2 files."""
    if not config.waveform_dir.exists():
        logger.warning("Waveform directory %s does not exist", config.waveform_dir)
        return []

    all_files = sorted(config.waveform_dir.rglob(f"*{config.file_extension}"))
    logger.info("Found %d total files", len(all_files))

    # Group by stem (remove channel prefix and extension)
    by_stem: Dict[str, Dict[str, Path]] = {}
    for fpath in all_files:
        name = fpath.name
        if config.ch1_pattern in name or config.ch2_pattern in name:
            # Remove channel pattern and extension to get stem
            base = name.replace(config.ch1_pattern, "").replace(config.ch2_pattern, "")
            base = re.sub(r"\.[^.]+$", "", base)

            if base not in by_stem:
                by_stem[base] = {}

            if config.ch1_pattern in name:
                by_stem[base]["ch1"] = fpath
            if config.ch2_pattern in name:
                by_stem[base]["ch2"] = fpath

    # Extract complete pairs
    pairs = []
    for base, channels in by_stem.items():
        if "ch1" in channels and "ch2" in channels:
            pairs.append((channels["ch1"], channels["ch2"]))

    logger.info("Found %d complete pairs", len(pairs))
    return pairs


def load_waveform(path: Path, channel_index: Optional[int] = None) -> Optional[Waveform]:
    """Load a single waveform from LeCroy .trc file.

    Args:
        path: Path to .trc file
        channel_index: Which channel to extract (0 or 1). If None, auto-detect from filename.
                      C1 files use channel 0, C2 files use channel 1.
    """
    try:
        # IMPORTANT: Must use parseAll=True to get correct voltage data!
        # parseAll=False returns incorrect scaled data (~50× too small)
        scope = lecroyparser.ScopeData(str(path), parseAll=True)
        time_s = np.asarray(scope.x, dtype=np.float64)

        # Auto-detect channel from filename if not specified
        if channel_index is None:
            if "C1_" in path.name or "Ch1" in path.name:
                channel_index = 0
            elif "C2_" in path.name or "Ch2" in path.name:
                channel_index = 1
            else:
                # Default to channel 0 if can't determine
                channel_index = 0
                logger.warning("Could not determine channel from filename %s, using channel 0", path.name)

        # When parseAll=True, scope.y is a list where y[i] is the i-th channel
        if isinstance(scope.y, list) and len(scope.y) > channel_index:
            voltage_v = np.asarray(scope.y[channel_index], dtype=np.float64)
        else:
            # Fallback for single-channel files
            voltage_v = np.asarray(scope.y[0] if isinstance(scope.y, list) else scope.y, dtype=np.float64)

        return Waveform(path=path, time_s=time_s, voltage_v=voltage_v)
    except Exception as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return None


def compute_baseline(time_ns: np.ndarray, voltage_v: np.ndarray, config: TwoChannelConfig) -> Tuple[float, float]:
    """Compute baseline mean and std from first 10 samples of waveform."""
    # Use first 10 samples (much simpler and more stable)
    n_baseline_samples = 10

    if voltage_v.size < n_baseline_samples:
        raise ValueError(f"Waveform has only {voltage_v.size} samples, need at least {n_baseline_samples}")

    segment = voltage_v[:n_baseline_samples]

    baseline = float(np.mean(segment))
    baseline_std = float(np.std(segment, ddof=0))
    return baseline, baseline_std


def find_peak(time_ns: np.ndarray, voltage_v: np.ndarray, config: TwoChannelConfig) -> Tuple[int, float]:
    """Find peak index and time."""
    if voltage_v.size == 0:
        raise ValueError("Empty waveform")

    if config.polarity_sign < 0:
        peak_idx = int(np.argmin(voltage_v))
    else:
        peak_idx = int(np.argmax(voltage_v))

    peak_time_ns = float(time_ns[peak_idx])
    return peak_idx, peak_time_ns


def find_threshold_crossing(time_ns: np.ndarray, aligned_signal_v: np.ndarray,
                            peak_idx: int, peak_time_ns: float,
                            config: TwoChannelConfig) -> float:
    """Find time when signal crosses threshold at fraction of peak amplitude.

    Searches backwards from peak to find first crossing point.
    Uses 50% of peak amplitude as threshold.
    Returns T0 in nanoseconds.
    """
    # Calculate threshold as fraction of peak amplitude
    peak_amplitude = aligned_signal_v[peak_idx]
    threshold = peak_amplitude * config.t0_threshold_fraction

    # Search backwards from peak
    search_start_ns = peak_time_ns - config.t0_search_window_ns
    search_mask = (time_ns >= search_start_ns) & (time_ns <= peak_time_ns)
    search_indices = np.flatnonzero(search_mask)

    if search_indices.size < 2:
        return float("nan")

    search_signal = aligned_signal_v[search_indices]
    search_times = time_ns[search_indices]

    # Find where signal exceeds threshold
    above_threshold = search_signal >= threshold

    if not np.any(above_threshold):
        return float("nan")

    # First crossing index in search region
    first_above = np.argmax(above_threshold)

    if first_above == 0:
        # Already above threshold at start of search
        return float(search_times[0])

    # Linear interpolation between points
    i0 = first_above - 1
    i1 = first_above
    t0 = search_times[i0]
    t1 = search_times[i1]
    v0 = search_signal[i0]
    v1 = search_signal[i1]

    if v1 == v0:
        return float(t0)

    # Interpolate
    t_cross = t0 + (threshold - v0) * (t1 - t0) / (v1 - v0)
    return float(t_cross)


def integrate_charge(time_ns: np.ndarray, aligned_signal_v: np.ndarray,
                     peak_time_ns: float, config: TwoChannelConfig) -> float:
    """Integrate charge in window around peak: 20ns left, 40ns right."""
    start_ns = peak_time_ns - config.charge_window_ns[0]
    end_ns = peak_time_ns + config.charge_window_ns[1]
    mask = (time_ns >= start_ns) & (time_ns <= end_ns)

    if mask.sum() < 2:
        return 0.0

    # trapezoid returns V*ns, convert to V*s
    return float(np.trapezoid(aligned_signal_v[mask], time_ns[mask]) * 1e-9)


def charge_to_energy_keV(charge_vs: float, calibration_keV_per_vs: float,
                        input_impedance_ohm: float = 50.0) -> float:
    """Convert charge (V⋅s) to energy (keV).

    Args:
        charge_vs: Integrated charge in volt-seconds
        calibration_keV_per_vs: Calibration factor (keV per V⋅s)
        input_impedance_ohm: Oscilloscope input impedance (default 50Ω)

    Returns:
        Energy in keV
    """
    return charge_vs * calibration_keV_per_vs


def calibrate_energy_from_compton_edge(neutron_charges_vs: np.ndarray,
                                     gamma_energy_keV: float = 478.0,
                                     percentile: float = 99.0) -> float:
    """Calculate calibration factor using Compton edge method (CORRECT physics).

    For gamma rays in scintillators, Compton scattering dominates. The maximum
    energy deposition is the Compton edge, not the full gamma energy.

    Args:
        neutron_charges_vs: Array of charge measurements for neutron events (V⋅s)
        gamma_energy_keV: Incident gamma energy (default 478 keV)
        percentile: Percentile to use for Compton edge (default 99th percentile)

    Returns:
        Calibration factor in keV per V⋅s
    """
    # Calculate Compton edge energy
    m_e_c2 = 511.0  # keV, electron rest mass energy
    compton_edge_keV = (gamma_energy_keV * (2 * gamma_energy_keV / m_e_c2) /
                        (1 + 2 * gamma_energy_keV / m_e_c2))

    # Use high percentile of charge distribution as Compton edge
    max_charge = np.percentile(neutron_charges_vs, percentile)

    return compton_edge_keV / max_charge


def calibrate_energy_from_neutron_peak(neutron_charges_vs: np.ndarray,
                                     neutron_peak_energy_keV: float = 478.0) -> float:
    """DEPRECATED: Incorrect method - use calibrate_energy_from_compton_edge instead.

    This function incorrectly assumes mean/median charge corresponds to full gamma energy.
    In reality, Compton scattering creates a continuum with Compton edge as maximum.
    """
    import warnings
    warnings.warn(
        "This calibration method is physically incorrect for Compton scattering. "
        "Use calibrate_energy_from_compton_edge() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    mean_charge = np.mean(neutron_charges_vs)
    return neutron_peak_energy_keV / mean_charge


def _max_consecutive_true(values: np.ndarray) -> int:
    """Find maximum consecutive True values."""
    best = count = 0
    for item in values:
        if item:
            count += 1
            best = max(best, count)
        else:
            count = 0
    return best


def detect_saturation(aligned_signal_v: np.ndarray, time_ns: np.ndarray,
                      peak_idx: int, config: TwoChannelConfig) -> bool:
    """Detect if waveform is saturated based on flatness around peak."""
    amplitude = float(aligned_signal_v[peak_idx])

    # Compute window in samples
    sample_interval_ns = float(np.median(np.diff(time_ns))) if time_ns.size > 1 else 1.0
    half_window_pts = max(1, int(np.ceil(config.saturation_flatness_window_ns / sample_interval_ns)))

    start_idx = max(0, peak_idx - half_window_pts)
    end_idx = min(aligned_signal_v.size, peak_idx + half_window_pts + 1)

    plateau_region = aligned_signal_v[start_idx:end_idx]
    if plateau_region.size == 0:
        return False

    peak_value = aligned_signal_v[peak_idx]
    within_tol = np.abs(plateau_region - peak_value) <= config.saturation_tolerance_v
    fraction = float(np.mean(within_tol))

    # Check for consecutive flat samples
    max_consecutive = _max_consecutive_true(within_tol)

    # Saturated if high fraction AND long consecutive run
    if fraction >= config.saturation_fraction and max_consecutive >= config.saturation_min_consecutive:
        return True

    # Also check boundary
    if peak_idx <= 1 or peak_idx >= aligned_signal_v.size - 2:
        return True

    return False


def analyze_channel(waveform: Waveform, config: TwoChannelConfig,
                    check_saturation: bool = False) -> Dict:
    """Analyze a single channel waveform."""
    time_ns = waveform.time_ns
    voltage_v = waveform.voltage_v

    # Compute baseline from first 100ns of waveform
    baseline_v, baseline_std_v = compute_baseline(time_ns, voltage_v, config)

    # Find peak
    peak_idx, peak_time_ns = find_peak(time_ns, voltage_v, config)

    # Baseline-corrected and polarity-aligned signal
    corrected_v = voltage_v - baseline_v
    aligned_signal_v = corrected_v * config.polarity_sign

    # Amplitude
    amplitude_v = float(aligned_signal_v[peak_idx])

    # Threshold crossing time (T0)
    t0_ns = find_threshold_crossing(time_ns, aligned_signal_v, peak_idx, peak_time_ns, config)

    # Charge integration
    charge_v_s = integrate_charge(time_ns, aligned_signal_v, peak_time_ns, config)

    # Saturation detection (only if requested)
    saturated = False
    if check_saturation:
        saturated = detect_saturation(aligned_signal_v, time_ns, peak_idx, config)

    return {
        "baseline_v": baseline_v,
        "baseline_std_v": baseline_std_v,
        "peak_time_ns": peak_time_ns,
        "amplitude_v": amplitude_v,
        "t0_ns": t0_ns,
        "charge_v_s": charge_v_s,
        "saturated": saturated,
    }


def analyze_pair(ch1_wf: Waveform, ch2_wf: Waveform,
                 config: TwoChannelConfig,
                 neutron_channel: str = "ch2") -> TwoChannelEvent:
    """Analyze a pair of waveforms.

    Args:
        ch1_wf: Channel 1 waveform
        ch2_wf: Channel 2 waveform
        config: Analysis configuration
        neutron_channel: Which channel to check for saturation ('ch1' or 'ch2')
    """
    # Analyze both channels
    ch1_result = analyze_channel(ch1_wf, config, check_saturation=(neutron_channel == "ch1"))
    ch2_result = analyze_channel(ch2_wf, config, check_saturation=(neutron_channel == "ch2"))

    # Compute time difference
    delta_t_ns = ch2_result["t0_ns"] - ch1_result["t0_ns"]

    return TwoChannelEvent(
        ch1_path=ch1_wf.path,
        ch2_path=ch2_wf.path,
        ch1_baseline_v=ch1_result["baseline_v"],
        ch1_baseline_std_v=ch1_result["baseline_std_v"],
        ch1_peak_time_ns=ch1_result["peak_time_ns"],
        ch1_amplitude_v=ch1_result["amplitude_v"],
        ch1_t0_ns=ch1_result["t0_ns"],
        ch1_charge_v_s=ch1_result["charge_v_s"],
        ch1_saturated=ch1_result["saturated"],
        ch2_baseline_v=ch2_result["baseline_v"],
        ch2_baseline_std_v=ch2_result["baseline_std_v"],
        ch2_peak_time_ns=ch2_result["peak_time_ns"],
        ch2_amplitude_v=ch2_result["amplitude_v"],
        ch2_t0_ns=ch2_result["t0_ns"],
        ch2_charge_v_s=ch2_result["charge_v_s"],
        ch2_saturated=ch2_result["saturated"],
        delta_t_ns=delta_t_ns,
    )


def extract_waveform_shape_features(wf: Waveform, config: TwoChannelConfig) -> Dict:
    """
    Extract shape features from a waveform that can help distinguish particle types.

    Features extracted:
    - Rise time (10% to 90% of peak)
    - Fall time (90% to 10% after peak)
    - Pulse width at half maximum (FWHM)
    - Peak position in time
    - Tail-to-peak ratio (integral of tail vs total)
    - Charge asymmetry (pre-peak vs post-peak)
    """
    time_ns = wf.time_ns
    voltage_v = wf.voltage_v

    # Baseline correction
    baseline_mean, baseline_std = compute_baseline(time_ns, voltage_v, config)
    corrected_v = voltage_v - baseline_mean

    # Apply polarity correction
    if config.pulse_polarity == "negative":
        corrected_v = -corrected_v

    # Find peak
    peak_idx = np.argmax(corrected_v)
    peak_amplitude = corrected_v[peak_idx]
    peak_time = time_ns[peak_idx]

    if peak_amplitude <= 0:
        return None

    # Define amplitude thresholds
    amp_10 = 0.1 * peak_amplitude
    amp_50 = 0.5 * peak_amplitude
    amp_90 = 0.9 * peak_amplitude

    # Rise time (10% to 90%)
    # Scan LEFT from peak: find last point above threshold before dropping below
    try:
        idx_10_rise = None
        idx_90_rise = None

        # Scan backwards from peak to find last point >= 90%
        for i in range(peak_idx, -1, -1):
            if corrected_v[i] >= amp_90:
                idx_90_rise = i  # Keep updating as long as we're above 90%
            else:
                break  # Dropped below 90%, use the last saved point

        # Continue scanning backwards to find last point >= 10%
        if idx_90_rise is not None:
            for i in range(idx_90_rise, -1, -1):
                if corrected_v[i] >= amp_10:
                    idx_10_rise = i  # Keep updating as long as we're above 10%
                else:
                    break  # Dropped below 10%, use the last saved point

        if idx_10_rise is not None and idx_90_rise is not None:
            rise_time_ns = time_ns[idx_90_rise] - time_ns[idx_10_rise]
        else:
            rise_time_ns = np.nan
    except (IndexError, ValueError):
        rise_time_ns = np.nan

    # Fall time (90% to 10% after peak)
    # Scan RIGHT from peak: find first point below threshold
    try:
        idx_90_fall = None
        idx_10_fall = None

        # Scan forward from peak to find first point < 90%
        for i in range(peak_idx, len(corrected_v)):
            if corrected_v[i] < amp_90:
                idx_90_fall = i
                break

        # Continue scanning forward to find first point < 10%
        if idx_90_fall is not None:
            for i in range(idx_90_fall, len(corrected_v)):
                if corrected_v[i] < amp_10:
                    idx_10_fall = i
                    break

        if idx_90_fall is not None and idx_10_fall is not None:
            fall_time_ns = time_ns[idx_10_fall] - time_ns[idx_90_fall]
        else:
            fall_time_ns = np.nan
    except (IndexError, ValueError):
        fall_time_ns = np.nan

    # FWHM (Full Width at Half Maximum)
    try:
        # Find half-max crossings
        above_half = corrected_v >= amp_50
        if np.any(above_half):
            half_max_indices = np.where(above_half)[0]
            fwhm_ns = time_ns[half_max_indices[-1]] - time_ns[half_max_indices[0]]
        else:
            fwhm_ns = np.nan
    except (IndexError, ValueError):
        fwhm_ns = np.nan

    # Charge integration windows
    # Total charge (symmetric around peak)
    charge_left_ns, charge_right_ns = config.charge_window_ns
    charge_start_time = peak_time - charge_left_ns
    charge_end_time = peak_time + charge_right_ns
    charge_mask = (time_ns >= charge_start_time) & (time_ns <= charge_end_time)

    # Pre-peak charge (left of peak)
    pre_charge_mask = (time_ns >= charge_start_time) & (time_ns <= peak_time)
    pre_charge = np.trapezoid(corrected_v[pre_charge_mask], time_ns[pre_charge_mask]) if np.any(pre_charge_mask) else 0.0

    # Post-peak charge (right of peak)
    post_charge_mask = (time_ns >= peak_time) & (time_ns <= charge_end_time)
    post_charge = np.trapezoid(corrected_v[post_charge_mask], time_ns[post_charge_mask]) if np.any(post_charge_mask) else 0.0

    total_charge = pre_charge + post_charge

    # Charge asymmetry
    if total_charge != 0:
        charge_asymmetry = (post_charge - pre_charge) / total_charge
    else:
        charge_asymmetry = np.nan

    # Tail-to-peak ratio (charge in tail region vs total)
    # Define tail as 50-100ns after peak
    tail_start = peak_time + 50.0
    tail_end = peak_time + 100.0
    tail_mask = (time_ns >= tail_start) & (time_ns <= tail_end)
    tail_charge = np.trapezoid(corrected_v[tail_mask], time_ns[tail_mask]) if np.any(tail_mask) else 0.0

    if total_charge > 0:
        tail_to_peak_ratio = tail_charge / total_charge
    else:
        tail_to_peak_ratio = np.nan

    return {
        'peak_amplitude_v': peak_amplitude,
        'peak_time_ns': peak_time,
        'rise_time_ns': rise_time_ns,
        'fall_time_ns': fall_time_ns,
        'fwhm_ns': fwhm_ns,
        'total_charge_v_s': total_charge * 1e-9,  # Convert to V·s
        'charge_asymmetry': charge_asymmetry,
        'tail_to_peak_ratio': tail_to_peak_ratio,
        'baseline_std_v': baseline_std
    }


def plot_stacked_waveforms(waveforms: List[Waveform], 
                          config: TwoChannelConfig,
                          title: str = "Stacked Waveforms",
                          save_path: Optional[Path] = None) -> None:
    """Plot all waveforms stacked on same axes (baseline-subtracted)."""
    if not waveforms:
        return
    
    limit = config.stack_plot_limit
    if limit and len(waveforms) > limit:
        waveforms = waveforms[:limit]
    
    cmap = plt.get_cmap("viridis", len(waveforms))
    colors = [cmap(i) for i in range(len(waveforms))]
    
    plt.figure(figsize=(12, 6))
    
    for idx, wf in enumerate(waveforms):
        time_ns = wf.time_ns
        voltage_v = wf.voltage_v
        
        # Quick baseline estimate (first 50 samples)
        baseline = np.mean(voltage_v[:min(50, voltage_v.size)])
        corrected = voltage_v - baseline
        
        plt.plot(time_ns, corrected, color=colors[idx], alpha=config.stack_alpha, linewidth=0.8)
    
    plt.axhline(0, color="black", linestyle=":", linewidth=0.8)
    plt.xlabel("Time [ns]")
    plt.ylabel("Voltage - baseline [V]")
    plt.title(f"{title} (n={len(waveforms)})")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
    
    if config.show_plots:
        plt.show()
    else:
        plt.close()


def plot_pair_comparison(ch1_wf: Waveform, ch2_wf: Waveform, 
                         event: TwoChannelEvent, config: TwoChannelConfig,
                         save_path: Optional[Path] = None) -> None:
    """Plot both channels with annotated features."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Channel 1
    time_ns_1 = ch1_wf.time_ns
    corrected_1 = (ch1_wf.voltage_v - event.ch1_baseline_v) * config.polarity_sign
    
    axes[0].plot(time_ns_1, corrected_1, color="tab:blue", linewidth=1.0)
    
    # Show baseline window (first 100ns)
    baseline_end = time_ns_1[0] + config.baseline_window_ns
    axes[0].axvspan(time_ns_1[0], baseline_end, color="gray", alpha=0.1, label="Baseline")
    
    # Show integration window
    int_start = event.ch1_peak_time_ns - config.charge_window_ns[0]
    int_end = event.ch1_peak_time_ns + config.charge_window_ns[1]
    axes[0].axvspan(int_start, int_end, color="purple", alpha=0.15, label="Integration")
    
    axes[0].axvline(event.ch1_peak_time_ns, color="tab:red", linestyle="--", label="Peak")
    if np.isfinite(event.ch1_t0_ns):
        axes[0].axvline(event.ch1_t0_ns, color="tab:orange", linestyle="-", label="T0")
    axes[0].axhline(0, color="black", linestyle=":", linewidth=0.7)
    axes[0].set_ylabel("CH1 [V]")
    axes[0].set_title(f"Channel 1 | Amp={event.ch1_amplitude_v:.3f}V | Q={event.ch1_charge_v_s:.3e}V·s")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(alpha=0.3)
    
    # Channel 2
    time_ns_2 = ch2_wf.time_ns
    corrected_2 = (ch2_wf.voltage_v - event.ch2_baseline_v) * config.polarity_sign
    
    axes[1].plot(time_ns_2, corrected_2, color="tab:green", linewidth=1.0)
    
    # Show baseline window (first 100ns)
    baseline_end = time_ns_2[0] + config.baseline_window_ns
    axes[1].axvspan(time_ns_2[0], baseline_end, color="gray", alpha=0.1, label="Baseline")
    
    # Show integration window
    int_start = event.ch2_peak_time_ns - config.charge_window_ns[0]
    int_end = event.ch2_peak_time_ns + config.charge_window_ns[1]
    axes[1].axvspan(int_start, int_end, color="purple", alpha=0.15, label="Integration")
    
    axes[1].axvline(event.ch2_peak_time_ns, color="tab:red", linestyle="--", label="Peak")
    if np.isfinite(event.ch2_t0_ns):
        axes[1].axvline(event.ch2_t0_ns, color="tab:orange", linestyle="-", label="T0")
    axes[1].axhline(0, color="black", linestyle=":", linewidth=0.7)
    axes[1].set_ylabel("CH2 [V]")
    sat_label = " [SAT]" if event.ch2_saturated else ""
    axes[1].set_title(f"Channel 2{sat_label} | Amp={event.ch2_amplitude_v:.3f}V | Q={event.ch2_charge_v_s:.3e}V·s")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(alpha=0.3)
    axes[1].set_xlabel("Time [ns]")
    
    # Overall title with delta_t
    if np.isfinite(event.delta_t_ns):
        fig.suptitle(f"Δt = {event.delta_t_ns:.2f} ns", fontsize=14, y=0.995)
    
    plt.tight_layout()
    
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
    
    if config.show_plots:
        plt.show()
    else:
        plt.close()


def plot_waveform_with_features(wf: Waveform, config: TwoChannelConfig, title: str = ""):
    """
    Plot a single waveform with all shape feature extraction windows annotated.
    """
    time_ns = wf.time_ns
    voltage_v = wf.voltage_v
    
    # Baseline correction
    baseline_mean, baseline_std = compute_baseline(time_ns, voltage_v, config)
    corrected_v = voltage_v - baseline_mean
    
    # Apply polarity correction
    if config.pulse_polarity == "negative":
        corrected_v = -corrected_v
    
    # Find peak
    peak_idx = np.argmax(corrected_v)
    peak_amplitude = corrected_v[peak_idx]
    peak_time = time_ns[peak_idx]
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Plot waveform
    ax.plot(time_ns, corrected_v * 1000, 'b-', linewidth=1.5, label='Waveform', alpha=0.7)
    
    # Mark baseline region
    baseline_mask = time_ns <= (time_ns[0] + config.baseline_window_ns)
    ax.axvspan(time_ns[baseline_mask][0], time_ns[baseline_mask][-1], 
               alpha=0.2, color='gray', label='Baseline Window')
    
    # Mark peak
    ax.plot(peak_time, peak_amplitude * 1000, 'r*', markersize=15, 
            label=f'Peak: {peak_amplitude*1000:.1f} mV @ {peak_time:.1f} ns')
    
    # Amplitude thresholds
    amp_10 = 0.1 * peak_amplitude
    amp_50 = 0.5 * peak_amplitude
    amp_90 = 0.9 * peak_amplitude
    
    # Draw threshold lines
    ax.axhline(amp_10 * 1000, color='orange', linestyle='--', alpha=0.5, linewidth=1, label='10% level')
    ax.axhline(amp_50 * 1000, color='purple', linestyle='--', alpha=0.5, linewidth=1, label='50% level (FWHM)')
    ax.axhline(amp_90 * 1000, color='red', linestyle='--', alpha=0.5, linewidth=1, label='90% level')
    
    # Rise time (10% to 90%)
    try:
        idx_10_rise = None
        idx_90_rise = None
        
        # Scan backwards from peak to find last point >= 90%
        for i in range(peak_idx, -1, -1):
            if corrected_v[i] >= amp_90:
                idx_90_rise = i
            else:
                break
        
        # Continue scanning backwards to find last point >= 10%
        if idx_90_rise is not None:
            for i in range(idx_90_rise, -1, -1):
                if corrected_v[i] >= amp_10:
                    idx_10_rise = i
                else:
                    break
        
        if idx_10_rise is not None and idx_90_rise is not None:
            ax.plot([time_ns[idx_10_rise], time_ns[idx_90_rise]], 
                    [corrected_v[idx_10_rise] * 1000, corrected_v[idx_90_rise] * 1000], 
                    'o-', color='green', linewidth=3, markersize=8, 
                    label=f'Rise Time: {time_ns[idx_90_rise] - time_ns[idx_10_rise]:.2f} ns')
            
            # Add arrow annotation
            ax.annotate('', xy=(time_ns[idx_90_rise], amp_90*1000), 
                       xytext=(time_ns[idx_10_rise], amp_10*1000),
                       arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    except (IndexError, ValueError):
        pass
    
    # Fall time (90% to 10% after peak)
    try:
        idx_90_fall = None
        idx_10_fall = None
        
        # Scan forward from peak to find first point < 90%
        for i in range(peak_idx, len(corrected_v)):
            if corrected_v[i] < amp_90:
                idx_90_fall = i
                break
        
        # Continue scanning forward to find first point < 10%
        if idx_90_fall is not None:
            for i in range(idx_90_fall, len(corrected_v)):
                if corrected_v[i] < amp_10:
                    idx_10_fall = i
                    break
        
        if idx_90_fall is not None and idx_10_fall is not None:
            ax.plot([time_ns[idx_90_fall], time_ns[idx_10_fall]], 
                    [corrected_v[idx_90_fall] * 1000, corrected_v[idx_10_fall] * 1000], 
                    'o-', color='red', linewidth=3, markersize=8, 
                    label=f'Fall Time: {time_ns[idx_10_fall] - time_ns[idx_90_fall]:.2f} ns')
            
            # Add arrow annotation
            ax.annotate('', xy=(time_ns[idx_10_fall], amp_10*1000), 
                       xytext=(time_ns[idx_90_fall], amp_90*1000),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    except (IndexError, ValueError):
        pass
    
    # FWHM
    try:
        above_half = corrected_v >= amp_50
        if np.any(above_half):
            half_max_indices = np.where(above_half)[0]
            fwhm_start = time_ns[half_max_indices[0]]
            fwhm_end = time_ns[half_max_indices[-1]]
            
            ax.plot([fwhm_start, fwhm_end], [amp_50 * 1000, amp_50 * 1000], 
                   'o-', color='purple', linewidth=3, markersize=8, 
                   label=f'FWHM: {fwhm_end - fwhm_start:.2f} ns')
            
            # Add arrow annotation
            ax.annotate('', xy=(fwhm_end, amp_50*1000 - 5), 
                       xytext=(fwhm_start, amp_50*1000 - 5),
                       arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    except (IndexError, ValueError):
        pass
    
    # Charge integration window
    charge_left_ns, charge_right_ns = config.charge_window_ns
    charge_start_time = peak_time - charge_left_ns
    charge_end_time = peak_time + charge_right_ns
    
    ax.axvspan(charge_start_time, charge_end_time, alpha=0.15, color='cyan', 
               label=f'Charge Window: -{charge_left_ns:.0f}/+{charge_right_ns:.0f} ns')
    
    # Tail region (50-100 ns after peak)
    tail_start = peak_time + 50.0
    tail_end = peak_time + 100.0
    ax.axvspan(tail_start, tail_end, alpha=0.15, color='yellow', 
               label='Tail Region (50-100 ns)')
    
    # Formatting
    ax.set_xlabel('Time (ns)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amplitude (mV)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(time_ns[0], time_ns[0] + 300)  # Show first 300 ns
    
    return fig, ax


def create_analysis_report(
    csv_path: Path,
    output_pdf: Path,
    waveform_dir: Optional[Path] = None,
    title: str = "Two-Channel Neutron-Gamma Analysis Report"
):
    """
    Create a comprehensive PDF report from analysis CSV results.
    
    Args:
        csv_path: Path to the CSV file with analysis results
        output_pdf: Path where PDF report should be saved
        waveform_dir: Optional path to waveform directory for example plots
        title: Report title
    """
    import pandas as pd
    from matplotlib.backends.backend_pdf import PdfPages
    from datetime import datetime
    
    # Read the data
    df = pd.read_csv(csv_path)
    
    # Create PDF
    with PdfPages(output_pdf) as pdf:
        
        # Page 1: Title and Summary Statistics
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle(title, fontsize=20, fontweight='bold', y=0.98)
        
        # Add summary text
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        summary_text = f"""
SUMMARY STATISTICS
{'=' * 80}

Dataset Information:
  • Total events analyzed: {len(df):,}
  • Date generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  • Data source: {csv_path.name}

Channel 1 (Gamma) Statistics:
  • Amplitude (V):     mean = {df['ch1_amplitude_v'].mean():.4f} ± {df['ch1_amplitude_v'].std():.4f}
                       range = [{df['ch1_amplitude_v'].min():.4f}, {df['ch1_amplitude_v'].max():.4f}]
  
  • Charge (V·s):      mean = {df['ch1_charge_v_s'].mean():.3e} ± {df['ch1_charge_v_s'].std():.3e}
                       range = [{df['ch1_charge_v_s'].min():.3e}, {df['ch1_charge_v_s'].max():.3e}]

Channel 2 (Neutron) Statistics:
  • Amplitude (V):     mean = {df['ch2_amplitude_v'].mean():.4f} ± {df['ch2_amplitude_v'].std():.4f}
                       range = [{df['ch2_amplitude_v'].min():.4f}, {df['ch2_amplitude_v'].max():.4f}]
  
  • Charge (V·s):      mean = {df['ch2_charge_v_s'].mean():.3e} ± {df['ch2_charge_v_s'].std():.3e}
                       range = [{df['ch2_charge_v_s'].min():.3e}, {df['ch2_charge_v_s'].max():.3e}]
  
  • Saturated events: {df['ch2_saturated'].sum()} ({100*df['ch2_saturated'].sum()/len(df):.1f}%)

Time-of-Flight (Coincidence):
  • Delta-t (ns):      mean = {df['delta_t_ns'].mean():.2f} ± {df['delta_t_ns'].std():.2f}
                       range = [{df['delta_t_ns'].min():.2f}, {df['delta_t_ns'].max():.2f}]

"""
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
                fontsize=11, verticalalignment='top', fontfamily='monospace')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: Amplitude Distributions
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Amplitude Distributions', fontsize=16, fontweight='bold')
        
        # CH1 amplitude
        axes[0, 0].hist(df['ch1_amplitude_v'], bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_xlabel('Amplitude (V)', fontsize=11)
        axes[0, 0].set_ylabel('Counts', fontsize=11)
        axes[0, 0].set_title('CH1 (Gamma) Amplitude', fontsize=12, fontweight='bold')
        axes[0, 0].grid(alpha=0.3)
        
        # CH2 amplitude
        axes[0, 1].hist(df['ch2_amplitude_v'], bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_xlabel('Amplitude (V)', fontsize=11)
        axes[0, 1].set_ylabel('Counts', fontsize=11)
        axes[0, 1].set_title('CH2 (Neutron) Amplitude', fontsize=12, fontweight='bold')
        axes[0, 1].grid(alpha=0.3)
        
        # CH1 vs CH2 amplitude correlation
        axes[1, 0].scatter(df['ch1_amplitude_v'], df['ch2_amplitude_v'], 
                          alpha=0.3, s=10, c='purple')
        axes[1, 0].set_xlabel('CH1 Amplitude (V)', fontsize=11)
        axes[1, 0].set_ylabel('CH2 Amplitude (V)', fontsize=11)
        axes[1, 0].set_title('Amplitude Correlation', fontsize=12, fontweight='bold')
        axes[1, 0].grid(alpha=0.3)
        
        # Amplitude ratio
        amp_ratio = df['ch2_amplitude_v'] / df['ch1_amplitude_v']
        axes[1, 1].hist(amp_ratio[np.isfinite(amp_ratio)], bins=50, 
                       alpha=0.7, color='orange', edgecolor='black')
        axes[1, 1].set_xlabel('CH2/CH1 Amplitude Ratio', fontsize=11)
        axes[1, 1].set_ylabel('Counts', fontsize=11)
        axes[1, 1].set_title('Amplitude Ratio Distribution', fontsize=12, fontweight='bold')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 3: Charge Distributions
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Integrated Charge Distributions', fontsize=16, fontweight='bold')
        
        # CH1 charge
        axes[0, 0].hist(df['ch1_charge_v_s']*1e9, bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0, 0].set_xlabel('Charge (V·ns)', fontsize=11)
        axes[0, 0].set_ylabel('Counts', fontsize=11)
        axes[0, 0].set_title('CH1 (Gamma) Charge', fontsize=12, fontweight='bold')
        axes[0, 0].grid(alpha=0.3)
        
        # CH2 charge
        axes[0, 1].hist(df['ch2_charge_v_s']*1e9, bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[0, 1].set_xlabel('Charge (V·ns)', fontsize=11)
        axes[0, 1].set_ylabel('Counts', fontsize=11)
        axes[0, 1].set_title('CH2 (Neutron) Charge', fontsize=12, fontweight='bold')
        axes[0, 1].grid(alpha=0.3)
        
        # CH1 vs CH2 charge correlation
        axes[1, 0].scatter(df['ch1_charge_v_s']*1e9, df['ch2_charge_v_s']*1e9, 
                          alpha=0.3, s=10, c='purple')
        axes[1, 0].set_xlabel('CH1 Charge (V·ns)', fontsize=11)
        axes[1, 0].set_ylabel('CH2 Charge (V·ns)', fontsize=11)
        axes[1, 0].set_title('Charge Correlation', fontsize=12, fontweight='bold')
        axes[1, 0].grid(alpha=0.3)
        
        # Charge vs amplitude for CH2
        axes[1, 1].scatter(df['ch2_amplitude_v'], df['ch2_charge_v_s']*1e9, 
                          alpha=0.3, s=10, c='green')
        axes[1, 1].set_xlabel('CH2 Amplitude (V)', fontsize=11)
        axes[1, 1].set_ylabel('CH2 Charge (V·ns)', fontsize=11)
        axes[1, 1].set_title('CH2 Amplitude vs Charge', fontsize=12, fontweight='bold')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 4: Time-of-Flight Analysis
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Time-of-Flight Analysis', fontsize=16, fontweight='bold')
        
        # Delta-t distribution
        axes[0, 0].hist(df['delta_t_ns'], bins=100, alpha=0.7, color='red', edgecolor='black')
        axes[0, 0].set_xlabel('Δt (CH2 - CH1) [ns]', fontsize=11)
        axes[0, 0].set_ylabel('Counts', fontsize=11)
        axes[0, 0].set_title('Time Difference Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        axes[0, 0].grid(alpha=0.3)
        
        # Delta-t vs CH2 amplitude
        axes[0, 1].scatter(df['ch2_amplitude_v'], df['delta_t_ns'], 
                          alpha=0.3, s=10, c='blue')
        axes[0, 1].set_xlabel('CH2 Amplitude (V)', fontsize=11)
        axes[0, 1].set_ylabel('Δt (ns)', fontsize=11)
        axes[0, 1].set_title('Δt vs CH2 Amplitude', fontsize=12, fontweight='bold')
        axes[0, 1].axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        axes[0, 1].grid(alpha=0.3)
        
        # Delta-t vs CH2 charge
        axes[1, 0].scatter(df['ch2_charge_v_s']*1e9, df['delta_t_ns'], 
                          alpha=0.3, s=10, c='green')
        axes[1, 0].set_xlabel('CH2 Charge (V·ns)', fontsize=11)
        axes[1, 0].set_ylabel('Δt (ns)', fontsize=11)
        axes[1, 0].set_title('Δt vs CH2 Charge', fontsize=12, fontweight='bold')
        axes[1, 0].axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        axes[1, 0].grid(alpha=0.3)
        
        # Peak times
        axes[1, 1].scatter(df['ch1_peak_time_ns'], df['ch2_peak_time_ns'], 
                          alpha=0.3, s=10, c='purple')
        axes[1, 1].set_xlabel('CH1 Peak Time (ns)', fontsize=11)
        axes[1, 1].set_ylabel('CH2 Peak Time (ns)', fontsize=11)
        axes[1, 1].set_title('Peak Time Correlation', fontsize=12, fontweight='bold')
        axes[1, 1].plot([df['ch1_peak_time_ns'].min(), df['ch1_peak_time_ns'].max()],
                       [df['ch1_peak_time_ns'].min(), df['ch1_peak_time_ns'].max()],
                       'k--', alpha=0.5, linewidth=1)
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 5: Event Classification
        fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Event Classification and Quality', fontsize=16, fontweight='bold')
        
        # Saturation status
        sat_counts = df['ch2_saturated'].value_counts()
        axes[0, 0].bar(['Non-saturated', 'Saturated'], 
                      [sat_counts.get(False, 0), sat_counts.get(True, 0)],
                      color=['green', 'red'], alpha=0.7, edgecolor='black')
        axes[0, 0].set_ylabel('Event Count', fontsize=11)
        axes[0, 0].set_title('CH2 Saturation Status', fontsize=12, fontweight='bold')
        axes[0, 0].grid(alpha=0.3, axis='y')
        for i, v in enumerate([sat_counts.get(False, 0), sat_counts.get(True, 0)]):
            axes[0, 0].text(i, v, f'{v:,}\n({100*v/len(df):.1f}%)', 
                          ha='center', va='bottom', fontweight='bold')
        
        # Baseline statistics - CH1
        axes[0, 1].hist(df['ch1_baseline_std_v']*1000, bins=50, 
                       alpha=0.7, color='blue', edgecolor='black')
        axes[0, 1].set_xlabel('Baseline Noise (mV)', fontsize=11)
        axes[0, 1].set_ylabel('Counts', fontsize=11)
        axes[0, 1].set_title('CH1 Baseline Noise', fontsize=12, fontweight='bold')
        axes[0, 1].grid(alpha=0.3)
        
        # Baseline statistics - CH2
        axes[1, 0].hist(df['ch2_baseline_std_v']*1000, bins=50, 
                       alpha=0.7, color='green', edgecolor='black')
        axes[1, 0].set_xlabel('Baseline Noise (mV)', fontsize=11)
        axes[1, 0].set_ylabel('Counts', fontsize=11)
        axes[1, 0].set_title('CH2 Baseline Noise', fontsize=12, fontweight='bold')
        axes[1, 0].grid(alpha=0.3)
        
        # Event distribution over measurement
        axes[1, 1].plot(range(len(df)), df['ch2_amplitude_v'], 
                       alpha=0.5, linewidth=0.5, color='green')
        axes[1, 1].set_xlabel('Event Number', fontsize=11)
        axes[1, 1].set_ylabel('CH2 Amplitude (V)', fontsize=11)
        axes[1, 1].set_title('Amplitude Stability Over Time', fontsize=12, fontweight='bold')
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Add metadata to PDF
        d = pdf.infodict()
        d['Title'] = title
        d['Author'] = 'Neutron Analysis Pipeline'
        d['Subject'] = 'Two-Channel Neutron-Gamma Coincidence Analysis'
        d['Creator'] = 'lib.py - create_analysis_report()'
        d['CreationDate'] = datetime.now()
    
    logger.info("PDF report saved to: %s", output_pdf)
