# This file is for testing the ytmusic API.
from ytmusicapi import YTMusic


ytm = YTMusic('test.json')

def search(song: str='', artist: str='') -> list[dict]:
    query = ''
    if not song:
        query = artist
    elif not artist:
        query = song
    else:
        query = song + ' by ' + artist
    return ytm.search(query)

