import tkinter as tk
from tkinter import scrolledtext
from tkinter import Toplevel, Listbox

class Autocomplete:
    """
    Adds notepad-like autocomplete feature to the text widget.
    """
    def __init__(self, scrolled_text):
        self.scrolled_text = scrolled_text

    def enable(self):
        self.scrolled_text.bind('<Key>', self.on_key_release)
        self.scrolled_text.bind("<FocusOut>", self.hide_autocomplete_options)
        self.scrolled_text.bind("<Button-1>", self.hide_autocomplete_options)

    def get_last_word(self, event):
        caret_pos = self.scrolled_text.index("insert")
        text_up_to_caret = self.scrolled_text.get("1.0", caret_pos) + event.char

        if text_up_to_caret[-1].isspace():
            return None
        
        words = text_up_to_caret.split()
        last_word = words[-1] if words else ""
        return last_word
    
    def replace_word_before_caret(self, replacement_text):
        caret_pos = self.scrolled_text.index("insert")
        text_up_to_caret = self.scrolled_text.get("1.0", caret_pos)
        if text_up_to_caret:
            word_start_index = text_up_to_caret.rfind(' ') + 1 if ' ' in text_up_to_caret else 0
            word_start_pos = f"{caret_pos.split('.')[0]}.{int(caret_pos.split('.')[1]) - len(text_up_to_caret) + word_start_index}"
            self.scrolled_text.delete(word_start_pos, caret_pos)
            self.scrolled_text.insert(word_start_pos, replacement_text)

    def on_key_release(self, event):
        if (event.keysym == "Tab" or event.keysym == "Down" or event.keysym == "Up") and hasattr(self, 'autocomplete_window') and self.autocomplete_window.winfo_exists():
            current_selection = self.listbox.curselection()

            if current_selection:
                self.listbox.selection_clear(current_selection)

                direction = 1 if event.keysym == "Tab" or event.keysym == "Down" else -1

                next_index = (current_selection[0] + direction) % self.listbox.size()
                self.listbox.select_set(next_index)
            return "break"
        
        if event.keysym == "Return" and hasattr(self, 'autocomplete_window') and self.autocomplete_window.winfo_exists():
            self.on_option_selected(None)
            self.hide_autocomplete_options()
            return "break"
        
        if event.keysym in ["BackSpace", "Delete", "Escape", "Left", "Right", "Up", "Down", "Control_L", "Control_R"]:
            self.hide_autocomplete_options(event)
            return
             
        current_word = self.get_last_word(event)
        self.show_autocomplete_options(current_word)
                
    def show_autocomplete_options(self, partial_word):
        if not partial_word:
            self.hide_autocomplete_options()
            return
        
        words = set(self.scrolled_text.get("1.0", tk.END).split())
        options = [o for o in words 
                   if o.lower().startswith(partial_word.lower())
                   and not o[0].isdigit()]

        if not options:
            self.hide_autocomplete_options()
            return
        
        if len(options) == 1 and options[0].lower() == partial_word.lower():
            self.hide_autocomplete_options()
            return
        
        # Create a top-level window for displaying options
        if not hasattr(self, 'autocomplete_window') or not self.autocomplete_window.winfo_exists():
            self.autocomplete_window = Toplevel()

            self.autocomplete_window.wm_attributes("-topmost", 1)  # Set the window to be on top of all others

            self.autocomplete_window.wm_overrideredirect(True)  # Hide the window border/title
            
            x, y, cx, cy = self.scrolled_text.bbox("insert")
            x += self.scrolled_text.winfo_rootx() + 25
            y += self.scrolled_text.winfo_rooty() + 25
            self.autocomplete_window.wm_geometry("+%d+%d" % (x, y))
            
            self.listbox = Listbox(self.autocomplete_window, selectmode=tk.SINGLE)
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
            
            self.listbox.bind("<<ListboxSelect>>", self.on_option_selected)
        
        # Update listbox options
        self.listbox.delete(0, tk.END)
        for option in options:
            self.listbox.insert(tk.END, option)
        self.listbox.config(height=len(options))

        # Select the first item by default
        self.listbox.select_set(0)

    def hide_autocomplete_options(self, event=None):
        if hasattr(self, 'autocomplete_window') and self.autocomplete_window.winfo_exists():
            self.autocomplete_window.destroy()
                
    def on_option_selected(self, event):
        self.listbox.itemconfig(self.listbox.curselection(), bg='blue', fg='white')
        
        # Get selected option
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        selection = self.listbox.get(index)

        self.replace_word_before_caret(selection)
        
        self.autocomplete_window.destroy()
        
# Example usage
def main():
    root = tk.Tk()
    root.title("Autocomplete ScrolledText Example")

    scrolled_text = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    scrolled_text.pack(fill=tk.BOTH, expand=True)

    Autocomplete(scrolled_text).enable()
    root.call('wm', 'attributes', '.', '-topmost', '1')
    root.mainloop()

if __name__ == "__main__":
    main()