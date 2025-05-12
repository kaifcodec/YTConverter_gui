[app]

# (str) Title of your application
title = YTConverter™

# (str) Package name (should be unique, use your domain reversed)
package.name = ytconverter

# (str) Package domain (used to generate the Java package)
package.domain = com.yourname

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

# (str) Android entry point, default is ok
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, uncomment to disable ActionBar and use fullscreen
# android.theme = '@android:style/Theme.NoTitleBar'

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to compile against
android.sdk = 31

# (str) Android NDK version to use
android.ndk = 23b

# (int) Android NDK API to use (this is the minimum API your app will support for native code)
android.ndk_api = 21

# (bool) Indicate if the build should be debug (unsigned) or release (signed)
#   For testing leave as debug; for publishing set to False and sign manually
android.debug = True

# (list) Android additional libraries to copy to libs/armeabi-v7a
#android.add_libs_armeabi_v7a = libs/armeabi-v7a/libxyz.so

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Python code to run before your main.py
# (useful if you need to inject env vars)
# p4a.bootstrap = sdl2

[buildozer]

# (int) Log level (0 = error only, 1 = warning, 2 = info, 3 = debug)
log_level = 2

# (bool) Whether to update the local copy of python-for-android
p4a.local_recipes = False

# (str) Path to a custom python-for-android checkout
#p4a.source_dir = ../python-for-android

# (str) Directory in which python-for-android should look for prebuilt recipes
#p4a.recipedir =

# (str) Android SDK directory (if you installed it manually)
#android.sdk_path = /path/to/android-sdk

# (str) Android NDK directory (if you installed it manually)
#android.ndk_path = /path/to/android-ndk

# (str) Ant directory (if using ant, not needed here)
#android.ant_path = /path/to/ant

# (str) Java directory (if you have multiple JDKs)
#java.home = /usr/lib/jvm/java-11-openjdk
