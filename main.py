import os
import subprocess
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from android.storage import primary_external_storage_path
from jnius import autoclass


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

        self.log_btn = Button(text="View Log")
        self.log_btn.bind(on_press=self.show_log)
        self.add_widget(self.log_btn)

        self.status = Label(text="Status: Idle")
        self.add_widget(self.status)

        self.app_dir = App.get_running_app().user_data_dir
        self.ffmpeg_path = os.path.join(self.app_dir, 'ffmpeg')
        self.ytdlp_path = os.path.join(self.app_dir, 'yt-dlp')
        self.log_path = os.path.join(self.app_dir, 'ytconverter_debug.log')

        self.setup_binaries()

    def extract_asset(self, asset_name, dest_path):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            asset_manager = PythonActivity.mActivity.getAssets()
            input_stream = asset_manager.open(f'bin/{asset_name}')
            with open(dest_path, 'wb') as out_file:
                buf = bytearray(4096)
                while True:
                    length = input_stream.read(buf)
                    if length == -1 or length == 0:
                        break
                    out_file.write(buf[:length])
            os.chmod(dest_path, 0o755)
            return True
        except Exception as e:
            self.log_error(f"Failed to extract asset: {asset_name}", e)
            return False

    def setup_binaries(self):
        try:
            ffmpeg_ok = True
            ytdlp_ok = True

            if not os.path.exists(self.ffmpeg_path):
                ffmpeg_ok = self.extract_asset('ffmpeg', self.ffmpeg_path)

            if not os.path.exists(self.ytdlp_path):
                ytdlp_ok = self.extract_asset('yt-dlp', self.ytdlp_path)

            if ffmpeg_ok and ytdlp_ok:
                self.status.text = "Status: Binaries setup OK"
            else:
                self.status.text = "Status: Binaries setup failed"
        except Exception as e:
            self.status.text = "Status: Exception during setup"
            self.log_error("setup_binaries", e)

    def get_download_path(self):
        return os.path.join(primary_external_storage_path(), 'Download')

    def log_error(self, context, exc):
        try:
            with open(self.log_path, 'a') as log_file:
                log_file.write(f"\n--- {context} ---\n")
                log_file.write(traceback.format_exc())
                log_file.write("\n")
        except Exception as log_exc:
            print(f"Logging failed: {log_exc}")
        print(f"[ERROR] {context}: {exc}")

    def run_command(self, cmd):
        try:
            subprocess.run(cmd, check=True)
            return True
        except FileNotFoundError as e:
            self.log_error("Command not found", e)
            return False
        except subprocess.CalledProcessError as e:
            self.log_error("Command failed", e)
            return False
        except Exception as e:
            self.log_error("Unexpected error", e)
            return False

    def download(self, format):
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "Status: Please enter a URL."
            return

        self.status.text = f"Status: Downloading {format.upper()}..."
        output_path = os.path.join(self.get_download_path(), '%(title)s.%(ext)s')

        base_cmd = ['yt-dlp', '--ffmpeg-location', self.ffmpeg_path, '-o', output_path]
        if format == 'mp3':
            base_cmd += ['-x', '--audio-format', 'mp3']
        else:
            base_cmd += ['-f', 'bestvideo+bestaudio', '--merge-output-format', 'mp4']
        base_cmd.append(url)

        if not self.run_command(base_cmd):
            fallback_cmd = [self.ytdlp_path, '--ffmpeg-location', self.ffmpeg_path, '-o', output_path]
            if format == 'mp3':
                fallback_cmd += ['-x', '--audio-format', 'mp3']
            else:
                fallback_cmd += ['-f', 'bestvideo+bestaudio', '--merge-output-format', 'mp4']
            fallback_cmd.append(url)

            if not self.run_command(fallback_cmd):
                self.status.text = f"Status: Failed to download {format.upper()}!"
                return

        self.status.text = f"Status: {format.upper()} downloaded to Downloads!"

    def download_mp3(self, instance):
        self.download('mp3')

    def download_mp4(self, instance):
        self.download('mp4')

    def show_log(self, instance):
        try:
            with open(self.log_path, 'r') as f:
                log_content = f.read()
        except FileNotFoundError:
            log_content = "No logs found."

        log_box = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        log_text = TextInput(text=log_content, readonly=True, size_hint_y=None)
        log_text.height = max(600, len(log_content.splitlines()) * 20)
        scroll.add_widget(log_text)

        close_btn = Button(text="Close", size_hint_y=None, height=50)
        popup = Popup(title='YTConverter Logs', content=log_box, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)

        log_box.add_widget(scroll)
        log_box.add_widget(close_btn)
        popup.open()


class YTConverterApp(App):
    def build(self):
        return YTDownloader()


if __name__ == '__main__':
    YTConverterApp().run()
