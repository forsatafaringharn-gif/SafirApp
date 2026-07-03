# -- coding: utf-8 -*-
import os, datetime, cv2, shutil, json
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from googletrans import Translator
except ImportError:
    Translator = None

try:
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

# --- V8 Multi-Modal Support ---
try:
    import PyPDF2
    from docx import Document
except ImportError:
    PyPDF2 = None
    Document = None

# =============================================================================
# DX-OS GLOBAL IDENTITY (SRS Section 2.3 & 5)
# =============================================================================
PROJECT_NAME = "DX-OS"
VERSION = "1.1 (V8-Stable)"
RELEASE_DATE = "1405/03/23"
OWNER = "Seyed Hossein Ahmadi"
CONTACT_MOBILE = "09191182313"
CONTACT_EMAIL = "neumedal@gmail.com"

class DX_OS_Engine:
    def __init__(self):
        self.owner = OWNER
        self.base_dir = "DX_OS_Data"
        self.config_f = os.path.join(self.base_dir, "config.txt")
        self.logo_f = os.path.join(self.base_dir, "logo_path.txt")
        self.user_info_f = os.path.join(self.base_dir, "user_info.json")

        self.folders = [
            "Images", "Audio", "Text", "Backups", 
            "Sync_Pool", "Videos", "General_Narratives"
        ] 
        self._init_sys()
        self.keywords = ['غذا', 'خوراکی', 'قومیت', 'نقش', 'ملیت', 'ویژگی', 'زبان', 'فرهنگ']

    def _init_sys(self):
        if not os.path.exists(self.base_dir): os.makedirs(self.base_dir)
        for f in self.folders: 
            p = os.path.join(self.base_dir, f)
            if not os.path.exists(p): os.makedirs(p)
        if not os.path.exists(self.config_f): self.save_ip("http://10.180.243.185:8080")

    # --- تنظیمات سیستم ---
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

    def save_user_identity(self, email, mobile):
        data = {"email": email, "mobile": mobile}
        with open(self.user_info_f, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True

    def get_user_identity(self):
        if os.path.exists(self.user_info_f):
            with open(self.user_info_f, "r", encoding="utf-8") as f: return json.load(f)
        return None

    # --- مدیریت داده‌ها ---
    def save_data(self, st, c=None):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        exts = {'camera': ('Images', '.jpg'), 'mic': ('Audio', '.wav'), 'video': ('Videos', '.avi'), 'keyboard': ('Text', '.txt')}

        folder, ext = exts.get(st, ('Text', '.txt'))
        fp = os.path.join(self.base_dir, folder, f"{st}_{ts}{ext}")
        if st == 'keyboard':
            with open(fp, "w", encoding="utf-8") as f: f.write(c or "")
        elif st != 'video':
            with open(fp, "wb") as f: f.write(c or b"")
        return fp

    def upload_manual_file(self, src, category):
        try:
            dst = os.path.join(self.base_dir, category, os.path.basename(src))
            shutil.copy(src, dst); return dst
        except Exception as e: return f"Error: {str(e)}"

    def read_advanced_text(self, file_path):
        """خواندن PDF, Word, TXT (SRS 1.3)"""
        text_content = ""
        try:
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f: text_content = f.read()
            elif file_path.endswith('.pdf') and PyPDF2:
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    for page in pdf.pages: text_content += page.extract_text()
            elif file_path.endswith('.docx') and Document:
                doc = Document(file_path)
                text_content = "\n".join([para.text for para in doc.paragraphs])
            else: return "Error: Unsupported format or library missing."
            return text_content
        except Exception as e: return f"Error: {str(e)}"

    def create_smart_backup(self):
        """بک‌آپ هوشمند (SRS 3.1)"""
        try:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = os.path.join(self.base_dir, "Backups", f"backup_{ts}")
            os.makedirs(dst)
            for item in os.listdir(self.base_dir):
                if item != "Backups":
                    s, d = os.path.join(self.base_dir, item), os.path.join(dst, item)
                    shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)
            return f"Backup successful: {dst}"
        except Exception as e: return f"Backup failed: {str(e)}"

    # --- پردازش و هوش مصنوعی ---
    def transcribe_audio(self, audio_path):
        if sr is None: return "Error: SpeechRecognition not installed."
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
                return r.recognize_google(audio, language="fa-IR")
        except Exception as e: return f"Error: {str(e)}"

    def sync_narratives_with_images(self):
        results = []
        img_dir = os.path.join(self.base_dir, "Images")
        if not os.path.exists(img_dir): return None
        for img in [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png'))]:
            base = os.path.splitext(img)[0]
            spec_p = os.path.join(self.base_dir, "Text", f"{base}.txt")
            gen_p = os.path.join(self.base_dir, "General_Narratives", f"{base.split('_')[0]}.txt")

            if os.path.exists(spec_p):
                with open(spec_p, "r", encoding="utf-8") as f: type, cont = "SPECIFIC", f.read()
            elif os.path.exists(gen_p):
                with open(gen_p, "r", encoding="utf-8") as f: type, cont = "GENERAL", f.read()
            else: type, cont = "NONE", "No narrative found."
            results.append(f"📸 {img}\n📌 {type}\n📝 {cont}\n{'-'*30}")
        return results

    def save_general_narrative(self, cat, text):
        p = os.path.join(self.base_dir, "General_Narratives", f"{cat}.txt")
        with open(p, "w", encoding="utf-8") as f: f.write(text)

    def get_general_narratives_list(self):
        p = os.path.join(self.base_dir, "General_Narratives")
        return [f.replace(".txt", "") for f in os.listdir(p) if f.endswith(".txt")]

    def get_filtered_translations(self):
        if Translator is None: return "Error: Install googletrans==4.0.0-rc1"
        tr, results = Translator(), []
        tf = os.path.join(self.base_dir, "Text")
        for f in [f for f in os.listdir(tf) if f.endswith('.txt')]:

            with open(os.path.join(tf, f), "r", encoding="utf-8") as file:
                c = file.read()
                if any(k in c for k in self.keywords):
                    try:
                        res = tr.translate(c, dest='en' if tr.detect(c).lang == 'fa' else 'fa').text
                        results.append(f"File: {f}\nOriginal: {c}\nTranslated: {res}\n{'-'*40}")
                    except: continue
        return results

    def export_to_pdf(self, content_list):
        if canvas is None: return "Error: reportlab not installed"
        fn = f"DX_OS_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(fn); y = 800
        for item in content_list:
            for line in item.split('\n'):
                c.drawString(50, y, line[:90]); y -= 15
                if y < 50: c.showPage(); y = 800
            y -= 10
        c.save(); return fn