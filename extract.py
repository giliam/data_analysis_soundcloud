#coding:utf8
import requests
import csv
import json

from secret_data import CLIENT_ID, CLIENT_SECRET

class SoundCloudAnalyse:
    #https://soundcloud.com/connect
    #https://api.soundcloud.com/oauth2/token
    # http://api.soundcloud.com/playlists/405726?client_id=YOUR_CLIENT_ID

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
                comments.append(self.get_comments_from_track(track['id']))
        return comments


if __name__ == "__main__":
    sca = SoundCloudAnalyse()
    print(sca.get_comments_from_playlists(["163043603"]))
