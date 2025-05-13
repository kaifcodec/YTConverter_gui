import os
import threading
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from jnius import autoclass

# Android paths
PythonActivity = autoclass('org.kivy.android.PythonActivity')
DOWNLOAD_DIR = os.path.join(
    PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath(), "downloads"
)

class LogBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.label = Label(text="", size_hint_y=None, halign="left", valign="top")
        self.label.bind(texture_size=self.label.setter("size"))
        self.label.text_size = (Window.width * 0.95, None)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.label)
        self.add_widget(scroll)

    def log(self, msg):
        self.label.text += f"\n{msg}"
        print(msg)

class YTDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)

        self.url_input = TextInput(
            hint_text="Paste YouTube URL here", multiline=False, size_hint_y=None, height="40dp"
        )
        self.add_widget(self.url_input)

        self.download_btn = Button(
            text="Download MP4", size_hint_y=None, height="40dp", on_press=self.download
        )
        self.add_widget(self.download_btn)

        self.logs = LogBox(size_hint=(1, 1))
        self.add_widget(self.logs)

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            self.logs.log(f"Created download folder:\n{DOWNLOAD_DIR}")
        else:
            self.logs.log(f"Using download folder:\n{DOWNLOAD_DIR}")

    def download(self, _):
        url = self.url_input.text.strip()
        if not url:
            self.logs.log("[Error] URL field is empty.")
            return

        self.download_btn.disabled = True
        threading.Thread(target=self.run_yt_dlp, args=(url,), daemon=True).start()

    def run_yt_dlp(self, url):
        output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "-o", output_path,
            url
        ]
        self.logs.log(f"Running yt-dlp...\n{url}")

        try:
            process = subprocess.run(cmd, capture_output=True, text=True)
            self.logs.log(process.stdout)
            if process.stderr:
                self.logs.log("[stderr]")
                self.logs.log(process.stderr)
        except Exception as e:
            self.logs.log(f"[Error] {e}")
        finally:
            self.download_btn.disabled = False

class YTApp(App):
    def build(self):
        return YTDownloader()

if __name__ == "__main__":
    YTApp().run()
