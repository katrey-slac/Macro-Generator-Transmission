from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt


def open_manual_data_popup(parent, sample_parameters):
    """
    Open a popup dialog to paste Excel-like data for samples, LPX, and LPY.
    Works the same as the Tkinter version but uses PyQt6 widgets.
    """

    # -------------------------------
    # Create dialog window
    # -------------------------------
    dialog = QDialog(parent)
    dialog.setWindowTitle("Paste Excel Data")
    dialog.setModal(True)
    main_layout = QVBoxLayout(dialog)

    # Instruction label
    label = QLabel("Enter one data set per line.")
    main_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

    # -------------------------------
    # Text input section (grid layout)
    # -------------------------------
    text_frame = QWidget()
    grid = QGridLayout(text_frame)

    grid.addWidget(QLabel("Sample Names"), 0, 0)
    grid.addWidget(QLabel("LPX Values"), 0, 1)
    grid.addWidget(QLabel("LPY Values"), 0, 2)

    sample_text = QTextEdit()
    lpx_text = QTextEdit()
    lpy_text = QTextEdit()

    # Make Tab move focus to next widget
    for te in [sample_text, lpx_text, lpy_text]:
        te.setTabChangesFocus(True)
        te.setFixedHeight(250)  # same height as Tkinter version
        te.setFixedWidth(150)  # adjust width

    # sample_text.setFixedWidth(200)
    # lpx_text.setFixedWidth(100)
    # lpy_text.setFixedWidth(100)
    # sample_text.setFixedHeight(250)
    # lpx_text.setFixedHeight(250)
    # lpy_text.setFixedHeight(250)

    grid.addWidget(sample_text, 1, 0)
    grid.addWidget(lpx_text, 1, 1)
    grid.addWidget(lpy_text, 1, 2)

    main_layout.addWidget(text_frame)

    # -------------------------------
    # Prefill existing values (if available)
    # -------------------------------
    if 'sample_names' in sample_parameters:
        sample_text.setPlainText("\n".join(sample_parameters['sample_names']))

    if 'lpxs' in sample_parameters:
        lpx_text.setPlainText("\n".join(str(x) for x in sample_parameters['lpxs']))

    if 'lpys' in sample_parameters:
        lpy_text.setPlainText("\n".join(str(y) for y in sample_parameters['lpys']))

    # -------------------------------
    # Buttons (Save / Cancel)
    # -------------------------------
    btn_layout = QHBoxLayout()
    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    cancel_btn = QPushButton("Cancel")
    cancel_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
    cancel_btn.clicked.connect(dialog.reject)
    btn_layout.addWidget(cancel_btn)

    save_btn = QPushButton("Save")
    save_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")

    def save_pasted_data():
        """Validate and store entered data."""
        try:
            names = [n.strip() for n in sample_text.toPlainText().splitlines() if n.strip()]
            lpxs = [float(n.strip()) for n in lpx_text.toPlainText().splitlines() if n.strip()]
            lpys = [float(n.strip()) for n in lpy_text.toPlainText().splitlines() if n.strip()]

            if not (len(names) == len(lpxs) == len(lpys)):
                raise ValueError("Column lengths mismatch")

            sample_parameters['sample_names'] = names
            sample_parameters['lpxs'] = lpxs
            sample_parameters['lpys'] = lpys

            dialog.accept()
        except ValueError:
            QMessageBox.critical(
                dialog,
                "Invalid Input",
                "LPX and LPY must be numeric and columns must have equal lengths.",
                QMessageBox.StandardButton.Ok
            )

    save_btn.clicked.connect(save_pasted_data)
    btn_layout.addWidget(save_btn)

    main_layout.addLayout(btn_layout)

    # -------------------------------
    # Show dialog (blocks until closed)
    # -------------------------------
    dialog.exec()
