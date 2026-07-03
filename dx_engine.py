# dx_engine.py
# -- coding: utf-8 -*-
import os, datetime, cv2, shutil
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

class DX_OS_Engine:
    def __init__(self):
        self.owner = "Sayed Hossain Ahmadi"
        self.base_dir = "DX_OS_Data"
        self.config_f = os.path.join(self.base_dir, "config.txt")
        self.logo_f = os.path.join(self.base_dir, "logo_path.txt")

        # تمام پوشه‌های مورد نیاز سیستم
        self.folders = [
            "Images", "Audio", "Text", "Backups", 
            "Sync_Pool", "Videos", "General_Narratives"
        ] 
        self._init_sys()
        self.keywords = ['غذا', 'خوراکی', 'قومیت', 'نقش', 'ملیت', 'ویژگی', 'زبان', 'فرهنگ']

    def _init_sys(self):
        """ایجاد ساختار پوشه‌بندی در ابتدای اجرا"""
        if not os.path.exists(self.base_dir): 
            os.makedirs(self.base_dir)
        for f in self.folders: 
            p = os.path.join(self.base_dir, f)
            if not os.path.exists(p): 
                os.makedirs(p)
        if not os.path.exists(self.config_f): 
            self.save_ip("http://10.180.243.185:8080")

    # --- تنظیمات شبکه و لوگو ---
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

    # --- مدیریت داده‌ها و ذخیره‌سازی ---
    def save_data(self, st, c=None):
        """ذخیره داده‌های خام (عکس، صدا، متن، ویدیو)"""
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        exts = {
            'camera': ('Images', '.jpg'), 
            'mic': ('Audio', '.wav'), 
            'video': ('Videos', '.avi'), 
            'keyboard': ('Text', '.txt')
        }
        folder, ext = exts.get(st, ('Text', '.txt'))
        fp = os.path.join(self.base_dir, folder, f"{st}_{ts}{ext}")

        if st == 'keyboard':
            with open(fp, "w", encoding="utf-8") as f: f.write(c or "")
        elif st != 'video':
            with open(fp, "wb") as f: f.write(c or b"")
        return fp

    def upload_manual_file(self, src, category):
        """آپلود دستی فایل‌ها به پوشه‌های مربوطه"""
        try:
            dest_folder = os.path.join(self.base_dir, category)
            fn = os.path.basename(src)
            dst = os.path.join(dest_folder, fn)
            shutil.copy(src, dst)
            return dst
        except Exception as e: return f"Error: {str(e)}"

    # --- مدیریت روایت‌های عمومی (General Narratives) ---
    def save_general_narrative(self, category, text):
        """ذخیره روایت‌های عمومی برای یک قومیت یا گروه"""

        path = os.path.join(self.base_dir, "General_Narratives", f"{category}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def get_general_narratives_list(self):
        """گرفتن لیست تمام روایت‌های عمومی تعریف شده"""
        path = os.path.join(self.base_dir, "General_Narratives")
        return [f.replace(".txt", "") for f in os.listdir(path) if f.endswith(".txt")]

    # --- سیستم هوشمند تبدیل صدا به متن (STT) ---
    def transcribe_audio(self, audio_path):
        """تبدیل فایل صوتی .wav به متن فارسی"""
        if sr is None:
            return "Error: کتابخانه SpeechRecognition نصب نیست. لطفاً pip install SpeechRecognition را اجرا کنید."
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                # استفاده از موتور گوگل برای زبان فارسی
                text = recognizer.recognize_google(audio_data, language="fa-IR")
                return text
        except sr.UnknownValueError:
            return "Error: صدای واضحی برای تبدیل به متن شناسایی نشد."
        except sr.RequestError as e:
            return f"Error: مشکل در اتصال به سرور گوگل: {e}"
        except Exception as e:
            return f"Error: {str(e)}"

    # --- سینک سلسله‌مراتبی (Hierarchical Sync) ---
    def sync_narratives_with_images(self):
        """تطبیق هوشمند عکس‌ها با روایت‌های اختصاصی یا عمومی"""
        results = []
        img_dir = os.path.join(self.base_dir, "Images")
        txt_dir = os.path.join(self.base_dir, "Text")
        gen_dir = os.path.join(self.base_dir, "General_Narratives")

        if not os.path.exists(img_dir): return None
        imgs = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

        for img in imgs:
            base_name = os.path.splitext(img)[0]
            specific_txt = f"{base_name}.txt"
            specific_path = os.path.join(txt_dir, specific_txt)

            # اولویت ۱: روایت اختصاصی (فایل متنی با نام دقیق عکس)
            if os.path.exists(specific_path):
                with open(specific_path, "r", encoding="utf-8") as f:
                    results.append(f"📸 Image: {img}\n📌 Type: SPECIFIC\n📝 Content: {f.read()}\n{'-'*30}")
            else:
                # اولویت ۲: روایت عمومی (بر اساس تگ نام فایل، مثلا Gilak_01 -> Gilak)
                tag = base_name.split('_')[0] 
                gen_path = os.path.join(gen_dir, f"{tag}.txt")
                if os.path.exists(gen_path):
                    with open(gen_path, "r", encoding="utf-8") as f:
                        results.append(f"📸 Image: {img}\n📌 Type: GENERAL ({tag})\n📝 Content: {f.read()}\n{'-'*30}")
                else:
                    # اولویت ۳: هیچ روایتی یافت نشد
                    results.append(f"📸 Image: {img}\n📌 Type: NONE\n📝 Content: No narrative found.\n{'-'*30}")

        return results if results else None

    # --- ترجمه و گزارش‌گیری ---
    def get_filtered_translations(self):
        """فیلتر کردن بر اساس کلمات کلیدی و ترجمه به انگلیسی/فارسی"""
        if Translator is None: return "Error: Install googletrans==4.0.0-rc1"
        tr = Translator()
        tf = os.path.join(self.base_dir, "Text")
        if not os.path.exists(tf): return None

        files = [f for f in os.listdir(tf) if f.endswith('.txt')]
        results = []
        for f in files:
            p = os.path.join(tf, f)
            with open(p, "r", encoding="utf-8") as file: 
                c = file.read()

                if any(key in c for key in self.keywords):
                    try:
                        det = tr.detect(c).lang
                        tgt = 'fa' if det == 'en' else 'en'
                        res = tr.translate(c, dest=tgt).text
                        results.append(f"File: {f}\nOriginal: {c}\nTranslated: {res}\n{'-'*40}")
                    except: continue
        return results if results else None

    def export_to_pdf(self, content_list):
        """خروجی گرفتن از نتایج به صورت فایل PDF"""
        if canvas is None: return "Error: reportlab not installed"
        try:
            fn = f"DX_OS_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            c = canvas.Canvas(fn)
            y = 800
            c.setFont("Helvetica", 10)
            for item in content_list:
                for line in item.split('\n'):
                    c.drawString(50, y, line[:90])
                    y -= 15
                y -= 10
                if y < 50: 
                    c.showPage()
                    y = 800
            c.save()
            return fn
        except Exception as e: return f"PDF Error: {str(e)}"