# Single-Molecule Kymograph Toolkit

Two desktop applications for **LUMICKS C-Trap** single-molecule fluorescence data (`.h5` kymographs), built with Python / Tkinter / Matplotlib:

| Tool | Entry point | Purpose |
|---|---|---|
| **KymoTracker 3.4** | `KymoTracker3.4 .py` | Interactive trajectory tracking in kymographs + MSD / diffusion / rate / fluorescence analysis |
| **Kymograph Sorter** | `kymograph_sorter.py` (+ `kymograph_theme.py`, `kymograph_force_analysis.py`) | File organizing & classification, kymograph stitching, background subtraction, force overlay & force-clamp DNA length analysis, annotation, 300-dpi export |

Both are developed on Windows, Python ≥ 3.8, and read `.h5` files via [`lumicks.pylake`](https://lumicks.github.io/pylake/).

---

## Table of Contents

- [KymoTracker 3.4](#kymotracker-34)
  - [Features](#features-kymotracker)
  - [Requirements](#requirements-kymotracker)
  - [Quick Start](#quick-start-kymotracker)
  - [Workflow](#workflow-kymotracker)
  - [Tracking Algorithms & Parameters](#tracking-algorithms--parameters)
  - [ROI Tools](#roi-tools)
  - [Multi-Channel & Multi-File Support](#multi-channel--multi-file-support)
  - [Analysis Modules](#analysis-modules)
  - [Export Formats](#export-formats)
  - [Trace Editing](#trace-editing)
  - [Keyboard Shortcuts & Mouse Interactions](#keyboard-shortcuts--mouse-interactions)
- [Kymograph Sorter](#kymograph-sorter)
  - [Features](#features-sorter)
  - [Requirements & File Layout](#requirements--file-layout)
  - [Quick Start](#quick-start-sorter)
  - [Main Window](#main-window)
  - [Sorting & Archiving](#sorting--archiving)
  - [Kymograph Stitching](#kymograph-stitching)
  - [Force & Distance Tools](#force--distance-tools)
  - [Force-Clamp DNA Length Analysis](#force-clamp-dna-length-analysis)
  - [Image Display Controls](#image-display-controls)
  - [Annotation Tools](#annotation-tools)
  - [Internationalization & Theme](#internationalization--theme)
- [Notes & Quirks](#notes--quirks)
- [License](#license)

---

# KymoTracker 3.4

An interactive **Tkinter + Matplotlib GUI** for tracking single-molecule trajectories in C-Trap kymographs. Built for day-to-day single-molecule fluorescence workflows: multi-channel (RGB) kymograph display, rectangle & freehand-polygon ROIs, one-click greedy/line tracking (pylake algorithms), per-channel parameter memory, and a full analysis suite — diffusion coefficients (MSD / CVE / OLS), segment-wise rates, sliding-window dynamics, velocity distributions, and trace/ROI fluorescence — with Excel/CSV/PNG export.

## Features (KymoTracker)

- **Multi-channel kymograph display** — red / green / blue channels, shown as single-channel pseudocolor (Reds/Greens/Blues colormap) or RGB composite; per-channel contrast sliders (0.1–10×)
- **Per-channel tracking parameters** — every channel keeps its own parameter set; switching channels saves/restores automatically
- **Interactive ROIs** — two-click rectangular ROI (Y-range, full width) and curved polygon ROI with vertex-level undo
- **Two pylake tracking algorithms** — `track_greedy` and `track_lines`, with all key parameters exposed in the GUI
- **Background-threaded tracking** — the UI never freezes during tracking (`ThreadPoolExecutor`)
- **Automatic unit conversion** — built-in nm ↔ bp (B-form DNA, 1 bp = 0.34 nm); positions reported in µm and/or bp throughout
- **Analysis suite** — diffusion (MSD fit / CVE / OLS), multi-segment & sliding-window MSD, velocity & rate, trace/ROI fluorescence
- **Trace editing** — click-delete, box-delete, point-level editing with backup/restore, and full undo history
- **Batch export** — Excel workbooks (standard / wide / long / summary layouts), per-trace CSVs with settings & metadata files, 300-dpi PNG figures, OriginLab-ready tables
- **Multi-file support** — load many `.h5` files at once, or scan a whole folder

## Requirements (KymoTracker)

```bash
pip install lumicks-pylake numpy pandas matplotlib scikit-image openpyxl
```

| Package | Role | Required? |
|---|---|---|
| `lumicks.pylake` | Reading C-Trap `.h5` files; tracking algorithms | ✅ |
| `numpy`, `pandas` | Data processing | ✅ |
| `matplotlib` (TkAgg) | Display & figures | ✅ |
| `openpyxl` | Excel export | ✅ |
| `scikit-image` | Polygon ROI masks (preferred) | Optional |
| `opencv-python` | Fallback for polygon masks | Optional |

> The code is compatible with both old and new pylake APIs (`kymo.red_image` / `kymo.red` / `kymo.get_image()`). If channel loading fails, try `pip install --upgrade lumicks-pylake`.

## Quick Start (KymoTracker)

```bash
python "KymoTracker3.4 .py"
```

> ⚠️ The filename contains a space before `.py` — quote it on the command line (or rename the file).

## Workflow (KymoTracker)

1. **Load files** — `Load H5 Files` (multi-select) or `Load Folder` (loads every `.h5` whose filename contains "kymograph", case-insensitive). Files with a single kymograph load automatically; otherwise pick the kymograph from the list.
2. **(Optional) Preprocessing** — flip the Y axis if needed.
3. **Draw an ROI** — rectangle or curved polygon (see [ROI Tools](#roi-tools)).
4. **Configure tracking** — choose channel (red/green/blue), algorithm and parameters, then press **START TRACKING**. Tracking runs in a background thread.
5. **Filter & edit** — filter by minimum duration/length; delete bad traces or individual points; undo as needed.
6. **Analyze** — diffusion, rates, velocity, fluorescence (see [Analysis Modules](#analysis-modules)).
7. **Export** — Excel / CSV / PNG via the **Export** dialog.

## Tracking Algorithms & Parameters

Tracking is performed by **pylake's built-in algorithms** (sub-pixel localization handled internally by pylake):

| Algorithm | pylake function | GUI parameters (defaults) |
|---|---|---|
| **Greedy** (default) | `lk.track_greedy` | `line_width` (5, range 1–20), `pixel_threshold` (1.0), `window` (8, range 1–20), `sigma` (None — optional number) |
| **Lines** | `lk.track_lines` | `line_width` (5), `max_lines` (10, range 1–50) |

Post-processing:

- **Min length filter** (`filter_length`, default 20 points) — traces shorter than this are dropped; if filtering would remove everything, the raw traces are kept with a warning.
- **Min Duration (s)** — secondary time-based filter applied on demand.
- Before tracking, signal statistics (min/max/mean) are logged; a warning is shown if `pixel_threshold` ≥ image maximum.

All parameters are stored **per channel** (`line_width`, `pixel_threshold`, `filter_length`, `min_duration`) and restored when you switch channels.

## ROI Tools

| ROI type | How to use |
|---|---|
| **Rectangle** | Click two points on the image; only the **Y range** is used (X always spans the full width) |
| **Curved polygon** | Left-click to add vertices (connected by straight lines, no smoothing); **Z** = undo last vertex, **Enter** = finish (≥ 3 vertices), **Esc** = cancel |

- Polygon vertices are converted to a boolean mask (scikit-image preferred, OpenCV fallback); pixels outside the mask are zeroed before tracking.
- `Edit Points` shows/resets vertices; `Clear ROI` removes the ROI.

## Multi-Channel & Multi-File Support

- **Channels**: red / green / blue tracked independently — `tracks_dict = {'red', 'green', 'blue'}`. Display modes: *Pseudocolor* (single channel) or *RGB Composite*.
- **Contrast**: independent 0.1–10× slider per channel.
- **Files**: any number of `.h5` files can be loaded side by side; switching files/kymographs preserves each channel's tracks and settings.

Unit handling:

- Pixel size and line time are read from the kymograph (`pixelsize_um`, line timestamps).
- DNA conversion constants are hard-coded: **1 bp = 0.34 nm**, 1 µm ≈ 2941.18 bp (B-form DNA).

## Analysis Modules

### Diffusion coefficient (MSD)

Three estimators (Michalet & Berglund, *Phys. Rev. E* 2012 framework):

- **MSD linear fit** — *D* = slope / 2, with R²
- **CVE** (covariance-based estimator) — corrects for localization error σ (default 30 nm)
- **OLS** — ordinary least squares benchmark

Supports custom time windows (drag the green/blue boundary lines on the plot), 50 s window analysis, and multi-track histograms. Vectorized NumPy implementation (>5× faster than naive loops).

### Multi-segment MSD

Split a trace into segments by **dragging on the plot**, **manual entry** (table dialog), or **automatic N-way equal split**. Per segment: *D* (µm²/s and bp²/s), R², and anomalous diffusion exponent α (log–log fit). Defaults: max lag 20 s, fit over first 50 % of points.

### Sliding-window MSD

Default 30 s window, lag sampling 5, fit 10 points, max lag 15, overlap 0/25/50 %. Outputs *D* distribution statistics in both µm²/s and bp²/s.

### Velocity & rate

- **Instantaneous velocity** — point-wise difference or local linear fit (window 11 points); |v| filter default 1000 bp/s; 30-bin distribution histogram
- **Multi-segment rate** — drag-defined segments; endpoint (simple) rate + polyfit rate in µm/s and bp/s, with R² and standard errors
- **Velocity overview** — whole-channel velocity time course + histogram
- **Duration-weighted rate** — `compute_weighted_fit_rate_bp_s`

### Fluorescence

- **Trace fluorescence** — position + intensity over time, lifetime, normalization, smoothing
- **ROI fluorescence** — total/mean photon counts inside the ROI over time, with smoothing & normalization

### Segment statistics

Every exported summary row includes: point count, start/end time & position, duration, lifetime (frames/s), net displacement, total path length, mean / absolute-mean / SD velocity, and intensity statistics (mean, max, integrated, Δ, relative change).

## Export Formats

### Excel (`.xlsx`, via openpyxl)

| Layout | Sheets | Content |
|---|---|---|
| **Standard** | `Red_Track1`, … | One sheet per trace: Track_ID, Channel, Point_ID, Relative Time (s), Lifetime, Time (s), Position (µm), Summed Photon Counts, Velocity (µm/s) (+ optional raw indices) |
| **Wide** | `Red_Wide` | One column set per track, NaN-padded |
| **Long** | `Red_Long` | Stacked rows |
| **Long Merged** | `All_Tracks_Merged` | All channels with Track_Label |
| **Summary** | `Red_Summary` | Per-track statistics |
| — | `Metadata` | Source file, kymo name, date, dimensions, pixel size, line time, Y-flip, ROI |
| — | `Tracking_Settings` | Algorithm & parameters per channel |

### CSV

One file per trace, plus `<name>_KymotrackerSettings.csv` and `<name>_metadata.csv`.

### Analysis-specific exports

- **MSD** → workbook with `MSD_Summary`, `MSD_RawData`, `MSD_FitLines`, `MSD_OriginReady`, `MSD_OriginReady_bp2`, `TrackData`, `Analysis_Info`, `Diffusion_Parameters`
- **Velocity** → 8 sheets (Summary, SegmentPoints, InstantVelocity, LocalInstantVelocity, VelocitySeries_Selected, VelocityDistribution_Raw/_Filtered, SegmentFit)
- **Rate** → RawData / FittedData / Statistics / Summary; optional OriginLab-ready triple CSV
- **ROI fluorescence** → ROIPoints / ROISummary

### PNG

- Main kymograph figure: **300 dpi**
- Toolbar quick-save: 150 dpi, auto-named `{source_file}_{kymo_name}_kymograph.png`, with toast notification
- Analysis figures: 300 dpi

## Trace Editing

| Tool | Behavior |
|---|---|
| **Click Del** | Delete the trace nearest to the click (tolerance 0.5 data units) |
| **Box Del** | Rectangle-select to delete all intersecting traces |
| **Undo** | Restores whole-trace deletions from the history stack |
| **Delete Bad Points** | Point-level editor: left-click marks/unmarks points, right-click un-marks; live preview on the main figure; a deep-copy backup is taken first and can be restored with **Restore Backup** |

## Keyboard Shortcuts & Mouse Interactions

| Context | Input | Action |
|---|---|---|
| Polygon ROI | Left click | Add vertex |
| Polygon ROI | `Z` | Undo last vertex |
| Polygon ROI | `Enter` | Finish ROI (≥ 3 vertices) |
| Polygon ROI | `Esc` | Cancel ROI |
| Segment lists | Right click / `Delete` | Remove segment |
| Point editor | Left click | Mark/unmark point for deletion |
| Point editor | Right click | Undo mark |
| Diffusion plot | Drag green/blue lines | Adjust analysis time window |
| Multi-segment analyses | Drag on plot | Define time segments (✂️ click to cut trace) |

### Internal architecture (single file, ~10k lines)

| Class | Role |
|---|---|
| `KymoTrackerGUI` | Main window (1600×900); owns files, channels, tracks, ROI, analyses, exports |
| `CurvedPolygonROI` | Freehand polygon ROI tool |
| `ManualSegmentInputDialog` | Table-based manual time-segment entry (with auto equal-split) |
| `CacheManager` | Thread-safe FIFO cache (image redraws) |
| `ImageProcessor` | Vectorized normalization / contrast / RGB compositing |
| `MSDCalculator` | Vectorized MSD + linear fit |
| `RateCalculator` | Linear-fit / endpoint / moving-average rates |
| `CustomNavigationToolbar` | Intercepts the save button for auto-named async PNG export |
| `ExportDialog` | Export format picker |

Tracking and PNG saving run on background threads (`ThreadPoolExecutor`, max 2 workers); the UI updates via `root.after`. MSD, contrast and RGB compositing are NumPy-vectorized; image caches avoid redundant redraws. GUI text is in **English**; log output and code comments are partly in Chinese (CJK fonts configured automatically: Microsoft YaHei / SimHei / PingFang).

---

# Kymograph Sorter

A **ttkbootstrap / Tkinter + Matplotlib** desktop application for organizing, viewing and exporting C-Trap kymographs and scan images — sort files into category folders, stitch kymographs along the time axis, subtract backgrounds, overlay force curves, run force-clamp DNA length analysis, annotate figures, and export publication-ready 300-dpi PNGs. All in one bilingual (中文 / English) window.

## Features (Sorter)

- **File sorting** — batch-import images and C-Trap `.h5` kymographs, then **copy or move** them into user-defined category folders; link existing folders, filter by type, auto-advance to the next file after each classification
- **Built-in viewer** — H5 kymographs rendered as RGB composites; per-channel toggles, gain (0.1–500) & offset sliders, Y-flip, 1:1 aspect, µm/kbp axis units, adjustable tick steps
- **Kymograph stitching** — concatenate multiple `.h5` kymographs temporally (left = early, right = late) with per-file gain, line-time resampling, and memory-mapped fallback for large data; result loads straight back into the viewer with dashed seam lines
- **Background subtraction** — four modes: zero frame, temporal percentile, spatial side-columns, and a draggable ROI; median or mean statistics with optional row smoothing
- **Force & distance** — overlay any force channel under the kymograph (shared time axis); export force/distance channels to CSV with configurable downsampling
- **Force-clamp DNA length analysis** — select constant-force segments by dragging, compute Δdistance, local & pooled rates; CSV + JSON export
- **Scan mode** — frame-by-frame viewing of multi-frame scans
- **Annotation tools** — lines, arrows, text, dots; full styling; redrawn on every export
- **High-resolution export** — save the current view (with force curve and annotations) as a 300-dpi PNG; optional Auto Save on every classification
- **Bilingual UI** — one-click 中文 / English switch

## Requirements & File Layout

```bash
pip install ttkbootstrap pillow numpy pandas matplotlib h5py
pip install lumicks-pylake   # optional, required for .h5 support
```

| Package | Role | Required? |
|---|---|---|
| `ttkbootstrap` | UI framework & theme | ✅ |
| `numpy`, `pandas` | Data processing | ✅ |
| `Pillow` | Image loading | ✅ |
| `matplotlib` (TkAgg) | Display & figures | ✅ |
| `h5py` | Force-clamp analysis (reads Force LF/HF, Distance) | ✅ for that module |
| `lumicks.pylake` | Reading `.h5` kymographs/scans | Optional — without it the app still works on plain images |

These files must live in the **same directory**:

```
kymograph_sorter.py          # main application (entry point)
kymograph_theme.py           # custom ttkbootstrap theme ("kymograph") + toolbar flattening
kymograph_force_analysis.py  # ForceAnalysisWindow: force-clamp DNA length analysis
```

## Quick Start (Sorter)

```bash
python kymograph_sorter.py
```

1. **添加单个 / Batch Import** — add input folders (batch import adds the chosen folder *and all its first-level subfolders*)
2. Browse files in the viewer (↑ / ↓ keys); adjust gain/offset, crop, subtract background
3. Press **输出 (Output)** to scan a destination root — every subfolder becomes a category button
4. Click a category button to **copy/move** the current file into it (Auto Save optionally exports a 300-dpi PNG alongside)
5. Use **拼接 (Stitch)** to merge consecutive kymographs, or **保存 (Save)** to export the current figure

## Main Window

The window is split into a 330 px sidebar (left) and a workspace (right).

**Sidebar**

1. **输入源管理 (Input Source)** — add/remove/clear input folders; filter checkboxes for images and H5
2. **力与距离 (Force & Distance)** — force-clamp analysis entry, background subtraction tab, downsampling rate (default 100 Hz), force/distance CSV export
3. **文件列表 (File List)** — filename + location; H5 rows shown in grey; already-archived files are prefixed with 「✓」

**Workspace**

- Top toolbar: **输出 / 关联 / 拼接 / 新建 / 标注 / 保存 / 语言切换**, plus Copy-vs-Move mode selector
- Settings notebook (background, display, export tabs)
- Visualization area: kymograph/scan figure with optional force subplot; status bar at the bottom

## Sorting & Archiving

- **Categories** (`name → folder` mapping) are created three ways:
  - **输出 (Output)** — pick a root folder; all its subfolders register as categories
  - **关联 (Link)** — register a single existing folder
  - **新建 (New)** — create a new folder under a chosen parent
- Category buttons are laid out in a 2-column grid; **right-click a button to remove** that category.
- **Copy / Move mode** (radio buttons): copy uses `shutil.copy2`; move additionally removes stale copies of the file from *other* category folders.
- Archiving runs in a background thread and **auto-advances** to the next file when done.
- **Auto Save**: when enabled, classifying a file also exports the current figure (with force curve and all annotations) to the destination folder at 300 dpi, using the configured figure size (default 5.0 × 4.0 in).

## Kymograph Stitching

Open via **拼接 (Stitch)**. Add ≥ 2 H5 files in temporal order (left = early, right = late); each row has its own gain (0.01–500).

- Each file's `line_time_seconds` is read; the **fastest** (smallest) line time becomes the common grid.
- Slower kymographs are upsampled along time with nearest-neighbor (`np.repeat`); faster ones are downsampled by bin averaging.
- Common height = smallest row count across files/channels.
- If a single float32 channel would exceed **200 MB**, data is streamed through an `np.memmap` temp file instead of RAM.
- Channels (red/green/blue) are stitched independently and saved as `np.savez_compressed` with keys `line_time`, `pixel_size` (hard-coded 0.1 µm), `stitch_times`.
- Output naming parses `YYYYMMDD-HHMMSS Kymograph N` filenames → e.g. `Stitch: 103015 K1 + 104522 K2 (Date: 20240820).npz`, saved next to the first input file.
- The stitched result is **loaded back into the main viewer automatically**, with white dashed seam lines at the junctions.

## Force & Distance Tools

- **Force overlay** — pick a channel (Force 1x/1y/2x/2y) from the dropdown to draw it in a shared-X subplot below the kymograph; data is sliced to the kymograph's start/stop range and downsampled to ~100 Hz.
- **CSV export** (`导出力与距离数据`) — tick HF (raw) and/or Downsampled channels; downsampling uses pylake's `downsampled_by` toward the configured target rate (default 100 Hz); `Distance` / `Distance 1` are interpolated onto the force timestamps with `np.interp`. Outputs `<file>_force_export.csv` plus `<file>_desc.txt` (the H5 description).

## Force-Clamp DNA Length Analysis

Entry: sidebar section 2 → **恒力 DNA 长度分析** (opens `ForceAnalysisWindow`, 1250×840, three shared-X plots: distance / force / rate).

- Reads **Force LF/HF** and **Distance** channels directly with h5py; HF is block-averaged to ≤ 100 Hz.
- Force is interpolated onto distance timestamps; gaps larger than 3× the median sampling interval become NaN (no extrapolation).
- Constant-force gating: target force ± tolerance (optionally on |F|); segments need ≥ 3 points and ≥ minimum duration (default 1 s).
- Per-segment rolling median smoothing (default 0.5 s), rolling local OLS rate (default 2 s window, nm/s), and Δdistance from baseline medians (default 1 s at each end).
- Outputs pooled slope (nm/s) with R², force mean/SD, per-segment slopes; exports `_constant_force.csv` + `_analysis.json` (full parameters & method notes), plus PNG/PDF figures.
- **Scope note**: the analysis reports the *instrument* distance — it deliberately does **not** convert to dsDNA/ssDNA contour length or bp/s.

Full usage, definitions and validation tests: **[README_ConstantForceAnalysis.md](README_ConstantForceAnalysis.md)**. Run the numerical regression suite with:

```bash
python -m unittest -v test_force_analysis
```

## Image Display Controls

| Control | Range / behavior |
|---|---|
| RGB channel checkboxes | Toggle red/green/blue independently |
| Gain slider | 0.1–500 (default 25); display = `(raw + offset) × gain / 255` |
| Offset slider | −5 … +5 (default 0) |
| Reset | Restore gain/offset defaults |
| Flip Y | Mirror the vertical axis |
| 等比 (1:1) | Lock aspect ratio (auto-locked for scans, auto-unlocked for kymographs) |
| Y axis units | µm ↔ kbp (conversion uses 0.34 nm/bp by default, editable) |
| X/Y Step | Tick spacing (defaults 20.0 s / 1.0 µm) |
| W/H | Output figure size in inches (for Save / Auto Save) |
| Two-point ROI crop | H5 only; activates a red dashed MultiCursor spanning image and force subplot |

## Annotation Tools

Open via **标注 (Annot)** — a floating 420×640 panel.

- **Tools**: horizontal line, vertical line, free line, arrow, text, dot
- **Styling**: 8 preset colors + custom color picker, line width 0.5–5, line style (solid/dashed/dotted/dash-dot), opacity 0.1–1.0, font size 6–48 pt
- Lines/arrows: two clicks with live preview; right-click cancels
- Text: left-click to place (draggable), right-click opens a live editor (type to update, deletable)
- Undo last / clear all; annotations are **redrawn on every PNG/Auto Save export** and cleared when switching files

## Internationalization & Theme

- ~200 UI strings in a built-in `I18N` dict (zh/en); the **EN/中文** button rebuilds the UI in the other language while restoring input folders, category buttons, file list state and the current selection.
- Custom ttkbootstrap theme **"kymograph"** (registered by `kymograph_theme.py`): light base, teal primary `#237F78`, dark `#27363B`, Microsoft YaHei UI 10 pt, 30 px Treeview rows, flattened Matplotlib toolbar.
- Matplotlib's built-in `s` / `f` shortcuts are removed globally to avoid conflicts.
- Keyboard: `↑` / `↓` switch files; `Enter` in entries/spinboxes applies & refreshes; right-click a category button to remove it; hover the file list for a full-path tooltip. (There are no number-key classification shortcuts — classification is done by clicking category buttons.)

### Supported formats

- **Images**: `.png` `.jpg` `.jpeg` `.tif` `.tiff` `.bmp` `.gif`
- **H5** (via pylake): kymographs (first kymo, `red/green/blue_image`, 99.5-percentile scaling; physical axes from `line_time_seconds` × columns and rows × `pixel_size_um` — deliberately *not* `scan_width_um`, to avoid stretching) and scans (multi-frame 3D scans split into frames with a navigation spinbox)
- **Stitched data**: `.npz` produced by the Stitch tool (auto-loaded)

---

## Notes & Quirks

- **`KymoTracker3.4 .py` contains a space** before `.py` — quote it on the command line, or rename the file before publishing.
- `.h5` files must come from a LUMICKS C-Trap (read via pylake).
- The 0.34 nm/bp constant assumes **B-form DNA** — it does not apply to RNA or protein.
- Default values (KymoTracker): line_width 5, pixel_threshold 1.0, window 8, max_lines 10, filter_length 20, localization σ 30 nm, sliding window 30 s, |v| cap 1000 bp/s.
- Kymograph Sorter hard-codes `pixel_size = 0.1 µm` for stitched output; the 200 MB memmap threshold and ~100 Hz force display downsampling are fixed constants.
- Sorter's display compositing uses `(raw + offset) × gain / 255`, while snapshot export uses `(raw / max99.5) × gain` — exported PNGs may differ slightly from the screen.
- Already-archived files are marked with a 「✓」 prefix in Sorter's file list.
- Version history is kept as separate files (`KymoTracker3.x-*.py`, `kymograph_sorter*.py`) following the author's one-file-per-version convention.
- A few legacy/dead code paths remain in KymoTracker (duplicate method definitions, unused imports) — harmless, kept for reference.

## License

For internal laboratory research use only.
