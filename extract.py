#coding:utf8
import requests
import csv
import json
import shutil
from secret_data import CLIENT_ID, CLIENT_SECRET
import sys
from pydub import AudioSegment

class SoundCloudAnalyse:
    #https://soundcloud.com/connect
    #https://api.soundcloud.com/oauth2/token
    #http://api.soundcloud.com/playlists/405726?client_id=YOUR_CLIENT_ID
    
    _api_root_ = "http://api.soundcloud.com/"
    _root_ = "http://soundcloud.com/"
    _playlists_ = _api_root_+"playlists/"
    _tracks_ = _api_root_+"tracks/"
    _resolve_ = _api_root_ + "resolve/"
    _end_ = "?client_id=" + CLIENT_ID

    def get_tracks_from_playlist(self,playlist_id):
        r_tracks = requests.get(self._playlists_ + str(playlist_id) + "?client_id=" + CLIENT_ID) 
        return json.loads(r_tracks.text)['tracks']

    def get_comments_from_track(self,track_id):
        r_comments = requests.get(self._tracks_ + str(track_id) + "/comments/?client_id=" + CLIENT_ID)
        return json.loads(r_comments.text)

    def get_comments_from_playlists(self,playlists):
        comments = []
        for playlist in playlists:
            tracks = self.get_tracks_from_playlist(playlist)
            for track in tracks:
                if track['sharing'] == 'public':
                    print(track['stream_url'])
                else:
                    print track['sharing']
                comments.append(self.get_comments_from_track(track['id']))
        return []

    def get_stream(self, track_id):
        r_track = requests.get(self._tracks_ + str(track_id) + "/stream?client_id=" + CLIENT_ID,stream=True) 
        if r_track.status_code == 200:
            f = open(str(track_id)+".mp3", 'wb')
            i = 0
            for chunk in r_track.iter_content(chunk_size=1024): 
                i+=1
                if chunk:
                    sys.stdout.write("Downloaded: %d bytes \r" % (1024*i) )
                    sys.stdout.flush()
                    f.write(chunk)
            f.close()
            song = AudioSegment.from_mp3(str(track_id) + ".mp3")
            song.export(str(track_id) + ".wav", format="wav")
            
            
        else:
            print("Unable to reach such file (" + str(track_id) + ").")

    def resolve_url(self, url):
        r_track = requests.get(self._resolve_ + "?url=" + url+"&client_id=" + CLIENT_ID)
        if r_track.status_code == 200 or r_track.status_code == 302:
            return json.loads(r_track.text)['id']
        else:
            print r_track
            raise Exception("unable to resolve url")
        
    def get_tracks_by_genre(self, genre):
        return
        
if __name__ == "__main__":
    sca = SoundCloudAnalyse()
    sca.get_stream("217399086")
    #~ print(sca.get_comments_from_playlists(["163424726"]))
    #~ print sca.resolve_url("https://soundcloud.com/adham-safena-1/fade-to-white")
