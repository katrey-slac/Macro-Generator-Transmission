import os
import sys
from PyQt5 import QtWidgets, QtCore


# Main Window class - subclass QWidget so we can override closeEvent safely
class MacroGenerator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Sample data dictionary (like your tkinter sample_parameters)
        self.sample_data = {}

        self.setWindowTitle("Macro Generator")
        self.setGeometry(100, 100, 800, 600)  # window size

        # Layouts - vertical main layout
        main_layout = QtWidgets.QVBoxLayout(self)

        # ========== Save Location Section ==========
        folder_group = QtWidgets.QGroupBox("Save Location")
        folder_layout = QtWidgets.QGridLayout()
        folder_group.setLayout(folder_layout)

        # Select Home Directory Button
        self.home_directory_path = ""

        select_home_btn = QtWidgets.QPushButton("Select Home Directory folder")
        select_home_btn.setStyleSheet("background-color: PaleTurquoise; color: black;")
        select_home_btn.clicked.connect(self.select_home_directory)
        folder_layout.addWidget(select_home_btn, 0, 0)

        # Label to display home directory path with horizontal scroll
        self.home_dir_label = QtWidgets.QLabel()
        self.home_dir_label.setStyleSheet("color: DeepSkyBlue;")
        self.home_dir_label.setMinimumWidth(400)
        self.home_dir_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # allow text selection
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.home_dir_label)
        scroll_area.setFixedHeight(30)  # just enough for one line of text
        folder_layout.addWidget(scroll_area, 0, 1, 1, 2)

        # Macro name entry and label
        folder_layout.addWidget(QtWidgets.QLabel("Macro name:"), 2, 0)
        self.macro_name_edit = QtWidgets.QLineEdit()
        folder_layout.addWidget(self.macro_name_edit, 2, 1)
        macro_note = QtWidgets.QLabel("**Cannot include spaces, use - or _. e.g. macro_20250328_air")
        macro_note.setWordWrap(True)
        folder_layout.addWidget(macro_note, 2, 2)

        # Data folder entry and label
        folder_layout.addWidget(QtWidgets.QLabel("Data folder name:"), 3, 0)
        self.data_folder_edit = QtWidgets.QLineEdit()
        folder_layout.addWidget(self.data_folder_edit, 3, 1)

        same_as_macro_btn = QtWidgets.QPushButton("Same as macro")
        same_as_macro_btn.setStyleSheet("background-color: PaleTurquoise; color: black;")
        same_as_macro_btn.clicked.connect(self.set_data_folder_same_as_macro)
        folder_layout.addWidget(same_as_macro_btn, 4, 1, 1, 1)

        main_layout.addWidget(folder_group)

        # ========== Scan Parameters Section ==========
        scan_group = QtWidgets.QGroupBox("Scan Parameters")
        scan_layout = QtWidgets.QGridLayout()
        scan_group.setLayout(scan_layout)

        # Exposure Time
        scan_layout.addWidget(QtWidgets.QLabel("Exposure Time (seconds):"), 0, 0)
        self.exposure_time_spin = QtWidgets.QSpinBox()
        self.exposure_time_spin.setMaximum(100000)
        scan_layout.addWidget(self.exposure_time_spin, 1, 0)

        # Sleep Time
        scan_layout.addWidget(QtWidgets.QLabel("Sleep Time (seconds):"), 0, 1)
        self.sleep_time_spin = QtWidgets.QSpinBox()
        self.sleep_time_spin.setMaximum(100000)
        scan_layout.addWidget(self.sleep_time_spin, 1, 1)

        # Number of Images
        scan_layout.addWidget(QtWidgets.QLabel("Number of Images:"), 0, 2)
        self.num_images_spin = QtWidgets.QSpinBox()
        self.num_images_spin.setMaximum(100000)
        scan_layout.addWidget(self.num_images_spin, 1, 2)

        # Number of Loops
        scan_layout.addWidget(QtWidgets.QLabel("Number of Loops:"), 0, 3)
        self.num_loops_spin = QtWidgets.QSpinBox()
        self.num_loops_spin.setMaximum(100000)
        scan_layout.addWidget(self.num_loops_spin, 1, 3)

        # Scattering Range dropdown (SAXS, WAXS, Both)
        scan_layout.addWidget(QtWidgets.QLabel("Scattering Range"), 0, 4)
        self.axs_combo = QtWidgets.QComboBox()
        self.axs_combo.addItems(["SAXS", "WAXS", "Both"])
        scan_layout.addWidget(self.axs_combo, 1, 4)

        main_layout.addWidget(scan_group)

        # ========== Dark and Rocking Section ==========
        dark_rock_group = QtWidgets.QWidget()
        dark_rock_layout = QtWidgets.QHBoxLayout()
        dark_rock_group.setLayout(dark_rock_layout)

        # Dark Collection Group
        dark_group = QtWidgets.QGroupBox("Dark Collection")
        dark_layout = QtWidgets.QGridLayout()
        dark_group.setLayout(dark_layout)

        dark_layout.addWidget(QtWidgets.QLabel("Take dark data every ___ samples."), 0, 1)
        self.dark_frequency_spin = QtWidgets.QSpinBox()
        self.dark_frequency_spin.setMaximum(100000)
        dark_layout.addWidget(self.dark_frequency_spin, 1, 1)

        dark_layout.addWidget(QtWidgets.QLabel("Dark exposure time (seconds):"), 0, 2)
        self.dark_exposure_spin = QtWidgets.QSpinBox()
        self.dark_exposure_spin.setMaximum(100000)
        dark_layout.addWidget(self.dark_exposure_spin, 1, 2)

        dark_rock_layout.addWidget(dark_group)

        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        dark_rock_layout.addWidget(separator)

        # Rocking Group
        rocking_group = QtWidgets.QGroupBox("Rocking")
        rocking_layout = QtWidgets.QGridLayout()
        rocking_group.setLayout(rocking_layout)

        rocking_layout.addWidget(QtWidgets.QLabel("lpx in mm"), 0, 1)
        self.rock_lpx_edit = QtWidgets.QLineEdit("0")
        rocking_layout.addWidget(self.rock_lpx_edit, 1, 1)

        rocking_layout.addWidget(QtWidgets.QLabel("lpy in mm"), 0, 2)
        self.rock_lpy_edit = QtWidgets.QLineEdit("0")
        rocking_layout.addWidget(self.rock_lpy_edit, 1, 2)

        dark_rock_layout.addWidget(rocking_group)

        main_layout.addWidget(dark_rock_group)

        # ========== Sample Parameters Section ==========
        sample_group = QtWidgets.QGroupBox("Sample Parameters")
        sample_layout = QtWidgets.QHBoxLayout()
        sample_group.setLayout(sample_layout)

        self.enter_excel_btn = QtWidgets.QPushButton("Enter Sample Information")
        self.enter_excel_btn.setStyleSheet("background-color: PaleTurquoise; color: black;")
        self.enter_excel_btn.clicked.connect(self.open_excel_data_popup)
        sample_layout.addWidget(self.enter_excel_btn)

        main_layout.addWidget(sample_group)

        # ========== Cameras Section ==========
        cameras_group = QtWidgets.QGroupBox("Camera Parameters")
        cameras_layout = QtWidgets.QGridLayout()
        cameras_group.setLayout(cameras_layout)

        cameras_layout.addWidget(QtWidgets.QLabel("What cameras do you want to use?"), 0, 1)

        self.bottom_camera_check = QtWidgets.QCheckBox("Bottom Camera")
        cameras_layout.addWidget(self.bottom_camera_check, 1, 0)

        self.side_camera_check = QtWidgets.QCheckBox("Side Camera")
        cameras_layout.addWidget(self.side_camera_check, 1, 1)

        self.top_camera_check = QtWidgets.QCheckBox("Top Camera")
        cameras_layout.addWidget(self.top_camera_check, 1, 2)

        main_layout.addWidget(cameras_group)

        # ========== Footer Section ==========
        footer_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(footer_layout)

        # Spacer to push label right
        footer_layout.addStretch()

        credit_label = QtWidgets.QLabel("Katerina Reynolds 2025")
        credit_label.setStyleSheet("color: indianred; font-size: 8pt;")
        footer_layout.addWidget(credit_label)

        # Save button at the bottom center
        save_btn = QtWidgets.QPushButton("Save File")
        save_btn.setStyleSheet("background-color: DarkOliveGreen; color: black; font-weight: bold;")
        save_btn.clicked.connect(self.create_macro_file)
        main_layout.addWidget(save_btn, alignment=QtCore.Qt.AlignHCenter)

    # ========== Methods ==========

    def select_home_directory(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Home Directory")
        if folder:
            self.home_directory_path = folder
            self.home_dir_label.setText(folder)

    def set_data_folder_same_as_macro(self):
        self.data_folder_edit.setText(self.macro_name_edit.text())

    def open_excel_data_popup(self):
        # Popup window for Excel paste, similar to your tkinter Toplevel
        popup = ExcelDataPopup(self.sample_data, self)
        popup.exec_()

    def create_macro_file(self):
        # Validate inputs like in your tkinter code

        # Check home directory selected
        if not self.home_directory_path:
            QtWidgets.QMessageBox.critical(self, "Home Directory Not Selected",
                                           "Please select a home directory.")
            return

        macro_name = self.macro_name_edit.text().strip()
        if " " in macro_name or not macro_name:
            QtWidgets.QMessageBox.critical(self, "Invalid Macro Name",
                                           "Macro name cannot contain spaces and cannot be empty.\nPlease use underscores (_) or hyphens (-).")
            return

        exposure_time = self.exposure_time_spin.value()
        if exposure_time == 0:
            QtWidgets.QMessageBox.critical(self, "Invalid Exposure Time",
                                           "Exposure time cannot be zero. Please correct.")
            return

        num_images = self.num_images_spin.value()
        if num_images == 0:
            QtWidgets.QMessageBox.critical(self, "Invalid Number of Images",
                                           "Number of images cannot be zero. Please correct.")
            return

        num_loops = self.num_loops_spin.value()
        if num_loops == 0:
            QtWidgets.QMessageBox.critical(self, "Invalid Number of Loops",
                                           "Number of loops cannot be zero. Please correct.")
            return

        if not self.sample_data.get("sample_names"):
            QtWidgets.QMessageBox.critical(self, "Sample Information Missing",
                                           "Please input sample information.")
            return

        axs_value = self.axs_combo.currentText()
        if not axs_value:
            QtWidgets.QMessageBox.critical(self, "Scattering Range Not Selected",
                                           "Please select scattering range.")
            return

        sleep_time = self.sleep_time_spin.value()
        dark_frequency = self.dark_frequency_spin.value()
        dark_exposure = self.dark_exposure_spin.value()

        # Rocking values
        try:
            rock_lpx = float(self.rock_lpx_edit.text())
        except ValueError:
            rock_lpx = 0.0

        try:
            rock_lpy = float(self.rock_lpy_edit.text())
        except ValueError:
            rock_lpy = 0.0

        # Data folder name
        data_folder_name = self.data_folder_edit.text().strip()
        if not data_folder_name:
            data_folder_name = macro_name

        spec_base_dir = os.path.join(self.home_directory_path, data_folder_name).replace("\\", "/")
        spec_base_dir = spec_base_dir.replace("X:/bl1-5/", "")

        # Compose rocking lines for the macro
        rocking_lines = ""
        if rock_lpx != 0.0:
            rocking_lines += f"rock lpx {rock_lpx}\n"
        if rock_lpy != 0.0:
            rocking_lines += f"rock lpy {rock_lpy}\n"
        is_rocking = rock_lpx != 0.0 or rock_lpy != 0.0

        # Cameras info
        cameras = {
            "bottom": self.bottom_camera_check.isChecked(),
            "side": self.side_camera_check.isChecked(),
            "top": self.top_camera_check.isChecked()
        }

        camera_lines = ""
        for label, checked in cameras.items():
            if checked:
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
                'pd enable # Enable SAXS 1M detector \n                 pdw enable #Enable WAXS detector',
                'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir2)) \n                  eval(sprintf("pdw savepath %s/WAXS", pilatus_baseDir2))',
                'pd save # save SAXS data \n                    pdw save	# save WAXS data',
                'pd disable  # Disable SAXS detector after scan \n                  pdw disable  # Disable WAXS detector after scan'
            ]
        }

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

                {detector_map.get(axs_value, [])[1]}

                eval(sprintf("newfile %s/%s", spec_base_dir, data_dir))
                {detector_map.get(axs_value, [])[2]}

                {detector_map.get(axs_value, [])[3]}

                # Take the actual data
                eval(sprintf("loopscan %d %f %f", num_images, dark_exposure, wait_time))

                {detector_map.get(axs_value, [])[4]}
                # Implement sleep time between scans if required
                if (sleep_time > 0) {{
                printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
                sleep(sleep_time)
                p ".... DON'T hit control-C until we sleep again\\n"
                sopen
                }}
                }}
            """

        # Compose the macro content string exactly as you had in tkinter
        content = f"""
exposure_time = {exposure_time}          # exposure time for each image (in seconds)
num_loops = {num_loops}                # number of images in the scan 
sleep_time = {sleep_time}                # sleep time between each image (in seconds), enter a value of 0 to disable it
num_images = {num_images}
dark_frequency = {dark_frequency}
dark_exposure = {dark_exposure}

#Define the sample names
sample_names = {self.sample_data['sample_names']}

# Define list of coordinates (lpx, lpy)
lpx_positions = {self.sample_data['lpxs']}  # x positions
lpy_positions = {self.sample_data['lpys']}    # y positions
num_positions = {len(self.sample_data['lpxs'])}  # Get the number of coordinates

############################
#File name and location
############################

spec_baseDir = "{spec_base_dir + '/'}" 		#Needs trailing '/'
pilatus_baseDir2 = sprintf('~/data/%s', spec_baseDir)

loop_ctr = 0
pos_ctr = 0

# if (!exists("run_ctr")) {{  # Check if run_ctr exists, initialize if not
#     run_ctr = 0;
# }}
run_ctr += 1  # Increment global run counter to prevent accidental deletion

# Execute directory creation using Linux based commands
unix(sprintf('mkdir -p %s', pilatus_baseDir2))
{detector_map.get(axs_value, [])[0]}

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

            {detector_map.get(axs_value, [])[1]}

            eval(sprintf("newfile %s/%s", spec_baseDir, data_dir))
            {detector_map.get(axs_value, [])[2]}

            {detector_map.get(axs_value, [])[3]}

            #Take the actual data
            eval(sprintf("loopscan %d %f %f", num_images, exposure_time, wait_time))

            {detector_map.get(axs_value, [])[4]}
            
            # Implement sleep time between scans if required
            if (sleep_time > 0) {{
                printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
                sleep(sleep_time)
                p ".... DON'T hit control-C until we sleep again\\n"
            }}
    }}
}}

{ 'rock no' if is_rocking else '' }
"""

        # Save the file
        file_path = os.path.join(self.home_directory_path, f"{macro_name}.txt")
        try:
            with open(file_path, "w") as f:
                f.write(content)
            QtWidgets.QMessageBox.information(self, "File Saved", f"File saved as:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error Saving File", f"Could not save file:\n{str(e)}")

    # Override closeEvent properly to confirm exit without crash
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Quit?",
            "Are you sure you want to quit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


# Popup window for entering sample data
class ExcelDataPopup(QtWidgets.QDialog):
    def __init__(self, sample_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sample Data Entry")
        self.sample_data = sample_data

        self.resize(750, 500)

        layout = QtWidgets.QVBoxLayout(self)

        # Instruction text
        instructions = QtWidgets.QLabel(
            "Paste your data directly into each column below (one value per line).\n"
            "Each column must have the same number of lines."
        )
        layout.addWidget(instructions)

        # --- Create 3-column layout ---
        column_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(column_layout)

        # Column 1: Sample Names
        sample_col = QtWidgets.QVBoxLayout()
        column_layout.addLayout(sample_col)
        sample_label = QtWidgets.QLabel("Sample Names")
        self.sample_text = QtWidgets.QTextEdit()
        sample_col.addWidget(sample_label)
        sample_col.addWidget(self.sample_text)

        # Column 2: LPX
        lpx_col = QtWidgets.QVBoxLayout()
        column_layout.addLayout(lpx_col)
        lpx_label = QtWidgets.QLabel("LPX Values")
        self.lpx_text = QtWidgets.QTextEdit()
        lpx_col.addWidget(lpx_label)
        lpx_col.addWidget(self.lpx_text)

        # Column 3: LPY
        lpy_col = QtWidgets.QVBoxLayout()
        column_layout.addLayout(lpy_col)
        lpy_label = QtWidgets.QLabel("LPY Values")
        self.lpy_text = QtWidgets.QTextEdit()
        lpy_col.addWidget(lpy_label)
        lpy_col.addWidget(self.lpy_text)

        # # Paste Button Row
        # paste_layout = QtWidgets.QHBoxLayout()
        # layout.addLayout(paste_layout)

        # paste_label = QtWidgets.QLabel("Paste Excel data:")
        # paste_layout.addWidget(paste_label)

        # paste_btn = QtWidgets.QPushButton("Paste to All")
        # paste_btn.clicked.connect(self.paste_text)
        # paste_layout.addWidget(paste_btn)

        # Bottom Buttons
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self.process_text)
        button_layout.addWidget(ok_btn)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

    # def paste_text(self):
    #     # Split clipboard data into columns and assign to appropriate text boxes
    #     clipboard = QtWidgets.QApplication.clipboard()
    #     text = clipboard.text().strip()
    #     lines = text.split("\n")
    #
    #     names, lpxs, lpys = [], [], []
    #
    #     for line in lines:
    #         cols = line.split("\t")
    #         if len(cols) >= 3:
    #             names.append(cols[0].strip())
    #             lpxs.append(cols[1].strip())
    #             lpys.append(cols[2].strip())
    #
    #     self.sample_text.setPlainText("\n".join(names))
    #     self.lpx_text.setPlainText("\n".join(lpxs))
    #     self.lpy_text.setPlainText("\n".join(lpys))

    def process_text(self):
        names = self.sample_text.toPlainText().strip().splitlines()
        lpxs = self.lpx_text.toPlainText().strip().splitlines()
        lpys = self.lpy_text.toPlainText().strip().splitlines()

        if not (names and lpxs and lpys):
            QtWidgets.QMessageBox.warning(self, "Missing Data", "All three fields must be filled.")
            return

        if not (len(names) == len(lpxs) == len(lpys)):
            QtWidgets.QMessageBox.warning(self, "Mismatch", "Each column must have the same number of entries.")
            return

        try:
            lpxs_float = [float(x) for x in lpxs]
            lpys_float = [float(y) for y in lpys]
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid Numbers", "LPX and LPY values must be numeric.")
            return

        self.sample_data["sample_names"] = [n.strip() for n in names]
        self.sample_data["lpxs"] = lpxs_float
        self.sample_data["lpys"] = lpys_float

        QtWidgets.QMessageBox.information(self, "Data Saved", f"Stored {len(names)} samples.")
        self.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MacroGenerator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
