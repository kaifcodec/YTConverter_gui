import os
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')

# Path setup
LIB_DIR = "/data/data/org.kivy.ytconverter/lib/"
DOWNLOAD_DIR = os.path.join(PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath(), "downloads")

BINARIES = {
    "yt-dlp": os.path.join(LIB_DIR, "libyt-dlp.so"),
    "ffmpeg": os.path.join(LIB_DIR, "libffmpeg.so"),
}

class LogBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.label = Label(text="", size_hint_y=None, halign="left", valign="top")
        self.label.bind(texture_size=self.label.setter("size"))
        scroll = ScrollView()
        scroll.add_widget(self.label)
        self.add_widget(scroll)

    def log(self, message):
        self.label.text += f"\n{message}"
        print(message)

class YTApp(App):
    def build(self):
        self.logbox = LogBox()
        self.setup()
        return self.logbox

    def log(self, msg):
        self.logbox.log(msg)

    def setup(self):
        self.log("Initializing YTConverter with native libs...")
        self.ensure_download_dir()
        self.ensure_permissions()
        self.download_sample_video()

    def ensure_download_dir(self):
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            self.log(f"Created download directory: {DOWNLOAD_DIR}")
        else:
            self.log(f"Download directory exists: {DOWNLOAD_DIR}")

    def ensure_permissions(self):
        for name, path in BINARIES.items():
            try:
                os.chmod(path, 0o755)
                self.log(f"{name} permission set to 755 at {path}")
            except Exception as e:
                self.log(f"[Error] Failed to chmod {name}: {e}")

    def download_sample_video(self):
        ytdlp_path = BINARIES["yt-dlp"]
        ffmpeg_path = BINARIES["ffmpeg"]
        url = "https://www.youtube.com/watch?v=BaW_jenozKc"

        self.log(f"Using yt-dlp: {ytdlp_path}")
        self.log(f"Using ffmpeg: {ffmpeg_path}")
        self.log(f"Output directory: {DOWNLOAD_DIR}")

        try:
            result = subprocess.run([
                ytdlp_path,
                "--ffmpeg-location", ffmpeg_path,
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
                url
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log("yt-dlp output:")
            self.log(result.stdout)
        except FileNotFoundError as fnf:
            self.log(f"[Error] Command not found: {fnf}")
        except Exception as e:
            self.log(f"[Error] Failed to run yt-dlp: {e}")

if __name__ == '__main__':
    YTApp().run()

