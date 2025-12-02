import tkinter as tk
from tkinter import messagebox

def open_manual_data_popup(root, sample_parameters):
    """Open a popup window to paste Excel data for samples, LPX, and LPY."""
    popup = tk.Toplevel(root)
    popup.title("Paste Excel Data")

    tk.Label(popup, text="Enter in one data set per line.").pack(pady=5)

    text_frame = tk.Frame(popup)
    text_frame.pack(padx=10, pady=5)

    tk.Label(text_frame, text="Sample Names").grid(row=0, column=0)
    tk.Label(text_frame, text="LPX Values").grid(row=0, column=1)
    tk.Label(text_frame, text="LPY Values").grid(row=0, column=2)

    sample_text = tk.Text(text_frame, height=15, width=20)
    lpx_text = tk.Text(text_frame, height=15, width=10)
    lpy_text = tk.Text(text_frame, height=15, width=10)

    sample_text.grid(row=1, column=0, padx=5)
    lpx_text.grid(row=1, column=1, padx=5)
    lpy_text.grid(row=1, column=2, padx=5)

    # Bind tab key to move focus to next field
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"  # prevent default tab insertion

    sample_text.bind("<Tab>", focus_next_widget)
    lpx_text.bind("<Tab>", focus_next_widget)
    lpy_text.bind("<Tab>", focus_next_widget)

    # Prefill existing values (if available)

    if 'sample_names' in sample_parameters:
        sample_text.insert(tk.END, "\n".join(sample_parameters['sample_names']))

    if 'lpxs' in sample_parameters:
        lpx_text.insert(tk.END, "\n".join(str(x) for x in sample_parameters['lpxs']))

    if 'lpys' in sample_parameters:
        lpy_text.insert(tk.END, "\n".join(str(y) for y in sample_parameters['lpys']))

    def save_pasted_data():
        try:
            names = [n.strip() for n in sample_text.get("1.0", tk.END).splitlines() if n.strip()]
            lpxs = [float(n.strip()) for n in lpx_text.get("1.0", tk.END).splitlines() if n.strip()]
            lpys = [float(n.strip()) for n in lpy_text.get("1.0", tk.END).splitlines() if n.strip()]

            if not (len(names) == len(lpxs) == len(lpys)):
                raise ValueError("Column lengths mismatch")

            sample_parameters['sample_names'] = names
            sample_parameters['lpxs'] = lpxs
            sample_parameters['lpys'] = lpys
            popup.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "LPX and LPY must be numeric and columns must match length.", parent=popup)

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Cancel", command=popup.destroy, bg="red3", fg="white").pack(side="left", padx=5)
    tk.Button(btn_frame, text="Save", command=save_pasted_data, bg="green", fg="white").pack(side="right", padx=5)

