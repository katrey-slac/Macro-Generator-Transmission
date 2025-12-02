import pandas as pd
import tkinter as tk
from tkinter import messagebox


# ---- Load and prepare data ----
def load_data(filepath):
    """Load Excel file and compute coordinates."""
    df = pd.read_excel(filepath, header=3, usecols="A:D", sheet_name="Fill out")

    def generate_position_dict(x_start, y_start, rows, cols, x_spacing, y_spacing):
        positions = {}
        pos_counter = 1
        for r in range(rows):
            for c in range(cols):
                x = x_start + c * x_spacing
                y = y_start + r * y_spacing
                positions[pos_counter] = (x, y)
                pos_counter += 1
        positions["_rows"] = rows
        positions["_cols"] = cols
        return positions

    base_coords = {
        key.lower(): value
        for key, value in {
            "washers_v1": generate_position_dict(0.5, 0.5, 3, 5, 1, 1),
            "Films - Circles V1": generate_position_dict(7, 6, 7, 7, 11, 12.33),
            "Capillary - 1.5 OD": generate_position_dict(1.15, 50, 1, 15, 5.5, 0),
            "Capillary - 1.0 OD": generate_position_dict(1.15, 50, 1, 15, 5.5, 0),
            "Capillary - 2.0 OD": generate_position_dict(1.15, 50, 1, 15, 5.5, 0),
            "NMR - 5.0 OD": generate_position_dict(1.15, 50, 1, 15, 5.5, 0)
        }.items()
    }

#The locations for this first version will not be representative of the next capillary cassettes as they were changed

    def compute_coordinates(row):
        ctype = row["Cassette Type"].lower().strip()
        pos = row["Position"]
        slot = row["Cassette #"]
        bx, by = base_coords[ctype][pos]
        columns = 4
        x_spacing = 110
        y_spacing = 98
        x_shift = ((slot - 1) % columns) * x_spacing
        y_shift = ((slot - 1) // columns) * y_spacing
        return bx + x_shift, by + y_shift

    df[["x", "y"]] = df.apply(compute_coordinates, axis=1, result_type="expand")
    return df, base_coords


# ---- Cassette details window ----
def show_cassette_details(cassette_num, df, base_coords, sample_parameters):
    """Open a detail window for a single cassette."""
    subdf = df[df["Cassette #"] == cassette_num]
    if subdf.empty:
        return

    ctype = subdf.iloc[0]["Cassette Type"].lower().strip()

    # Get layout dict
    layout = base_coords[ctype]

    # Extract rows and columns from metadata
    rows = layout["_rows"]
    cols = layout["_cols"]

    # Get positions (ignore "_rows" and "_cols" keys)
    positions = [k for k in layout.keys() if isinstance(k, int)]

    pos_to_data = {
        row["Position"]: (row["Sample Name*"], row["x"], row["y"])
        for _, row in subdf.iterrows()
    }

    win = tk.Toplevel()
    win.title(f"Cassette {cassette_num} - {ctype} Details")

    # --- Main container frame ---
    main_frame = tk.Frame(win)
    main_frame.pack(fill="both", expand=True)

    # --- Canvas and scrollbars ---
    canvas = tk.Canvas(main_frame)
    canvas.pack(side="top", fill="x")
    h_scroll = tk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
    h_scroll.pack(side="bottom", fill="x")
    canvas.configure(xscrollcommand=h_scroll.set)

    # Inner frame inside canvas to hold your widgets
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    entry_widgets = {}
    coord_labels = {}

    for idx, pos in enumerate(positions):
        r = idx // cols
        c = idx % cols
        frame = tk.Frame(inner_frame, borderwidth=1, relief="solid", width=120, height=80, bg= "powder blue")
        frame.grid_propagate(False)
        frame.grid(row=r, column=c, padx=5, pady=5)

        if pos in pos_to_data:
            name, x, y = pos_to_data[pos]
            tk.Label(frame, text=f"{pos} {name}", font="SegoeUI 10 bold").pack()
            coord_label = tk.Label(frame, text=f"Current: ({x:.2f}, {y:.2f})", bg= "powder blue")
            coord_label.pack()
            coord_labels[pos] = coord_label

            entry_frame = tk.Frame(frame)
            entry_frame.pack()

            tk.Label(entry_frame, text="X:").pack(side="left")
            x_entry = tk.Entry(entry_frame, width=7)
            x_entry.insert(0, f"{x:.2f}")
            x_entry.pack(side="left")

            tk.Label(entry_frame, text="  Y:").pack(side="left")
            y_entry = tk.Entry(entry_frame, width=7)
            y_entry.insert(0, f"{y:.2f}")
            y_entry.pack(side="left")

            entry_widgets[pos] = (name, x_entry, y_entry)
        else:
            tk.Label(frame, text="Empty").pack()
    # Update scrollregion to fit all widgets
    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas_height = min(inner_frame.winfo_reqheight(), 550)
    canvas_width = min(inner_frame.winfo_reqwidth(), 1200)
    canvas.configure(height=canvas_height, width=canvas_width)

        # --- Save button at bottom of main_frame ---
    save_btn = tk.Button(main_frame, text="Save", command=lambda: save_coords(),
                         bg="chartreuse2", fg="black")
    save_btn.pack(pady=10)

    # # --- Auto-fit window size with max limits ---
    # req_width = inner_frame.winfo_reqwidth()
    # req_height = inner_frame.winfo_reqheight()
    # final_width = min(req_width + 20, 1000)
    # final_height = min(req_height + 20, 1600)

    # win.geometry(f"{final_width}x{final_height}")
    win.update_idletasks()
    # win.minsize(200, 150)
    # win.maxsize(1200, 650)

    def save_coords():
        # Update dataframe and sample_parameters when user clicks Save
        for pos, (name, x_entry, y_entry) in entry_widgets.items():
            try:
                new_x = float(x_entry.get())
                new_y = float(y_entry.get())
                df.loc[ (df["Cassette #"] == cassette_num) & (df["Position"] == pos), ["x", "y"]] = [new_x, new_y]

                # Only update label if it exists
                if pos in coord_labels:
                    coord_labels[pos].config(text=f"Current: ({new_x}, {new_y})")

            except ValueError:
                tk.messagebox.showerror("Error", f"Invalid number for position {pos}", parent=win)

        # Update the shared sample_parameters dictionary
        sample_parameters["sample_names"] = list(df["Sample Name*"])
        sample_parameters["lpxs"] = list(df["x"])
        sample_parameters["lpys"] = list(df["y"])

        tk.messagebox.showinfo("Saved", "Coordinates updated successfully.", parent=win)

    # save_btn = tk.Button(win, text="Save", command=save_coords, bg="chartreuse2", fg="black")
    # save_btn.pack(pady=10, anchor="center")

    # save_btn.grid(row=rows + 1, column=0, columnspan=cols, pady=10)


# ---- Draw layout and attach to root ----
def open_excel_data_popup(root, df, base_coords, sample_parameters):
    """Opens the layout GUI and updates sample_parameters in real-time."""
    # df, base_coords = load_data(filepath)
    #
    # # Initial update of sample_parameters when GUI opens
    # sample_parameters["sample_names"] = list(df["Sample Name"])
    # sample_parameters["lpxs"] = list(df["x"])
    # sample_parameters["lpys"] = list(df["y"])

    layout_win = tk.Toplevel(root)
    layout_win.title("Cassette Layout")

    frame = tk.Frame(layout_win)
    frame.pack(padx=20, pady=20)

    rows, cols = 3, 4
    slot = 1

    for r in range(rows):
        for c in range(cols):
            if slot == 12:
                btn_text = "Slot 12\nStandards"
                btn_state = "disabled"
                btn_bg = "light grey"
                cmd = None
            else:
                subdf = df[df["Cassette #"] == slot]
                if not subdf.empty:
                    ctype = subdf.iloc[0]["Cassette Type"]
                    btn_text = f"Slot {slot}\n{ctype}"
                    btn_state = "normal"
                    btn_bg = "light blue"
                    cmd = lambda s=slot: show_cassette_details(s, df, base_coords, sample_parameters)
                else:
                    btn_text = f"Slot {slot}\n(Empty)"
                    btn_state = "disabled"
                    btn_bg = "light grey"
                    cmd = None

            btn = tk.Button(
                frame, text=btn_text, width=15, height=4,
                state=btn_state, bg=btn_bg, command=cmd
            )
            btn.grid(row=r, column=c, padx=10, pady=10)
            slot += 1
