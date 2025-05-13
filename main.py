import os
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from jnius import autoclass

# Paths
activity = autoclass('org.kivy.android.PythonActivity').mActivity
LIB_DIR = activity.getApplicationInfo().nativeLibraryDir
DOWNLOAD_DIR = os.path.join(activity.getExternalFilesDir(None).getAbsolutePath(), "downloads")

BINARIES = {
    "yt-dlp": os.path.join(LIB_DIR, "libyt-dlp.so"),
    "ffmpeg": os.path.join(LIB_DIR, "libffmpeg.so"),
}

class YTDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        # Input URL
        self.url_input = TextInput(hint_text="Enter YouTube URL here", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.url_input)

        # Format selection
        self.format_spinner = Spinner(
            text='Select Format',
            values=('MP4 (Video)', 'MP3 (Audio)'),
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.format_spinner)

        # Download Button
        self.download_button = Button(text="Download", size_hint_y=None, height=50, on_press=self.download_video)
        self.add_widget(self.download_button)

        # View Logs Button
        self.view_logs_btn = Button(text="View Logs", size_hint_y=None, height=40, on_press=self.show_logs_popup)
        self.add_widget(self.view_logs_btn)

        # Log Box (hidden, but stores logs)
        self.log_text = ""
        self.log_popup = None

        self.ensure_setup()

    def log(self, message):
        self.log_text += f"{message}\n"
        print(message)  # Also prints to Android Logcat

    def show_logs_popup(self, instance):
        content = BoxLayout(orientation='vertical')
        log_label = Label(text=self.log_text, size_hint_y=None, halign='left', valign='top')
        log_label.bind(texture_size=log_label.setter('size'))

        scroll = ScrollView()
        scroll.add_widget(log_label)
        content.add_widget(scroll)

        close_btn = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        self.log_popup = Popup(title="Logs", content=content, size_hint=(0.95, 0.8))
        close_btn.bind(on_press=self.log_popup.dismiss)
        self.log_popup.open()

    def ensure_setup(self):
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
            self.log(f"Created download directory: {DOWNLOAD_DIR}")
        for name, path in BINARIES.items():
            try:
                os.chmod(path, 0o755)
                self.log(f"{name} executable permission set: {path}")
            except Exception as e:
                self.log(f"Error setting permission for {name}: {e}")

    def download_video(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.log("Error: URL is empty.")
            return

        format_choice = self.format_spinner.text
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        args = [
            BINARIES["yt-dlp"],
            "--ffmpeg-location", BINARIES["ffmpeg"],
            "-o", output_template
        ]

        if format_choice.startswith("MP4"):
            args += ["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"]
        elif format_choice.startswith("MP3"):
            args += ["-x", "--audio-format", "mp3"]
        else:
            self.log("Please select a format before downloading.")
            return

        args.append(url)
        self.log(f"Starting download...\nURL: {url}\nFormat: {format_choice}\nOutput: {output_template}")

        try:
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log(result.stdout)
        except Exception as e:
            self.log(f"[Error] Download failed: {e}")

class YTApp(App):
    def build(self):
        return YTDownloader()

if __name__ == '__main__':
    YTApp().run()
