# macro_writer.py
import os
from tkinter import messagebox
from success_SPEC_copy import show_success_popup
from pathlib import Path




def create_trans_macro_file(
    root,
    home_directory,
    data_folder,
    macro_name,
    exposure_time,
    sleep_time,
    num_images,
    num_loops,
    dark_frequency,
    dark_exposure,
    rock_lpx,
    rock_lpy,
    sample_parameters,
    AXS,
    cameras
):
    """
    Create a macro text file for a transmission experiment.
    """

    # Validate inputs
    if not home_directory:
        messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.", parent=root)
        return

    if " " in macro_name:
        messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces. Use underscores (_) or hyphens (-).",
                             parent=root)
        return

    if exposure_time == 0 or num_images == 0 or num_loops == 0:
        messagebox.showerror("Invalid Values",
                             "Exposure time, number of images, and number of loops must be greater than zero.",
                             parent=root)
        return

    if not sample_parameters.get('sample_names'):
        messagebox.showerror("Sample Information Missing",
                             "Please input sample information.", parent=root)
        return

    if not AXS:
        messagebox.showerror("Scattering Range Not Selected",
                             "Please select scattering range.", parent=root)
        return

    # Prepare directories and file paths
    spec_baseDir = (home_directory + "\\" + data_folder).replace("\\", "/")

    spec_baseDir = Path(spec_baseDir)
    spec_baseDir = Path(*spec_baseDir.parts[2:])
    spec_baseDir = "/" + spec_baseDir.as_posix()

    rocking_lines = ""
    if rock_lpx != 0.0:
        rocking_lines += f"rock lpx {rock_lpx}\n        "
    if rock_lpy != 0.0:
        rocking_lines += f"rock lpy {rock_lpy}\n        "
    is_rocking = rock_lpx != 0.0 or rock_lpy != 0.0

    # Camera lines
    camera_lines = ""
    for label, active in cameras.items():
        if active:
            camera_lines += f'         epics_put("MSD_Local_Cameras:BL1-5_{label}_camera:save_frame", base_filename)\n'

    # Detector commands
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
            'pd enable # Enable SAXS 1M detector \n         pdw enable #Enable WAXS detector',
            'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2)) \n          eval(sprintf("pdw savepath %s/WAXS", pilatus_baseDir2))',
            'pd save # save SAXS data \n            pdw save	# save WAXS data',
            'pd disable  # Disable SAXS detector after scan \n          pdw disable  # Disable WAXS detector after scan'
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

                {detector_map.get(AXS, [])[1]}

                eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
                {detector_map.get(AXS, [])[2]}

                {detector_map.get(AXS, [])[3]}
                
                # Take the actual data
                eval(sprintf("loopscan %d %f %f", dark_num_images, dark_exposure, wait_time))

                {detector_map.get(AXS, [])[4]}
                # Implement sleep time between scans if required
                if (sleep_time > 0) {{
                printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
                sleep(sleep_time)
                p ".... DON'T hit control-C until we sleep again\\n"
                sopen
                }}
                }}
            """

    # Macro content
    content = f"""
exposure_time = {exposure_time}      # exposure time for each image (in seconds)
num_loops = {num_loops}                # number of images in the scan 
sleep_time = {sleep_time}                # sleep time between each image (in seconds), enter a value of 0 to disable it
num_images = {num_images}

dark_frequency = {dark_frequency}
dark_exposure = {dark_exposure}
dark_num_images = 1

# Define list of coordinates (lpx, lpy)
sample_names = {sample_parameters['sample_names']}
lpx_positions = {sample_parameters['lpxs']}
lpy_positions = {sample_parameters['lpys']}
num_positions = {len(sample_parameters['lpxs'])}

############################
#File name and location
############################

spec_baseDir = "{spec_baseDir + "/"}" 		#Needs trailing '/'
pilatus_baseDir2 = sprintf('~/data/%s', spec_baseDir)

loop_ctr = 0
pos_ctr = 0
rock no

run_ctr += 1

# Execute directory creation using Linux based commands
unix(sprintf('mkdir -p %s', pilatus_baseDir2))
{detector_map.get(AXS, [])[0]}

pd stop
sleep(5)

sopen

for (loop_ctr=0; loop_ctr < num_loops; loop_ctr++) {{
    for (pos_ctr = 0; pos_ctr < num_positions; pos_ctr++) {{    # Loop through coordinates
        {dark_frame_block}
        base_filename = sample_names[pos_ctr]

        # Move to the next coordinate pair
        umv lpx lpx_positions[pos_ctr]
        umv lpy lpy_positions[pos_ctr]

        sopen
        #Create a variable for file name containing the data
        data_dir = sprintf("%s_run%d_loop%d_pos%d", base_filename, run_ctr, loop_ctr, pos_ctr) #No trailing '/'
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

        {detector_map.get(AXS, [])[1]}
        
        eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
        
        {detector_map.get(AXS, [])[2]}
        
        {detector_map.get(AXS, [])[3]}
        
        #Take the actual data
        eval(sprintf("loopscan %d %f %f", num_images, exposure_time, wait_time))
        
        {detector_map.get(AXS, [])[4]}

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

    file_path = os.path.join(home_directory, f"{macro_name}.txt")
    print(file_path)

    # Check for overwrite
    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("File Exists",
                                        "A file with that name already exists.\nDo you want to overwrite it?",
                                        parent=root)
        if not overwrite:
            return      # Exit function if user chooses not to overwrite

    # Write file
    try:
        with open(file_path, "w") as file:
            file.write(content)
        show_success_popup(root, home_directory, macro_name)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)



###########################################################################################################


# Main function to create the macro text file with user inputs
def create_photos_macro_file(root, home_directory, data_folder, macro_name, sample_parameters):
    """
    Create a macro text file for preliminary photos of samples.
    """
    if not home_directory:
        messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.", parent=root)
        return

    if " " in macro_name:
        messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces. Use underscores (_) or hyphens (-).",
                             parent=root)
        return

    if not sample_parameters.get('sample_names'):
        messagebox.showerror("Sample Information Missing",
                             "Please input sample information.", parent=root)
        return

    macro_name += "_prelim_photos"

    spec_baseDir = os.path.join(home_directory, data_folder).replace("\\", "/")
    spec_baseDir = spec_baseDir.replace("X:/bl1-5/", "")

    content = f"""
#Define the sample names
sample_names = {sample_parameters['sample_names']}

# Define list of coordinates (lpx, lpy)
lpx_positions = {sample_parameters['lpxs']}  # x positions
lpy_positions = {sample_parameters['lpys']}    # y positions
num_positions = {len(sample_parameters['lpxs'])}  # Get the number of coordinates

 # Loop through coordinates
for (pos_ctr = 0; pos_ctr < num_positions; pos_ctr++) {{
    base_filename = sample_names[pos_ctr]
    
    # Move to the next coordinate pair
    umv lpx lpx_positions[pos_ctr]
    umv lpy lpy_positions[pos_ctr]
    
     #save images from cameras (if any listed)
    epics_put("MSD_Local_Cameras:BL1-5_bottom_camera:save_frame", base_filename)
    epics_put("MSD_Local_Cameras:BL1-5_top_camera:save_frame", base_filename)
}}
"""

    file_path = os.path.join(home_directory, f"{macro_name}.txt")

    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("File Exists",
                                        "A file with that name already exists.\nDo you want to overwrite it?",
                                        parent=root)
        if not overwrite:
            return

    try:
        with open(file_path, "w") as file:
            file.write(content)
        show_success_popup(root, home_directory, macro_name)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)
