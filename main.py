import os
import subprocess
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, Rectangle

# Conditional import for jnius, only on Android
if platform == 'android':
    from jnius import autoclass
    # Paths for Android
    activity = autoclass('org.kivy.android.PythonActivity').mActivity
    APP_ROOT = activity.getFilesDir().getAbsolutePath()
    LIB_DIR = activity.getApplicationInfo().nativeLibraryDir
    # Attempt to get external downloads dir, fallback to internal if not available/writable
    try:
        ext_storage = activity.getExternalFilesDir(None)
        if ext_storage:
            DOWNLOAD_DIR = os.path.join(ext_storage.getAbsolutePath(), "YTDownloader")
        else:
            DOWNLOAD_DIR = os.path.join(APP_ROOT, "YTDownloader")
    except Exception: # Fallback if getExternalFilesDir is problematic
        DOWNLOAD_DIR = os.path.join(APP_ROOT, "YTDownloader")

else: # For desktop testing
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    LIB_DIR = os.path.join(APP_ROOT, "bin") # Create a 'bin' folder in your project for desktop testing
    DOWNLOAD_DIR = os.path.join(APP_ROOT, "downloads")
    # Ensure dummy binary paths exist for desktop testing if you want to test the logic
    # You'd need to place yt-dlp and ffmpeg executables (e.g. .exe on windows) in the 'bin' folder.
    if not os.path.exists(LIB_DIR):
        os.makedirs(LIB_DIR)
        print(f"Desktop: Created dummy binary directory: {LIB_DIR}")
    # Example: Create dummy files if they don't exist for desktop testing
    # open(os.path.join(LIB_DIR, "yt-dlp"), 'a').close()
    # open(os.path.join(LIB_DIR, "ffmpeg"), 'a').close()


# Define binary names based on platform (e.g., .exe for windows if testing there)
YT_DLP_BIN = "libyt-dlp.so" if platform == 'android' else "yt-dlp" # or "yt-dlp.exe"
FFMPEG_BIN = "libffmpeg.so" if platform == 'android' else "ffmpeg" # or "ffmpeg.exe"

BINARIES = {
    "yt-dlp": os.path.join(LIB_DIR, YT_DLP_BIN),
    "ffmpeg": os.path.join(LIB_DIR, FFMPEG_BIN),
}

class YTDownloaderLayout(BoxLayout):
    """
    Main layout for the YouTube Downloader application.
    Handles UI elements, download logic, and logging.
    """
    status_message = StringProperty("Ready. Enter a URL to begin.")
    download_in_progress = BooleanProperty(False)
    log_text = StringProperty("") # Stores all log messages

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=[20, 20, 20, 20], spacing=15, **kwargs)

        # App Title
        title_label = Label(
            text="YT Downloader Deluxe",
            font_size='28sp',  # Larger font size
            bold=True,
            size_hint_y=None,
            height=50,
            color=(0.2, 0.6, 0.86, 1) # A nice blue
        )
        self.add_widget(title_label)

        # Input Section
        input_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=120)
        self.url_input = TextInput(
            hint_text="Enter YouTube URL here",
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size='16sp',
            padding=[10, 10, 10, 10],
            background_color=(0.95, 0.95, 0.95, 1), # Light grey background
            foreground_color=(0,0,0,1)
        )
        input_layout.add_widget(self.url_input)

        self.format_spinner = Spinner(
            text='MP4 (Video)', # Default to MP4
            values=('MP4 (Video)', 'MP3 (Audio)'),
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=(0.2, 0.6, 0.86, 1), # Blue background for spinner
            color=(1,1,1,1) # White text
        )
        input_layout.add_widget(self.format_spinner)
        self.add_widget(input_layout)

        # Download Button
        self.download_button = Button(
            text="Download",
            size_hint_y=None,
            height=60,
            font_size='18sp',
            bold=True,
            background_color=(0.1, 0.75, 0.3, 1), # Green color
            color=(1,1,1,1) # White text
        )
        self.download_button.bind(on_press=self.initiate_download)
        self.add_widget(self.download_button)

        # Status Label
        self.status_label = Label(
            text=self.status_message,
            size_hint_y=None,
            height=40,
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1) # Grey text
        )
        self.bind(status_message=self.status_label.setter('text'))
        self.add_widget(self.status_label)
        
        # Spacer to push logs button to bottom
        self.add_widget(BoxLayout(size_hint_y=1)) 

        # View Logs Button
        self.view_logs_btn = Button(
            text="View Logs",
            size_hint_y=None,
            height=50,
            font_size='16sp',
            background_color=(0.8, 0.8, 0.8, 1), # Light grey
            color=(0,0,0,1) # Black text
        )
        self.view_logs_btn.bind(on_press=self.show_logs_popup)
        self.add_widget(self.view_logs_btn)

        self.log_popup = None
        self.ensure_setup()

    def log(self, message, level="INFO"):
        """Logs a message to the internal log and prints it."""
        log_entry = f"[{level}] {message}\n"
        self.log_text += log_entry
        print(log_entry.strip()) # Also prints to Android Logcat or console
        if level == "ERROR" or level == "CRITICAL":
            self.status_message = f"Error: {message}"
        elif level == "SUCCESS":
             self.status_message = message


    def ensure_setup(self):
        """Ensures download directory and binary permissions are set."""
        self.log("Starting setup verification...")
        if not os.path.exists(DOWNLOAD_DIR):
            try:
                os.makedirs(DOWNLOAD_DIR)
                self.log(f"Created download directory: {DOWNLOAD_DIR}")
            except Exception as e:
                self.log(f"Failed to create download directory: {DOWNLOAD_DIR}. Error: {e}", "CRITICAL")
                self.status_message = "Error: Cannot create download folder."
                return

        self.log(f"Download directory: {DOWNLOAD_DIR}")
        self.log(f"App root directory: {APP_ROOT}")
        self.log(f"Native library directory: {LIB_DIR}")

        for name, path in BINARIES.items():
            self.log(f"Checking binary: {name} at {path}")
            if os.path.exists(path):
                self.log(f"Binary {name} found.")
                if platform == 'android': # Chmod is mainly for Unix-like systems
                    try:
                        # Check current permissions
                        st_mode = os.stat(path).st_mode
                        is_executable = bool(st_mode & 0o111) # Check execute bits for owner, group, other
                        
                        if not is_executable:
                            self.log(f"Setting executable permission for {name}...")
                            os.chmod(path, 0o755) # rwxr-xr-x
                            self.log(f"{name} executable permission set.", "SUCCESS")
                        else:
                            self.log(f"{name} already has execute permissions.")
                            
                    except Exception as e:
                        self.log(f"Error setting permission for {name}: {e}", "ERROR")
            else:
                self.log(f"Binary {name} NOT FOUND at {path}. Downloads will likely fail.", "CRITICAL")
                self.status_message = f"Error: {name} binary missing."
        self.log("Setup verification complete.")

    def show_logs_popup(self, instance):
        """Displays a popup window with the accumulated logs."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        log_display_label = Label(
            text=self.log_text,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size='12sp',
            markup=True # Allows simple text styling if needed later
        )
        log_display_label.bind(texture_size=log_display_label.setter('size'))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(log_display_label)
        content.add_widget(scroll_view)

        # Button layout for Close and Clear
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        clear_logs_btn = Button(text="Clear Logs", on_press=self.clear_logs, background_color=(0.9, 0.4, 0.4, 1))
        close_btn = Button(text="Close", background_color=(0.6, 0.6, 0.6, 1))
        
        button_layout.add_widget(clear_logs_btn)
        button_layout.add_widget(close_btn)
        content.add_widget(button_layout)

        if self.log_popup:
            self.log_popup.dismiss() # Dismiss if already open

        self.log_popup = Popup(
            title="Application Logs",
            content=content,
            size_hint=(0.9, 0.85),
            auto_dismiss=False # User must explicitly close
        )
        close_btn.bind(on_press=self.log_popup.dismiss)
        self.log_popup.open()
    
    def clear_logs(self, instance):
        """Clears the log text and updates the log popup if open."""
        self.log_text = "Logs cleared.\n"
        if self.log_popup and self.log_popup.content:
            # Find the ScrollView's Label child to update its text
            scroll_view = self.log_popup.content.children[1] # Assuming ScrollView is the second child from top
            if isinstance(scroll_view, ScrollView) and scroll_view.children:
                log_label_in_popup = scroll_view.children[0]
                log_label_in_popup.text = self.log_text
        self.log("Logs have been cleared by user.", "INFO")


    def initiate_download(self, instance):
        """Validates input and starts the download process in a new thread."""
        if self.download_in_progress:
            self.log("Download already in progress. Please wait.", "WARNING")
            self.status_message = "Download in progress..."
            return

        url = self.url_input.text.strip()
        if not url:
            self.log("URL is empty. Please enter a valid YouTube URL.", "ERROR")
            self.status_message = "Error: URL cannot be empty."
            return
        
        # Basic URL validation (can be improved with regex for stricter checking)
        if not (url.startswith("http://") or url.startswith("https://")):
            self.log(f"Invalid URL format: {url}", "ERROR")
            self.status_message = "Error: Invalid URL format."
            return

        self.download_in_progress = True
        self.download_button.disabled = True
        self.download_button.text = "Downloading..."
        self.status_message = "Preparing to download..."

        # Start download in a separate thread to avoid UI freeze
        thread = threading.Thread(target=self._execute_download_thread, args=(url,))
        thread.daemon = True # Allows app to exit even if thread is running
        thread.start()

    def _execute_download_thread(self, url):
        """
        Executes the yt-dlp command. This method runs in a separate thread.
        Uses Clock.schedule_once to update UI elements from the main thread.
        """
        try:
            format_choice = self.format_spinner.text
            # Ensure filename is somewhat sanitized, replace common problematic chars
            # This is a basic sanitation. For robust sanitation, a library might be better.
            safe_title_template = "%(title)s.%(ext)s".replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            output_template = os.path.join(DOWNLOAD_DIR, safe_title_template)

            # Construct base command for yt-dlp
            # Using --no-warnings to reduce verbose output unless debugging
            # Using --progress to get progress updates (though parsing it live is complex)
            # Using --no-mtime to prevent setting file modification time from server
            command = [
                BINARIES["yt-dlp"],
                "--ffmpeg-location", BINARIES["ffmpeg"],
                "-o", output_template,
                "--no-warnings",
                "--no-mtime", 
                # "--progress" # yt-dlp's progress hook is better for live updates
            ]

            if format_choice.startswith("MP4"):
                # Prefer h264 for wider compatibility if available
                command += ["-f", "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", "--merge-output-format", "mp4"]
            elif format_choice.startswith("MP3"):
                command += ["-x", "--audio-format", "mp3", "--audio-quality", "0"] # 0 is best quality for VBR
            else: # Should not happen with Spinner
                Clock.schedule_once(lambda dt: self.log("Invalid format selected.", "ERROR"))
                Clock.schedule_once(lambda dt: self._finalize_download(success=False, message="Invalid format."))
                return

            command.append(url) # Add the URL to download

            Clock.schedule_once(lambda dt: self.log(f"Executing command: {' '.join(command)}", "DEBUG"))
            Clock.schedule_once(lambda dt: self.status_message_update("Download started... This may take a while."))
            
            # Execute the command
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
            
            # Log output line by line
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    # Schedule UI updates on the main thread
                    Clock.schedule_once(lambda dt, line=line: self.log(line.strip(), "PROCESS"))
                    # Simple progress parsing (can be made more sophisticated)
                    if "%" in line and "ETA" in line:
                         Clock.schedule_once(lambda dt, line=line: self.status_message_update(line.strip()))
                process.stdout.close()

            return_code = process.wait()

            if return_code == 0:
                Clock.schedule_once(lambda dt: self.log("Download and processing completed successfully.", "SUCCESS"))
                Clock.schedule_once(lambda dt: self._finalize_download(success=True, message="Download Complete!"))
            else:
                Clock.schedule_once(lambda dt: self.log(f"yt-dlp process exited with code {return_code}.", "ERROR"))
                Clock.schedule_once(lambda dt: self._finalize_download(success=False, message=f"Download failed (code {return_code}). Check logs."))

        except FileNotFoundError as fnf_error:
            Clock.schedule_once(lambda dt: self.log(f"Error: A required binary (yt-dlp or ffmpeg) was not found. {fnf_error}", "CRITICAL"))
            Clock.schedule_once(lambda dt: self._finalize_download(success=False, message="Critical Error: Binary missing."))
        except subprocess.CalledProcessError as cpe:
            error_output = cpe.output if cpe.output else "No output."
            Clock.schedule_once(lambda dt: self.log(f"Download failed with CalledProcessError. Output: {error_output}", "ERROR"))
            Clock.schedule_once(lambda dt: self._finalize_download(success=False, message="Download failed. Check logs."))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.log(f"An unexpected error occurred during download: {e}", "CRITICAL"))
            Clock.schedule_once(lambda dt: self._finalize_download(success=False, message="Unexpected error. Check logs."))

    def _finalize_download(self, success, message):
        """Called after download attempt to update UI."""
        self.download_in_progress = False
        self.download_button.disabled = False
        self.download_button.text = "Download"
        self.status_message = message
        if success:
            self.url_input.text = "" # Clear URL on success
            self.log(f"File saved in: {DOWNLOAD_DIR}", "INFO")
            # Could add a button to open download folder if Kivy supports it easily on Android
            # from kivy.utils import open_url
            # open_url(f"file://{DOWNLOAD_DIR}") # This might not work directly on all Android versions for folders
        else:
            self.log("Download process finished with errors.", "ERROR")

    def status_message_update(self, message):
        """Helper to update status message from threads."""
        self.status_message = message


class YTDownloaderApp(App):
    def build(self):
        # Set a background color for the window (optional, for better aesthetics)
        # from kivy.core.window import Window
        # Window.clearcolor = (0.98, 0.98, 0.98, 1) # Very light grey
        return YTDownloaderLayout()

if __name__ == '__main__':
    # Ensure the dummy binary paths are created for desktop testing if they don't exist
    if platform != 'android':
        if not os.path.exists(BINARIES["yt-dlp"]):
            print(f"Desktop Warning: yt-dlp binary not found at {BINARIES['yt-dlp']}. Downloads will fail.")
            # open(BINARIES["yt-dlp"], 'a').close() # Create dummy file
        if not os.path.exists(BINARIES["ffmpeg"]):
            print(f"Desktop Warning: ffmpeg binary not found at {BINARIES['ffmpeg']}. Downloads will fail.")
            # open(BINARIES["ffmpeg"], 'a').close() # Create dummy file
            
    YTDownloaderApp().run()

