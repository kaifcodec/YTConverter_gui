[app]

# (str) Title of your application
title = YTConverter

# (str) Application versioning (required)
version = 1.0.0

# (str) Package name (should be unique, use your domain reversed)
package.name = ytconverter

# (str) Package domain (used to generate the Java package)
package.domain = com.kaif

# (str) Source code entry point (your main.py)
source.dir = .
source.include_exts = py,png,kv,txt

# (list) Application requirements
#   Note: ffmpeg is provided by python-for-android
requirements = python3,kivy,yt-dlp,ffmpeg

# (str) Icon of the app
# icon.filename = data/icon.png

# (str) Supported orientation (portrait|landscape|all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (bool) Hide the statusbar
android.hide_status_bar = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (str) Android Build-Tools version (must match your GitHub Actions install)
android.build_tools_version = 33.0.2

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use (must match your GitHub Actions install)
android.ndk = 23b

# (int) Android NDK API to use (minimum native code support)
android.ndk_api = 21

# (bool) Build as debug (unsigned) or release (signed)
android.debug = True

[buildozer]

# (int) Log level (0 = error only, 2 = info, 3 = debug)
log_level = 2

# (bool) Don’t let p4a re-download SDK/NDK—use what's in the env
p4a.local_recipes = False

# (str) Point Buildozer at the SDK we installed in GitHub Actions
android.sdk_path = $ANDROID_SDK_ROOT

# (str) Point Buildozer at the NDK we installed in GitHub Actions
android.ndk_path = $ANDROID_NDK_HOME

# (str) Java home (should pick up the JDK set by setup-java)
#java.home = /usr/lib/jvm/java-17-temurin
