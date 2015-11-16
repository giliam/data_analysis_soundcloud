#coding:utf8
import requests
import csv
import json
import shutil
from secret_data import CLIENT_ID, CLIENT_SECRET

class SoundCloudAnalyse:
    #https://soundcloud.com/connect
    #https://api.soundcloud.com/oauth2/token
    #http://api.soundcloud.com/playlists/405726?client_id=YOUR_CLIENT_ID

    def get_tracks_from_playlist(self,playlist_id):
        r_tracks = requests.get("http://api.soundcloud.com/playlists/" + str(playlist_id) + "?client_id=" + CLIENT_ID) 
        return json.loads(r_tracks.text)['tracks']

    def get_comments_from_track(self,track_id):
        r_comments = requests.get("http://api.soundcloud.com/tracks/" + str(track_id) + "/comments/?client_id=" + CLIENT_ID)
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
        r_track = requests.get("http://api.soundcloud.com/tracks/" + str(track_id) + "/stream?client_id=" + CLIENT_ID,stream=True) 
        if r_track.status_code == 200:
            with open("test.wav", 'wb') as f:
                for chunk in r_track.iter_content(chunk_size=1024): 
                    if chunk:
                        f.write(chunk)
        else:
            print("Unable to reach such file (" + str(track_id) + ").")


if __name__ == "__main__":
    sca = SoundCloudAnalyse()
    sca.get_stream("228081985")
    print(sca.get_comments_from_playlists(["163424726"]))
