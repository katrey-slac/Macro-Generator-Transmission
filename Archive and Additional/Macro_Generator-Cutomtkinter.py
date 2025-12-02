import customtkinter as ctk
import tkinter as tk
import os
from customtkinter import CTkToplevel
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def safe_int(value, default=0):
    """
    Convert value to int, return default if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """
    Convert value to float, return default if conversion fails.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def on_closing():
    if tk.messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()

def select_folder(folder_var):
    folder_selected = tk.filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

def update_scrollregion(event=None):
    canvas.config(scrollregion=canvas.bbox("all"))

def update_label(var_value, label_var):
    label_var.set(var_value.get())

# opens a popup to enter the sample names, lpxs, lpys and then saves that data
sample_popup_window = None
def open_sample_popup(sample_count_var, sample_data):
    global sample_popup_window

    num_samples = safe_int(sample_count_var.get())
    if num_samples == 0:
        return

    # Check if popup already exists and is still open
    if sample_popup_window is not None and sample_popup_window.winfo_exists():
        sample_popup_window.focus_force()  # bring existing window to front
        return

    # Create a popup window
    sample_popup_window = CTkToplevel(root)
    sample_popup_window.title("Enter Sample Information")
    sample_popup_window.transient(root)    # stay on top of root

    def close_sample_popup():
        global sample_popup_window
        if sample_popup_window is not None:
            sample_popup_window.destroy()
            sample_popup_window = None

    # Register the window close protocol
    sample_popup_window.protocol("WM_DELETE_WINDOW", close_sample_popup)

    # Container frame to hold canvas and buttons separately
    content_frame = ctk.CTkFrame(sample_popup_window)
    content_frame.pack(fill=ctk.BOTH, expand=True)

    max_per_row = 10  # Maximum number of samples per row
    entry_width = 112  # Approximate pixel width for one sample column
    # Calculate required canvas width
    num_columns = min(num_samples, max_per_row)
    canvas_width = num_columns * entry_width
    rows_needed = (num_samples + max_per_row - 1) // max_per_row  # ceiling division
    canvas_height = min(rows_needed * 140, 360)  # 140px per row, capped at 360

    # Create a scrollable canvas to hold the sample entry form
    canvas = tk.Canvas(content_frame, width=canvas_width, height=canvas_height)
    canvas.pack(side="left", fill="both", expand=True)

    # Add vertical scrollbar to canvas
    scrollbar = ctk.CTkScrollbar(content_frame,  command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Internal frame that will hold all the entry widgets
    form_frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=form_frame, anchor="nw")

    # Update scroll region whenever form_frame is resized
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    form_frame.bind("<Configure>", on_frame_configure)

    # Initialize lists for storing user inputs
    sample_entries, lpx_entries, lpy_entries = [], [], []

    # Fetch previous data if exists, or fill with empty strings
    prev_names = sample_data.get("sample_names", [""] * num_samples)
    prev_lpxs = sample_data.get("lpxs", [""] * num_samples)
    prev_lpys = sample_data.get("lpys", [""] * num_samples)

    for i in range(num_samples):
        base_row = (i // max_per_row) * 5
        column = i % max_per_row

        # Create table headers for each sample dynamically
        ctk.CTkLabel(form_frame, text=f"Sample {i + 1}", font=("Arial", 10, "bold")).grid(row=base_row, column=column,
                                                                                      padx=5, pady=5)

        # Create entry field for sample names
        ctk.CTkLabel(form_frame, text="Name:").grid(row=base_row + 1, column=column, padx=5, pady=2)
        name_entry = ctk.CTkEntry(form_frame, width=15)
        name_entry.insert(0, prev_names[i])
        name_entry.grid(row=base_row + 2, column=column, padx=5, pady=2)
        sample_entries.append(name_entry)

        # Create entry fields for LPX and LPY (position coordinates)
        ctk.CTkLabel(form_frame, text="Position (lpx, lpy):").grid(row=base_row + 3, column=column, padx=5, pady=2)
        position_frame = ctk.CTkFrame(form_frame)
        position_frame.grid(row=base_row + 4, column=column, padx=5, pady=2)

        # LPX entry field
        lpx_entry = ctk.CTkEntry(position_frame, width=7)
        lpx_entry.insert(0, str(prev_lpxs[i]))
        lpx_entry.pack(side=ctk.LEFT)

        # Comma seperator
        ctk.CTkLabel(position_frame, text=",").pack(side=ctk.LEFT)

        # LPY entry field
        lpy_entry = ctk.CTkEntry(position_frame, width=7)
        lpy_entry.insert(0, str(prev_lpys[i]))
        lpy_entry.pack(side=ctk.LEFT)

        lpx_entries.append(lpx_entry)
        lpy_entries.append(lpy_entry)

    # Save function to validate input and store the results
    def save_data():
        for i in range(num_samples):
            name = sample_entries[i].get().strip()
            lpx = lpx_entries[i].get().strip()
            lpy = lpy_entries[i].get().strip()

            # Check if sample name is missing
            if not name:
                tk.messagebox.showerror("Missing Sample Name", f"Sample {i + 1} name is required.", parent=sample_popup_window)
                return

            # Check for spaces in sample name
            if " " in name:
                tk.messagebox.showerror("Invalid Sample Name", f"Sample {i + 1} name cannot contain spaces.",
                                        parent=sample_popup_window)
                return

            # Check for missing LPX or LPY values
            if not lpx or not lpy:
                tk.messagebox.showerror("Missing Input", f"LPX and LPY must be filled for Sample {i + 1}.",
                                        parent=sample_popup_window)
                return

        # Save the entered values to the provided sample_data dictionary
        try:
            sample_data["sample_names"] = [e.get().strip() for e in sample_entries]
            sample_data["lpxs"] = [safe_float(e.get().strip()) for e in lpx_entries]
            sample_data["lpys"] = [safe_float(e.get().strip()) for e in lpy_entries]
            close_sample_popup()  # Only close if all inputs are valid
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "LPX and LPY must be numbers.", parent=sample_popup_window)

    # Buttons for Save and Cancel
    button_frame = ctk.CTkFrame(sample_popup_window)
    button_frame.pack(side=ctk.BOTTOM, anchor="center", padx=10, pady=10)

    ctk.CTkButton(button_frame, text="Cancel", command=close_sample_popup, text_color="white", fg_color="red").pack(side="left",
                                                                                                    padx=5)
    ctk.CTkButton(button_frame, text="Save", command=save_data, text_color="white", fg_color="green").pack(side="right", padx=5)



excel_data_popup_window = None
def open_excel_data_popup(sample_count_var, sample_data):
    global excel_data_popup_window

    num_samples = safe_int(sample_count_var.get())
    if num_samples == 0:
        return

    # If popup already exists and is open, just bring it to front and return
    if excel_data_popup_window is not None and excel_data_popup_window.winfo_exists():
        excel_data_popup_window.focus_force()
        return

    # Create new popup window
    excel_data_popup_window = CTkToplevel(root)
    excel_data_popup_window.title("Paste Excel Data")
    excel_data_popup_window.transient(root)     # Make popup stay on top of root window

    # When popup is closed, reset the global variable
    def on_close():
        global excel_data_popup_window
        excel_data_popup_window.destroy()
        excel_data_popup_window = None

    excel_data_popup_window.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkLabel(excel_data_popup_window,
             text="Paste values copied from Excel into the fields below.\nEach should be one column of values (one per line).",
             justify="left").pack(pady=5)

    # Main paste area
    text_frame = ctk.CTkFrame(excel_data_popup_window)
    text_frame.pack(padx=10, pady=5)

    ctk.CTkLabel(text_frame, text="Sample Names").grid(row=0, column=0)
    ctk.CTkLabel(text_frame, text="LPX Values").grid(row=0, column=1)
    ctk.CTkLabel(text_frame, text="LPY Values").grid(row=0, column=2)

    sample_text = ctk.CTkTextbox(text_frame, height=15, width=20)
    sample_text.grid(row=1, column=0, padx=5)

    lpx_text = ctk.CTkTextbox(text_frame, height=15, width=20)
    lpx_text.grid(row=1, column=1, padx=5)

    lpy_text = ctk.CTkTextbox(text_frame, height=15, width=20)
    lpy_text.grid(row=1, column=2, padx=5)

    # Restore previous pasted values if they exist
    if "excel_raw_names" in sample_data:
        sample_text.insert("1.0", sample_data["excel_raw_names"])
    if "excel_raw_lpxs" in sample_data:
        lpx_text.insert("1.0", sample_data["excel_raw_lpxs"])
    if "excel_raw_lpys" in sample_data:
        lpy_text.insert("1.0", sample_data["excel_raw_lpys"])

    def save_pasted_data():
        raw_names = sample_text.get("1.0", ctk.END).strip()
        raw_lpxs = lpx_text.get("1.0", ctk.END).strip()
        raw_lpys = lpy_text.get("1.0", ctk.END).strip()

        names = raw_names.splitlines()
        lpxs = raw_lpxs.splitlines()
        lpys = raw_lpys.splitlines()

        if not (len(names) == len(lpxs) == len(lpys)):
            tk.messagebox.showerror("Mismatch", "Each column must have the same number of values.", parent=excel_data_popup_window)
            return

        if len(names) != num_samples:
            confirm = tk.messagebox.askyesno(
                "Sample Count Mismatch",
                f"You selected {num_samples} samples, but pasted {len(names)}.\nProceed and overwrite count?",
                parent=excel_data_popup_window
            )
            if not confirm:
                return
            sample_count_var.set(str(len(names)))  # Update dropdown

        try:
            # Save parsed values
            sample_data["sample_names"] = [name.strip() for name in names]
            sample_data["lpxs"] = [safe_float(val.strip()) for val in lpxs]
            sample_data["lpys"] = [safe_float(val.strip()) for val in lpys]

            # Save raw pasted values for restoring later
            sample_data["excel_raw_names"] = raw_names
            sample_data["excel_raw_lpxs"] = raw_lpxs
            sample_data["excel_raw_lpys"] = raw_lpys
            on_close()

        except ValueError:
            tk.messagebox.showerror("Invalid Input", "LPX and LPY must be numeric.", parent=excel_data_popup_window)

    # Buttons
    button_frame = ctk.CTkFrame(excel_data_popup_window)
    button_frame.pack(pady=10)

    ctk.CTkButton(button_frame, text="Cancel", command=excel_data_popup_window.destroy, fg_color="red", text_color="white").pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Save", command=save_pasted_data, fg_color="green", text_color="white").pack(side="right", padx=5)


# Main function to create the macro text file with user inputs
def create_macro_file():
    if not home_directory_var.get():
        tk.messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.",
                             parent=root)

    # Validate macro name
    if " " in macro_name_var.get():
        tk.messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces.\nPlease use underscores (_) or hyphens (-).",
                             parent=root)
        return

    # Validate values for inputs
    if safe_int(exposure_time_var.get()) == 0:
        tk.messagebox.showerror("Invalid Exposure Time",
                             "Exposure time cannot be zero. Please correct.",
                             parent=root)
        return

    if safe_int(num_images_var.get()) == 0:
        tk.messagebox.showerror("Invalid Number of Images",
                             "Number of images cannot be zero. Please correct.",
                             parent=root)
        return

    if safe_int(num_loops_var.get()) == 0:
        tk.messagebox.showerror("Invalid Number of Loops",
                             "Number of loops cannot be zero. Please correct.",
                             parent=root)
        return

    if not sample_parameters.get('sample_names'):
        tk.messagebox.showerror("Sample Information Missing",
                             "Please input sample information.",
                             parent=root)
        return

    if not AXS_var.get():
        messagebox.showerror("Scattering Range Not Selected",
                             "Please select scattering range.",
                             parent=root)

    # Retrieve values from the input fields
    macro_name = macro_name_var.get()
    exposure_time = safe_int(exposure_time_var.get())
    sleep_time = safe_int(sleep_time_var.get())
    num_images = safe_int(num_images_var.get())
    num_loops = safe_int(num_loops_var.get())
    num_pos = sample_count_var.get()
    dark_frequency = safe_int(dark_frequency_var.get())
    dark_duration = safe_int(dark_duration_var.get())

    try:
        rock_lpx = safe_float(rock_lpx_var.get())
    except ValueError:
        rock_lpx = 0.0  # or handle as needed
    try:
        rock_lpy = safe_float(rock_lpy_var.get())
    except ValueError:
        rock_lpy = 0.0
    print("Rocking input values:", rock_lpx, rock_lpy)

    # base_Dir = home_directory_var.get()+ "\\" + data_folder_var.get()
    spec_base_Dir = (home_directory_var.get() + "\\" + data_folder_var.get()).replace("\\", "/")
    spec_base_Dir = spec_base_Dir.replace("X:/bl1-5/", "")
    print(spec_base_Dir)

    rocking_lines = ""
    if rock_lpx != 0.0:
        rocking_lines += f"rock lpx {rock_lpx}\n"
    if rock_lpy != 0.0:
        rocking_lines += f"rock lpy {rock_lpy}\n"
    is_rocking = rock_lpx != 0.0 or rock_lpy != 0.0

    camera_map = {
        "Bottom Camera": "BL1-5_bottom_camera",
        "Side Camera": "BL1-5_side_camera",
        "Top Camera": "BL1-5_top_camera"
    }

    camera_lines = ""

    if bottom_cam_var.get():
        camera_lines += f'          epics_put("MSD_Local_Cameras:{camera_map["Bottom Camera"]}:save_frame", base_filename)\n'
    if side_cam_var.get():
        camera_lines += f'          epics_put("MSD_Local_Cameras:{camera_map["Side Camera"]}:save_frame", base_filename)\n'
    if top_cam_var.get():
        camera_lines += f'          epics_put("MSD_Local_Cameras:{camera_map["Top Camera"]}:save_frame", base_filename)\n'

    detector_map = axs_mapping = {
        "SAXS": [
            'pd enable # Enable SAXS 1M detector',
            'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2))',
            'pd save # save SAXS data',
            'pd disable  # Disable SAXS detector after scan'
        ],
        "WAXS": [
            'pdw enable #Enable WAXS detector',
            'eval(sprintf("pd savepath %s/WAXS", pilatus_baseDir2))',
            'pdw save	# save WAXS data',
            'pdw disable  # Disable WAXS detector after scan'
        ],
        "Both": [
            'pd enable # Enable SAXS 1M detector \n            pdw enable #Enable WAXS detector',
            'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2)) \n             eval(sprintf("pdw savepath %s/WAXS", pilatus_baseDir2))',
            'pd save # save SAXS data \n               pdw save	# save WAXS data',
            'pd disable  # Disable SAXS detector after scan \n             pdw disable  # Disable WAXS detector after scan'
        ]
    }

    # remove dark data capture from macro if unnecessary
    dark_frame_block = ""
    if dark_frequency != 0:
        dark_frame_block = f"""
                if (pos_ctr % dark_frequency == 0) {{
                sclose
                sleep({sleep_time})
                data_dir = sprintf("dark_run%d_pos%d_", run_ctr, pos_ctr)  # No trailing '/'
                p data_dir

                p "Taking data"

                wait_time = 0
                loopscan_command = sprintf("loopscan %d %f %f", num_images, dark_exposure, wait_time)

                {detector_map.get(AXS_var.get(), [])[0]}

                eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
                {detector_map.get(AXS_var.get(), [])[1]}

                {detector_map.get(AXS_var.get(), [])[2]}

                # Take the actual data
                eval(loopscan_command)

                {detector_map.get(AXS_var.get(), [])[3]}
                # Implement sleep time between scans if required
                if (sleep_time > 0) {{
                printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
                sleep(sleep_time)
                p ".... DON'T hit control-C until we sleep again\\n"
                sopen
                }}
                }}

            """

    # Define the content of the text file with user-defined values - this is the meat
    content = f"""
exposure_time = {exposure_time}          # exposure time for each image (in seconds)
num_loops = {num_loops}                # number of images in the scan 
sleep_time = {sleep_time}                # sleep time between each image (in seconds), enter a value of 0 to disable it
num_images = {num_images}
dark_frequency = {dark_frequency}
dark_exposure = {dark_duration}

#Define the sample names
sample_names = {sample_parameters['sample_names']}

# Define list of coordinates (lpx, lpy)
lpx_positions = {sample_parameters['lpxs']}  # x positions
lpy_positions = {sample_parameters['lpys']}    # y positions
num_positions = {len(sample_parameters['lpxs'])}  # Get the number of coordinates

############################
#File name and location
############################

spec_baseDir = "{spec_base_Dir + "/"}" 		#Needs trailing '/'
pilatus_baseDir2 = sprintf('~/data/%s', spec_baseDir)

loop_ctr = 0
pos_ctr = 0

# if (!exists("run_ctr")) {{  # Check if run_ctr exists, initialize if not
#     run_ctr = 0;
# }}
run_ctr += 1  # Increment global run counter to prevent accidental deletion

# Execute directory creation using Linux based commands
unix(sprintf('mkdir -p %s', pilatus_baseDir2))
unix(sprintf('mkdir -p %s/SAXS %s/WAXS', pilatus_baseDir2, pilatus_baseDir2))

##############
pd stop

sleep(5.0)

{rocking_lines.strip()}

sopen

for (loop_ctr=0; loop_ctr < num_loops; loop_ctr++) {{
    for (pos_ctr = 0; pos_ctr < num_positions; pos_ctr++) {{  # Loop through coordinates
        {dark_frame_block}
        base_filename = sample_names[pos_ctr]

        # Move to the next coordinate pair
        umv lpx lpx_positions[pos_ctr]
        umv lpy lpy_positions[pos_ctr]

        sopen
        #Create a variable for file name containing the data
        data_dir = sprintf("%s_run%d_loop%d_pos%d", base_filename, run_ctr, loop_ctr, pos_ctr)  #No trailing '/'
        sleep(5)

        #save images from cameras (if any listed)
{camera_lines.rstrip()}

        p data_dir

        #############################################################################
        # Create directories for SAXS and WAXS and save data in those
        #############################################################################
            p "Taking data"

            wait_time = 0
            loopscan_command = sprintf("loopscan %d %f %f", num_images, exposure_time, wait_time)

            {detector_map.get(AXS_var.get(), [])[0]}

            eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
            {detector_map.get(AXS_var.get(), [])[1]}

            {detector_map.get(AXS_var.get(), [])[2]}

            #Take the actual data
            eval(loopscan_command)

            {detector_map.get(AXS_var.get(), [])[3]}

            # Implement sleep time between scans if required
            if (sleep_time > 0) {{
                printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
                sleep(sleep_time)
                p ".... DON'T hit control-C until we sleep again\\n"
            }}    
    }}    
}}

{'rock no' if is_rocking else ''}

"""

    file_path = f"{home_directory_var.get()}/{macro_name}.txt"
    print(file_path)

    # If a valid file path is selected, check if file exists and then write content to the file
    try:
        if file_path:
            if os.path.exists(file_path):
                overwrite = messagebox.askyesno("File Exists",
                                                "A file with that name already exists.\nDo you want to overwrite it?",
                                                parent=root)
                if not overwrite:
                    return  # Exit function if user chooses not to overwrite

    # if the file is open it will trigger Errno 13. This checks for that and will produce a prompt for the user
    except PermissionError:
        messagebox.showerror(
            "Permission Denied",
            f"Cannot access or overwrite the file '{file_path}'.\n\nPlease close the file if it's open in another program and restart the application."
        )
        return
    # write/save the text file
    try:
        with open(file_path, "w") as file:
            file.write(content)

        # Show success popup
        messagebox.showinfo("Success", "File saved successfully!", parent=root)

    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)

####################################################################################################################

# --- Build Main Window ---
root = ctk.CTk()
root.title("Macro Generator")
root.protocol("WM_DELETE_WINDOW", on_closing)

frame = ctk.CTkFrame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

# Save Location Section
folder_names = ctk.CTkFrame(frame)
folder_names.grid(row=0, column=0, sticky="ew", pady=5)

home_directory_var = ctk.StringVar()
home_button = ctk.CTkButton(folder_names, text="Select Home Directory", command=lambda: select_folder(home_directory_var))
home_button.grid(row=0, column=0, padx=5, pady=5)

# Label inside a scrollable area
canvas = ctk.CTkCanvas(folder_names, width=400, height=24)
canvas.grid(row=0, column=1, padx=5)
scroll_x = ctk.CTkScrollbar(folder_names, orientation="horizontal", command=canvas.xview)
scroll_x.grid(row=1, column=1, sticky="ew")
canvas.configure(xscrollcommand=scroll_x.set)
label_frame = ctk.CTkFrame(canvas)
canvas.create_window((0, 0), window=label_frame, anchor="nw")
home_label = ctk.CTkLabel(label_frame, textvariable=home_directory_var, text_color="blue")
home_label.grid(row=0, column=0)
home_label.bind("<Configure>", update_scrollregion)

# Macro/Data folder names
macro_name_var = ctk.StringVar()
ctk.CTkLabel(folder_names, text="Macro name:").grid(row=2, column=0, padx = 5, pady=5, sticky="e")
ctk.CTkEntry(folder_names, textvariable=macro_name_var, width=300).grid(row=2, column=1, pady=5, sticky="w")
ctk.CTkLabel(folder_names, text="**Cannot include spaces, use - or _. e.g. macro_20250328_air", wraplength=200).grid(row=2, column=1, padx=(250,5))

data_folder_var = ctk.StringVar()
ctk.CTkLabel(folder_names, text="Data folder name:").grid(row=3, column=0, padx = 5, pady=5, sticky="e")
ctk.CTkEntry(folder_names, textvariable=data_folder_var, width=300).grid(row=3, column=1, pady=5, sticky="w")
ctk.CTkButton(folder_names, text="Same as macro", command=lambda: update_label(macro_name_var, data_folder_var)).grid(row=4, column=1, padx=5)

# Scan Parameters
scan_frame = ctk.CTkFrame(frame)
scan_frame.grid(row=1, column=0, sticky="ew", pady=5)
exposure_time_var = ctk.StringVar()
sleep_time_var    = ctk.StringVar()
num_images_var    = ctk.StringVar()
num_loops_var     = ctk.StringVar()
AXS_var           = ctk.StringVar()

param_list = [
    ("Exposure Time (s):", exposure_time_var),
    ("Sleep Time (s):", sleep_time_var),
    ("Number of Images:", num_images_var),
    ("Number of Loops:", num_loops_var),
    ("Scattering Range:", AXS_var)
]
for col, (text, var) in enumerate(param_list):
    ctk.CTkLabel(scan_frame, text=text).grid(row=0, column=col, padx=5, pady=5)
    if text == "Scattering Range:":
        ctk.CTkOptionMenu(scan_frame, variable=var, values=["SAXS","WAXS","Both"], width=100).grid(row=1, column=col, padx=5, pady=5)
    else:
        ctk.CTkEntry(scan_frame, textvariable=var, width=100).grid(row=1, column=col, padx=5, pady=5)

# Dark Collection & Rocking
dr_frame = ctk.CTkFrame(frame)
dr_frame.grid(row=2, column=0, sticky="ew", pady=5)

# Dark section
dark_frame = ctk.CTkFrame(dr_frame, fg_color = "transparent")
dark_frame.grid(row=0, column=0, padx=5)
dark_frequency_var = ctk.StringVar(value="0")
dark_duration_var  = ctk.StringVar(value="0")
ctk.CTkLabel(dark_frame, text="Take dark data every ___ samples:").grid(row=0, column=0, padx=5)
ctk.CTkEntry(dark_frame, textvariable=dark_frequency_var, width=80).grid(row=1, column=0, padx=5)
ctk.CTkLabel(dark_frame, text="Dark exposure time (s):").grid(row=0, column=1, padx=5)
ctk.CTkEntry(dark_frame, textvariable=dark_duration_var, width=80).grid(row=1, column=1, padx=5)

# Red vertical separator line
separator = ctk.CTkFrame(dr_frame, width=10, height=59)
separator.grid(row=0, column=1,)

# Rocking section
rock_frame = ctk.CTkFrame(dr_frame, fg_color = "transparent")
rock_frame.grid(row=0, column=2, padx=5, sticky="W")
rock_lpx_var = ctk.StringVar(value="0")
rock_lpy_var = ctk.StringVar(value="0")
ctk.CTkLabel(rock_frame, text="lpx (mm):").grid(row=0, column=0, padx=5)
ctk.CTkEntry(rock_frame, textvariable=rock_lpx_var, width=80).grid(row=1, column=0, padx=5)
ctk.CTkLabel(rock_frame, text="lpy (mm):").grid(row=0, column=1, padx=5)
ctk.CTkEntry(rock_frame, textvariable=rock_lpy_var, width=80).grid(row=1, column=1, padx=5)

sample_parameters = {}
# Sample Parameters
sample_frame = ctk.CTkFrame(frame)
sample_frame.grid(row=3, column=0, sticky="ew", pady=5)
sample_count_var = ctk.StringVar(value="1")
ctk.CTkLabel(sample_frame, text="How many samples?").grid(row=0, column=0, padx=5)
ctk.CTkOptionMenu(sample_frame, variable=sample_count_var, values=[str(i) for i in range(1,301)], width=60).grid(row=0, column=1, padx=5)
ctk.CTkButton(sample_frame, text="Enter Individual Sample Info", command=lambda: open_sample_popup(sample_count_var, sample_parameters)).grid(row=1, column=0, padx=5)
ctk.CTkButton(sample_frame, text="Paste Excel Data", command=lambda: open_excel_data_popup(sample_count_var, sample_parameters)).grid(row=1, column=1, padx=5)

# Camera Parameters
cam_frame = ctk.CTkFrame(frame)
cam_frame.grid(row=4, column=0, sticky="ew", pady=5)

# BooleanVars for each camera option
bottom_cam_var = ctk.BooleanVar()
side_cam_var = ctk.BooleanVar()
top_cam_var = ctk.BooleanVar()

ctk.CTkLabel(cam_frame, text="Select up to 3 cameras:").grid(row=0, column=0, columnspan=3, padx=5, pady=(0, 5))

# Create checkboxes with labels
ctk.CTkCheckBox(cam_frame, text="Bottom Camera", variable=bottom_cam_var).grid(row=1, column=0, padx=5, pady=5)
ctk.CTkCheckBox(cam_frame, text="Side Camera", variable=side_cam_var).grid(row=1, column=1, padx=5, pady=5)
ctk.CTkCheckBox(cam_frame, text="Top Camera", variable=top_cam_var).grid(row=1, column=2, padx=5, pady=5)

# Save Button
ctk.CTkButton(root, text="Save File", command=create_macro_file).pack(pady=10)

root.mainloop()
