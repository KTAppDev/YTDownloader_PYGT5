from pytube import YouTube
from pytube import Search
from pytube import Playlist
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QRadioButton
import os
from sys import platform
import subprocess
import func
import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # important used to make internet coms legit - windows issue


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        uic.loadUi("MainUiWindow.ui", self)
        self.download_button = self.findChild(QPushButton, "download_button")
        self.open_folder = self.findChild(QPushButton, "open_folder")
        self.update_label = self.findChild(QLabel, "update_label")
        self.op_input = self.findChild(QLineEdit, "op_input")
        self.link = self.findChild(QLineEdit, "link")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")
        self.download_list_button = self.findChild(QPushButton, "download_list_button")

        # Actions
        self.download_button.clicked.connect(lambda: self.download_clicked())
        self.open_folder.clicked.connect(lambda: self.open_folder_clicked())
        self.download_list_button.clicked.connect(lambda: self.open_folder_clicked())

    def download_clicked(self):
        radio_button_state = "radio edit clean audio"
        if self.link.text() == '':
            self.update_label.setText("ERROR - Please enter a song name and artiste")
            return
        if self.select_audio.isChecked():
            radio_button_state = "official audio"
        elif self.select_raw_audio.isChecked():
            radio_button_state = "raw official audio"
        elif self.select_clean_audio.isChecked():
            radio_button_state = "radio edit clean audio"

        self.update_label.setText('Searching...')
        default_loc = func.get_os() + '/Youtube/'  # Default folder
        if self.op_input.text() == '':
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state), default_loc)
        else:
            user_location = default_loc + self.op_input.text()
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state),
                user_location)
        self.update_label.setText(download_info[0])
        file_path = download_info[1]
        song_info = download_info[2]
        try:
            func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
        except Exception as e:
            print(str(e))

        self.link.setText("")
        self.download_button.disabled = False

    def open_folder_clicked(self):
        # desktop = os.path.expanduser("~\\Desktop\\")
        # print(desktop)
        default_loc = func.get_os() + '/Youtube/'
        print(default_loc)
        if self.op_input.text() == '':
            path = default_loc
        else:
            path = default_loc + self.op_input.text()

        if platform == "win32":
            try:
                os.startfile(path)
            except Exception as e:
                print(e)

        elif platform == "darwin":
            try:
                subprocess.Popen(["open", path])
            except Exception as e:
                print(e)
        else:
            try:
                print(platform)
                subprocess.Popen(["xdg-open", path])
            except Exception as e:
                print(e)

    def download_list_clicked(self):
        try:
            list_of_songs = func.get_songs_from_text('listofsongs.txt')
            self.update_label.setText("text file found...")
        except Exception as e:
            self.update_label.setText(str(e))

        radio_button_state = "radio edit clean audio"
        if self.select_audio.isChecked():
            radio_button_state = "official audio"
        elif self.select_raw_audio.isChecked():
            radio_button_state = "raw official audio"
        elif self.select_clean_audio.isChecked():
            radio_button_state = "radio edit clean audio"

        self.update_label.setText('Searching...')
        default_loc = func.get_os() + '/Youtube/'  # Default folder
        if self.op_input.text() == '':
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state), default_loc)
        else:
            user_location = default_loc + self.op_input.text()
            download_info = self.youtube_single_download(
                self.searchtube(self.link.text(), radio_button_state),
                user_location)
        self.update_label.setText(download_info[0])
        file_path = download_info[1]
        song_info = download_info[2]
        try:
            self.update_label.setText('converting...')
            func.rename_file(file_path)  # remove the word downloaded 11 characters, its the title so i add mp4
            self.update_label.setText('converted...')
        except Exception as e:
            self.update_label.setText(e)

        self.link.setText("")

        # *************************** YOUTUBE STUFF *************************

    def youtube_single_download(self, link, op):
        if not link:
            self.update_label.setText('Error - no song specified or song downloaded already')
            return
        # print('single download func ran')
        yt = YouTube(link[0])
        # print(f'single download func debug 2 {yt}')
        yt.streams.filter(only_audio=True)
        self.update_label.setText('Starting download...')
        stream = yt.streams.get_by_itag(140)
        file_path = stream.download(output_path=op)
        self.update_label.setText('Download complete')
        info_list = [yt.title, file_path, yt.vid_info]
        return info_list

    def searchtube(self, txt, radio_button_state):
        if txt == '':
            return []
        # print('search func ran')
        self.update_label.setText('Searching for your song...')
        video_list = []
        s = Search(f'{txt} {radio_button_state}')
        for obj in s.results:
            x = str(obj)  # in the future see if theyy have an easier way to use these youtube obj in search results. I doubt what i'm doing is the easy way lol
            video_id = x[x.rfind('=') + 1:].strip('>')
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_list.append(video_url)
            self.update_label.setText('getting list of matching audio')
        self.update_label.setText('Search complete')
        return video_list

    def download_youtube_playlist(self):
        print('playlist func ran')
        pl = input('Paste playlist here >')
        playlist = Playlist(pl)
        print('*' * 40)
        print(f'Playlist contains {len(playlist)} items')
        print('*' * 40)
        for url in playlist[:3]:
            self.youtube_single_download(url)

    def download_list_of_songs_from_file(self, list_of_songs):
        print('playlist from file func ran')
        self.update_label.setText('Getting list of songs from file')
        # playlist = Playlist(pl)
        # print('*' * 40)
        self.update_label.setText(f'File contains {len(list_of_songs)} songs')
        # print('*' * 40)
        for song in list_of_songs:
            self.update_label.setText(f'Currently downloading song - {song}')
            self.youtube_single_download(song)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainuiwindow = MainUiWindow()

    widget = QStackedWidget()
    widget.addWidget(mainuiwindow)
    widget.setFixedHeight(450)
    widget.setFixedWidth(550)
    widget.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(e)
