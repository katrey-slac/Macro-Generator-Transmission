import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from data_popup_V1 import open_manual_data_popup
from excel_data_popup import open_excel_data_popup, load_data
from macro_writer_trans import create_trans_macro_file, create_photos_macro_file

import os

class MacroGeneratorTransmissionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Generator")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables
        self.home_directory_var = tk.StringVar()
        self.macro_name_var = tk.StringVar()
        self.data_folder_var = tk.StringVar()
        self.exposure_time_var = tk.IntVar()
        self.sleep_time_var = tk.IntVar()
        self.num_images_var = tk.IntVar()
        self.num_loops_var = tk.IntVar()
        self.df = None
        self.base_coords = None
        self.excel_data_file_var = tk.StringVar()
        self.sample_parameters = {}
        self.dx_shift=tk.StringVar(value="0")
        self.dy_shift = tk.StringVar(value="0")
        self.AXS_var = tk.StringVar()
        self.dark_frequency_var = tk.IntVar()
        self.dark_exposure_var = tk.IntVar()
        self.dark_images_var = tk.IntVar()
        self.rock_lpx_var = tk.StringVar(value="0")
        self.rock_lpy_var = tk.StringVar(value="0")
        self.camera_vars = {}

        # Build GUI
        self.create_title()
        self.create_folder_section()
        self.create_scan_params_section()
        self.create_dark_and_rocking_section()
        self.create_sample_params_section()
        self.create_camera_section()
        self.create_prelim_photos_section()
        self.create_footer()

    # --- GUI Sections ---
    def create_title(self):
        header = tk.Frame(self.root, bg="DeepSkyBlue4")
        header.pack(fill="x")

        title_label = tk.Label(
            header,
            text="Transmission",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="DeepSkyBlue4"
        )
        title_label.pack(pady=5)


    def create_folder_section(self):
        frame = tk.LabelFrame(self.root, text="Save Location")
        frame.pack(padx=10, pady=10, fill="x")

        # -------------------------------
        # Home Directory with scrollable canvas
        # -------------------------------
        home_frame = tk.Frame(frame)
        home_frame.grid(row=0, column=0, columnspan=3, sticky="w", pady=(10, 0))

        # Button to select home directory
        tk.Button(home_frame, text="Select Home Directory", bg="PaleTurquoise1",
                  command=self.select_home_directory).grid(row=0, column=0, padx=(10, 0))

        # Canvas to hold label
        self.canvas = tk.Canvas(home_frame, height=20, width=400)
        self.canvas.grid(row=0, column=1, sticky="w")

        # Horizontal scrollbar
        scrollbar = tk.Scrollbar(home_frame, orient="horizontal", command=self.canvas.xview)
        scrollbar.grid(row=1, column=1, sticky="ew")
        self.canvas.configure(xscrollcommand=scrollbar.set)

        # Frame inside canvas
        self.label_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.label_frame, anchor="nw")

        # Label showing selected folder
        self.home_label = tk.Label(self.label_frame, textvariable=self.home_directory_var, fg="DeepSkyBlue4")
        self.home_label.grid(row=0, column=0)
        self.home_label.bind("<Configure>", self.update_scrollregion)  # update scroll region

        # Macro Name
        tk.Label(frame, text="Macro name:").grid(row=1, column=0, sticky="e", padx=(0, 5))
        tk.Entry(frame, textvariable=self.macro_name_var, width=40).grid(row=1, column=1, sticky="w")
        tk.Label(frame, text="**Cannot include spaces, use - or _ e.g. macro_20250328_air", wraplength=200).grid(row=1, column=2, sticky="w")

        # Data Folder
        tk.Label(frame, text="Data folder name:").grid(row=2, column=0, sticky="e", padx=(5, 5))
        tk.Entry(frame, textvariable=self.data_folder_var, width=40).grid(row=2, column=1, sticky="w")
        tk.Button(frame, text="Same as macro", bg="PaleTurquoise1",
                  command=lambda: self.data_folder_var.set(self.macro_name_var.get())).grid(row=3, column=1, sticky="w", pady=(5,5))


    def create_scan_params_section(self):
        frame = tk.LabelFrame(self.root, text="Scan Parameters")
        frame.pack(padx=10, pady=10, fill="x")

        # Make left and right columns expand so content stays centered
        frame.columnconfigure(0, weight=1)  # left spacer
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=0)
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)
        frame.columnconfigure(5, weight=0)
        frame.columnconfigure(6, weight=1)  # right spacer

        labels = ["Exposure Time [s]:", "Sleep Time [s]:", "Number of Images:", "Number of Loops:", "Scattering Range:"]
        vars = [self.exposure_time_var, self.sleep_time_var, self.num_images_var, self.num_loops_var, self.AXS_var]
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=0, column=i, padx=5)
        # Entries
        tk.Entry(frame, textvariable=self.exposure_time_var, width=10).grid(row=1, column=0, pady=(0,10))
        tk.Entry(frame, textvariable=self.sleep_time_var, width=10).grid(row=1, column=1, pady=(0,10))
        tk.Entry(frame, textvariable=self.num_images_var, width=10).grid(row=1, column=2, pady=(0,10))
        tk.Entry(frame, textvariable=self.num_loops_var, width=10).grid(row=1, column=3, pady=(0,10))
        ttk.Combobox(frame, textvariable=self.AXS_var, values=["SAXS", "WAXS", "Both"], width=10, state="readonly").grid(
            row=1, column=4, pady=(0,10))

    def create_dark_and_rocking_section(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="x")

        # Dark Collection
        dark_frame = tk.LabelFrame(frame, text="Dark Collection")
        dark_frame.grid(row=0, column=0, padx=(0,5))

        tk.Label(dark_frame, text="Take dark data\nevery _ samples:").grid(row=0, column=0, padx=(10,10))
        tk.Entry(dark_frame, textvariable=self.dark_frequency_var, width=10).grid(row=1, column=0, pady=(0,10))
        tk.Label(dark_frame, text="Dark exposure time [s]:").grid(row=0, column=1, padx=(0,10))
        tk.Entry(dark_frame, textvariable=self.dark_exposure_var, width=10).grid(row=1, column=1, pady=(0,10))
        tk.Label(dark_frame, text=" Number of dark images:").grid(row=0, column=2, padx=(0, 10))
        tk.Entry(dark_frame, textvariable=self.dark_images_var, width=10).grid(row=1, column=2, pady=(0, 10))

        # Rocking
        rock_frame = tk.LabelFrame(frame, text="Rocking")
        rock_frame.grid(row=0, column=1, padx=(5,0))

        tk.Label(rock_frame, text="lpx [mm]").grid(row=0, column=0, padx=(10,0), pady=(10,0))
        tk.Entry(rock_frame, textvariable=self.rock_lpx_var, width=10).grid(row=1, column=0, padx=(10,0), pady=(0,10))
        tk.Label(rock_frame, text="lpy [mm]").grid(row=0, column=1, padx=(20,10))
        tk.Entry(rock_frame, textvariable=self.rock_lpy_var, width=10).grid(row=1, column=1, padx=(10,10), pady=(0,15))

    def create_sample_params_section(self):
        frame = tk.LabelFrame(self.root, text="Sample Parameters")
        frame.pack(padx=10, pady=10, fill="x")

        # Make left and right columns expand so content stays centered
        frame.columnconfigure(0, weight=1)  # left spacer
        frame.columnconfigure(1, weight=0)  # button 1
        frame.columnconfigure(2, weight=0)  # "OR"
        frame.columnconfigure(3, weight=0)  # button 2
        frame.columnconfigure(4, weight=0)  # button 3
        frame.columnconfigure(5, weight=1)  # right spacer

        # Centered buttons and label
        tk.Button(
            frame,
            text="Enter Sample Info Manually",
            bg="PaleTurquoise1",
            command=self.open_manual_data_popup
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="OR").grid(row=0, column=2, padx=5)

        tk.Button(
            frame,
            text="Select Excel File",
            bg="PaleTurquoise1",
            command=self.select_excel_data_file
        ).grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            frame,
            text="Sample Info from Excel",
            bg="PaleTurquoise1",
            command=self.open_excel_data_popup
        ).grid(row=0, column=4, padx=5, pady=5)

        # dxdy_frame = tk.Frame(frame)
        # dxdy_frame.grid(row=1, column=1, padx=(0, 20))
        # # dxdy_frame.pack()
        # tk.Label(dxdy_frame, text= "dx:").grid(row=0, column=0, padx=(10,0))
        # tk.Entry(dxdy_frame, textvariable=self.dx_shift, width=10).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        # tk.Label(dxdy_frame, text="dy:").grid(row=0, column=1, padx=(10, 0))
        # tk.Entry(dxdy_frame, textvariable=self.dy_shift, width=10).grid(row=1, column=1, padx=(10, 0), pady=(0, 10))


    def create_camera_section(self):
        frame = tk.LabelFrame(self.root, text="Camera Parameters")
        frame.pack(padx=10, pady=10, fill="x")

        tk.Label(frame, text="Choose cameras to use:").grid(row=0, column=0, columnspan=5)

        camera_labels = ["bottom", "side", "top"]

        # Configure five columns: left spacer | buttons | right spacer
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=0)
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=1)

        for i, cam in enumerate(camera_labels):
            var = tk.IntVar()
            tk.Checkbutton(frame, text=f"{cam.title()} Camera", variable=var).grid(
                row=1, column=i + 1, padx=10, pady=5
            )
            self.camera_vars[cam] = var

    def create_prelim_photos_section(self):
        frame = tk.LabelFrame(self.root, text="Preliminary Photos")
        frame.pack(padx=10, pady=10, fill="x")

        # Configure columns so the center stays in the middle
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        frame.columnconfigure(2, weight=1)

        # Description text — centered across the top
        tk.Label(frame, text="Take photos of sample positions.").grid(
            row=0, column=0, columnspan=3        )

        # Centered button in the middle column
        tk.Button(
            frame,
            text="Save Photo Macro",
            bg="SpringGreen2",
            command=self.create_photos_macro_file
        ).grid(row=1, column=1, pady=(5,10))

    def create_footer(self):
        frame = tk.Frame(self.root, height=40)  # give a reasonable height
        frame.pack(fill="x", pady=5)

        # prevent frame from shrinking to contents so vertical centering works
        frame.pack_propagate(False)

        # Center the button using place (relx=0.5 is 50% of frame width)
        button = tk.Button(
            frame,
            text="Save Macro File",
            bg="chartreuse2",
            command=self.create_trans_macro_file
        )
        button.place(relx=0.5, rely=0.5, anchor="center")

        # Watermark on the right; pack keeps it stuck to the right edge
        label = tk.Label(
            frame,
            text="Katerina Reynolds 2025",
            fg="indianred",
            font=("Arial", 8)
        )
        label.pack(side="right", padx=10)

    # -------------------------------
    # Functions
    # -------------------------------
    def update_scrollregion(self, event=None):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

    def select_home_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.home_directory_var.set(folder)

    def open_manual_data_popup(self):
        open_manual_data_popup(self.root, self.sample_parameters)

    def select_excel_data_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.excel_data_file_var.set(file)
            # Reset state so new file loads properly
            self.df = None
            self.base_coords = None
            self.sample_parameters = {}
            print(self.excel_data_file_var.get())

    def load_excel_file(self):
        self.df, self.base_coords = load_data(self.excel_data_file_var.get())
        self.sample_parameters["sample_names"] = list(self.df["Sample Name*"])
        self.sample_parameters["lpxs"] = list(self.df["x"])
        self.sample_parameters["lpys"] = list(self.df["y"])

    def open_excel_data_popup(self):
        # Check if a file has been selected
        if not self.excel_data_file_var.get():
            messagebox.showerror("Error", "Please select an Excel file first.")
            return  # Stop here, do NOT continue
        # load file
        self.load_excel_file()
        open_excel_data_popup(
            self.root,
            self.df,
            self.base_coords,
            self.sample_parameters
        )
        # print(self.sample_parameters)

    def create_trans_macro_file(self):
        create_trans_macro_file(
            self.root,
            self.home_directory_var.get(),
            self.data_folder_var.get(),
            self.macro_name_var.get(),
            self.exposure_time_var.get(),
            self.sleep_time_var.get(),
            self.num_images_var.get(),
            self.num_loops_var.get(),
            self.dark_frequency_var.get(),
            self.dark_exposure_var.get(),
            self.dark_images_var.get(),
            self.rock_lpx_var.get(),
            self.rock_lpy_var.get(),
            self.sample_parameters,
            self.AXS_var.get(),
            {label: var.get() for label, var in self.camera_vars.items()}
            # self.camera_vars
            # parent=self.root
        )

    def create_photos_macro_file(self):
        create_photos_macro_file(
            self.root,
            self.home_directory_var.get(),
            self.macro_name_var.get(),
            self.sample_parameters
        )



# -------------------------------
# Run GUI
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MacroGeneratorTransmissionGUI(root)
    root.mainloop()