from flaskr.backend import Backend
from unittest.mock import patch, mock_open, MagicMock
import pytest


# TODO(Project 1): Write tests for Backend methods.
@patch("flaskr.backend.Backend.user_exists")
def test_signin_matchPassword(mock_user_exists):
    # we instanciate a mock so we can access its return value
    mock = MagicMock()
    # set the return value of a specific function
    mock.Client.return_value.bucket.return_value.blob.return_value.open.return_value.__enter__.return_value.read.return_value = "123"
    #mock.Client.return_value.bucket.return_value.blob.return_value.__enter__.return_value.read.__iter__.return_value = ["123"]
    # pass the mock as parameter
    mock_user_exists.return_value = True
    db = Backend(mock)
    assert db.sign_in("usuario", "123") == True


@patch("flaskr.backend.Backend.user_exists")
def test_signin_noMatchPassword(mock_user_exists):
    mock = MagicMock()
    mock.Client.return_value.bucket.return_value.blob.return_value.open.return_value.__enter__.return_value.read.return_value = "123"
    mock_user_exists.return_value = True
    db = Backend(mock)
    assert db.sign_in("usuario", "124") == False


@patch("flaskr.backend.Backend.user_exists")
def test_signin_userDoesntExists(mock_user_exists):
    # we instanciate a mock so we can access its return value
    mock = MagicMock()
    mock.Client.return_value.bucket.return_value.blob.return_value.open.return_value.__enter__.return_value.read.return_value = "123"
    mock_user_exists.return_value = False
    db = Backend(mock)
    assert db.sign_in("usuario", "123") == False


@patch("flaskr.backend.Backend.user_exists")
def test_sign_up_NewUserCreated(mock_user_exists):
    mock_user_exists.return_value = False
    mock = MagicMock()
    db = Backend(mock)
    assert db.sign_up("usuario", "123") == True


@patch("flaskr.backend.Backend.user_exists")
def test_sign_up_UserAlredyExists(mock_user_exists):
    mock_user_exists.return_value = True
    mock = MagicMock()
    db = Backend(mock)
    assert db.sign_up("usuario", "123") == False


class mock_blob:

    def __init__(self, n):
        self.name = n

    def open(self, mode):
        return mock_open(read_data="test comment")()


def test_user_exists():
    mock = MagicMock()
    blob = mock_blob("userName")
    mock.Client.return_value.list_blobs.return_value.__iter__.return_value = [
        blob
    ]
    db = Backend(mock)
    assert db.user_exists("userName") == True


def test_get_image():
    mock = MagicMock()
    expected_return = "image"
    mock.Client.return_value.bucket.return_value.blob.return_value.open.return_value.__enter__.return_value.read.return_value = expected_return
    db = Backend(mock)
    assert db.get_image("image.jpg") == expected_return


@patch("flaskr.backend.Backend.user_exists")
def test_add_comment(mock_user_exists):
    mock_user_exists.return_value = True
    mock = MagicMock()
    db = Backend(mock)
    db.add_comment("page1", "user1", "test comment")
    mock.Client.return_value.bucket.return_value.blob.return_value.upload_from_string.assert_called_once_with(
        "test comment")


def test_get_comments():
    mock = MagicMock()
    mock.Client.return_value.bucket.return_value.list_blobs.return_value = [
        mock_blob("page1/user1/2022-10-03_11-25-16")
    ]
    db = Backend(mock)
    comments = db.get_comments("page1")
    assert comments == [("user1", "2022-10-03_11-25-16", "test comment")]


def test_get_user_profile_picture_blob_exists():
    mock = MagicMock()
    mock.Client.return_value.bucket.return_value.blob.return_value.exists.return_value = True
    mock.Client.return_value.bucket.return_value.blob.return_value.generate_signed_url.return_value = "https://example.com/signed_url"
    db = Backend(mock)
    result = db.get_user_profile_picture("username")
    assert result == "https://example.com/signed_url"


def test_get_user_profile_picture_blob_doesnt_exist():
    mock = MagicMock()
    mock.Client.return_value.bucket.return_value.blob.return_value.exists.return_value = False
    db = Backend(mock)
    result = db.get_user_profile_picture("username")
    assert result == "https://storage.googleapis.com/author_images/Default.png"
