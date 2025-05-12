import os
import shutil
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from jnius import autoclass, cast

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
AssetManager = autoclass('android.content.res.AssetManager')

# Path setup
CACHE_DIR = PythonActivity.mActivity.getCacheDir().getAbsolutePath()
BIN_DIR = os.path.join(CACHE_DIR, "ytconverter_bin")
DOWNLOAD_DIR = os.path.join(PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath(), "downloads")

# Assets
BINARIES = ["ffmpeg", "yt-dlp"]

# Log handling
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
        self.log("Initializing YTConverter...")
        self.ensure_download_dir()
        self.copy_binaries_if_missing()
        self.download_sample_video()

    def ensure_download_dir(self):
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            self.log(f"Created download directory: {DOWNLOAD_DIR}")
        else:
            self.log(f"Download directory exists: {DOWNLOAD_DIR}")

    def extract_asset(self, asset_name, output_path):
        try:
            asset_manager = PythonActivity.mActivity.getAssets()
            input_stream = asset_manager.open(f"bin/{asset_name}")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                buffer = bytearray(1024)
                while True:
                    read = input_stream.read(buffer)
                    if read == -1:
                        break
                    f.write(buffer[:read])
            input_stream.close()
            os.chmod(output_path, 0o755)
            self.log(f"Copied asset '{asset_name}' to '{output_path}' with chmod 755")
        except Exception as e:
            self.log(f"Failed to extract asset '{asset_name}': {e}")

    def copy_binaries_if_missing(self):
        for binary in BINARIES:
            full_path = os.path.join(BIN_DIR, binary)
            if not os.path.exists(full_path):
                self.log(f"{binary} missing, copying from assets...")
                self.extract_asset(binary, full_path)
            else:
                self.log(f"{binary} exists at: {full_path}")
                os.chmod(full_path, 0o755)  # Ensure executable every time
                self.log(f"{binary} permission updated (755)")

    def download_sample_video(self):
        url = "https://www.youtube.com/watch?v=BaW_jenozKc"  # Sample video for test
        ytdlp_path = os.path.join(BIN_DIR, "yt-dlp")
        ffmpeg_path = os.path.join(BIN_DIR, "ffmpeg")

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
