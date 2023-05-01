from unittest.mock import patch, mock_open, MagicMock
import pytest
from .wikimusic import get_wikipedia_articles, get_wikipedia_article, get_iframe_spotify_songs


@patch("flaskr.wikimusic.get_wikipedia_article")
def test_get_wikipedia_articles(mock_get_wikipedia_article):
    mock = MagicMock()
    mock.get.return_value.json.return_value = {
        "query": {
            "search": [{
                "title": "new song"
            }]
        }
    }
    mock_get_wikipedia_article.return_value = "new article"
    articles = get_wikipedia_articles("black bird", mock)
    print(articles)
    assert articles == ["new article"]


def test_get_wikipedia_article():
    mock = MagicMock()
    mock.get.return_value.json.return_value = {
        "query": {
            "pages": {
                "articles": {
                    "title": "article1",
                    "extract": "body of article",
                    "fullurl": "article.com"
                }
            }
        }
    }

    articles = get_wikipedia_article("black bird", mock)

    assert articles == {
        'title': 'article1',
        'extract': 'body of article',
        'fullurl': 'article.com'
    }


@patch("flaskr.wikimusic._getToken")
def test_get_iframe_spotify_songs_case1(mock__getToken):
    mock = MagicMock()
    mock.get.return_value.json.return_value = {
        "tracks": {
            "items": {
                0: {
                    "id": "song1"
                }
            }
        }
    }

    iframes = get_iframe_spotify_songs("black bird", "beatles", mock)

    assert iframes == '<iframe src="https://open.spotify.com/embed?uri=spotify:track:song1" class="spotify_song" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'


@patch("flaskr.wikimusic._getToken")
def test_get_iframe_spotify_songs_case2(mock__getToken):
    mock = MagicMock()
    mock.get.return_value.json.return_value = {
        "tracks": {
            "items": {
                0: {
                    "id": "song1",
                    "id": "song2",
                    "id": "song3",
                    "id": "song4",
                    "id": "song5",
                    "id": "song6"
                }
            }
        }
    }

    iframes = get_iframe_spotify_songs("black bird", "beatles", mock)
    answer = '<iframe src="https://open.spotify.com/embed?uri=spotify:track:song6" class="spotify_song" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>'
    assert iframes == answer
