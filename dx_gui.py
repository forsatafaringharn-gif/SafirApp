# dx_gui.py - PART 1 (Optimized UI)
# -- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2, threading, datetime, os
from dx_engine import DX_OS_Engine

class DX_OS_GUI:
    def __init__(self, root):
        self.engine = DX_OS_Engine(); self.root = root
        self.root.title(f"DX-OS | {self.engine.owner}")

        # افزایش ارتفاع برای نمایش کامل دکمه‌ها در تمام مانیتورها
        self.root.geometry("650x950") 
        self.root.configure(bg="#2C0000")
        self._setup_ui()

    def _setup_ui(self):
        # --- Header / Logo Section ---
        self.logo_frame = tk.Frame(self.root, bg="#2C0000"); self.logo_frame.pack(pady=15)
        self.logo_label = tk.Label(self.logo_frame, bg="#2C0000"); self.logo_label.pack(); self.load_logo()
        tk.Button(self.logo_frame, text="🖼️ Change Logo", command=self.upload_logo, font=("Tahoma", 8), bg="#D4AF37", fg="#2C0000", cursor="hand2").pack(pady=5)

        h = tk.Frame(self.root, bg="#D4AF37", height=60); h.pack(fill="x")
        tk.Label(h, text="DX-OS OPERATING SYSTEM", font=("Arial", 18, "bold"), bg="#D4AF37", fg="#2C0000").pack(pady=15)

        # --- Main Action Container ---
        m = tk.Frame(self.root, bg="#2C0000"); m.pack(expand=True, fill="both", padx=30, pady=10)

        # Primary Buttons (Standardized Size)
        btns = [
            ("👁️ Live Preview", self.action_preview, "#E6E6FA"), 
            ("📸 Capture Photo", self.action_camera, "#D4AF37"), 
            ("🎙️ Audio Record/Upload", self.action_mic, "#D4AF37"), 
            ("✍️ Write Narrative", self.action_text, "#D4AF37")
        ]
        for t, cmd, clr in btns: 
            tk.Button(m, text=t, command=cmd, width=30, font=("Tahoma", 12, "bold"), bg=clr, fg="#2C0000", cursor="hand2").pack(pady=6)

        tk.Frame(m, height=2, bg="#D4AF37").pack(fill="x", pady=15)

        # --- Upload Section ---
        up_frame = tk.Frame(m, bg="#2C0000"); up_frame.pack()
        tk.Button(up_frame, text="📤 Upload Img", command=lambda: self.manual_upload("Images"), bg="#D4AF37", width=12).pack(side="left", padx=5)

        tk.Button(up_frame, text="📤 Upload Vid", command=lambda: self.manual_upload("Videos"), bg="#D4AF37", width=12).pack(side="left", padx=5)

        # --- Management & Intelligence Section (Slightly smaller font for better fit) ---
        tk.Button(m, text="⚙️ Sync Hierarchical Narratives", command=self.action_sync, width=30, font=("Tahoma", 11, "bold"), bg="#C0C0C0", fg="#2C0000", cursor="hand2").pack(pady=8)
        tk.Button(m, text="📚 Manage General Narratives", command=self.action_manage_general, width=30, font=("Tahoma", 11, "bold"), bg="#ADD8E6", fg="#2C0000", cursor="hand2").pack(pady=5)
        tk.Button(m, text="🌐 Translate Narratives", command=self.action_translate, width=30, font=("Tahoma", 11, "bold"), bg="#C0C0C0", fg="#2C0000", cursor="hand2").pack(pady=5)
        tk.Button(m, text="⚙️ Camera Settings", command=self.open_settings, width=30, font=("Tahoma", 11, "bold"), bg="#F0E68C", fg="#2C0000", cursor="hand2").pack(pady=5)

        # The bottom button - now with more space and clear contrast
        tk.Button(m, text="🔄 Sync with Android", command=lambda: messagebox.showinfo("Sync", "Syncing..."), width=30, font=("Tahoma", 12, "bold"), bg="#A52A2A", fg="white", cursor="hand2").pack(pady=15)

        self.status_var = tk.StringVar(value="System Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", bg="#1A0000", fg="#D4AF37").pack(side="bottom", fill="x")

    def update_status(self, txt): self.status_var.set(txt)

    def load_logo(self):
        p = self.engine.get_logo_path()
        if p and os.path.exists(p):
            try:
                img = Image.open(p).convert("RGB"); img.thumbnail((120, 120)); ph = ImageTk.PhotoImage(img)
                self.logo_label.config(image=ph, text=""); self.logo_label.image = ph
            except: self.logo_label.config(text="[ IMAGE ERROR ]", fg="#D4AF37")
        else: self.logo_label.config(text="[ LOGO ]", fg="#D4AF37", font=("Arial", 12, "bold"))

    def upload_logo(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg .jpeg .png .gif")])
        if p: self.engine.save_logo_path(p); self.load_logo(); messagebox.showinfo("Logo", "Logo updated!")

    def _get_url(self):
        ip = self.engine.get_ip(); return f"{ip}/video" if not ip.endswith("/video") else ip

    def manual_upload(self, cat):
        f = filedialog.askopenfilename()
        if f:
            res = self.engine.upload_manual_file(f, cat)
            if "Error" in str(res): messagebox.showerror("Error", res)
            else: messagebox.showinfo("Success", f"Uploaded to {cat}: {res}")
    # --- Audio & Speech to Text Logic ---
    def action_mic(self):
        """مدیریت ورودی صوتی و تبدیل آن به متن"""
        res = messagebox.askyesno("Audio to Text", "Do you want to upload a voice file?\n(Yes: Upload / No: Record Placeholder)")
        if res:
            f = filedialog.askopenfilename(filetypes=[("Audio", ".wav")])
            if f: 
                dst = self.engine.upload_manual_file(f, "Audio")
                self._process_audio_to_text(dst)
        else:
            # ذخیره یک فایل صوتی پیش‌فرض برای تست در صورت عدم آپلود
            f = self.engine.save_data('mic')
            self.update_status("🎙️ Audio Saved. Transcribing...")
            self._process_audio_to_text(f)

    def _process_audio_to_text(self, audio_path):
        """تبدیل فایل صوتی به متن و ذخیره به عنوان روایت (Narrative)"""
        self.update_status("⌛ Converting Speech to Text...")
        text_result = self.engine.transcribe_audio(audio_path)

        if "Error" in text_result:
            messagebox.showerror("Transcription Error", text_result)
            self.update_status("Transcription Failed")
        else:
            # استخراج نام فایل برای سینک کردن با عکس (مثلاً Gilak_01.wav -> Gilak_01.txt)
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            txt_path = os.path.join(self.engine.base_dir, "Text", f"{base_name}.txt")

            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(text_result)

            self.update_status("✅ Audio converted to Narrative!")
            messagebox.showinfo("Success", f"Text extracted:\n\n{text_result}\n\nSaved to: {txt_path}")

    # --- Intelligent Sync & Management ---
    def action_sync(self):
        self.update_status("⚙️ Syncing Hierarchical Narratives...")
        res = self.engine.sync_narratives_with_images()
        if not res: 
            messagebox.showinfo("Sync", "No images found to sync."); return
        sw = tk.Toplevel(self.root); sw.title("Sync Results"); sw.geometry("600x700"); sw.configure(bg="#2C0000")
        txt = tk.Text(sw, font=("Tahoma", 11), bg="#FDF5E6", fg="#2C0000", padx=10, pady=10); txt.pack(expand=True, fill="both", padx=20, pady=20)
        txt.insert("1.0", "\n\n".join(res)); txt.config(state="disabled")
        self.update_status("Sync Complete")

    def action_manage_general(self):
        gw = tk.Toplevel(self.root); gw.title("General Narratives Manager"); gw.geometry("500x600"); gw.configure(bg="#2C0000")
        tk.Label(gw, text="Manage General Ethnicity/Group Narratives", font=("Arial", 12, "bold"), bg="#2C0000", fg="#D4AF37").pack(pady=10)

        list_frame = tk.Frame(gw, bg="#2C0000"); list_frame.pack(pady=10)
        lbs = tk.Listbox(list_frame, font=("Tahoma", 11), width=30, bg="#FDF5E6", fg="#2C0000")
        lbs.pack(side="left")

        def load_list():
            lbs.delete(0, "end")
            for item in self.engine.get_general_narratives_list(): lbs.insert("end", item)
        load_list()

        edit_frame = tk.Frame(gw, bg="#2C0000"); edit_frame.pack(pady=10, padx=20, fill="both", expand=True)
        tk.Label(edit_frame, text="Category (Tag) e.g: Gilak", bg="#2C0000", fg="white").pack()
        ent_cat = tk.Entry(edit_frame, font=("Tahoma", 12), justify="center"); ent_cat.pack(pady=5, fill="x")

        tk.Label(edit_frame, text="Narrative Text:", bg="#2C0000", fg="white").pack()

        txt_gen = tk.Text(edit_frame, font=("Tahoma", 11), height=10, bg="white", fg="#2C0000"); txt_gen.pack(pady=5, fill="both", expand=True)

        def save_gen():
            cat = ent_cat.get().strip()
            text = txt_gen.get("1.0", "end-1c").strip()
            if cat and text:
                self.engine.save_general_narrative(cat, text)
                load_list(); messagebox.showinfo("Saved", f"General narrative for {cat} saved!")
            else: messagebox.showwarning("Error", "Please enter both category and text!")

        tk.Button(edit_frame, text="💾 Save General Narrative", command=save_gen, bg="#D4AF37", fg="#2C0000", font=("Tahoma", 11, "bold")).pack(pady=10)

        def select_item(e):
            sel = lbs.curselection()
            if sel:
                cat = lbs.get(sel[0])
                ent_cat.delete(0, "end"); ent_cat.insert(0, cat)
                with open(os.path.join(self.engine.base_dir, "General_Narratives", f"{cat}.txt"), "r", encoding="utf-8") as f:
                    txt_gen.delete("1.0", "end"); txt_gen.insert("1.0", f.read())

        lbs.bind("<<ListboxSelect>>", select_item)

    def action_translate(self):
        self.update_status("🌐 Filtering & Translating...")
        res = self.engine.get_filtered_translations()
        if isinstance(res, str): messagebox.showerror("Error", res); return
        if not res: messagebox.showinfo("No Results", "No relevant narratives found."); return
        tw = tk.Toplevel(self.root); tw.title("Filtered Translations"); tw.geometry("500x600"); tw.configure(bg="#2C0000")
        tk.Label(tw, text="Filtered Narratives", font=("Arial", 14, "bold"), bg="#2C0000", fg="#D4AF37").pack(pady=10)
        txt_area = tk.Text(tw, font=("Tahoma", 11), bg="#FDF5E6", fg="#2C0000", padx=10, pady=10); txt_area.pack(expand=True, fill="both", padx=20, pady=10)
        txt_area.insert("1.0", "\n".join(res)); txt_area.config(state="disabled")
        def save_pdf():
            f = self.engine.export_to_pdf(res)
            messagebox.showinfo("PDF Export", f"Saved as: {f}")
        tk.Button(tw, text="📄 Export to PDF", command=save_pdf, bg="#D4AF37", fg="#2C0000", font=("Tahoma", 10, "bold"), width=20).pack(pady=10)
        self.update_status("Displaying Translations")

    def open_settings(self):
        sw = tk.Toplevel(self.root); sw.title("IP Config"); sw.geometry("400x200")
        tk.Label(sw, text="Enter Mobile IP:").pack(pady=20)
        ent = tk.Entry(sw, font=("Consolas", 12), justify="center"); ent.insert(0, self.engine.get_ip()); ent.pack(pady=10, padx=20, fill="x")
        def save():
            if ent.get().strip(): self.engine.save_ip(ent.get().strip()); messagebox.showinfo("Saved", "IP updated!"); sw.destroy()
        tk.Button(sw, text="💾 Save", command=save, bg="#D4AF37", width=20).pack(pady=20)

    def action_preview(self):
        pw = tk.Toplevel(self.root); pw.title("Live Stream"); pw.geometry("640x600")
        ct = tk.Frame(pw); ct.pack(expand=True, fill="both")
        lbl = tk.Label(ct, text="Connecting...", bg="black", fg="white"); lbl.pack(expand=True, fill="both")
        tk.Button(ct, text="🔴 Start Recording", command=lambda: threading.Thread(target=self.action_video).start(), bg="#B22222", fg="white", font=("Tahoma", 12, "bold"), cursor="hand2").pack(pady=10)
        url = self._get_url(); cap = cv2.VideoCapture(url)
        def update():
            if not pw.winfo_exists(): cap.release(); return
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); img = ImageTk.PhotoImage(Image.fromarray(frame))
                lbl.config(image=img, text=""); lbl.image = img
            else: lbl.config(text="Camera offline!")
            pw.after(10, update)
        update()

    def action_camera(self):
        self.update_status("📸 Capturing...")
        try:
            cap = cv2.VideoCapture(self._get_url()); ret, frame = cap.read()
            if ret:

                f = self.engine.save_data('camera'); cv2.imwrite(f, frame)
                self.update_status("Photo Saved!"); messagebox.showinfo("Success", f"Saved: {f}")
            cap.release()
        except Exception as e: messagebox.showerror("Error", str(e))

    def action_video(self):
        rw = tk.Toplevel(self.root); rw.title("Recording"); rw.geometry("300x150"); rw.configure(bg="#B22222")
        tk.Label(rw, text="🔴 RECORDING...", fg="white", bg="#B22222", font=("Arial", 14, "bold")).pack(expand=True)
        rw.grab_set(); self.update_status("🎥 Recording (10s)...")
        try:
            cap = cv2.VideoCapture(self._get_url()); f = self.engine.save_data('video')
            out = cv2.VideoWriter(f, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
            st = datetime.datetime.now()
            while (datetime.datetime.now() - st).seconds < 10:
                ret, frame = cap.read()
                if ret: out.write(frame)
                else: break
            cap.release(); out.release(); rw.destroy()
            self.update_status("Video Saved!"); messagebox.showinfo("Success", f"Saved: {f}")
        except Exception as e:
            if rw.winfo_exists(): rw.destroy()
            messagebox.showerror("Error", str(e))

    def action_text(self):
        tw = tk.Toplevel(self.root); tw.title("Write Narrative"); tw.geometry("500x450"); tw.configure(bg="#FDF5E6")
        toolbar = tk.Frame(tw, bg="#D4AF37", height=40); toolbar.pack(fill="x")
        def save_txt():
            c = txt.get("1.0", "end-1c")
            if c.strip():
                f = self.engine.save_data('keyboard', c)
                messagebox.showinfo("Saved", f"Text saved: {f}"); tw.destroy()
            else: messagebox.showwarning("Warning", "Text area is empty!")
        def clear_txt(): txt.delete("1.0", "end")
        tk.Button(toolbar, text="💾 Save", command=save_txt, bg="#D4AF37", fg="#2C0000", font=("Tahoma", 9, "bold")).pack(side="left", padx=5, pady=5)
        tk.Button(toolbar, text="🗑️ Clear", command=cleartxt, bg="#D4AF37", fg="#2C0000", font=("Tahoma", 9, "bold")).pack(side="left", padx=5, pady=5)
        txt = tk.Text(tw, font=("Tahoma", 12), bg="white", fg="#2C0000", padx=10, pady=10); txt.pack(expand=True, fill="both", padx=10, pady=10)
        self.update_status("✍️ Writing Narrative...")

if __name__ == "__main__":
    root = tk.Tk(); app = DX_OS_GUI(root); root.mainloop()
