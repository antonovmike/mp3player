import getpass
import gi
import m3u8
import music_tag
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


def read_window_settings():
    with open('window_settings') as f:
        settings = f.read().splitlines()
    width = int(settings[0].split('=')[1])
    height = int(settings[1].split('=')[1])
    return [width, height]


def read_play_list():
    with open('play_list') as f:
        songs = f.readlines()
    return [song.strip() for song in songs]


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Player")
        height = read_window_settings()[0]
        width = read_window_settings()[1]
        self.set_default_size(width, height)

        grid = Gtk.Grid()

        toolbar = Gtk.Toolbar()

        prev_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("media-skip-backward-symbolic", 16), label="Previous")
        toolbar.insert(prev_button, 0)

        play_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", 16), label="Play")
        toolbar.insert(play_button, 1)

        stop_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("media-playback-stop-symbolic", 16), label="Stop")
        toolbar.insert(stop_button, 2)

        next_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("media-skip-forward-symbolic", 16), label="Next")
        toolbar.insert(next_button, 3)

        progressbar = Gtk.ToolItem()
        progressbar.add(Gtk.ProgressBar())
        toolbar.insert(progressbar, 4)

        random_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("view-refresh-symbolic", 16), label="Random")
        toolbar.insert(random_button, 5)

        repeat_button = Gtk.ToolButton.new(Gtk.Image.new_from_icon_name("media-playlist-repeat-symbolic", 16), label="Repeat")
        toolbar.insert(repeat_button, 6)

        file_tree = FileTree()

        scroll = Gtk.ScrolledWindow()
        scroll.add(file_tree)

        self.playlist = PlayList('play_list.m3u')
        self.listbox = Gtk.ListBox()
        for song in self.playlist.songs:
            self.listbox.add(Gtk.Label(label=song))

        paned = Gtk.Paned()
        paned.pack1(scroll, True, False)
        paned.pack2(self.listbox, True, False)

        grid.attach(toolbar, 0, 0, 1, 1)
        grid.attach(paned, 0, 1, 1, 1)
        self.add(grid)

        GLib.idle_add(self.update_paned_position, paned)

    def update_paned_position(self, paned):
        width = paned.get_allocated_width()
        paned.set_position(int(width * 0.3))

    def populate_file_store(self, store, path):
        for item in os.listdir(path):
            item_fullname = os.path.join(path, item)
            item_is_folder = os.path.isdir(item_fullname)
            if item_is_folder:
                store.append(None, [item, item_fullname])
                self.populate_file_store(store, item_fullname)
            else:
                store.append(None, [item, item_fullname])


class FileTree(Gtk.TreeView):
    def __init__(self):
        Gtk.TreeView.__init__(self)
        self.file_store = Gtk.TreeStore(str, str)
        self.set_model(self.file_store)

        file_column = Gtk.TreeViewColumn("Files", Gtk.CellRendererText(), text=0)
        self.append_column(file_column)

        user = getpass.getuser()
        directory = f"/home/{user}/Music"

        root = self.file_store.append(None, [directory, directory])
        self.add_directory(root, directory)

    def add_directory(self, parent, path):
        # Recursively add all files and directories to the TreeStore model
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directory = self.file_store.append(parent, [item, item_path])
                self.add_directory(directory, item_path)
            else:
                self.file_store.append(parent, [item, item_path])


class PlayList:
    def __init__(self, filename):
        self.filename = filename
        self.songs = self.read_play_list()

    def read_play_list(self):
        m3u8_obj = m3u8.load(self.filename)
        songs = [song.title for song in m3u8_obj.segments]
        return songs

    def update_playlist(self, playlist_store):
        playlist_store.clear()
        for song in self.songs:
            playlist_store.append([""])


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
