[app]

title = YTConverter
version = 1.0.0
package.name = ytconverter
package.domain = com.kaif

source.dir = .
source.include_exts = py,png,kv,txt

requirements = python3,kivy,yt-dlp,ffmpeg

# Uncomment and set your icon path if you have one
# icon.filename = data/icon.png

orientation = portrait
fullscreen = 0
android.hide_status_bar = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 31
android.build_tools_version = 33.0.2
android.minapi = 21

# Make sure this matches the one you installed
android.ndk = 23b
android.ndk_api = 21
android.debug = True

# Optional but recommended for speed
#android.private_storage = True

[buildozer]

log_level = 2

# Point to manually installed SDK and NDK
android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/android-sdk/ndk/23.1.7779620

# Accept licenses automatically
android.accept_sdk_license = True

# Disable recipe override
p4a.local_recipes = False

# Optional Java home if needed
#java.home = /usr/lib/jvm/java-17-temurin
