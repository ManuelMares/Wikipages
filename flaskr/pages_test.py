from flaskr import create_app
import pytest
from unittest.mock import patch, mock_open, MagicMock
from flask import request
import json


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.


def integration_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome to our Wiki!" in resp.get_data()
    resp = client.get("/home")
    assert resp.status_code == 200
    assert b"Welcome to our Wiki!" in resp.get_data()


# TODO(Project 1): Write tests for other routes.
def integration_home_signup(client):
    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b"Create an account" in resp.get_data()


def integration_home_login(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log in" in resp.get_data()


def integration_upload(client):
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"Select a file to upload:" in resp.get_data()


def integration_about(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"Welcome to our Wiki!" in resp.get_data()


def integration_wiki_list(client):
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"Pages contained in this Wiki" in resp.get_data()


def integration_wiki_page(client):
    resp = client.get("/pages/Super%20Mario%20Kart")
    assert resp.status_code == 200
    assert b"Super Mario Kart[a] is a kart racing game developed and published by Nintendo" in resp.get_data(
    )


def integration_current_page(client):
    resp = client.get('/pages/Super%20Mario%20Kart')
    assert resp.status_code == 200
    assert b'Super Mario Kart[a] is a kart racing game developed and published by Nintendo' in resp.data

    resp = client.post('/pages/Super%20Mario%20Kart',
                       data={'comment': 'This is a test comment.'},
                       follow_redirects=True)

    # Check that the response status code is 200 and the comment is displayed in the page content
    assert resp.status_code == 200
    assert b'This is a test comment.' in resp.data


def integration_current_page_comment(client):
    # Test for an existing page
    existing_page_path = "Sample_Page"
    resp = client.get(f"/pages/{existing_page_path}")
    assert resp.status_code == 200
    assert b"Sample page content" in resp.get_data()

    # Test comment submission
    comment_text = "This is a test comment."
    resp = client.post(f"/pages/{existing_page_path}",
                       data={"comment": comment_text},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert bytes(comment_text, encoding='utf-8') in resp.get_data()


def integration_wiki_wikimusic_startpage(client):
    resp = client.get("/wikimusic")
    assert resp.status_code == 200
    assert b"(Re)search for a song!" in resp.get_data()


def integration_wiki_wikimusic_post_Correct(client):
    resp = client.post("/wikimusic",
                       data={
                           "artist": "beatles",
                           "songname": "yesterday"
                       })
    print(resp)
    assert resp.status_code == 200
    assert b"Yesterday (Beatles song)" in resp.get_data()


def integration_wiki_wikimusic_post_EmptyAnswer(client):
    resp = client.post("/wikimusic", data={"artist": "", "songname": ""})
    print(resp)
    assert resp.status_code == 200
    assert b"SONG NOT FOUND" in resp.get_data()
