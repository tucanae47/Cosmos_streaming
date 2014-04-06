cosmos_streaming_torrent
========================

Python stream torrents PB: recently i met Cosmos Space Time Odyssey and i fall in love of it, most of the times im bussy so i want to watch Cosmos at the time i need without waiting torrents to download normal way, nor waiting for Famous TV Channels Schedules, so i did this script, i hope to make it better with the time.

## Requirements
* python 2.7.6
* python-libtorrent:  (libtorrent-rasterbar version 0.16 or later)  <http://www.rasterbar.com/products/libtorrent/>
* BeautifulSoup:  <http://www.crummy.com/software/BeautifulSoup/> : famous html parsing library.
* Requests : http://docs.python-requests.org/en/latest/ : famous http python library.
* mplayer or vlc (although vlc is not yet supported)

## Credits 
The hard job is on guys here, thanks to them i was able to write this. :-) 
* <http://p2ptube.sourceforge.net/> : python torrent streaming, the core of the streaming is from btcat.py from coder owner, i just use that code in my script
* <https://github.com/danfolkes/Magnet2Torrent> : great tool to convert magnet links to torrents, i use it inside my script too. 
* TPB : you know ;)

## Usage:
* install dependencies with easy_install, this will work straighforward on most linux machines, in macosx with macports you can install kind of fast
libtorrent, but it could be a pain in some environments, as it was for me. 
* turn an ipython console:
```python
    from Cosmos_Streaming import Torrent_Cosmos
    t=Torrent_Cosmos()
    t.searchForCosmos()
    t.selectItemAndPlay(0)
```
## TODO:
* become a pro torrent streaming api, like peerflix.
* organize code.
* make it a console tool.













