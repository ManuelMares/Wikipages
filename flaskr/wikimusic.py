import requests
import base64
from requests import post
import json


def get_wikipedia_articles(songName, r=requests):
    articles = f'https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&inprop=url&utf8=&format=json&srlimit=20&srsearch={songName}&origin=*'
    req = r.get(articles).json()
    articles = []
    for options in req['query']['search']:
        articles.append(get_wikipedia_article(options["title"]))
    return articles


def get_wikipedia_article(search, r=requests):
    fullSearch = "https://en.wikipedia.org/w/api.php?action=query&titles=" + search + "&prop=extracts|pageimages|info&pithumbsize=400&inprop=url&redirects=&format=json&origin=*"
    request = r.get(fullSearch).json()
    articles = {}
    for key, value in request['query']['pages'].items():
        articles["title"] = value["title"]
        articles["extract"] = value["extract"]
        articles["fullurl"] = value["fullurl"]
    return articles


def get_iframe_spotify_songs(songName, artist, r=requests):
    token = _getToken()
    search = f"https://api.spotify.com/v1/search?q=track:{songName}%20artist:{artist}&type=track"
    headers = {"Authorization": "Bearer " + token}
    result = r.get(search, headers=headers).json()

    if len(result["tracks"]["items"]) == 1:
        return f'<iframe src="https://open.spotify.com/embed?uri=spotify:track:{result["tracks"]["items"][0]["id"]}" class="spotify_song" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    else:
        answer = ""
        for index in range(min(len(result["tracks"]["items"]), 5)):
            answer += f'<iframe src="https://open.spotify.com/embed?uri=spotify:track:{result["tracks"]["items"][index]["id"]}" class="spotify_song" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
        return answer


def _getToken():
    clientId = 'cf411c3a8a534946a579f1497e786401'
    clientSecret = 'acf2d5debbd04a61914ab089877b7835'
    auth_string = clientId + ":" + clientSecret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token
