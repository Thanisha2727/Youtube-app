from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import Clock
from kivy.metrics import dp
import yt_dlp
import threading
# App-la add pannu - main function-ku munnadi
import os


class YouTubeDownloaderApp(MDApp):
    def __init__(self):
        super().__init__()
        self.dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Blue"


        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20)
        )


        app_bar = MDTopAppBar(
            title="YouTube Downloader",
            elevation=4,
            md_bg_color=[0.2, 0.2, 0.6, 1],
            specific_text_color=[1, 1, 1, 1],
        )
        main_layout.add_widget(app_bar)

        # Content Card
        content_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(20),
            elevation=3,
            radius=[dp(15), ],
            size_hint_y=None,
            height=dp(400)
        )

        # Welcome message
        welcome_label = MDLabel(
            text="🎬 Download YouTube Videos",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content_card.add_widget(welcome_label)

        # URL input with icon
        self.url_input = MDTextField(
            hint_text="Paste YouTube URL here...",
            mode="rectangle",
            icon_left="youtube",
            size_hint_y=None,
            height=dp(60),
            line_color_focus=[0.2, 0.2, 0.6, 1]
        )
        content_card.add_widget(self.url_input)

        # Download button with icon
        self.download_btn = MDRaisedButton(
            text="START DOWNLOAD",
            icon="download",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.2, 0.2, 0.6, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1]
        )
        self.download_btn.bind(on_press=self.start_download)
        content_card.add_widget(self.download_btn)

        # Progress section
        progress_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80)
        )

        self.progress_bar = MDProgressBar(
            value=0,
            size_hint_y=None,
            height=dp(8)
        )
        self.progress_bar.opacity = 0
        progress_layout.add_widget(self.progress_bar)

        self.status_label = MDLabel(
            text="Ready to download",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        progress_layout.add_widget(self.status_label)

        content_card.add_widget(progress_layout)

        # Download location info
        location_label = MDLabel(
            text="📁 Download Location: Current Folder",
            halign="center",
            theme_text_color="Hint",
            size_hint_y=None,
            height=dp(30)
        )
        content_card.add_widget(location_label)

        main_layout.add_widget(content_card)

        # Features card
        features_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10),
            elevation=2,
            radius=[dp(10), ],
            size_hint_y=None,
            height=dp(150)
        )

        features_title = MDLabel(
            text="✨ Features",
            theme_text_color="Primary",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        features_card.add_widget(features_title)

        features_list = [
            "✅ HD Quality (up to 1080p)",
            "✅ Fast Download Speed",
            "✅ MP4 Format",
            "✅ Auto Title Saving"
        ]

        for feature in features_list:
            feature_label = MDLabel(
                text=feature,
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(25)
            )
            features_card.add_widget(feature_label)

        main_layout.add_widget(features_card)

        return main_layout

    def start_download(self, instance):
        video_url = self.url_input.text.strip()

        if not video_url:
            self.show_dialog("⚠️ Input Error", "Please enter a YouTube URL")
            return

        if "youtube.com" not in video_url and "youtu.be" not in video_url:
            self.show_dialog("❌ Invalid URL", "Please enter a valid YouTube URL")
            return

        # Disable button and show progress
        self.download_btn.disabled = True
        self.download_btn.text = "DOWNLOADING..."
        self.progress_bar.opacity = 1
        self.status_label.text = "🔄 Starting download..."
        self.status_label.theme_text_color = "Primary"

        # Start download in thread
        thread = threading.Thread(target=self.download_video, args=(video_url,))
        thread.daemon = True
        thread.start()

    def download_video(self, video_url):
        def progress_hook(d):
            if d['status'] == 'downloading':
                if '_percent_str' in d:
                    percent_str = d['_percent_str'].strip()
                    try:
                        if '%' in percent_str:
                            percent = float(percent_str.replace('%', ''))
                            status = f"⬇️ Downloading... {percent_str}"
                            Clock.schedule_once(lambda dt: self.update_progress(percent, status))
                    except ValueError:
                        status = f"⬇️ Downloading... {percent_str}"
                        Clock.schedule_once(lambda dt: self.update_progress(0, status))

            elif d['status'] == 'finished':
                Clock.schedule_once(lambda dt: self.download_complete())

            elif d['status'] == 'error':
                Clock.schedule_once(lambda dt: self.download_error(str(d.get('error', 'Unknown error'))))

        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            Clock.schedule_once(lambda dt: self.download_error(str(e)))

    def update_progress(self, percent, status):
        self.progress_bar.value = percent
        self.status_label.text = status

    def download_complete(self):
        self.progress_bar.value = 100
        self.status_label.text = "✅ Download Complete!"
        self.status_label.theme_text_color = "Custom"
        self.status_label.text_color = [0, 0.5, 0, 1]  # Green color
        self.download_btn.disabled = False
        self.download_btn.text = "START DOWNLOAD"
        self.progress_bar.opacity = 0
        self.url_input.text = ""
        self.show_dialog("🎉 Success", "Video downloaded successfully!")

    def download_error(self, error_message):
        self.status_label.text = "❌ Download Failed!"
        self.status_label.theme_text_color = "Error"
        self.download_btn.disabled = False
        self.download_btn.text = "START DOWNLOAD"
        self.progress_bar.opacity = 0
        self.progress_bar.value = 0
        self.show_dialog("🚨 Error", f"Download failed:\n{error_message}")

    def show_dialog(self, title, text):
        # Close existing dialog if open
        if self.dialog:
            self.dialog.dismiss()

        # Create new dialog without radius parameter (causing the error)
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=[1, 1, 1, 1],
                    md_bg_color=[0.2, 0.2, 0.6, 1],
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


if __name__ == "__main__":
    YouTubeDownloaderApp().run()