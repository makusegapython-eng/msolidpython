from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
import yt_dlp
import threading
import sys,os

Window.clearcolor=(0.325,0.741,0.91,1)
Window.set_title("MSOLID-VIDEO DOWNLOADER")

class YDLLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"Error: {msg}")

def resource_path(file):
    return os.path.join(getattr(sys,'_MEIPASS',os.getcwd()),file)


class DownloderApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical',spacing=10,padding=10,**kwargs)
        self.logo=Image(source=resource_path("msolid.png"),size_hint=(1,1))
        self.add_widget(self.logo)
        self.label=Label(text='ENTER YOUTUBE URL',color=(1,1,1,1),font_size=40)
        self.add_widget(self.label)

        self.progress=ProgressBar(max=100,value=0,size_hint=(1,None),height=20)
        self.add_widget(self.progress)

        self.urlinput=TextInput(hint_text="Youtube link",size_hint=(1,0.2))
        self.add_widget(self.urlinput)

        self.pastebutton=Button(text="PASTE LINK",size_hint=(0.5,0.5),font_size=20,background_normal="",background_color=(0.024,0.941,0.192,0.93))
        self.pastebutton.bind(on_press=self.clipboard)
        self.add_widget(self.pastebutton)

        self.button=Button(text="DOWNLOAD",size_hint=(0.5,0.5),font_size=20,background_normal="",background_color=(0.941,0.094,0.031,1))
        self.button.bind(on_press=self.start_download)
        self.add_widget(self.button)
    def update_label(self, text, *args):
        # This safely updates the UI from the main thread
        self.label.text = text

    def update_progress(self,value):
        self.progress.value=value

    def progress_hook(self, d):
        if d['status'] == 'downloading':

            # REAL SAFE VALUE from yt-dlp
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')

            if total:
                percent = (downloaded / total) * 100

                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.update_progress(percent))
                Clock.schedule_once(lambda dt: self.update_label(f"Downloading... {int(percent)}%"))

        elif d['status'] == 'finished':
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.update_progress(100))
            Clock.schedule_once(lambda dt: self.update_label("Done"))

    def clipboard(self,instance):
        text=Clipboard.paste()
        if text:
            self.urlinput.text=text
            self.label.text="URL IS PASTED"
        else:
            self.label.text="URL NOT PASTED"

    def start_download(self,instance):
        self.progress.value=0
        self.label.text="Start downloading......"
        action=threading.Thread(target=self.download_video)
        action.daemon = True
        action.start()
        
    def download_video(self):
        url=self.urlinput.text.strip()
        if not url:
            Clock.schedule_once(lambda dt:self.update_label("Please enter a URL"))
            return
        options={
                'format':'bestvideo+bestaudio/best',
                'merge_output_format':'mp4',
                'progress_hooks': [self.progress_hook],
                'outtmpl': '%(title)s.%(ext)s',
                'ffmpeg_location':resource_path('ffmpeg.exe'),
                'logger': YDLLogger(),  # Fixes the AttributeError
                'quiet': True,
                'no_warnings': True
            }
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([url])

                    Clock.schedule_once(lambda dt: self.update_label("DOWNLOAD COMPLETE"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_label(f"Error:{str(e)}"))

class MyApp(App):
    def build(self):
        self.title="MSOLID"
        return DownloderApp()
    
if __name__=="__main__":
    MyApp().run()