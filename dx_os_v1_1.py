# -*- coding: utf-8 -*-
import os, datetime, threading, cv2, tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
try: from googletrans import Translator
except: Translator = None

class DX_OS_Engine:
    def __init__(self):
        self.owner = "Sayed Hossain Ahmadi"; self.base_dir = "DX_OS_Data"
        self.config_f = os.path.join(self.base_dir, "config.txt"); self.logo_f = os.path.join(self.base_dir, "logo_path.txt")
        self.folders = ["Images", "Audio", "Text", "Backups", "Sync_Pool", "Videos"]; self._init_sys()
    def _init_sys(self):
        if not os.path.exists(self.base_dir): os.makedirs(self.base_dir)
        for f in self.folders:
            p = os.path.join(self.base_dir, f)
            if not os.path.exists(p): os.makedirs(p)
        if not os.path.exists(self.config_f): self.save_ip("http://10.180.243.185:8080")
    def get_ip(self):
        try:
            with open(self.config_f, "r", encoding="utf-8") as f: return f.read().strip()
        except: return "http://10.180.243.185:8080"
    def save_ip(self, ip):
        with open(self.config_f, "w", encoding="utf-8") as f: f.write(ip)
    def get_logo_path(self):
        if os.path.exists(self.logo_f):
            try:
                with open(self.logo_f, "r", encoding="utf-8") as f: return f.read().strip()
            except: return None
        return None
    def save_logo_path(self, p):
        with open(self.logo_f, "w", encoding="utf-8") as f: f.write(p)
    def save_data(self, st, c=None):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        exts = {'camera':('Images','.jpg'), 'mic':('Audio','.wav'), 'video':('Videos','.avi'), 'keyboard':('Text','.txt')}
        folder, ext = exts.get(st, ('Text', '.txt'))
        fp = os.path.join(self.base_dir, folder, f"{st}_{ts}{ext}")
        if st == 'keyboard':
            with open(fp, "w", encoding="utf-8") as f: f.write(c or "")
        elif st != 'video':
            with open(fp, "wb") as f: f.write(c or b"")
        return fp
    def translate_narratives(self):
        if not Translator: return "Error: Install googletrans==4.0.0-rc1"
        tr = Translator(); tf = os.path.join(self.base_dir, "Text")
        files = [f for f in os.listdir(tf) if f.endswith('.txt')]
        if not files: return "No files found."
        for f in files:
            p = os.path.join(tf, f)
            with open(p, "r", encoding="utf-8") as file: c = file.read()
            try:
                det = tr.detect(c).lang; tgt = 'fa' if det == 'en' else 'en'
                res = tr.translate(c, dest=tgt).text
                with open(p.replace(".txt", f"_trans_{tgt}.txt"), "w", encoding="utf-8") as file: file.write(res)
            except: continue
        return f"Translated {len(files)} files."

class DX_OS_GUI:
    def __init__(self, root):
        self.engine = DX_OS_Engine(); self.root = root
        self.root.title(f"DX-OS | {self.engine.owner}"); self.root.geometry("600x800"); self.root.configure(bg="#2C0000")
        self._setup_ui()
    def _setup_ui(self):
        self.logo_frame = tk.Frame(self.root, bg="#2C0000"); self.logo_frame.pack(pady=20)
        self.logo_label = tk.Label(self.logo_frame, bg="#2C0000"); self.logo_label.pack(); self.load_logo()
        tk.Button(self.logo_frame, text="🖼️ Change Logo", command=self.upload_logo, font=("Tahoma", 8), bg="#D4AF37", fg="#2C0000", cursor="hand2").pack(pady=5)
        h = tk.Frame(self.root, bg="#D4AF37", height=60); h.pack(fill="x")
        tk.Label(h, text="DX-OS OPERATING SYSTEM", font=("Arial", 18, "bold"), bg="#D4AF37", fg="#2C0000").pack(pady=15)
        m = tk.Frame(self.root, bg="#2C0000"); m.pack(expand=True, fill="both", padx=30, pady=20)
        btns = [("👁️ Live Preview", self.action_preview, "#E6E6FA"), ("📸 Capture Photo", self.action_camera, "#D4AF37"), ("🎙️ Record Audio", self.action_mic, "#D4AF37"), ("✍️ Write Narrative", self.action_text, "#D4AF37")]

        for text, cmd, clr in btns: tk.Button(m, text=text, command=cmd, width=30, font=("Tahoma", 12, "bold"), bg=clr, fg="#2C0000", cursor="hand2").pack(pady=10)
        tk.Frame(m, height=2, bg="#D4AF37").pack(fill="x", pady=20)
        tk.Button(m, text="🌐 Translate Narratives", command=self.action_translate, width=30, font=("Tahoma", 11, "bold"), bg="#C0C0C0", fg="#2C0000", cursor="hand2").pack(pady=5)
        tk.Button(m, text="⚙️ Camera Settings", command=self.open_settings, width=30, font=("Tahoma", 11, "bold"), bg="#F0E68C", fg="#2C0000", cursor="hand2").pack(pady=5)
        tk.Button(m, text="🔄 Sync with Android", command=lambda: messagebox.showinfo("Sync", "Syncing..."), width=30, font=("Tahoma", 12, "bold"), bg="#A52A2A", fg="white", cursor="hand2").pack(pady=10)
        self.status_var = tk.StringVar(value="System Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", bg="#1A0000", fg="#D4AF37").pack(side="bottom", fill="x")
    def load_logo(self):
        p = self.engine.get_logo_path()
        if p and os.path.exists(p):
            try:
                img = Image.open(p).convert("RGB"); img.thumbnail((120, 120)); ph = ImageTk.PhotoImage(img)
                self.logo_label.config(image=ph, text=""); self.logo_label.image = ph
            except: self.logo_label.config(text="[ IMAGE ERROR ]", fg="#D4AF37")
        else: self.logo_label.config(text="[ LOGO ]", fg="#D4AF37", font=("Arial", 12, "bold"))
    def upload_logo(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg .jpeg .png *.gif")])
        if p: self.engine.save_logo_path(p); self.load_logo(); messagebox.showinfo("Logo", "Logo updated!")
    def _get_url(self):
        ip = self.engine.get_ip(); return f"{ip}/video" if not ip.endswith("/video") else ip
    def action_translate(self):
        self.update_status("🌐 Translating..."); res = self.engine.translate_narratives()
        self.update_status("Complete!"); messagebox.showinfo("Translation", res)
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
    def action_mic(self):
        f = self.engine.save_data('mic'); self.update_status("Audio Saved!"); messagebox.showinfo("Success", f"Saved: {f}")
    def action_text(self):
        tw = tk.Toplevel(self.root); tw.title("Narrative Editor"); tw.geometry("450x400")
        tb = tk.Frame(tw, bg="#D4AF37", height=40); tb.pack(side="top", fill="x")
        txt = tk.Text(tw, font=("Tahoma", 12)); txt.pack(expand=True, fill="both", padx=10, pady=10)
        def save():
            c = txt.get("1.0", "end-1c")
            if c.strip():
                f = self.engine.save_data('keyboard', c); self.update_status("Note Saved!"); messagebox.showinfo("Success", f"Saved: {f}"); tw.destroy()
            else: messagebox.showwarning("Empty", "Please write something!")
        tk.Button(tb, text="💾 Save Note", command=save, bg="#D4AF37", fg="#2C0000", font=("Tahoma", 10, "bold"), cursor="hand2", relief="flat", padx=10).pack(side="right", padx=10, pady=5)
    def update_status(self, msg): self.status_var.set(msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = DX_OS_GUI(root)
    root.mainloop()