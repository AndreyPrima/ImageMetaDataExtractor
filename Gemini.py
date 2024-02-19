import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ExifTags
import csv
import json
import xmltodict
import yaml


def get_image_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image.getexif()
        metadata = {}

        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    gps_info = {}
                    for gps_tag, gps_value in value.items():
                        gps_tag_name = ExifTags.GPSTAGS.get(gps_tag, gps_tag)
                        gps_info[gps_tag_name] = gps_value
                    metadata[tag_name] = gps_info
                else:
                    metadata[tag_name] = value  # Include additional data from the image's EXIF data
        else:
            metadata["Error"] = "No EXIF data found in the image."

        return metadata
    except IOError as e:
        return f"Error opening image: {str(e)}"
    except AttributeError as e:
        return f"Error extracting metadata: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def save_metadata_to_file(metadata, file_format):
    file_path = filedialog.asksaveasfilename(defaultextension="." + file_format,
                                             filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")])
    if file_path:
        try:
            with open(file_path, "w", newline='') as f:
                if file_format == "txt":
                    for key, value in metadata.items():
                        f.write(f"{key}: {value}\n")
                elif file_format == "csv":
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(["Field", "Value"])
                    for key, value in metadata.items():
                        csv_writer.writerow([key, value])
                elif file_format == "json":
                    json.dump(metadata, f, indent=4)
                elif file_format == "xml":
                    xml_data = xmltodict.unparse({"metadata": metadata}, pretty=True)
                    f.write(xml_data)
                elif file_format == "yaml":
                    yaml.dump(metadata, f, default_flow_style=False)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")

            messagebox.showinfo("Success", "Metadata saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving metadata: {str(e)}")


metadata = {}


def open_image():
    global metadata  # Use the global metadata variable
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")])

    try:
        if file_path:
            metadata = get_image_metadata(file_path)
            metadata_text = "\n".join([f"{key}: {value}" for key, value in metadata.items()])
            metadata_label.config(text=metadata_text)

            image = Image.open(file_path)
            image.thumbnail((800, 600))
            img_preview = ImageTk.PhotoImage(image)

            preview_label.config(image=img_preview)
            preview_label.image = img_preview

            error_label.config(text="")  # Clear any previous error message
            status_bar.config(text="Image loaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        status_bar.config(text="Error loading image.")
    finally:
        app.update_idletasks()

    save_button.config(command=lambda: save_metadata_to_file(metadata, file_format_var.get()))


def change_background_color():
    color = colorchooser.askcolor()[1]
    if color:
        set_window_background(color)


def show_about_info():
    messagebox.showinfo("About", "Image Metadata Extractor\nVersion 1.0\nCreated by Your Name")


def set_window_background(background_color):
    app.config(bg=background_color)
    metadata_label.config(bg=background_color)


def toggle_dark_mode():
    current_bg = app.cget("bg")
    if current_bg == "white":
        set_dark_mode()
    else:
        set_light_mode()


def set_dark_mode():
    app.config(bg="#333333")
    metadata_label.config(bg="#333333", fg="white")
    open_button.config(bg="#555555", fg="white")
    save_button.config(bg="#555555", fg="white")
    preview_label.config(bg="#555555")
    file_format_label.config(bg="#333333", fg="white")
    file_format_menu.config(bg="#333333", fg="white", highlightbackground="#333333")
    status_bar.config(bg="#555555", fg="white")
    error_label.config(bg="#555555", fg="white")
    app.update_idletasks()


def set_light_mode():
    app.config(bg="white")
    metadata_label.config(bg="white", fg="black")
    open_button.config(bg=None, fg="black")
    save_button.config(bg=None, fg="black")
    preview_label.config(bg=None)
    file_format_label.config(bg="white", fg="black")
    file_format_menu.config(bg="white", fg="black", highlightbackground="white")
    status_bar.config(bg=None, fg="black")
    error_label.config(bg=None, fg="black")
    app.update_idletasks()


app = tk.Tk()
app.title("Image Metadata Extractor")
app.geometry("800x600")

open_button = tk.Button(app, text="Open Image", command=open_image)
open_button.pack(pady=10)

metadata_label = tk.Label(font=("Helvetica", 12), bg='#888888', bd=1, relief="solid", anchor="w", justify="left",
                          fg="black")
metadata_label.pack(fill="x", padx=10, pady=5)

preview_label = tk.Label()
preview_label.pack(pady=10)

file_format_var = tk.StringVar(value="txt")
file_format_label = tk.Label(app, text="Save Format:")
file_format_label.pack(pady=5)
file_format_options = ["TXT", "CSV", "JSON", "XML", "YAML"]
file_format_menu = tk.OptionMenu(app, file_format_var, *file_format_options)
file_format_menu.pack(pady=5)

dark_mode_button = tk.Button(app, text="Toggle Dark Mode", command=toggle_dark_mode)
dark_mode_button.pack(pady=5)

save_button = tk.Button(app, text="Save Metadata", command=lambda: save_metadata_to_file(metadata, file_format_var.get()))
save_button.pack(pady=10)

error_label = tk.Label(text="", fg="black")
error_label.pack(pady=5)

status_bar = tk.Label(app, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

menu_bar = tk.Menu(app)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Image", command=open_image)
file_menu.add_command(label="Save Metadata", command=lambda: save_metadata_to_file(metadata, file_format_var.get()))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=app.quit)

view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Change Background Color", command=change_background_color)
view_menu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about_info)

menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="View", menu=view_menu)
menu_bar.add_cascade(label="Help", menu=help_menu)

app.config(menu=menu_bar)

app.resizable(True, True)
app.protocol("WM_DELETE_WINDOW", app.quit)

if __name__ == "__main__":
    app.mainloop()
