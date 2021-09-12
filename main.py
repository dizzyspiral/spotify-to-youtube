import sys
import csv
import argparse
from ytmusicapi import YTMusic

def load_spotify_playlist(playlist_file):
    songs = []

    with open(playlist_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in reader:
            songs.append("{} {}".format(row[1], row[3]))

    return songs

def search_for_songs(ytmusic, search_strings):
    video_ids = []

    for s in search_strings:
        result = ytmusic.search(s)
        try:
            video_ids.append(result[1]['videoId'])
        except:
            print("Unable to get video ID for song '{}'".format(s))

    return video_ids

def make_playlist(ytmusic, name, description):
    try:
        res = ytmusic.search(name, filter="playlists", scope="library")
        playlist_id = res[0]['browseId']
    except:
        playlist_id = ytmusic.create_playlist(name, description)

    return playlist_id

def add_songs(ytmusic, playlist_id, video_ids):
    skipped_songs = 0

    for video_id in video_ids:
        try:
            ytmusic.add_playlist_items(playlist_id, [video_id])
        except:
            skipped_songs += 1

    if skipped_songs > 0:
        print("Skipped adding {} songs (probably duplicates)".format(skipped_songs))

def add_likes(ytmusic, video_ids):
    for video_id in video_ids:
        ytmusic.rate_song(video_id, rating='LIKE')

def get_args():
    parser = argparse.ArgumentParser(description='Import a Spotify playlist to YouTube Music')
    parser.add_argument('auth', type=str, help='ytmusicapi auth file')
    parser.add_argument('file', type=str, help='Exported Spotify playlist CSV file')
    parser.add_argument('-p', '--playlist', type=str, help='Playlist name')
    parser.add_argument('-d', '--description', type=str, help='Playlist description', default="")
    parser.add_argument('-l', '--likes', action='store_true', help='Add songs to your liked songs instead of a YouTube Music playlist')

    args = parser.parse_args()

    if not args.playlist and not args.likes:
        parser.print_usage()
        print("Error: --playlist or --likes must be specified")
        sys.exit()

    if args.playlist and args.likes:
        parser.print_usage()
        print("Error: --playlist and --likes cannot both be specified")
        sys.exit()

    return args

if  __name__ == '__main__':
    args = get_args()

    print("Connecting to YouTube Music...")
    ytmusic = YTMusic(args.auth)
    print("Loading exported Spotify playlist...")
    songs = load_spotify_playlist(args.file)
    print("Searching for songs on YouTube...")
    video_ids = search_for_songs(ytmusic, songs)

    if args.likes:
        add_likes(ytmusic, video_ids)
    else:
        print("Creating playlist...")
        playlist_id = make_playlist(ytmusic, args.playlist, args.description)
        print("Adding songs...")
        add_songs(ytmusic, playlist_id, video_ids)

    print("Done!")
