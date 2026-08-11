import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from modules.config import load_settings, save_settings
from modules.scanner import scan_directory
from modules.indexer import VectorIndex
from modules.packer import pack_context

PRESET_EXTENSIONS = [
    ".py", ".cs", ".js", ".ts", ".jsx", ".tsx", ".html", 
    ".css", ".rs", ".go", ".cpp", ".c", ".h", 
    ".java", ".json", ".yaml", ".md", ".sql"
]

def close_pyinstaller_splash():
    """Closes the PyInstaller splash screen if it is active."""
    try:
        import pyi_splash
        if pyi_splash.is_alive():
            pyi_splash.close()
    except ImportError:
        pass  # Normal Python environment (not packaged via PyInstaller)

def launch_gui():
    settings = load_settings()

    root = tk.Tk()
    root.title("Code-RAG Builder & Context Packer")
    root.geometry("680x540")
    root.minsize(600, 480)

    # Style Configuration
    style = ttk.Style()
    style.theme_use("clam")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Dismiss splash screen 200ms after window initializes
    root.after(200, close_pyinstaller_splash)

    # ==========================================
    # TAB 1: SEARCH & PACK
    # ==========================================
    tab_main = ttk.Frame(notebook)
    notebook.add(tab_main, text=" 🔍 Query & Pack ")

    # Directory Frame
    frame_dir = ttk.LabelFrame(tab_main, text="Target Directory", padding=10)
    frame_dir.pack(fill="x", padx=10, pady=5)

    dir_var = tk.StringVar(value=settings.get("target_dir", "."))
    ttk.Entry(frame_dir, textvariable=dir_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def browse_dir():
        selected = filedialog.askdirectory(initialdir=dir_var.get())
        if selected:
            dir_var.set(selected)
            settings["target_dir"] = selected
            save_settings(settings)

    ttk.Button(frame_dir, text="Browse", command=browse_dir).pack(side="right")

    # Options Frame
    frame_opts = ttk.LabelFrame(tab_main, text="Search Settings", padding=10)
    frame_opts.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame_opts, text="Max Full Files Included (Top-K):").grid(row=0, column=0, sticky="w")
    top_k_var = tk.IntVar(value=settings.get("top_k", 5))
    ttk.Spinbox(frame_opts, from_=1, to=50, textvariable=top_k_var, width=5).grid(row=0, column=1, sticky="w", padx=5)

    # Query Input
    frame_query = ttk.LabelFrame(tab_main, text="AI Query / Prompt Context", padding=10)
    frame_query.pack(fill="both", expand=True, padx=10, pady=5)
    
    query_text = tk.Text(frame_query, height=6, wrap="word")
    query_text.pack(fill="both", expand=True)

    # Console Log Output
    frame_log = ttk.Frame(tab_main, padding=5)
    frame_log.pack(fill="x", padx=10)
    status_var = tk.StringVar(value="Ready")
    ttk.Label(frame_log, textvariable=status_var, font=("TkDefaultFont", 9, "italic")).pack(side="left")

    # Action Button & Worker Thread
    def execute_rag_pipeline():
        user_query = query_text.get("1.0", tk.END).strip()
        target_dir = dir_var.get()
        k = top_k_var.get()

        if not user_query:
            messagebox.showwarning("Warning", "Please enter a query before running.")
            return

        # -------------------------------------------------------------------
        # BROWSER-STYLE DOWNLOAD PROMPT (Save As dialog)
        # -------------------------------------------------------------------
        default_file_name = settings.get("output_file", "packed_context.txt")
        save_path_str = filedialog.asksaveasfilename(
            title="Download Context As...",
            initialdir=target_dir,
            initialfile=default_file_name,
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("XML Files", "*.xml"),
                ("All Files", "*.*")
            ]
        )

        # Abort if user closes/cancels the save dialog
        if not save_path_str:
            return

        destination_path = Path(save_path_str)

        # Save run preferences
        settings["target_dir"] = target_dir
        settings["top_k"] = k
        settings["output_file"] = destination_path.name
        save_settings(settings)

        def worker():
            try:
                status_var.set("Scanning workspace directory...")
                exts = set(settings.get("extensions", []))
                files = scan_directory(target_dir, extensions=exts)
                
                if not files:
                    status_var.set("No matching files found.")
                    messagebox.showinfo("No Files", "No files matching your selected extensions were found.")
                    return

                status_var.set(f"Found {len(files)} files. Updating vector index...")
                cache_folder = str(Path(target_dir) / ".rag_cache")
                index = VectorIndex(cache_dir=cache_folder)
                index.index_files(files)

                status_var.set("Performing semantic search...")
                results = index.search(user_query, top_k=k)

                status_var.set(f"Saving packed context to {destination_path.name}...")
                pack_context(results, user_query, str(destination_path))

                status_var.set(f"✓ Context saved to {destination_path.name}")
                messagebox.showinfo("Download Complete", f"Context file successfully saved to:\n\n{destination_path}")
            except Exception as err:
                status_var.set("Error during execution.")
                messagebox.showerror("Error", f"An error occurred:\n{str(err)}")

        threading.Thread(target=worker, daemon=True).start()

    btn_run = ttk.Button(tab_main, text="⚡ Index Codebase & Save Context...", command=execute_rag_pipeline)
    btn_run.pack(fill="x", padx=10, pady=10)

    # ==========================================
    # TAB 2: EXTENSIONS & PREFERENCES
    # ==========================================
    tab_ext = ttk.Frame(notebook)
    notebook.add(tab_ext, text=" ⚙️ Extensions & Settings ")

    frame_ext_list = ttk.LabelFrame(tab_ext, text="Select Included File Extensions", padding=10)
    frame_ext_list.pack(fill="both", expand=True, padx=10, pady=5)

    active_exts = set(settings.get("extensions", []))
    checkbox_vars = {}

    # Render Grid of Extension Checkboxes
    ext_grid_frame = ttk.Frame(frame_ext_list)
    ext_grid_frame.pack(fill="both", expand=True)

    cols = 4
    for i, ext in enumerate(PRESET_EXTENSIONS):
        var = tk.BooleanVar(value=(ext in active_exts))
        checkbox_vars[ext] = var
        chk = ttk.Checkbutton(ext_grid_frame, text=ext, variable=var)
        chk.grid(row=i // cols, column=i % cols, sticky="w", padx=10, pady=5)

    # Custom Extensions
    frame_custom = ttk.LabelFrame(tab_ext, text="Custom Extensions (Comma separated)", padding=10)
    frame_custom.pack(fill="x", padx=10, pady=5)

    custom_exts = [e for e in active_exts if e not in PRESET_EXTENSIONS]
    custom_var = tk.StringVar(value=", ".join(custom_exts))
    ttk.Entry(frame_custom, textvariable=custom_var).pack(fill="x")

    def save_extension_settings():
        selected = [ext for ext, v in checkbox_vars.items() if v.get()]
        
        # Parse custom extensions
        raw_custom = custom_var.get().split(",")
        for c in raw_custom:
            cleaned = c.strip().lower()
            if cleaned:
                if not cleaned.startswith("."):
                    cleaned = f".{cleaned}"
                if cleaned not in selected:
                    selected.append(cleaned)

        settings["extensions"] = selected
        save_settings(settings)

    ttk.Button(tab_ext, text="💾 Save Preferences", command=save_extension_settings).pack(pady=10)

    # Auto-save when closing window
    def on_closing():
        save_extension_settings()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()