# Copyright (c) 2011-2020 Eric Froemling
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
"""UI functionality related to using iTunes for soundtracks."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import ba

if TYPE_CHECKING:
    from typing import Any, List, Optional, Callable


class MacMusicAppPlaylistSelectWindow(ba.OldWindow):
    """Window for selecting an iTunes playlist."""

    def __init__(self, callback: Callable[[Any], Any],
                 existing_playlist: Optional[str], existing_entry: Any):
        from ba.internal import get_music_player, MacMusicAppMusicPlayer
        self._r = 'editSoundtrackWindow'
        self._callback = callback
        self._existing_playlist = existing_playlist
        self._existing_entry = copy.deepcopy(existing_entry)
        self._width = 520.0
        self._height = 520.0
        self._spacing = 45.0
        v = self._height - 90.0
        v -= self._spacing * 1.0
        super().__init__(root_widget=ba.containerwidget(
            size=(self._width, self._height), transition='in_right'))
        btn = ba.buttonwidget(parent=self._root_widget,
                              position=(35, self._height - 65),
                              size=(130, 50),
                              label=ba.Lstr(resource='cancelText'),
                              on_activate_call=self._back)
        ba.containerwidget(edit=self._root_widget, cancel_button=btn)
        ba.textwidget(parent=self._root_widget,
                      position=(20, self._height - 54),
                      size=(self._width, 25),
                      text=ba.Lstr(resource=self._r + '.selectAPlaylistText'),
                      color=ba.app.title_color,
                      h_align="center",
                      v_align="center",
                      maxwidth=200)
        self._scrollwidget = ba.scrollwidget(parent=self._root_widget,
                                             position=(40, v - 340),
                                             size=(self._width - 80, 400))
        self._column = ba.columnwidget(parent=self._scrollwidget)

        # So selection loops through everything and doesn't get stuck
        # in sub-containers.
        ba.containerwidget(edit=self._scrollwidget,
                           claims_left_right=True,
                           claims_tab=True,
                           selection_loop_to_parent=True)
        ba.containerwidget(edit=self._column,
                           claims_left_right=True,
                           claims_tab=True,
                           selection_loop_to_parent=True)

        ba.textwidget(parent=self._column,
                      size=(self._width - 80, 22),
                      text=ba.Lstr(resource=self._r + '.fetchingITunesText'),
                      color=(0.6, 0.9, 0.6, 1.0),
                      scale=0.8)
        musicplayer = get_music_player()
        assert isinstance(musicplayer, MacMusicAppMusicPlayer)
        musicplayer.get_playlists(self._playlists_cb)
        ba.containerwidget(edit=self._root_widget,
                           selected_child=self._scrollwidget)

    def _playlists_cb(self, playlists: List[str]) -> None:
        if self._column:
            for widget in self._column.get_children():
                widget.delete()
            for playlist in playlists:
                txt = ba.textwidget(parent=self._column,
                                    size=(self._width - 80, 30),
                                    text=playlist,
                                    v_align='center',
                                    maxwidth=self._width - 110,
                                    selectable=True,
                                    on_activate_call=ba.Call(
                                        self._sel, playlist),
                                    click_activate=True)
                if playlist == self._existing_playlist:
                    ba.columnwidget(edit=self._column,
                                    selected_child=txt,
                                    visible_child=txt)

    def _sel(self, selection: str) -> None:
        if self._root_widget:
            ba.containerwidget(edit=self._root_widget, transition='out_right')
            self._callback({'type': 'iTunesPlaylist', 'name': selection})

    def _back(self) -> None:
        ba.containerwidget(edit=self._root_widget, transition='out_right')
        self._callback(self._existing_entry)
