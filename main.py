import os
import sys
import math
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from fpdf import FPDF
from datetime import datetime
from tkinter import PhotoImage

# -------------------------------
# 🔍 Analyzer Function
# -------------------------------
def analyze_folder(folder_path):
    total_folder = 0
    total_file = 0
    total_file_line = 0
    media_file = 0
    text_file = 0
    empty_file = 0
    no_ext_file = 0
    hidden_file = 0
    line_per_ext = {}
    file_count_per_ext = {}
    max_file = ("", 0)

    def is_text_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except:
            return False

    for root, dirs, files in os.walk(folder_path):
        total_folder += len(dirs)
        for file in files:
            total_file += 1
            file_path = os.path.join(root, file)

            if file.startswith('.'):
                hidden_file += 1

            if is_text_file(file_path):
                text_file += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        total_file_line += line_count

                        _, ext = os.path.splitext(file)
                        ext = ext.lower() if ext else "no_extension"

                        if ext == "no_extension":
                            no_ext_file += 1

                        if line_count == 0:
                            empty_file += 1

                        line_per_ext[ext] = line_per_ext.get(ext, 0) + line_count
                        file_count_per_ext[ext] = file_count_per_ext.get(ext, 0) + 1

                        if line_count > max_file[1]:
                            max_file = (file_path, line_count)

                except:
                    pass
            else:
                media_file += 1

    avg_lines = round(total_file_line / text_file, 2) if text_file else 0

    return {
        "total_folder": total_folder,
        "total_file": total_file,
        "text_file": text_file,
        "media_file": media_file,
        "total_file_line": total_file_line,
        "no_ext_file": no_ext_file,
        "hidden_file": hidden_file,
        "empty_file": empty_file,
        "max_file": max_file,
        "avg_lines": avg_lines,
        "line_per_ext": line_per_ext,
        "file_count_per_ext": file_count_per_ext,
    }

# -------------------------------
# 🌈 GUI Functions
# -------------------------------
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder_selected)

def generate_report():
    folder_path = folder_entry.get()
    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Invalid folder path!")
        return

    result = analyze_folder(folder_path)

    report_lines = []
    report_lines.append("📊 Summary Report\n" + "-"*50)
    report_lines.append(f"📁 Total folders            : {result['total_folder']}")
    report_lines.append(f"📄 Total files              : {result['total_file']}")
    report_lines.append(f"📄 Text files               : {result['text_file']}")
    report_lines.append(f"🖼️ Media files              : {result['media_file']}")
    report_lines.append(f"📝 Total lines in text      : {result['total_file_line']}")
    report_lines.append(f"📂 Files with no extension  : {result['no_ext_file']}")
    report_lines.append(f"📂 Hidden files             : {result['hidden_file']}")
    report_lines.append(f"📄 Empty text files         : {result['empty_file']}")
    report_lines.append(f"⭐ Longest file              : {result['max_file'][0]} ({result['max_file'][1]} lines)")
    report_lines.append(f"📊 Average lines per text   : {result['avg_lines']}")

    report_lines.append("\n📊 Line count per extension:")
    for ext, lines in sorted(result['line_per_ext'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"{ext} = {lines} lines")

    report_lines.append("\n📊 File count per extension:")
    for ext, count in sorted(result['file_count_per_ext'].items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"{ext} = {count} files")

    report_lines.append("\n📊 Average lines per extension:")
    for ext in result['line_per_ext']:
        avg = round(result['line_per_ext'][ext] / result['file_count_per_ext'][ext], 2)
        report_lines.append(f"{ext} = {avg} avg lines")

    final_report = "\n".join(report_lines)

    text_area.config(state='normal')
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, final_report)
    text_area.tag_add("title", "1.0", "1.20")
    text_area.tag_config("title", foreground="purple", font=("Arial", 14, "bold"))
    text_area.tag_config("ext", foreground="blue")
    text_area.tag_config("count", foreground="green")

    global last_report
    last_report = final_report
    text_area.config(state='disabled')

# -------------------------------
# 🖋️ Save as Text File
# -------------------------------
def save_txt():
    if not last_report:
        messagebox.showerror("Error", "Please generate a report first!")
        return

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    default_name = f"report_{now}.txt"
    output_dir = _documents_dir()

    filepath = filedialog.asksaveasfilename(
        initialdir=output_dir,
        initialfile=default_name,
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not filepath:
        return

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(last_report)
        messagebox.showinfo("Success", f"Text file saved as: {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

# -------------------------------
# 🧰 PDF Helper Functions
# -------------------------------
def _find_existing_font(*paths):
    for path in paths:
        if path and os.path.isfile(path):
            return path
    return None

def _replace_report_icons(line):
    icon_map = {
        "📊": "[Stats]",
        "📁": "[Folder]",
        "📄": "[File]",
        "🖼️": "[Media]",
        "📝": "[Lines]",
        "📂": "[Folder]",
        "⭐": "[Top]",
    }
    normalized = line
    for icon, replacement in icon_map.items():
        normalized = normalized.replace(icon, replacement)
    return normalized

def _to_latin1_safe(text):
    return text.encode("latin-1", errors="replace").decode("latin-1")

def _pdf_write_line(pdf, line_height, text):
    try:
        pdf.multi_cell(0, line_height, text, new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.multi_cell(0, line_height, text)
        pdf.set_x(pdf.l_margin)

def _documents_dir():
    docs_path = os.path.join(os.path.expanduser("~"), "Documents")
    return docs_path if os.path.isdir(docs_path) else os.path.expanduser("~")

def _resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def _set_window_icon(window):
    png_icon_path = _resource_path("logo.png")
    ico_icon_path = _resource_path("logo.ico")

    try:
        if os.name == "nt" and os.path.isfile(ico_icon_path):
            window.iconbitmap(ico_icon_path)
            return
    except Exception:
        pass

def _load_header_logo(max_width=84, max_height=84):
    logo_path = _resource_path("logo.png")
    if not os.path.isfile(logo_path):
        return None

    image = PhotoImage(file=logo_path)
    scale = max(1, math.ceil(max(image.width() / max_width, image.height() / max_height)))
    if scale > 1:
        image = image.subsample(scale, scale)
    return image

    try:
        if os.path.isfile(png_icon_path):
            icon_image = PhotoImage(file=png_icon_path)
            window.iconphoto(True, icon_image)
            window._icon_image_ref = icon_image
    except Exception:
        pass

# -------------------------------
# 🖨️ Save as PDF File
# -------------------------------
def save_pdf():
    if not last_report:
        messagebox.showerror("Error", "Please generate a report first!")
        return
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    default_name = f"report_{now}.pdf"
    output_dir = _documents_dir()
    filepath = filedialog.asksaveasfilename(
        initialdir=output_dir,
        initialfile=default_name,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not filepath:
        return
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        regular_font = _find_existing_font(
            os.path.join(script_dir, "NotoSans-Regular.ttf"),
            os.path.join(script_dir, "DejaVuSans.ttf"),
            "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/google-noto/NotoSansBengali-Regular.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
            "/usr/share/fonts/lohit-bengali-fonts/Lohit-Bengali.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        )
        bold_font = _find_existing_font(
            os.path.join(script_dir, "NotoSans-Bold.ttf"),
            os.path.join(script_dir, "DejaVuSans-Bold.ttf"),
            "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/google-noto/NotoSansBengali-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        )

        use_unicode_font = False
        header_style = "B"
        font_family = "Helvetica"

        if regular_font:
            try:
                pdf.add_font("ReportFont", fname=regular_font)
                if bold_font:
                    pdf.add_font("ReportFont", style="B", fname=bold_font)
                else:
                    header_style = ""
                font_family = "ReportFont"
                use_unicode_font = True
            except Exception:
                font_family = "Helvetica"
                header_style = "B"
                use_unicode_font = False

        pdf.set_font(font_family, size=12)

        for raw_line in last_report.splitlines():
            line = _replace_report_icons(raw_line)
            if not use_unicode_font:
                line = _to_latin1_safe(line)

            if raw_line.startswith("📊 Summary Report"):
                pdf.set_font(font_family, style=header_style, size=16)
                try:
                    _pdf_write_line(pdf, 10, line)
                except Exception:
                    _pdf_write_line(pdf, 10, _to_latin1_safe(line))
                pdf.set_font(font_family, size=12)
            elif raw_line.startswith("-"):
                try:
                    _pdf_write_line(pdf, 6, line)
                except Exception:
                    _pdf_write_line(pdf, 6, _to_latin1_safe(line))
            elif raw_line.strip() == "":
                pdf.ln(2)
            else:
                try:
                    _pdf_write_line(pdf, 7, line)
                except Exception:
                    _pdf_write_line(pdf, 7, _to_latin1_safe(line))
        pdf.output(filepath)
        messagebox.showinfo("Success", f"PDF file saved as: {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the PDF: {e}")

# -------------------------------
# 🆘 Help/About Dialog
# -------------------------------
def show_about():
    messagebox.showinfo(
        "About File Analyzer",
        "File Analyzer Pro\n\nDeveloped for professionals.\n\nFeatures:\n- Modern UI (Light/Dark)\n- Detailed file/folder analysis\n- Save report as TXT/PDF\n- Fast, reliable, and easy to use\n\n© 2024 YourBrand. All rights reserved."
    )

# -------------------------------
# 🪟 Main Window
# -------------------------------
last_report = ""

# --- Loading Indicator ---
# loading_var = tk.BooleanVar(value=False)
def set_loading(state):
    loading_var.set(state)
    if state:
        gen_btn.config(state='disabled')
        save_txt_btn.config(state='disabled')
        save_pdf_btn.config(state='disabled')
        loading_label.place(relx=0.5, rely=0.5, anchor='center')
    else:
        gen_btn.config(state='normal')
        save_txt_btn.config(state='normal')
        save_pdf_btn.config(state='normal')
        loading_label.place_forget()

# --- Theme Function ---
def apply_theme(dark):
    if dark:
        root.configure(bg="#23272e")
        style.configure('TFrame', background="#23272e")
        style.configure('TLabel', background="#23272e", foreground="#e0e0e0")
        style.configure('Header.TLabel', background="#23272e", foreground="#f7c873")
        style.configure('Footer.TLabel', background="#23272e", foreground="#888")
        style.configure('TButton', background="#353b45", foreground="#f7c873")
        text_area.config(bg="#181a20", fg="#e0e0e0", insertbackground="#fff")
        about_btn.config(style='TButton')
    else:
        root.configure(bg="#f7f9fa")
        style.configure('TFrame', background="#f7f9fa")
        style.configure('TLabel', background="#f7f9fa", foreground="#222")
        style.configure('Header.TLabel', background="#e3eaf2", foreground="#2d415a")
        style.configure('Footer.TLabel', background="#f7f9fa", foreground="#888")
        style.configure('TButton', background="#e3eaf2", foreground="#2d415a")
        text_area.config(bg="#fffaf0", fg="#222", insertbackground="#222")
        about_btn.config(style='TButton')

# --- Main Window Root ---
root = tk.Tk()
root.title("File Analyzer Pro")
root.geometry("950x750")
_set_window_icon(root)

# --- Tkinter Variables (must be after root) ---
loading_var = tk.BooleanVar(value=False)
# loading_var = tk.BooleanVar(value=False)

style = ttk.Style()
style.theme_use('clam')

# Dark mode variable and toggle
is_dark = tk.BooleanVar(value=False)
def toggle_dark():
    apply_theme(is_dark.get())

# --- Header with Logo/Icon ---
header_frame = ttk.Frame(root, style='TFrame')
header_frame.pack(fill='x', pady=(0, 10))
logo_img = None
try:
    logo_img = _load_header_logo(84, 84)
    if logo_img is None:
        raise FileNotFoundError("logo.png not found")
    logo_label = tk.Label(
        header_frame,
        image=logo_img,
        bg="#e3eaf2",
        width=84,
        height=84
    )
    logo_label.pack(side='left', padx=(20, 10), pady=8)
except Exception:
    logo_label = tk.Label(
        header_frame,
        text="🗂️",
        font=("Segoe UI Emoji", 32),
        bg="#e3eaf2",
        width=84,
        height=84
    )
    logo_label.pack(side='left', padx=(20, 10), pady=8)

header_text = ttk.Label(header_frame, text="File Analyzer Pro", style='Header.TLabel', anchor='w')
header_text.pack(side='left', pady=8)

subtitle = ttk.Label(header_frame, text="Analyze, Summarize & Export Your Files Effortlessly", font=("Segoe UI", 11), background="#e3eaf2", foreground="#4a6073")
subtitle.pack(side='left', padx=(15,0), pady=8)

about_btn = ttk.Button(header_frame, text="?", width=3, command=show_about)
about_btn.pack(side='right', padx=20, pady=8)

# --- Dark Mode Toggle ---
dark_toggle_row = ttk.Frame(root)
dark_toggle_row.pack(fill='x', padx=20)
dark_toggle = ttk.Checkbutton(dark_toggle_row, text="🌙 Dark Mode", variable=is_dark, command=toggle_dark, style='TButton')
dark_toggle.pack(side='right')

main_frame = ttk.Frame(root, padding=20, style='TFrame')
main_frame.pack(fill='both', expand=True)

folder_row = ttk.Frame(main_frame)
folder_row.pack(fill='x', pady=10)

folder_label = ttk.Label(folder_row, text="📂 Select Folder:")
folder_label.pack(side='left', padx=(0, 10))

folder_entry = ttk.Entry(folder_row, width=70)
folder_entry.pack(side='left', padx=(0, 10))

browse_btn = ttk.Button(folder_row, text="Browse", command=browse_folder)
browse_btn.pack(side='left')

btn_row = ttk.Frame(main_frame)
btn_row.pack(fill='x', pady=10)

# --- Generate Report with Loading ---
def generate_report_with_loading():
    set_loading(True)
    root.after(100, _do_generate_report)

def _do_generate_report():
    try:
        generate_report()
    finally:
        set_loading(False)
        root.update()

gen_btn = ttk.Button(btn_row, text="🔍 Analyze Folder", command=generate_report_with_loading)
gen_btn.pack(side='left', padx=(0, 10))

save_txt_btn = ttk.Button(btn_row, text="💾 Save as Text File", command=save_txt)
save_txt_btn.pack(side='left', padx=(0, 10))

save_pdf_btn = ttk.Button(btn_row, text="📝 Save as PDF", command=save_pdf)
save_pdf_btn.pack(side='left', padx=(0, 10))

# --- Loading Label ---
loading_label = tk.Label(main_frame, text="Analyzing... Please wait.", font=("Segoe UI", 16, "bold"), bg="#f7f9fa", fg="#2d415a")

# --- ScrolledText ---
text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 11), bg="#fffaf0", fg="#222", height=22)
text_area.pack(expand=True, fill='both', pady=10)

# --- Footer ---
footer = ttk.Label(root, text="© 2024 YourBrand • File Analyzer Pro v1.0", style='Footer.TLabel', anchor='center')
footer.pack(fill='x', pady=(10, 0))

apply_theme(False)

# --- Button Hover Effects ---
def on_enter(e): e.widget.config(cursor="hand2")
def on_leave(e): e.widget.config(cursor="arrow")
for btn in [gen_btn, save_txt_btn, save_pdf_btn, about_btn, browse_btn, dark_toggle]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

root.mainloop()
