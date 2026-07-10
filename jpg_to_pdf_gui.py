import os
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
import img2pdf
from tkinterdnd2 import TkinterDnD, DND_FILES


class JPGtoPDFApp:

    # Any image with a smaller side under this many pixels is treated
    # as an intentional blank spacer page rather than real content.
    MIN_BLANK_PX = 10

    # Used to size a blank page when there are no "real" images in the
    # batch to infer a sensible size from (rough Letter-ish proportions).
    DEFAULT_BLANK_SIZE = (850, 1100)

    def __init__(self, root):

        self.root = root
        self.root.title("JPG → PDF Combiner")

        self.root.geometry("1200x750")
        self.root.minsize(1000,700)

        self.images = []
        self.current_preview = None

        if getattr(sys, 'frozen', False):
            self.launch_dir = os.path.dirname(
                sys.executable
            )
        else:
            self.launch_dir = os.path.dirname(
                os.path.abspath(__file__)
            )

        self.build_ui()


    def build_ui(self):

        main = tk.Frame(self.root)
        main.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ---------------- LEFT ----------------

        left = tk.Frame(main)
        left.pack(
            side="left",
            fill="y"
        )

        tk.Label(
            left,
            text="Import Images",
            font=("Arial",11,"bold")
        ).pack()

        tk.Button(
            left,
            text="Browse Images",
            command=self.add_images
        ).pack(
            fill="x",
            pady=5
        )

        drop_area = tk.Label(
            left,
            text="Drag & Drop Images Here",
            relief="groove",
            height=6
        )

        drop_area.pack(
            fill="x",
            pady=5
        )

        drop_area.drop_target_register(
            DND_FILES
        )

        drop_area.dnd_bind(
            "<<Drop>>",
            self.drop_files
        )

        tk.Label(
            left,
            text="Image Order",
            font=("Arial",11,"bold")
        ).pack(
            pady=(20,5)
        )

        self.listbox = tk.Listbox(
            left,
            width=40,
            height=20
        )

        self.listbox.pack()

        self.listbox.bind(
            "<<ListboxSelect>>",
            self.show_preview
        )

        controls = tk.Frame(left)
        controls.pack(pady=5)

        tk.Button(
            controls,
            text="↑",
            width=5,
            command=self.move_up
        ).grid(row=0,column=0)

        tk.Button(
            controls,
            text="↓",
            width=5,
            command=self.move_down
        ).grid(row=0,column=1)

        tk.Button(
            controls,
            text="Sort A-Z",
            command=self.sort_images
        ).grid(row=0,column=2)

        # ---------------- RIGHT ----------------

        right = tk.Frame(main)
        right.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20
        )

        tk.Label(
            right,
            text="Preview",
            font=("Arial",11,"bold")
        ).pack()

        self.preview_canvas = tk.Canvas(
            right,
            bg="white"
        )

        self.preview_canvas.pack(
            fill="both",
            expand=True
        )

        self.preview_canvas.bind(
            "<Configure>",
            self.resize_preview
        )

        # ---------------- BOTTOM ----------------

        bottom = tk.Frame(self.root)
        bottom.pack(
            fill="x",
            padx=10,
            pady=10
        )

        bottom.columnconfigure(
            1,
            weight=1
        )

        tk.Label(
            bottom,
            text="Output Folder:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.output_var = tk.StringVar(
            value=self.launch_dir
        )

        tk.Entry(
            bottom,
            textvariable=self.output_var
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5
        )

        tk.Button(
            bottom,
            text="Browse",
            command=self.select_output
        ).grid(
            row=0,
            column=2
        )

        tk.Label(
            bottom,
            text="Filename:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        self.filename_var = tk.StringVar(
            value="combined_output.pdf"
        )

        tk.Entry(
            bottom,
            textvariable=self.filename_var
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5
        )

        self.create_button = tk.Button(
            bottom,
            text="Create PDF",
            height=2,
            command=self.make_pdf
        )

        self.create_button.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(15,5)
        )

        # ---- Progress bar + status label ----

        self.progress = ttk.Progressbar(
            bottom,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.progress.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew"
        )

        self.status_var = tk.StringVar(value="")

        tk.Label(
            bottom,
            textvariable=self.status_var,
            anchor="w"
        ).grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(5,0)
        )


    def add_images(self):

        files = filedialog.askopenfilenames(
            filetypes=[
                ("JPEG Images","*.jpg *.jpeg")
            ]
        )

        self.process_files(files)


    def drop_files(self,event):

        files = self.root.tk.splitlist(
            event.data
        )

        self.process_files(files)


    def process_files(self, files):

        for f in files:

            if (
                f.lower().endswith(
                    (".jpg",".jpeg")
                )
                and f not in self.images
            ):

                self.images.append(f)

        self.refresh_list()

        if self.images:

            first = os.path.splitext(
                os.path.basename(
                    self.images[0]
                )
            )[0]

            self.filename_var.set(
                f"combined_{first}.pdf"
            )


    def refresh_list(self):

        self.listbox.delete(
            0,
            tk.END
        )

        for img in self.images:

            self.listbox.insert(
                tk.END,
                os.path.basename(img)
            )


    def show_preview(self,event):

        sel = self.listbox.curselection()

        if not sel:
            return

        self.current_preview = (
            self.images[sel[0]]
        )

        self.display_preview(
            self.current_preview
        )


    def resize_preview(self,event):

        if self.current_preview:

            self.display_preview(
                self.current_preview
            )


    def display_preview(self,path):

        img = Image.open(path)

        w = max(
            self.preview_canvas.winfo_width()-20,
            100
        )

        h = max(
            self.preview_canvas.winfo_height()-20,
            100
        )

        img.thumbnail((w,h))

        photo = ImageTk.PhotoImage(img)

        self.preview_canvas.delete(
            "all"
        )

        self.preview_canvas.create_image(
            w//2,
            h//2,
            image=photo
        )

        self.preview_canvas.image = photo


    def move_up(self):

        sel=self.listbox.curselection()

        if not sel or sel[0]==0:
            return

        i=sel[0]

        self.images[i-1],self.images[i]=(
            self.images[i],
            self.images[i-1]
        )

        self.refresh_list()
        self.listbox.selection_set(i-1)


    def move_down(self):

        sel=self.listbox.curselection()

        if not sel:
            return

        i=sel[0]

        if i==len(self.images)-1:
            return

        self.images[i+1],self.images[i]=(
            self.images[i],
            self.images[i+1]
        )

        self.refresh_list()
        self.listbox.selection_set(i+1)


    def sort_images(self):

        self.images.sort()
        self.refresh_list()


    def select_output(self):

        folder=filedialog.askdirectory()

        if folder:
            self.output_var.set(folder)


    def make_pdf(self):

        if not self.images:

            messagebox.showerror(
                "Error",
                "No images selected"
            )

            return

        out = os.path.join(
            self.output_var.get(),
            self.filename_var.get()
        )

        # Lock down the UI while the conversion runs
        self.create_button.config(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("Starting...")

        images_snapshot = list(self.images)

        worker = threading.Thread(
            target=self._convert_worker,
            args=(images_snapshot, out),
            daemon=True
        )

        worker.start()


    def _convert_worker(self, images, out):
        """Runs on a background thread. Only touches Tk via self.root.after()."""

        total_steps = len(images) + 1  # +1 for the final write step
        prepared = []

        try:

            # First pass: look at every image's real pixel size so we
            # know how to size any blank spacer pages. img2pdf needs
            # each page between 3 and 14400 PDF units, so a 1x1 filler
            # image can't be handed to it directly - it has to be
            # regenerated at a sane size first.
            real_sizes = []

            for path in images:
                with Image.open(path) as im:
                    w, h = im.size

                if min(w, h) >= self.MIN_BLANK_PX:
                    real_sizes.append((w, h))

            if real_sizes:
                target_w = sum(s[0] for s in real_sizes) // len(real_sizes)
                target_h = sum(s[1] for s in real_sizes) // len(real_sizes)
            else:
                target_w, target_h = self.DEFAULT_BLANK_SIZE

            with tempfile.TemporaryDirectory() as tmp_dir:

                for idx, path in enumerate(images, start=1):

                    with Image.open(path) as im:
                        w, h = im.size
                        # Validate/decode so any genuinely broken file
                        # (not just an intentional tiny blank) is caught.
                        im.verify()

                    if min(w, h) < self.MIN_BLANK_PX:

                        path_to_use = self._make_blank_page(
                            tmp_dir, idx, target_w, target_h
                        )

                        label = f"Inserting blank page {idx}/{len(images)}"

                    else:

                        path_to_use = path
                        label = (
                            f"Processing {idx}/{len(images)}: "
                            f"{os.path.basename(path)}"
                        )

                    prepared.append(path_to_use)

                    pct = int((idx / total_steps) * 100)

                    self.root.after(
                        0,
                        self._update_progress,
                        pct,
                        label
                    )

                self.root.after(
                    0,
                    self._update_progress,
                    int((len(images) / total_steps) * 100),
                    "Building PDF..."
                )

                pdf_bytes = img2pdf.convert(prepared)

                with open(out, "wb") as f:
                    f.write(pdf_bytes)

            self.root.after(0, self._update_progress, 100, "Done")
            self.root.after(0, self._conversion_finished, out, None)

        except Exception as exc:

            self.root.after(0, self._conversion_finished, out, exc)


    def _make_blank_page(self, tmp_dir, idx, width, height):
        """Generate a plain white filler image sized to be a valid PDF page."""

        safe_w = max(width, self.MIN_BLANK_PX)
        safe_h = max(height, self.MIN_BLANK_PX)

        blank = Image.new("RGB", (safe_w, safe_h), "white")

        path = os.path.join(tmp_dir, f"_blank_{idx}.jpg")
        blank.save(path, "JPEG")

        return path


    def _update_progress(self, pct, message):

        self.progress["value"] = pct
        self.status_var.set(message)


    def _conversion_finished(self, out, error):

        self.create_button.config(state="normal")

        if error is not None:

            self.progress["value"] = 0
            self.status_var.set("Failed")

            messagebox.showerror(
                "Error",
                f"Could not create PDF:\n{error}"
            )

            return

        self.status_var.set(f"Saved: {out}")

        messagebox.showinfo(
            "Done",
            f"Saved:\n{out}"
        )


root = TkinterDnD.Tk()
app = JPGtoPDFApp(root)
root.mainloop()