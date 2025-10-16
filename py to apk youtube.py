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
import requests
import json
import threading


class YouTubeInfoApp(MDApp):
    def __init__(self):
        super().__init__()
        self.dialog = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"

        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20)
        )

        # App Bar
        app_bar = MDTopAppBar(
            title="YouTube Video Info",
            elevation=4,
            md_bg_color=[0.2, 0.2, 0.6, 1],
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
            height=dp(450)
        )

        # Title
        welcome_label = MDLabel(
            text="🎬 Get YouTube Video Info",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            bold=True
        )
        content_card.add_widget(welcome_label)

        # URL Input
        self.url_input = MDTextField(
            hint_text="Paste YouTube URL here...",
            mode="rectangle",
            icon_left="youtube",
            size_hint_y=None,
            height=dp(60)
        )
        content_card.add_widget(self.url_input)

        # Get Info Button
        self.info_btn = MDRaisedButton(
            text="GET VIDEO INFO",
            icon="information",
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.2, 0.2, 0.6, 1]
        )
        self.info_btn.bind(on_press=self.get_video_info)
        content_card.add_widget(self.info_btn)

        # Info Display Area
        self.info_label = MDLabel(
            text="Enter YouTube URL to get video information",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(150)
        )
        content_card.add_widget(self.info_label)

        main_layout.add_widget(content_card)

        return main_layout

    def get_video_info(self, instance):
        video_url = self.url_input.text.strip()

        if not video_url:
            self.show_dialog("Input Error", "Please enter a YouTube URL")
            return

        self.info_btn.disabled = True
        self.info_btn.text = "FETCHING INFO..."
        self.info_label.text = "🔄 Fetching video information..."

        # Start in thread
        thread = threading.Thread(target=self.fetch_video_data, args=(video_url,))
        thread.daemon = True
        thread.start()

    def fetch_video_data(self, video_url):
        try:
            # Simple API call to get video info (without downloading)
            # Using a free API service
            api_url = f"https://noembed.com/embed?url={video_url}"
            response = requests.get(api_url, timeout=10)
            data = response.json()

            if 'title' in data:
                video_info = f"""
📹 **Title:** {data.get('title', 'N/A')}
👤 **Author:** {data.get('author_name', 'N/A')}
🕒 **Duration:** {data.get('duration', 'N/A')}
👁️ **Views:** {data.get('views', 'N/A')}
📅 **Upload Date:** {data.get('upload_date', 'N/A')}

✅ Video information fetched successfully!
                """
                Clock.schedule_once(lambda dt: self.show_video_info(video_info, True))
            else:
                Clock.schedule_once(lambda dt: self.show_error("Could not fetch video info"))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"))

    def show_video_info(self, info, success=True):
        self.info_label.text = info
        self.info_btn.disabled = False
        self.info_btn.text = "GET VIDEO INFO"

        if success:
            self.show_dialog("Success", "Video information fetched successfully!")
        else:
            self.show_dialog("Error", "Failed to get video information")

    def show_error(self, error_msg):
        self.info_label.text = f"❌ {error_msg}"
        self.info_btn.disabled = False
        self.info_btn.text = "GET VIDEO INFO"
        self.show_dialog("Error", error_msg)

    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


if __name__ == "__main__":
    YouTubeInfoApp().run()