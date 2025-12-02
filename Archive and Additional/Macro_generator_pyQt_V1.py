from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGroupBox, QFileDialog, QMessageBox, QScrollArea,
    QComboBox, QSpinBox, QCheckBox, QGridLayout
)
from PyQt6.QtCore import Qt
from data_popup_PyQt_V1 import open_manual_data_popup
from excel_data_popup import open_excel_data_popup, load_data
from macro_writer import create_trans_macro_file, create_photos_macro_file
import sys
import os


class MacroGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Generator")

        # -------------------------------
        # Variables
        # -------------------------------
        self.home_directory = ""
        self.macro_name = ""
        self.data_folder = ""
        self.exposure_time = 0
        self.sleep_time = 0
        self.num_images = 0
        self.num_loops = 0
        self.AXS = ""
        self.dark_frequency = 0
        self.dark_exposure = 0
        self.rock_lpx = "0"
        self.rock_lpy = "0"
        self.camera_vars = {}
        self.sample_parameters = {}
        self.df = None
        self.base_coords = None
        self.excel_data_file = ""

        # -------------------------------
        # Build GUI
        # -------------------------------
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.create_folder_section())
        main_layout.addWidget(self.create_scan_params_section())
        main_layout.addWidget(self.create_dark_and_rocking_section())
        main_layout.addWidget(self.create_sample_params_section())
        main_layout.addWidget(self.create_camera_section())
        main_layout.addWidget(self.create_prelim_photos_section())
        main_layout.addWidget(self.create_footer())

        self.setLayout(main_layout)

    # --- GUI Sections ---
    def create_folder_section(self):
        group = QGroupBox("Save Location")
        layout = QGridLayout()

        # Select Home Directory
        select_btn = QPushButton("Select Home Directory")
        select_btn.setStyleSheet("background-color: PaleTurquoise;")
        select_btn.clicked.connect(self.select_home_directory)
        layout.addWidget(select_btn, 0, 0)

        # Scrollable area for showing the path
        self.home_label = QLabel("")
        self.home_label.setStyleSheet("color: DeepSkyBlue;")
        self.home_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(40)
        scroll.setWidget(self.home_label)
        layout.addWidget(scroll, 0, 1, 1, 2)

        # Macro name
        layout.addWidget(QLabel("Macro name:"), 1, 0)
        self.macro_entry = QLineEdit()
        layout.addWidget(self.macro_entry, 1, 1)
        layout.addWidget(QLabel("**Cannot include spaces; use - or _"), 1, 2)

        # Data folder name
        layout.addWidget(QLabel("Data folder name:"), 2, 0)
        self.data_entry = QLineEdit()
        layout.addWidget(self.data_entry, 2, 1)

        same_btn = QPushButton("Same as macro")
        same_btn.setStyleSheet("background-color: PaleTurquoise;")
        same_btn.clicked.connect(lambda: self.data_entry.setText(self.macro_entry.text()))
        layout.addWidget(same_btn, 3, 1)

        group.setLayout(layout)
        return group

    def create_scan_params_section(self):
        group = QGroupBox("Scan Parameters")
        layout = QGridLayout()

        labels = [
            "Exposure Time (s):", "Sleep Time (s):",
            "Number of Images:", "Number of Loops:", "Scattering Range:"
        ]
        for i, label in enumerate(labels):
            layout.addWidget(QLabel(label), 0, i)

        # Entries
        self.exposure_spin = QSpinBox()
        self.sleep_spin = QSpinBox()
        self.num_images_spin = QSpinBox()
        self.num_loops_spin = QSpinBox()
        self.AXS_combo = QComboBox()
        self.AXS_combo.addItems(["SAXS", "WAXS", "Both"])

        widgets = [
            self.exposure_spin, self.sleep_spin,
            self.num_images_spin, self.num_loops_spin, self.AXS_combo
        ]
        for i, w in enumerate(widgets):
            layout.addWidget(w, 1, i)

        group.setLayout(layout)
        return group

    def create_dark_and_rocking_section(self):
        container = QWidget()
        layout = QHBoxLayout()

        # --- Dark Collection ---
        dark_group = QGroupBox("Dark Collection")
        dark_layout = QGridLayout()
        dark_layout.addWidget(QLabel("Take dark data every _ samples:"), 0, 0)
        self.dark_freq_spin = QSpinBox()
        dark_layout.addWidget(self.dark_freq_spin, 1, 0)
        dark_layout.addWidget(QLabel("Dark exposure time (s):"), 0, 1)
        self.dark_exp_spin = QSpinBox()
        dark_layout.addWidget(self.dark_exp_spin, 1, 1)
        dark_group.setLayout(dark_layout)

        # --- Rocking ---
        rock_group = QGroupBox("Rocking")
        rock_layout = QGridLayout()
        rock_layout.addWidget(QLabel("lpx in mm"), 0, 0)
        self.lpx_entry = QLineEdit("0")
        rock_layout.addWidget(self.lpx_entry, 1, 0)
        rock_layout.addWidget(QLabel("lpy in mm"), 0, 1)
        self.lpy_entry = QLineEdit("0")
        rock_layout.addWidget(self.lpy_entry, 1, 1)
        rock_group.setLayout(rock_layout)

        layout.addWidget(dark_group)
        layout.addWidget(rock_group)
        container.setLayout(layout)
        return container

    def create_sample_params_section(self):
        group = QGroupBox("Sample Parameters")
        layout = QGridLayout()

        manual_btn = QPushButton("Enter Sample Info Manually")
        manual_btn.setStyleSheet("background-color: PaleTurquoise;")
        manual_btn.clicked.connect(self.open_manual_data_popup)
        layout.addWidget(manual_btn, 0, 1)

        layout.addWidget(QLabel("OR"), 0, 2)

        excel_btn = QPushButton("Select Excel File")
        excel_btn.setStyleSheet("background-color: PaleTurquoise;")
        excel_btn.clicked.connect(self.select_excel_data_file)
        layout.addWidget(excel_btn, 0, 3)

        open_excel_btn = QPushButton("Sample Info from Excel")
        open_excel_btn.setStyleSheet("background-color: PaleTurquoise;")
        open_excel_btn.clicked.connect(self.open_excel_data_popup)
        layout.addWidget(open_excel_btn, 0, 4)

        group.setLayout(layout)
        return group

    def create_camera_section(self):
        group = QGroupBox("Camera Parameters")
        layout = QGridLayout()
        layout.addWidget(QLabel("Choose cameras to use:"), 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        camera_labels = ["bottom", "side", "top"]
        for i, cam in enumerate(camera_labels):
            checkbox = QCheckBox(f"{cam.title()} Camera")
            layout.addWidget(checkbox, 1, i + 1)
            self.camera_vars[cam] = checkbox

        group.setLayout(layout)
        return group

    def create_prelim_photos_section(self):
        group = QGroupBox("Preliminary Photos")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(QLabel("Take photos of sample positions."))

        save_btn = QPushButton("Save Photo Macro")
        save_btn.setStyleSheet("background-color: SpringGreen;")
        save_btn.clicked.connect(self.create_photos_macro_file)
        layout.addWidget(save_btn)

        group.setLayout(layout)
        return group

    def create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout()

        # Center button
        save_btn = QPushButton("Save Macro File")
        save_btn.setStyleSheet("background-color: chartreuse; font-weight: bold;")
        save_btn.clicked.connect(self.create_trans_macro_file)
        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addStretch()

        # Watermark
        label = QLabel("Katerina Reynolds 2025")
        label.setStyleSheet("color: indianred; font-size: 10px;")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignRight)

        footer.setLayout(layout)
        return footer

    # -------------------------------
    # Functions
    # -------------------------------
    def closeEvent(self, event):
        """Ask before quitting."""
        reply = QMessageBox.question(
            self, "Quit", "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def select_home_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.home_directory = folder
            self.home_label.setText(folder)

    def open_manual_data_popup(self):
        open_manual_data_popup(self, self.sample_parameters)

    def select_excel_data_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file:
            self.excel_data_file = file
            print(file)

    def load_excel_file(self):
        if self.df is None or self.base_coords is None:
            self.df, self.base_coords = load_data(self.excel_data_file)
            self.sample_parameters["sample_names"] = list(self.df["Sample Name"])
            self.sample_parameters["lpxs"] = list(self.df["x"])
            self.sample_parameters["lpys"] = list(self.df["y"])

    def open_excel_data_popup(self):
        self.load_excel_file()
        open_excel_data_popup(self, self.df, self.base_coords, self.sample_parameters)

    def create_trans_macro_file(self):
        create_trans_macro_file(
            self,
            self.home_directory,
            self.data_entry.text(),
            self.macro_entry.text(),
            self.exposure_spin.value(),
            self.sleep_spin.value(),
            self.num_images_spin.value(),
            self.num_loops_spin.value(),
            self.dark_freq_spin.value(),
            self.dark_exp_spin.value(),
            self.lpx_entry.text(),
            self.lpy_entry.text(),
            self.sample_parameters,
            self.AXS_combo.currentText(),
            {label: var.isChecked() for label, var in self.camera_vars.items()}
        )

    def create_photos_macro_file(self):
        create_photos_macro_file(
            self,
            self.home_directory,
            self.data_entry.text(),
            self.macro_entry.text(),
            self.sample_parameters
        )


# -------------------------------
# Run GUI
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MacroGeneratorGUI()
    window.show()
    sys.exit(app.exec())
