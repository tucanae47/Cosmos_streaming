

#http://www.rasterbar.com/products/libtorrent/manual.html
import libtorrent as lt
import time
import types
import sys
from subprocess import *
import thread
import shutil
import tempfile
import os.path as pt
from time import sleep
from BeautifulSoup import BeautifulSoup
import requests
class Torrent_Cosmos:
     def __init__(self):
         self.cache={}
         self.completed=False
         self.ses=None
         self.h=None
         self.piecestart=None
         self.pieceend=None
         self.offset1=None
         self.offset2=None
         self.piecesperite=None
         self.outputcmd=None
         self.torrents=[]
         #self.cur_selected=None
     
     def searchForCosmos(self):
         r= requests.get('https://thepiratebay.se/search/cosmos%20space%20time%20odyssey/0/7/200')
         soup = BeautifulSoup(r.content)
         table = soup.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=="searchResult")
         rows = table.findAll(lambda tag: tag.name=='tr' and not tag.has_key('class')  )
         self.torrents=[]
         i=0
         for tr in rows:
             ithItem=tr.findChildren('td')
             seeders=ithItem[2].getText()
             leechers=ithItem[3].getText()
             name=ithItem[1].findAll('a')[0].getText()
             magnet=ithItem[1].findAll('a')[1]['href']
             torrent=ithItem[1].findAll('a')[0]['href']
             self.torrents.append({'s':seeders,'l':leechers, 'name':name,'magnet':magnet,'torrent':torrent})
             print "%d seeders:%s, leechers:%s, name:%s "%(i,leechers, seeders,name)
             i+=1
     
     def selectItemAndPlay(self, ith):
         selected=self.torrents[ith]
         print 'loading magnet', selected['magnet']
         self.start(selected['magnet'],0,'/tmp','mplayer -fs -')
         #self.start(selected['magnet'],0,'/tmp','vlc -f -')


     def magnet2torrent(self,magnet, output_name=None):
        if output_name and \
                not pt.isdir(output_name) and \
                not pt.isdir(pt.dirname(pt.abspath(output_name))):
            print("Invalid output folder: " + pt.dirname(pt.abspath(output_name)))
            print("")
            sys.exit(0)

        tempdir = tempfile.mkdtemp()
        ses = lt.session()
        params = {
            'save_path': tempdir,
            'duplicate_is_error': True,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        handle = lt.add_magnet_uri(ses, magnet, params)

        print("Downloading Metadata (this may take a while)")
        while (not handle.has_metadata()):
            try:
                sleep(1)
            except KeyboardInterrupt:
                print("Aborting...")
                ses.pause()
                print("Cleanup dir " + tempdir)
                shutil.rmtree(tempdir)
                sys.exit(0)
        ses.pause()
        print("Done")

        torinfo = handle.get_torrent_info()
        torfile = lt.create_torrent(torinfo)

        output = pt.abspath(torinfo.name() + ".torrent")

        if output_name:
            if pt.isdir(output_name):
                output = pt.abspath(pt.join(
                    output_name, torinfo.name() + ".torrent"))
            elif pt.isdir(pt.dirname(pt.abspath(output_name))):
                output = pt.abspath(output_name)

        print("Saving torrent file here : " + output + " ...")
        torcontent = lt.bencode(torfile.generate())
        f = open(output, "wb")
        f.write(lt.bencode(torfile.generate()))
        f.close()
        print("Saved! Cleaning up dir: " + tempdir)
        ses.remove_torrent(handle)
        shutil.rmtree(tempdir)

        return output 
     def printstatus(self):
            state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            s = self.h.status()
            print >> sys.stderr,'%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s\n' % (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, state_str[s.state]),
            #if s.state == 4:
            #       break
            sys.stdout.flush()
            l = ''
            i = 0
            for p in s.pieces:
                    if i >= self.piecestart and i <= self.pieceend:
                            if p == True:
                                    l = l + '1'
                            if p == False:
                                    l = l + '0'
                    i = i+1
            print >> sys.stderr,l

     def addnewpieces(self):
            prio = self.h.piece_priorities()
            s = self.h.status()
            downloading = 0
            if len(s.pieces) == 0:
                    return
            for piece in range(self.piecestart,self.pieceend+1):
                    if prio[piece] != 0 and s.pieces[piece]==False:
                            downloading = downloading+1
            for piece in range(self.piecestart,self.pieceend+1):
                    if prio[piece] == 0 and downloading < self.piecesperite:
                            print >> sys.stderr,'downloading piece ',piece
                            self.h.piece_priority(piece,1)
                            downloading = downloading+1
            for piece in range(self.piecestart,self.pieceend+1):
                    if prio[piece] != 0 and s.pieces[piece]==False:
                            print >> sys.stderr,'high prio ',piece
                            self.h.piece_priority(piece,7)
                            break

     def getpiece(self,i):
            #global cache
            if i in self.cache:
                    ret = self.cache[i]
                    self.cache[i] = 0
                    return ret
            while True:
                    s = self.h.status()
                    if len(s.pieces)==0:
                            break
                    if s.pieces[i]==True:
                            break
                    time.sleep(.1)
            self.h.read_piece(i)
            while True:
                    #printstatus()
                    #addnewpieces()
                    piece = self.ses.pop_alert()
                    if isinstance(piece, lt.read_piece_alert):
                            if piece.piece == i:
                                    #sys.stdout.write(piece.buffer)
                                    return piece.buffer
                            else:
                                    print >> sys.stderr,'store somewhere'
                                    self.cache[piece.piece] = piece.buffer
                            break
                    time.sleep(.1)

     def writethread(self):
            stream = 0
            print "state"
            for piece in range(self.piecestart,self.pieceend+1):
                    buf=self.getpiece(piece)
                    if piece==self.piecestart:
                            buf = buf[self.offset1:]
                    if piece==self.pieceend:
                            buf = buf[:self.offset2]
                    print >> sys.stderr, 'output',piece,len(buf)
                    if self.outputcmd=='-':
                            stream = sys.stdout
                    else:
                            if stream == 0:                 
                                    stream = Popen(self.outputcmd.split(' '), stdin=PIPE).stdin
                    try:
                            stream.write(buf)
                    except Exception, err:
                            print err
                            self.ses.remove_torrent(self.h)
                            self.completed = True
                            exit(0)
                    time.sleep(.1)
            self.ses.remove_torrent(self.h)
            self.completed = True

     def start(self,magnet,fileid,outdir,_outputcmd):
            self.outputcmd=_outputcmd
            torrent=self.magnet2torrent(magnet)
            info = lt.torrent_info(torrent)
            #self.ses = lt.session()
            print torrent, outdir, self.ses,fileid,self.outputcmd

            #cur_t_handle=self.ses.add_torrent({'url':torrent, 'save_path':outdir})
            #print cur_t_handle
            #info=cur_t_handle.get_torrent_info()
            self.piecesperite = 40*1024*1024/info.piece_length() # 40 MB
            print >> sys.stderr, 'piecesperite',self.piecesperite
            print >> sys.stderr, 'info.piece_length()',info.piece_length()
            sizes = []
            i = 0
            for f in info.files():
                    self.piecestart = f.offset/info.piece_length()
                    self.pieceend = (f.offset+f.size)/info.piece_length()
                    sizes.append(f.size)
                    print >> sys.stderr, i,f.path,f.size,f.offset,self.piecestart,self.pieceend
                    i=i+1
            if fileid == 'list':
                    return
            if fileid == 'max':
                    fileid = sizes.index(max(sizes))
            else:
                    fileid = int(fileid)

            f = info.files()[fileid]
            print >> sys.stderr, f.path
            self.piecestart = f.offset/info.piece_length()
            self.pieceend = (f.offset+f.size)/info.piece_length()
            self.offset1 = f.offset%info.piece_length() #how many bytes need to be removed from the 1st piece
            self.offset2 = ((f.offset+f.size)%info.piece_length()) #how many bytes need we keep from the last piece
            print >> sys.stderr,self.piecestart,self.pieceend,self.offset1,self.offset2,info.piece_length()
            print >> sys.stderr,(self.pieceend-self.piecestart+1)*info.piece_length()-(self.offset1+self.offset2),f.size
            self.ses = lt.session()

            state = None
            #state = lt.bdecode(open(state_file, "rb").read())
            self.ses.start_dht(state)
            self.ses.add_dht_router("router.bittorrent.com", 6881)
            self.ses.add_dht_router("router.utorrent.com", 6881)
            self.ses.add_dht_router("router.bitcomet.com", 6881)

            self.ses.listen_on(6881, 6891)
            self.ses.set_alert_mask(lt.alert.category_t.storage_notification)
            self.h = self.ses.add_torrent({'ti': info, 'save_path': outdir})
            for i in range(info.num_pieces()):
                    self.h.piece_priority(i,0)
            print >> sys.stderr,'starting', self.h.name()
            for i in range(self.piecestart,self.piecestart+self.piecesperite):
                if i <= self.pieceend:
                    self.h.piece_priority(i,7)
                    print >> sys.stderr,'downloading piece '+str(i)
            thread.start_new_thread(self.writethread,())
            while not self.completed:
                    self.printstatus()
                    self.addnewpieces()
                    time.sleep(1)

