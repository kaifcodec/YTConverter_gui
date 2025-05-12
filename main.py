# ytconverter_gui.py

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import subprocess

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

    def download(self, format):
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "Status: Please enter a URL."
            return

        self.status.text = f"Status: Downloading {format}..."
        try:
            if format == 'mp3':
                cmd = [
                    'yt-dlp',
                    '-x', '--audio-format', 'mp3',
                    url
                ]
            else:
                cmd = [
                    'yt-dlp',
                    '-f', 'bestvideo+bestaudio',
                    url
                ]
            subprocess.run(cmd, check=True)
            self.status.text = f"Status: {format.upper()} Downloaded!"
        except subprocess.CalledProcessError:
            self.status.text = "Status: Error during download."

    def download_mp3(self, instance):
        self.download('mp3')

    def download_mp4(self, instance):
        self.download('mp4')

class YTConverterApp(App):
    def build(self):
        return YTDownloader()

if __name__ == '__main__':
    YTConverterApp().run()
