# Macro Generator

A simple GUI tool for generating SPEC macro files at BL1-5. Instead of writing macros by hand, you fill out a form and it spits out a ready-to-run macro file.

## What it does

- Generates transmission experiment macros for SAXS, WAXS, or both
- Handles sample positions from Excel files or manual entry
- Supports multiple cassette types (washers, films, capillaries, NMR tubes)
- Creates preliminary photo macros to check your sample positions
- Lets you tweak individual sample coordinates before running

## Requirements

- Python 3.x
- pandas
- tkinter (usually comes with Python)

Install pandas if you don't have it:

## How to run

## Quick start

1. **Pick a save location** - Click "Select Home Directory" and choose where you want the macro saved
2. **Name your macro** - No spaces allowed, use underscores (e.g., `my_experiment_001`)
3. **Set your scan parameters** - Exposure time, number of images, loops, etc.
4. **Add sample info** - Either paste it manually or load from an Excel file
5. **Hit "Save Macro File"** - You'll get a command to copy into SPEC

## Loading samples from Excel

Your Excel file needs a sheet called "Fill out" with these columns starting at row 4:

- Column A: Cassette #
- Column B: Position
- Column C: Cassette Type
- Column D: Sample Name*

Click "Select Excel File" first, then "Sample Info from Excel" to open the layout view. You can click on individual cassette slots to adjust coordinates if needed.

## Files

| File | What it does |
|------|--------------|
| macro_generator_gui.py | Main GUI window |
| excel_data_popup.py | Handles Excel import and cassette layout view |
| data_popup_V1.py | Manual data entry popup |
| macro_writer.py | Actually writes the macro files |
| success_SPEC_copy.py | Shows the success popup with the SPEC command |

## Cassette types supported

- Washers V1 (3x5 grid)
- Films - Circles V1 (7x7 grid)
- Capillary - 1.0, 1.5, 2.0 OD (1x15 row)
- NMR - 5.0 OD (1x15 row)

## Tips

- The "Same as macro" button copies your macro name to the data folder field
- Dark collection is optional - set frequency to 0 to skip it
- Rocking is optional - leave at 0 if you don't need it
- You can save a photo macro first to verify positions before your real run

## Troubleshooting

**"Please select an Excel file first"** - You clicked "Sample Info from Excel" before selecting a file. Click "Select Excel File" first.

**Coordinates look wrong** - Click on the cassette slot in the layout view to manually adjust x/y positions.

**Macro won't run in SPEC** - Make sure there are no spaces in your macro name.

---

*Katerina Reynolds, 2025*