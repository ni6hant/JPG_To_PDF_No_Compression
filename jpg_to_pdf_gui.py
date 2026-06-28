import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
import img2pdf
from tkinterdnd2 import TkinterDnD, DND_FILES


class JPGtoPDFApp:

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

        tk.Button(
            bottom,
            text="Create PDF",
            height=2,
            command=self.make_pdf
        ).grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=15
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

        out=os.path.join(
            self.output_var.get(),
            self.filename_var.get()
        )

        with open(out,"wb") as f:

            f.write(
                img2pdf.convert(
                    self.images
                )
            )

        messagebox.showinfo(
            "Done",
            f"Saved:\n{out}"
        )


root = TkinterDnD.Tk()
app = JPGtoPDFApp(root)
root.mainloop()