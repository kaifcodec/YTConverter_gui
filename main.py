import os
import yt_dlp
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from jnius import autoclass, cast

# Android file path & intent handling
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
File = autoclass('java.io.File')

DOWNLOAD_DIR = os.path.join(
    PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath(),
    "downloads"
)

class YTDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.selected_format = 'mp4'

        # URL input field
        self.url_input = TextInput(
            hint_text="Paste YouTube URL here",
            size_hint_y=None,
            height="40dp",
            multiline=False
        )
        self.add_widget(self.url_input)

        # Format selection (MP3/MP4)
        format_layout = GridLayout(cols=2, size_hint_y=None, height="40dp", spacing=5)
        self.mp4_btn = ToggleButton(text='MP4', group='format', state='down')
        self.mp3_btn = ToggleButton(text='MP3', group='format')
        self.mp4_btn.bind(on_press=lambda x: self.set_format('mp4'))
        self.mp3_btn.bind(on_press=lambda x: self.set_format('mp3'))
        format_layout.add_widget(self.mp4_btn)
        format_layout.add_widget(self.mp3_btn)
        self.add_widget(format_layout)

        # Button layout
        btn_layout = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
        self.download_button = Button(text="Download", background_color=(0.2, 0.6, 0.2, 1))
        self.download_button.bind(on_release=self.download_video)
        self.view_button = Button(text="View Downloads", background_color=(0.2, 0.2, 0.6, 1))
        self.view_button.bind(on_release=self.open_downloads)
        btn_layout.add_widget(self.download_button)
        btn_layout.add_widget(self.view_button)
        self.add_widget(btn_layout)

        # Log display
        self.log_label = Label(text="", size_hint_y=None, halign="left", valign="top")
        self.log_label.bind(texture_size=self.update_label_size)
        self.scrollview = ScrollView(size_hint=(1, 1))
        self.scrollview.add_widget(self.log_label)
        self.add_widget(self.scrollview)

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

    def update_label_size(self, instance, value):
        self.log_label.height = self.log_label.texture_size[1]
        self.log_label.text_size = (self.width - 20, None)

    def log(self, message):
        self.log_label.text += f"\n{message}"
        print(message)

    def set_format(self, fmt):
        self.selected_format = fmt
        self.log(f"[Format] Selected: {fmt}")

    def download_video(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.log("[Error] Please enter a valid URL.")
            return

        self.log(f"Starting download from: {url}")
        outtmpl = f'{DOWNLOAD_DIR}/%(title)s.%(ext)s'

        ydl_opts = {
            'outtmpl': outtmpl,
            'quiet': True,
            'progress_hooks': [self.hook]
        }

        if self.selected_format == 'mp4':
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4'
            })
        else:  # mp3
            ydl_opts.update({
                'format': 'bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.log(f"[Error] {str(e)}")

    def hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            self.log(f"Downloading... {percent}")
        elif d['status'] == 'finished':
            self.log("Download complete!")

    def open_downloads(self, instance):
        try:
            file = File(DOWNLOAD_DIR)
            uri = Uri.fromFile(file)
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "*/*")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivity(intent)
        except Exception as e:
            self.log(f"[Error] Could not open folder: {e}")

class YTApp(App):
    def build(self):
        return YTDownloader()

if __name__ == "__main__":
    YTApp().run()
