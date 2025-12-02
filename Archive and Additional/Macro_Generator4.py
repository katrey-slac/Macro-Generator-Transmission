import tkinter
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# message box to confirm GUI closure
def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()


# Store folder path in variable
def select_folder(folder_var):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)


# Ensures the scrollable area (in the home directory box) is updated after content is added
def update_scrollregion(event=None):
    canvas.config(scrollregion=canvas.bbox("all"))


# Update the label with the variable's value
def update_label(var_value, label_var):
    label_var.set(var_value.get())


def open_excel_data_popup(sample_data):
    popup = tk.Toplevel(root)
    popup.title("Paste Excel Data")

    tk.Label(popup,
             text="Paste values copied from Excel into the fields below.\nEach should be one column of values (one per line).",
             justify="left").pack(pady=5)

    # Frame for text areas and shared scrollbar
    text_frame = tk.Frame(popup)
    text_frame.pack(padx=10, pady=5)

    tk.Label(text_frame, text="Sample Names").grid(row=0, column=0)
    tk.Label(text_frame, text="LPX Values").grid(row=0, column=1)
    tk.Label(text_frame, text="LPY Values").grid(row=0, column=2)

    # Shared vertical scrollbar
    v_scroll = tk.Scrollbar(text_frame, orient="vertical")
    v_scroll.grid(row=1, column=3, sticky="ns")

    # Create text widgets
    sample_text = tk.Text(text_frame, height=15, width=20, yscrollcommand=lambda *args: sync_scroll(*args))
    lpx_text = tk.Text(text_frame, height=15, width=10, yscrollcommand=lambda *args: sync_scroll(*args))
    lpy_text = tk.Text(text_frame, height=15, width=10, yscrollcommand=lambda *args: sync_scroll(*args))

    # Place the text widgets
    sample_text.grid(row=1, column=0, padx=5)
    lpx_text.grid(row=1, column=1, padx=5)
    lpy_text.grid(row=1, column=2, padx=5)

    # Synchronize scrolling
    def sync_scroll(*args):
        sample_text.yview(*args)
        lpx_text.yview(*args)
        lpy_text.yview(*args)

    def on_text_scroll(*args):
        v_scroll.set(*args)
        sync_scroll("moveto", args[0])

    # Set the scrollbar to command all three widgets
    v_scroll.config(command=sync_scroll)

    # Link text widgets' yview to scrollbar
    sample_text.config(yscrollcommand=on_text_scroll)
    lpx_text.config(yscrollcommand=on_text_scroll)
    lpy_text.config(yscrollcommand=on_text_scroll)

    # Restore previously pasted values
    if "excel_raw_names" in sample_data:
        sample_text.insert("1.0", sample_data["excel_raw_names"])
    if "excel_raw_lpxs" in sample_data:
        lpx_text.insert("1.0", sample_data["excel_raw_lpxs"])
    if "excel_raw_lpys" in sample_data:
        lpy_text.insert("1.0", sample_data["excel_raw_lpys"])

    def save_pasted_data():
        raw_names = sample_text.get("1.0", tk.END).strip()
        raw_lpxs = lpx_text.get("1.0", tk.END).strip()
        raw_lpys = lpy_text.get("1.0", tk.END).strip()

        names = raw_names.splitlines()
        lpxs = raw_lpxs.splitlines()
        lpys = raw_lpys.splitlines()

        if not (len(names) == len(lpxs) == len(lpys)):
            tk.messagebox.showerror("Mismatch", "Each column must have the same number of values.", parent=popup)
            return

        try:
            sample_data["sample_names"] = [name.strip() for name in names]
            sample_data["lpxs"] = [float(val.strip()) for val in lpxs]
            sample_data["lpys"] = [float(val.strip()) for val in lpys]

            sample_data["excel_raw_names"] = raw_names
            sample_data["excel_raw_lpxs"] = raw_lpxs
            sample_data["excel_raw_lpys"] = raw_lpys

            popup.destroy()
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "LPX and LPY must be numeric.", parent=popup)

    # Buttons
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Cancel", command=popup.destroy, bg="red3", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Save", command=save_pasted_data, bg="green", fg="white").pack(side=tk.RIGHT, padx=5)


def show_success_popup(directory, macro_name):
    popup = tk.Toplevel(root)
    popup.title("Success")
    popup.geometry("500x175")
    popup.resizable(False, False)

    # Message Label
    tk.Label(popup, text="File saved successfully!\nRun this in SPEC:", font=("Arial", 10)).pack(pady=(10, 5))

    # Copyable Text
    cmd_text = f"qdo .{directory}/{macro_name}.txt"

    # Frame to contain the Text and Scrollbar
    text_frame = tk.Frame(popup)
    text_frame.pack(pady=(0, 10))

    # Horizontal scrollbar
    x_scroll = tk.Scrollbar(text_frame, orient="horizontal")
    x_scroll.pack(side="bottom", fill="x")

    # Text box with scrollbar
    text_box = tk.Text(text_frame, height=1, width=60, font=("Courier", 10),
                       wrap="none", xscrollcommand=x_scroll.set)
    text_box.insert(tk.END, cmd_text)
    text_box.configure(state="disabled")
    text_box.pack()
    x_scroll.config(command=text_box.xview)

    # Optional: Add copy button
    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(cmd_text)

    copy_btn = tk.Button(popup, text="Copy to Clipboard", command=copy_to_clipboard, bg="PaleTurquoise1", fg="black")
    copy_btn.pack()

    # Close Button
    tk.Button(popup, text="Close", command=popup.destroy, bg="red3", fg="white").pack(pady=5)


# Main function to create the macro text file with user inputs
def create_trans_macro_file():
    if not home_directory_var.get():
        messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.",
                             parent=root)

    # Validate macro name
    if " " in macro_name_var.get():
        messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces.\nPlease use underscores (_) or hyphens (-).",
                             parent=root)
        return

    # Validate values for inputs
    if exposure_time_var.get() == 0:
        messagebox.showerror("Invalid Exposure Time",
                             "Exposure time cannot be zero. Please correct.",
                             parent=root)
        return

    if num_images_var.get() == 0:
        messagebox.showerror("Invalid Number of Images",
                             "Number of images cannot be zero. Please correct.",
                             parent=root)
        return

    if num_loops_var.get() == 0:
        messagebox.showerror("Invalid Number of Loops",
                             "Number of loops cannot be zero. Please correct.",
                             parent=root)
        return

    if not sample_parameters.get('sample_names'):
        messagebox.showerror("Sample Information Missing",
                             "Please input sample information.",
                             parent=root)
        return

    if not AXS_var.get():
        messagebox.showerror("Scattering Range Not Selected",
                             "Please select scattering range.",
                             parent=root)

    # Retrieve values from the input fields
    macro_name = macro_name_var.get()
    exposure_time = exposure_time_var.get()
    sleep_time = sleep_time_var.get()
    num_images = num_images_var.get()
    num_loops = num_loops_var.get()
    dark_frequency = dark_frequency_var.get()
    dark_exposure = dark_exposure_var.get()

    try:
        rock_lpx = float(rock_lpx_var.get())
    except ValueError:
        rock_lpx = 0.0  # or handle as needed
    try:
        rock_lpy = float(rock_lpy_var.get())
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

    cameras = {
        "bottom": bottom_camera_var,
        "side": side_camera_var,
        "top": top_camera_var
    }

    camera_lines = ""
    for label, var in cameras.items():
        if var.get():
            camera_lines += f'         epics_put("MSD_Local_Cameras:BL1-5_{label}_camera:save_frame", base_filename)\n'

    detector_map = {
        "SAXS": [
            'unix(sprintf("mkdir -p %s/SAXS", pilatus_baseDir2))',
            'pd enable # Enable SAXS 1M detector',
            'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2))',
            'pd save # save SAXS data',
            'pd disable  # Disable SAXS detector after scan'
        ],
        "WAXS": [
            'unix(sprintf("mkdir -p %s/WAXS", pilatus_baseDir2))',
            'pdw enable #Enable WAXS detector',
            'eval(sprintf("pd savepath %s/WAXS", pilatus_baseDir2))',
            'pdw save	# save WAXS data',
            'pdw disable  # Disable WAXS detector after scan'
        ],
        "Both": [
            'unix(sprintf("mkdir -p %s/SAXS %s/WAXS", pilatus_baseDir2, pilatus_baseDir2))',
            'pd enable # Enable SAXS 1M detector \n       pdw enable #Enable WAXS detector',
            'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2)) \n        eval(sprintf("pdw savepath %s/WAXS", pilatus_baseDir2))',
            'pd save # save SAXS data \n        pdw save	# save WAXS data',
            'pd disable  # Disable SAXS detector after scan \n        pdw disable  # Disable WAXS detector after scan'
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

                {detector_map.get(AXS_var.get(), [])[1]}

                eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
                {detector_map.get(AXS_var.get(), [])[2]}

                {detector_map.get(AXS_var.get(), [])[3]}

                # Take the actual data
                eval(sprintf("loopscan %d %f %f", dark_num_images, dark_exposure, wait_time))

                {detector_map.get(AXS_var.get(), [])[4]}
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
dark_exposure = {dark_exposure}
dark_num_images = 1

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
rock no

# if (!exists("run_ctr")) {{  # Check if run_ctr exists, initialize if not
#     run_ctr = 0;
# }}
run_ctr += 1  # Increment global run counter to prevent accidental deletion

# Execute directory creation using Linux based commands
unix(sprintf('mkdir -p %s', pilatus_baseDir2))
{detector_map.get(AXS_var.get(), [])[0]}

##############
pd stop

sleep(5)

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
        {rocking_lines.strip()}

        wait_time = 0

        {detector_map.get(AXS_var.get(), [])[1]}

        eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
        {detector_map.get(AXS_var.get(), [])[2]}

        {detector_map.get(AXS_var.get(), [])[3]}

        #Take the actual data
        eval(sprintf("loopscan %d %f %f", num_images, exposure_time, wait_time))

        {detector_map.get(AXS_var.get(), [])[4]}

        # Implement sleep time between scans if required
        if (sleep_time > 0) {{
            printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
            sleep(sleep_time)
            p ".... DON'T hit control-C until we sleep again\\n"
        }}   
        {'rock no' if is_rocking else ''} 
        sclose
    }}       
}}



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

        show_success_popup(home_directory_var.get(), macro_name)

    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)


####################################################################################################################

# Main function to create the macro text file with user inputs
def create_photos_macro_file():
    if not home_directory_var.get():
        messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.",
                             parent=root)

    # Validate macro name
    if " " in macro_name_var.get():
        messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces.\nPlease use underscores (_) or hyphens (-).",
                             parent=root)
        return

    # Validate values for inputs
    if not sample_parameters.get('sample_names'):
        messagebox.showerror("Sample Information Missing",
                             "Please input sample information.",
                             parent=root)
        return

    # Retrieve values from the input fields
    macro_name = macro_name_var.get() + "_prelim_photos"

    # base_Dir = home_directory_var.get()+ "\\" + data_folder_var.get()
    spec_base_Dir = (home_directory_var.get() + "\\" + data_folder_var.get()).replace("\\", "/")
    spec_base_Dir = spec_base_Dir.replace("X:/bl1-5/", "")
    print(spec_base_Dir)

    # Define the content of the text file with user-defined values - this is the meat
    content = f"""
#Define the sample names
sample_names = {sample_parameters['sample_names']}

# Define list of coordinates (lpx, lpy)
lpx_positions = {sample_parameters['lpxs']}  # x positions
lpy_positions = {sample_parameters['lpys']}    # y positions
num_positions = {len(sample_parameters['lpxs'])}  # Get the number of coordinates

##############

for (pos_ctr = 0; pos_ctr < num_positions; pos_ctr++) {{  # Loop through coordinates
    base_filename = sample_names[pos_ctr]

    # Move to the next coordinate pair
    umv lpx lpx_positions[pos_ctr]
    umv lpy lpy_positions[pos_ctr]

    #save images from cameras (if any listed)
    epics_put("MSD_Local_Cameras:BL1-5_bottom_camera:save_frame", base_filename)
    epics_put("MSD_Local_Cameras:BL1-5_top_camera:save_frame", base_filename)
}}

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

        show_success_popup(home_directory_var.get(), macro_name)

    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)


####################################################################################################################


# Create the main GUI window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.title("Macro Generator")

# Create the overall frame
frame = tkinter.Frame(root, bg="dark red")
frame.pack()  # with .pack() Tkinter automatically places the widget in the window without needing to manually specify coordinates

# Create the subframe for the folder names section
folder_names = tkinter.LabelFrame(frame, text="Save Location")
folder_names.grid(row=0, column=0, padx=10, pady=10)

# Button and Label for Folder Selection
# Create a canvas to hold the label (text box) with horizontal scroll
canvas = tk.Canvas(folder_names, width=400, height=20)  # Adjust width as necessary
canvas.grid(row=0, column=1, columnspan=2)

# Add a horizontal scrollbar to the canvas
scroll_x = tk.Scrollbar(folder_names, orient="horizontal", command=canvas.xview)
scroll_x.grid(row=1, column=1, sticky="ew")
canvas.configure(xscrollcommand=scroll_x.set)


# Create a frame inside the canvas to place the label (text box) - placing label in canvas directly may complicate things
label_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=label_frame, anchor="nw")

# Now to populate the canvas and the frame with the home directory information...
home_directory_var = tk.StringVar()  # Variable to store selected folder path
home_directory_button = tk.Button(folder_names, text="Select Home Directory folder",
                                  command=lambda: select_folder(home_directory_var), bg="PaleTurquoise1",
                                  fg="black")  # button to select folder
home_directory_button.grid(row=0, column=0, pady=(10, 0), padx=(10, 0))  # location of button
home_directory_selection = tk.Label(label_frame, textvariable=home_directory_var,
                                    fg="DeepSkyBlue4")  # Display selected folder path
home_directory_selection.grid(row=0, column=1, columnspan=2)  # location of text box

# Ensure scroll region will update after being populated with text
home_directory_selection.bind("<Configure>", update_scrollregion)


# Now to fill in the users chosen name for the macro - this could include their sample name
macro_name_label = tk.Label(folder_names, text="Macro name:")
macro_name_label.grid(row=2, column=0, sticky="E", padx=(0, 5))
macro_name_var = tk.StringVar()
macro_name_entry = tk.Entry(folder_names, textvariable=macro_name_var, width=40)
macro_name_entry.grid(row=2, column=1, sticky="W")
macro_name_note = tk.Label(folder_names, text="**Cannot include spaces, use - or _. e.g. macro_20250328_air",
                           wraplength=200)
macro_name_note.grid(row=2, column=1, padx=(250, 5))

# Now to fill in the users chosen name for the data folder - they can choose to have it be named the same as their macro name
data_folder_label = tk.Label(folder_names, text="Data folder name:")
data_folder_label.grid(row=3, column=0, sticky="E", padx=(0, 5))
data_folder_var = tk.StringVar()
data_folder_entry = tk.Entry(folder_names, textvariable=data_folder_var, width=40)
data_folder_entry.grid(row=3, column=1, sticky="W")
data_folder_button = tk.Button(folder_names, text="Same as macro",
                               command=lambda: update_label(macro_name_var, data_folder_var), bg="PaleTurquoise1",
                               fg="black")  # button to select folder
data_folder_button.grid(row=4, column=1, sticky="W")  # location of button

###
scan_param_frame = tkinter.LabelFrame(frame, text="Scan Parameters")
scan_param_frame.grid(row=1, column=0, padx=10, pady=(0, 10))

# Label and entry for Exposure Time
exposure_time_label = tk.Label(scan_param_frame, text="Exposure Time (seconds):")
exposure_time_label.grid(row=0, column=0, padx=(5, 5))
exposure_time_var = tk.IntVar()
exposure_time_entry = tk.Entry(scan_param_frame, textvariable=exposure_time_var, width=10)
exposure_time_entry.grid(row=1, column=0)

# Label and entry for Sleep Time
sleep_time_label = tk.Label(scan_param_frame, text="Sleep Time (seconds):")
sleep_time_label.grid(row=0, column=1, padx=(5, 5))
sleep_time_var = tk.IntVar()
sleep_time_entry = tk.Entry(scan_param_frame, textvariable=sleep_time_var, width=10)
sleep_time_entry.grid(row=1, column=1)

# Label and entry for Number of Images
number_of_images_label = tk.Label(scan_param_frame, text="Number of Images:")
number_of_images_label.grid(row=0, column=2, padx=(5, 5))
num_images_var = tk.IntVar()
number_of_images_entry = tk.Entry(scan_param_frame, textvariable=num_images_var, width=10)
number_of_images_entry.grid(row=1, column=2)

# Label and entry for Number of Loops
number_of_loops_label = tk.Label(scan_param_frame, text="Number of Loops:")
number_of_loops_label.grid(row=0, column=3, padx=(5, 5))
num_loops_var = tk.IntVar()
number_of_loops_entry = tk.Entry(scan_param_frame, textvariable=num_loops_var, width=10)
number_of_loops_entry.grid(row=1, column=3)

# Label and entry for the kind of AXS - SAXS or WAXS
AXS_label = tk.Label(scan_param_frame, text="Scattering Range")
AXS_label.grid(row=0, column=4, padx=(5, 5))
AXS_var = tk.StringVar()
AXS_dropdown = ttk.Combobox(scan_param_frame, textvariable=AXS_var, values=["SAXS", "WAXS", "Both"], width=10,
                            state="readonly")
AXS_dropdown.grid(row=1, column=4, padx=(0, 10))

###
dark_and_rocking_frame = tk.Frame(frame)
dark_and_rocking_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

###
dark_frame = tkinter.LabelFrame(dark_and_rocking_frame, text="Dark Collection")
dark_frame.grid(row=0, column=0)

# "Take dark data every:" label
dark_frequency_label = tk.Label(dark_frame, text="Take dark data every ___ samples.")
dark_frequency_label.grid(row=0, column=1, padx=10)

# Entry box
dark_frequency_var = tk.IntVar()
dark_frequency_entry = tk.Entry(dark_frame, textvariable=dark_frequency_var, width=10)
dark_frequency_entry.grid(row=1, column=1)

# "dark exposure" label
dark_exposure_label = tk.Label(dark_frame, text="Dark exposure time (seconds):")
dark_exposure_label.grid(row=0, column=2, padx=10)

# Entry box
dark_exposure_var = tk.IntVar()
dark_exposure_entry = tk.Entry(dark_frame, textvariable=dark_exposure_var, width=10)
dark_exposure_entry.grid(row=1, column=2)

# Red vertical separator line
separator = tk.Frame(dark_and_rocking_frame, bg="dark red", width=10, height=59)
separator.grid(row=0, column=1, )

###
rocking_frame = tkinter.LabelFrame(dark_and_rocking_frame, text="Rocking")
rocking_frame.grid(row=0, column=2)

# LPX label and entry
rock_lpx_label = tk.Label(rocking_frame, text="lpx in mm")
rock_lpx_label.grid(row=0, column=1, padx=5)

rock_lpx_var = tk.StringVar(value="0")
rock_lpx_entry = tk.Entry(rocking_frame, width=10, textvariable=rock_lpx_var)
rock_lpx_entry.grid(row=1, column=1, padx=10)

# LPY label and entry
rock_lpy_label = tk.Label(rocking_frame, text="lpy in mm")
rock_lpy_label.grid(row=0, column=2, padx=(0, 5))

rock_lpy_var = tk.StringVar(value="0")
rock_lpy_entry = tk.Entry(rocking_frame, width=10, textvariable=rock_lpy_var)
rock_lpy_entry.grid(row=1, column=2, padx=(0, 10))

###
sample_param_frame = tkinter.LabelFrame(frame, text="Sample Parameters")
sample_param_frame.grid(row=3, column=0, padx=10, pady=(0, 10))

# Dictionary to store user input
sample_parameters = {}

# Button to open Excel-style paste popup
enter_excel_button = tk.Button(sample_param_frame, text="Enter Sample Information",
                               command=lambda: open_excel_data_popup(sample_parameters), bg="PaleTurquoise1",
                               fg="black")
enter_excel_button.grid(row=0, column=0, padx=5, pady=5)

###
cameras_frame = tkinter.LabelFrame(frame, text="Camera Parameters")
cameras_frame.grid(row=4, column=0, padx=10, pady=(0, 10))

cameras_label = tk.Label(cameras_frame, text="What cameras do you want to use?")
cameras_label.grid(row=0, column=1)

bottom_camera_var = tk.IntVar()
bottom_camera_button = tk.Checkbutton(cameras_frame, text="Bottom Camera", variable=bottom_camera_var, onvalue=1,
                                      offvalue=0)
bottom_camera_button.grid(row=1, column=0)

side_camera_var = tk.IntVar()
side_camera_button = tk.Checkbutton(cameras_frame, text="Side Camera", variable=side_camera_var, onvalue=1, offvalue=0)
side_camera_button.grid(row=1, column=1)

top_camera_var = tk.IntVar()
top_camera_button = tk.Checkbutton(cameras_frame, text="Top Camera", variable=top_camera_var, onvalue=1, offvalue=0)
top_camera_button.grid(row=1, column=2)

###
prelimphotos_frame = tkinter.LabelFrame(frame, text="")
prelimphotos_frame.grid(row=5, column=0, padx=10, pady=(0, 10))

prelimphotos_label = tk.Label(prelimphotos_frame, text='Take photos of sample positions.')
prelimphotos_label.grid(row=0, column=0)

# Save button — centered using `place` in the root window
save_photos_button = tk.Button(prelimphotos_frame, text="Save Photo Macro", command=create_photos_macro_file,
                               bg="DarkSeaGreen1", fg="black")
save_photos_button.grid(row=0, column=2, padx=10, pady=10)

###
# Footer row frame spans full width
footer_frame = tk.Frame(root)
footer_frame.pack(fill=tk.X, pady=10)

# Save button — centered using `place` in the root window
save_macro_button = tk.Button(root, text="Save File", command=create_trans_macro_file, bg="chartreuse4", fg="white")
save_macro_button.place(relx=0.5, rely=.9850, anchor="s")  # relx=0.5 centers horizontally

# Label — right-aligned inside the footer frame
credit_label = tk.Label(footer_frame, text="Katerina Reynolds 2025", font=("Arial", 8), fg="indianred")
credit_label.pack(side=tk.RIGHT, padx=10)

# Start the GUI event loop
root.mainloop()



