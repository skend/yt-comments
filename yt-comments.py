import os
import json
import sys

import googleapiclient.discovery


users = set()
MIN_SUB_COUNT = 5000


def get_api_key():
    with open("client_secrets.json") as f:
        data = json.load(f)
        return data['API_KEY']
    return None


def get_video_code():
    if len(sys.argv) < 2:
        print('Provide a YouTube URL')
        print('Example:')
        print('python yt-comments.py https://www.youtube.com/watch?v=auBBkqWvFL4')
        exit(-1)
    else:
        return sys.argv[1][32:]


def main():
    video_code = get_video_code()
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = get_api_key()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    send_request(youtube, video_code)
    check_channels(youtube)


def check_channels(youtube):
    print('Checking channels')
    for user in users:
        request = youtube.channels().list(
            part="snippet,statistics",
            id=user
        )
        response = request.execute()
        for item in response['items']:
            if 'subscriberCount' in item['statistics'] and int(item['statistics']['subscriberCount']) > MIN_SUB_COUNT:
                print(item['snippet']['title'] + ' --- ' + item['statistics']['subscriberCount'])
    

def send_request(youtube, video_code, pageToken=None):
    print('Retrieving comment page')
    request = youtube.commentThreads().list(
        part="snippet",
        maxResults=100,
        videoId=video_code,
        pageToken=pageToken
    )
    response = request.execute()

    for item in response['items']:
        topLevelComment = item['snippet']['topLevelComment']
        if item['id'] == topLevelComment['id'] and \
             topLevelComment['snippet']['textOriginal'][0] != '@':
            users.add(topLevelComment['snippet']['authorChannelId']['value'])
    
    if 'nextPageToken' in response:
        send_request(youtube, video_code, response['nextPageToken'])


if __name__ == "__main__":
    main()