import tkinter as tk
from PIL import Image
from pystray import Icon as icon, MenuItem as item
import threading
from datetime import datetime

from timetracker import calculate_total_grouped_by_labels, InvalidFormatError
from autocomplete import Autocomplete
from text_editing_basics import TextEditingBasics
from text_decorator import TextDecorator

from tkinter import scrolledtext

from tkinter import ttk

# Persistent GUI to interact with the timetracker.py script, embedded in a system tray icon and storing last state in a file.

window = None
def toggle_window(icon, item):
    if window.state() == "withdrawn":
        window.deiconify()
    else:
        window.withdraw()

def on_exit(icon, item):
    icon.stop()
    window.destroy()

def setup_tray_icon():
    icon_image = Image.open("icon.png")

    menu = (item('Toggle Window', toggle_window, default=True), item('Exit', on_exit))
    tray_icon = icon("test_icon", icon_image, "Time tracker", menu)
    tray_icon.run()

left_text_area_decorator = None

def process(content):
    with open('~save.txt', 'w') as file:
      file.write(content)

    left_text_area_decorator.clear_errors()

    sections = parse_sections(content)
    result = ""
    for section in sections:
        if section[0].startswith("# Note"):
            continue
        result = result + section[0] + "\n"
        try:
            result = result + calculate_total_grouped_by_labels(section[1]) + "\n\n"
        except InvalidFormatError as e:
            for line_number in e.line_numbers:
                left_text_area_decorator.show_error(line_number + section[2])
            result = result + f"{e.args[0]}\n\n"
    return result

def sync_text(*args):
    if left_text_area.edit_modified():
        right_text_area_current_scroll_position = right_text_area.yview()
        right_text_area.config(state=tk.NORMAL)
        right_text_area.delete('1.0', tk.END)
        content = process(left_text_area.get('1.0', tk.END))
        right_text_area.insert(tk.INSERT, content)

        left_text_area.edit_modified(False)

        right_text_area.yview_moveto(right_text_area_current_scroll_position[0])

def parse_sections(input_string):
    lines = input_string.split('\n')

    sections = [] 
    current_header = "" 
    current_content = []

    line_number = 0
    current_header_start_line = 0

    for line in lines:
        line_number = line_number + 1
        if line.startswith('#'):
            if current_header is not None:
                sections.append((current_header, '\n'.join(current_content), current_header_start_line))
                current_content = []
            current_header = line
            current_header_start_line = line_number
        else:
            current_content.append(line)
    if current_header is not None:
        sections.append((current_header, '\n'.join(current_content), current_header_start_line))

    non_empty_sections = [section for section in sections if section[0].strip() != '' or section[1].strip() != '']

    return non_empty_sections

is_left_text_area_visible = True

def add_missing_header_for_current_day():
    """
    # insert new header with current date at startup if it's not already there
    """
    now = datetime.now()
    day_header = now.strftime("# %A (%Y-%m-%d)")
    if not day_header in left_text_area.get('1.0', tk.END):
        left_text_area.insert(tk.END, "\n")
        left_text_area.insert(tk.END, day_header)
        left_text_area.insert(tk.END, "\n")
        left_text_area.insert(tk.END, now.strftime("%H:%M-??:?? <started>"))

def main():
    global window
    window = tk.Tk()
    window.title("Time tracker")
    window.overrideredirect(True)

    def set_window_position(twocol = True):
        if twocol:
            width = 800
            window.columnconfigure(0, weight=1)
        else:
            width = 400
            window.columnconfigure(0, weight=0)

        height = window.winfo_screenheight() / 2
        tray_height = 50
        x = window.winfo_screenwidth() - width
        y = window.winfo_screenheight() - height - tray_height
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def toggle_left_text_area():
        global is_left_text_area_visible
        if is_left_text_area_visible:
            left_text_area.grid_remove()
            is_left_text_area_visible = False
            set_window_position(twocol=False)

        else:
            left_text_area.grid()
            is_left_text_area_visible = True
            set_window_position(twocol=True)

    set_window_position()

    toggle_button = ttk.Button(window, text="Toggle mode", command=toggle_left_text_area)
    toggle_button.grid(column=1, row=1, sticky="w", padx=(10,5), pady=10)

    global left_text_area, right_text_area

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)

    left_text_area = scrolledtext.ScrolledText(window, width=1, height=1, undo=True)
    left_text_area.grid(column=0, row=0, sticky="nsew", padx=(10,5), pady=10)
    right_text_area = scrolledtext.ScrolledText(window, width=1, height=1)
    right_text_area.grid(column=1, row=0, sticky="nsew", padx=(5,10), pady=10)

    with open('~save.txt', 'r') as file:
      left_text_area.insert(tk.INSERT, file.read())

    add_missing_header_for_current_day()

    TextEditingBasics(left_text_area).enable()
    TextEditingBasics(right_text_area).enable()

    Autocomplete(left_text_area).enable()

    global left_text_area_decorator
    left_text_area_decorator = TextDecorator(left_text_area)

    # Bind the event of any change in the left text area
    left_text_area.bind("<<Modified>>", sync_text)

    sync_text()
    left_text_area.focus()
    left_text_area.see(tk.END)
    right_text_area.see(tk.END)

    # Initially, hide the window and show only the tray icon
    window.withdraw()

    threading.Thread(target=setup_tray_icon, daemon=True).start()
    window.call('wm', 'attributes', '.', '-topmost', '1') # always on top

    window.mainloop()

if __name__ == "__main__":
    main()
