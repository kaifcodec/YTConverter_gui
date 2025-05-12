import os
import shutil
import subprocess
import traceback

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from android.storage import primary_external_storage_path
from android import mActivity

class YTDownloader(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.add_widget(Label(text="Enter YouTube URL:"))
        self.url_input = TextInput(multiline=False)
        self.add_widget(self.url_input)

        self.mp3_btn = Button(text="Download as MP3")
        self.mp3_btn.bind(on_press=self.download_mp3)
        self.add_widget(self.mp3_btn)

        self.mp4_btn = Button(text="Download as MP4")
        self.mp4_btn.bind(on_press=self.download_mp4)
        self.add_widget(self.mp4_btn)

        self.status = Label(text="Status: Idle")
        self.add_widget(self.status)

        self.app_dir = App.get_running_app().user_data_dir
        self.ffmpeg_dest = os.path.join(self.app_dir, 'ffmpeg')
        self.log_path = os.path.join(self.app_dir, 'error.log')

        self.prepare_ffmpeg()

    def prepare_ffmpeg(self):
        try:
            if not os.path.exists(self.ffmpeg_dest):
                # Extract the ffmpeg binary from the assets folder
                AssetManager = mActivity.getAssets()
                with AssetManager.open("bin/ffmpeg") as input_stream, open(self.ffmpeg_dest, 'wb') as out_file:
                    while True:
                        buff = input_stream.read(1024)
                        if not buff:
                            break
                        out_file.write(buff)
                os.chmod(self.ffmpeg_dest, 0o755)
        except Exception as e:
            self.log_error("Failed to setup ffmpeg", e)
            self.status.text = "Status: Failed to setup ffmpeg"

    def get_download_path(self):
        return os.path.join(primary_external_storage_path(), 'Download')

    def log_error(self, context, exc):
        with open(self.log_path, 'a') as log_file:
            log_file.write(f"--- {context} ---\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n")
        print(f"[ERROR] {context}: {exc}")

    def download(self, format):
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "Status: Please enter a URL."
            return

        self.status.text = f"Status: Downloading {format.upper()}..."

        output_path = os.path.join(self.get_download_path(), '%(title)s.%(ext)s')

        cmd = [
            'yt-dlp',
            '--ffmpeg-location', self.ffmpeg_dest,
            '-o', output_path
        ]

        if format == 'mp3':
            cmd += ['-x', '--audio-format', 'mp3']
        else:
            cmd += ['-f', 'bestvideo+bestaudio', '--merge-output-format', 'mp4']

        cmd.append(url)

        try:
            subprocess.run(cmd, check=True)
            self.status.text = f"Status: {format.upper()} downloaded to Download folder!"
        except subprocess.CalledProcessError as e:
            self.status.text = "Status: Download failed!"
            self.log_error("Download failed", e)
        except Exception as e:
            self.status.text = "Status: Unexpected error!"
            self.log_error("Unexpected crash", e)

    def download_mp3(self, instance):
        self.download('mp3')

    def download_mp4(self, instance):
        self.download('mp4')


class YTConverterApp(App):
    def build(self):
        return YTDownloader()


if __name__ == '__main__':
    YTConverterApp().run()
