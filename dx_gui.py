# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2, threading, datetime, os
from dx_engine import DX_OS_Engine, PROJECT_NAME, VERSION, OWNER, CONTACT_MOBILE, CONTACT_EMAIL

class DX_OS_GUI:
    def __init__(self, root):
        self.engine = DX_OS_Engine(); self.root = root
        self.root.title(f"{PROJECT_NAME} | {OWNER}"); self.root.geometry("700x850")
        self.root.configure(bg="#2C0000")
        self.color_bg, self.color_gold, self.color_light, self.color_accent = "#2C0000", "#D4AF37", "#FDF5E6", "#A52A2A"
        self._setup_main_layout()

    def _setup_main_layout(self):
        self.toolbar = tk.Frame(self.root, bg="#1A0000", height=40); self.toolbar.pack(side="top", fill="x")
        tool_btns = [("🛡️ Backup", self.action_backup), ("⚙️ IP Settings", self.open_settings), ("ℹ️ About", self.show_about_panel)]
        for text, cmd in tool_btns:
            tk.Button(self.toolbar, text=text, command=cmd, bg="#333", fg="white", font=("Tahoma", 9), relief="flat", padx=10, cursor="hand2").pack(side="left", padx=5, pady=5)

        self.header_frame = tk.Frame(self.root, bg=self.color_bg); self.header_frame.pack(pady=20)
        self.logo_label = tk.Label(self.header_frame, bg=self.color_bg); self.logo_label.pack(); self.load_logo()
        tk.Button(self.header_frame, text="Change Logo", command=self.upload_logo, font=("Tahoma", 8), bg=self.color_gold, fg=self.color_bg).pack(pady=5)

        self.main_container = tk.Frame(self.root, bg=self.color_bg); self.main_container.pack(expand=True, fill="both", padx=30)
        if not self.engine.get_user_identity(): self._show_identity_form()
        else: self._show_dashboard()

        self.status_var = tk.StringVar(value="System Ready")
        tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", bg="#1A0000", fg=self.color_gold).pack(side="bottom", fill="x")

    def _show_identity_form(self):
        self.clear_container()
        f = tk.Frame(self.main_container, bg=self.color_bg); f.pack(expand=True)
        tk.Label(f, text="Welcome to DX-OS\nPlease enter your identity:", fg=self.color_gold, bg=self.color_bg, font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(f, text="Email:", fg="white", bg=self.color_bg).pack()
        self.ent_email = tk.Entry(f, justify="center", font=("Tahoma", 12)); self.ent_email.pack(pady=5)
        tk.Label(f, text="Mobile:", fg="white", bg=self.color_bg).pack()
        self.ent_mob = tk.Entry(f, justify="center", font=("Tahoma", 12)); self.ent_mob.pack(pady=5)
        def save():
            if self.ent_email.get() and self.ent_mob.get():
                self.engine.save_user_identity(self.ent_email.get(), self.ent_mob.get())
                self._show_dashboard()
            else: messagebox.showwarning("Error", "Fill all fields!")
        tk.Button(f, text="Enter DX-OS", command=save, bg=self.color_gold, fg=self.color_bg, font=("Tahoma", 12, "bold"), width=20).pack(pady=30)

    def _show_dashboard(self):
        self.clear_container()
        core_f = tk.LabelFrame(self.main_container, text=" Core Action Center ", fg=self.color_gold, bg=self.color_bg, font=("Arial", 10, "bold")); core_f.pack(fill="x", pady=10)
        btns = [("👁️ Live Preview", self.action_preview, "#E6E6FA"), ("📸 Capture Photo", self.action_camera, self.color_gold), ("🎙️ Audio Record", self.action_mic, self.color_gold), ("✍️ Write Narrative", self.action_text, self.color_gold)]
        r, c = 0, 0
        for text, cmd, clr in btns:
            tk.Button(core_f, text=text, command=cmd, width=20, font=("Tahoma", 11, "bold"), bg=clr, fg=self.color_bg, cursor="hand2").grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c > 1: c=0; r+=1

        mgmt_f = tk.LabelFrame(self.main_container, text=" Intelligence & Sync ", fg=self.color_gold, bg=self.color_bg, font=("Arial", 10, "bold")); mgmt_f.pack(fill="x", pady=10)

        tk.Button(mgmt_f, text="⚙️ Sync Hierarchical Narratives", command=self.action_sync, width=40, bg="#C0C0C0", fg=self.color_bg, font=("Tahoma", 10, "bold")).pack(pady=5)
        tk.Button(mgmt_f, text="📚 Manage General Narratives", command=self.open_narratives_panel, width=40, bg="#ADD8E6", fg=self.color_bg, font=("Tahoma", 10, "bold")).pack(pady=5)
        tk.Button(mgmt_f, text="🌐 Translate & Export PDF", command=self.action_translate, width=40, bg="#C0C0C0", fg=self.color_bg, font=("Tahoma", 10, "bold")).pack(pady=5)

        up_f = tk.Frame(self.main_container, bg=self.color_bg); up_f.pack(pady=20)
        tk.Button(up_f, text="📤 Image", command=lambda: self.manual_upload("Images"), bg=self.color_gold, width=10).pack(side="left", padx=5)
        tk.Button(up_f, text="📤 Video", command=lambda: self.manual_upload("Videos"), bg=self.color_gold, width=10).pack(side="left", padx=5)
        tk.Button(up_f, text="📄 PDF/Word", command=self.action_advanced_text, bg="#BDB76B", width=12).pack(side="left", padx=5)
        tk.Button(self.main_container, text="🔄 Sync with Android", command=lambda: messagebox.showinfo("Sync", "Syncing..."), width=40, font=("Tahoma", 12, "bold"), bg=self.color_accent, fg="white").pack(pady=20)

    def clear_container(self):
        for w in self.main_container.winfo_children(): w.destroy()
    def update_status(self, txt): self.status_var.set(txt)
    def load_logo(self):
        p = self.engine.get_logo_path()
        if p and os.path.exists(p):
            try:
                img = Image.open(p).convert("RGB"); img.thumbnail((100, 100)); ph = ImageTk.PhotoImage(img)
                self.logo_label.config(image=ph, text=""); self.logo_label.image = ph
            except: self.logo_label.config(text="[ ERROR ]", fg=self.color_gold)
        else: self.logo_label.config(text="[ LOGO ]", fg=self.color_gold, font=("Arial", 12, "bold"))
    def upload_logo(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg .jpeg .png")])
        if p: self.engine.save_logo_path(p); self.load_logo(); messagebox.showinfo("Logo", "Updated!")
    def _get_url(self):
        ip = self.engine.get_ip(); return f"{ip}/video" if not ip.endswith("/video") else ip
    def action_advanced_text(self):
        f = filedialog.askopenfilename(filetypes=[("Docs", "*.pdf .docx .txt")])
        if f:
            content = self.engine.read_advanced_text(f)
            tw = tk.Toplevel(self.root); tw.title("File Content"); tw.geometry("500x500")
            tx = tk.Text(tw, font=("Tahoma", 10), padx=10, pady=10); tx.pack(expand=True, fill="both")
            tx.insert("1.0", content); tx.config(state="disabled")
    def action_backup(self):
        messagebox.showinfo("Backup", self.engine.create_smart_backup())
    def show_about_panel(self):
        messagebox.showinfo("Identity", f"{PROJECT_NAME} V{VERSION}\n{OWNER}\n{CONTACT_MOBILE}\n{CONTACT_EMAIL}")
    def open_settings(self):
        sw = tk.Toplevel(self.root); sw.title("IP Config"); sw.geometry("300x150")
        ent = tk.Entry(sw, justify="center"); ent.insert(0, self.engine.get_ip()); ent.pack(pady=20)
        tk.Button(sw, text="Save IP", command=lambda: [self.engine.save_ip(ent.get()), sw.destroy()]).pack()
    def manual_upload(self, cat):
        f = filedialog.askopenfilename()
        if f: messagebox.showinfo("Success", f"Uploaded: {self.engine.upload_manual_file(f, cat)}")
    def action_preview(self):
        pw = tk.Toplevel(self.root); pw.title("Live Stream"); pw.geometry("640x600")
        lbl = tk.Label(pw, text="Connecting...", bg="black", fg="white"); lbl.pack(expand=True, fill="both")
        cap = cv2.VideoCapture(self._get_url())
        def update():
            if not pw.winfo_exists(): cap.release(); return
            ret, frame = cap.read()
            if ret:
                img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                lbl.config(image=img, text=""); lbl.image = img
            pw.after(10, update)
        update()
    def action_camera(self):

        try:
            cap = cv2.VideoCapture(self._get_url()); ret, frame = cap.read()
            if ret:
                f = self.engine.save_data('camera'); cv2.imwrite(f, frame)
                messagebox.showinfo("Success", f"Saved: {f}")
            cap.release()
        except Exception as e: messagebox.showerror("Error", str(e))
    def action_video(self):
        rw = tk.Toplevel(self.root); rw.title("Recording"); rw.geometry("300x150"); rw.configure(bg="#B22222")
        tk.Label(rw, text="🔴 RECORDING...", fg="white", bg="#B22222", font=("Arial", 14, "bold")).pack(expand=True)
        try:
            cap = cv2.VideoCapture(self._get_url()); f = self.engine.save_data('video')
            out = cv2.VideoWriter(f, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
            st = datetime.datetime.now()
            while (datetime.datetime.now() - st).seconds < 10:
                ret, frame = cap.read()
                if ret: out.write(frame)
                else: break
            cap.release(); out.release(); rw.destroy()
            messagebox.showinfo("Success", f"Video Saved: {f}")
        except Exception as e: messagebox.showerror("Error", str(e))
    def action_mic(self):
        f = filedialog.askopenfilename(filetypes=[("Audio", "*.wav")])
        if f:
            self.update_status("Transcribing...")
            text = self.engine.transcribe_audio(f)
            messagebox.showinfo("Transcription", text)
    def action_text(self):
        tw = tk.Toplevel(self.root); tw.title("Write Narrative"); tw.geometry("500x450"); tw.configure(bg=self.color_light)
        txt = tk.Text(tw, font=("Tahoma", 12), bg="white", fg=self.color_bg, padx=10, pady=10); txt.pack(expand=True, fill="both")
        def save():
            c = txt.get("1.0", "end-1c")
            if c.strip(): self.engine.save_data('keyboard', c); tw.destroy()
        tk.Button(tw, text="💾 Save", command=save, bg=self.color_gold).pack(pady=5)
    def action_sync(self):
        res = self.engine.sync_narratives_with_images()
        if res:
            sw = tk.Toplevel(self.root); sw.geometry("500x500"); t = tk.Text(sw); t.pack(expand=True, fill="both"); t.insert("1.0", "\n".join(res))
    def action_translate(self):
        res = self.engine.get_filtered_translations()
        if res:
            tw = tk.Toplevel(self.root); t = tk.Text(tw); t.pack(expand=True, fill="both"); t.insert("1.0", "\n".join(res))
            tk.Button(tw, text="📄 Export PDF", command=lambda: messagebox.showinfo("PDF", self.engine.export_to_pdf(res))).pack()
    def open_narratives_panel(self):
        messagebox.showinfo("Info", "General Narratives Module Active")

if __name__ == "__main__":
    root = tk.Tk(); app = DX_OS_GUI(root); root.mainloop()