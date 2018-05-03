from random import sample
import tabulate
import json
import os
import mutagen.mp3


class Duration:
    def __init__(self, string_time):
        try:
            hours, minutes, seconds = string_time.split(':')
        except Exception as exception:
            raise exception
        self.seconds = int(seconds)
        self.minutes = int(minutes)
        self.hours = int(hours)

    def __str__(self):
        return f"{self.hours}:{self.minutes}:{self.seconds}"

    def __add__(self, other):
        return Duration(f'{self.hours + other.hours}:{self.minutes + other.minutes}:{self.seconds + other.minutes}')

    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        return self.seconds == other.seconds and\
            self.minutes == other.minutes and\
            self.hours == other.hours

    def __hash__(self):
        return hash(str(self))

    def convert_to_seconds(self):
        result = self.hours * 3600 + self.minutes * 60 + self.seconds
        return result

    def convert_to_minutes(self):
        result = self.hours * 60 + self.minutes
        return result

    def convert_to_hours(self):
        return self.hours


def validate_song_arguments(title, artist, album, song_length):
    if type(title) is not str:
        raise TypeError

    if type(artist) is not str:
        raise TypeError

    if type(album) is not str:
        raise TypeError

    if type(song_length) is not str:
        raise TypeError

    if ':' not in song_length:
        raise ValueError


class Song:
    def __init__(self, title, artist, album, duration):
        validate_song_arguments(title, artist, album, duration)

        self.title = title
        self.artist = artist
        self.album = album
        self.duration = Duration(duration)

    def __str__(self):
        return
        f'{self.title}-{self.artist} from {self.album}-{str(self.duration)}'

    def __repr__(self):
        return f'{self.title} - {self.artist} - {self.duration}'

    def __eq__(self, other):
        return self.title == other.title and\
            self.artist == other.artist and\
            self.album == other.album and\
            self.duration == other.duration

    def __hash__(self):
        return hash(str(self))

    def length(self, seconds=False, minutes=False, hours=False):
        result = str(self.duration)

        if seconds and not minutes and not hours:
            result = self.duration.convert_to_seconds()

        elif minutes and not seconds and not hours:
            result = self.duration.convert_to_minutes()

        elif hours and not seconds and not minutes:
            result = self.duration.convert_to_hours()

        return result


def validate_playlist_arguments(name, repeat, shuffle):
    if type(name) is not str:
        raise TypeError

    if type(repeat) is not bool:
        raise TypeError

    if type(shuffle) is not bool:
        raise TypeError


class Playlist:
    def __init__(self, name="", repeat=False, shuffle=False):
        validate_playlist_arguments(name, repeat, shuffle)

        self.name = name
        self.repeat = repeat
        self.shuffle = shuffle
        self.songs = []
        self.played = []

    def add_song(self, Song):
        self.songs.append(Song)

    def remove_song(self, Song):
        self.songs.remove(Song)

    def add_songs(self, songs):
        self.songs.extend(songs)

    def total_length(self):
        total = sum([song.duration for song in self.songs])
        return str(total.convert_to_seconds())

    def count_artist(self, artist):
        return sum([1 for song in self.songs if song.artist == artist])

    def artists(self):
        return {f'{song.artist}': self.count_artist(song.artist)
                for song in self.songs}

    def next_song(self):
        result = None
        if len(self.played) == 0:
            if self.shuffle:
                self.songs = sample(self.songs, len(self.songs))
            self.played.append(self.songs[0])

            result = self.songs[0]
        elif len(self.played) == len(self.songs) and self.repeat:
            self.played = [self.songs[0]]
            result = self.songs[0]
        else:
            last_song_index = self.songs.index(self.played[-1])
            current = self.songs[last_song_index + 1]
            self.played.append(current)
            result = current
        return result

    def print_playlist(self):
        return tabulate.tabulate([[song.artist, song.title, song.duration]
                                  for song in self.songs],
                                 headers=['Artist', 'Song', 'Length'],
                                 tablefmt='orgtbl')

    def get_song_list(self, songs):
        song_list = [song.__dict__ for song in songs]
        return song_list

    def playlist_to_json_dict(self):
        json_dict = {}
        for key, value in self.__dict__.items():
            if type(value) is list:
                json_dict[key] = self.get_song_list(value)
            else:
                json_dict[key] = value

        return json_dict

    def change_playlist_name(self):
        playlist_name = self.name
        if ' ' in self.name:
            return playlist_name.replace(' ', '-')

    def save(self):
        name = self.change_playlist_name()
        json_dict = self.playlist_to_json_dict()

        with open(f'{name}.json', "w") as file:
            json.dump(json_dict, file, indent=4)

    @classmethod
    def read_json_from_file(self, path):
        with open(path, "r") as file:
            json_dict = json.load(file)

        return json_dict

    @classmethod
    def set_song_list(self, songs):
        song_list = [Song(**song) for song in songs]
        return song_list

    @classmethod
    def load(cls, path):
        json_dict = cls.read_json_from_file(path)
        obj = cls()
        for key, value in json_dict.items():
            if type(value) is list:
                song_list = cls.set_song_list(value)
                setattr(obj, key, song_list)
            else:
                setattr(obj, key, value)

        return obj


class MusicCrawler:
    def __init__(self, path):
        self.path = path

    def get_duration_from_seconds(self, in_seconds):
        in_seconds = int(in_seconds)
        hours = in_seconds // 3600
        minutes = (in_seconds % 3600) // 60
        seconds = in_seconds % 60

        return f"{hours}:{minutes}:{seconds}"

    def generate_playlist(self, name=""):
        playlist = Playlist()
        with os.scandir(self.path) as it:
            for entry in it:
                if entry.is_file():
                    audio = mutagen.mp3.EasyMP3(entry)
                    song = Song(title=(audio.tags['title'][0]),
                                artist=(audio.tags['artist'][0]),
                                album=(audio.tags['album'][0]),
                                duration=self.get_duration_from_seconds(
                                    audio.info.length))
                    playlist.add_song(song)
        return playlist


def main():
    crawler = MusicCrawler("/home/kristin/Downloads/Rihanna - BOOM.-WEB-2018")
    playlist = crawler.generate_playlist(name="Rihhana Playlist")
    print(playlist.print_playlist())


if __name__ == '__main__':
    main()
