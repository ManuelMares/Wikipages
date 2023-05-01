# TODO(Project 1): Implement Backend according to the requirements.
from datetime import timezone, datetime
from google.oauth2 import service_account
from datetime import datetime
import json
import os

from google.cloud import storage
from google.cloud.storage.blob import Blob


class Backend:

    def __init__(self, st=storage):

        with open('google_cloud_auth.json') as source:
            info = json.load(source)

        storage_credentials = service_account.Credentials.from_service_account_info(
            info)

        self.storage_client = st.Client(credentials=storage_credentials)

        self.bucketName_content = "group_wiki_content"
        self.bucketName_users = "users_and_passwords"
        self.bucketName_images = "author_images"
        self.bucketName_comments = "comment--bucket"
        self.bucketName_profile_pictures = "wiki_viewer_user_data"

        self.bucket_content = self.storage_client.bucket(
            self.bucketName_content)
        self.bucket_users = self.storage_client.bucket(self.bucketName_users)
        self.bucket_images = self.storage_client.bucket(self.bucketName_images)
        self.bucket_comments = self.storage_client.bucket(
            self.bucketName_comments)
        self.bucket_profile_pictures = self.storage_client.bucket(
            self.bucketName_profile_pictures)

        # self.readContent = opener
        # self.writeContent = opener
        # self.readUser = opener
        # self.writeUser = opener

    def get_user_profile_picture(self, username):
        blob = self.bucket_profile_pictures.blob("profile_pictures/" + username)
        blob.content_type = "image/png"
        url_lifetime = int(datetime.now(tz=timezone.utc).timestamp()) + 3600
        if blob.exists():
            return blob.generate_signed_url(expiration=url_lifetime,
                                            method="GET")
        else:
            return "https://storage.googleapis.com/author_images/Default.png"

    def upload_profile_picture(self, path, name):
        blob = self.bucket_profile_pictures.blob("profile_pictures/" + name)
        blob.content_type = "image/png"
        blob.cache_control = 0
        blob.upload_from_filename(path)

    def get_user_bio(self, username):
        blob = self.bucket_profile_pictures.blob("bios/" + username)
        if blob.exists():
            with blob.open("r") as f:
                return (f.read())
        else:
            return None

    def upload_user_bio(self, text, name):
        blob = self.bucket_profile_pictures.blob("bios/" + name)
        blob.cache_control = 0
        with blob.open("w") as user:
            user.write(text)

    def get_wiki_page(self, name):
        """ This method gets the content of a given wiki page from the content bucket.

        Args:
            name: A string corresponding to the name of the wiki page (txt file).

        Returns:
            The content of the wiki page as a string.
        """
        blob = self.bucket_content.blob(name + ".txt")
        with blob.open("r") as f:
            return (f.read())

    def get_all_page_names(self):
        pages = []
        blobs = self.storage_client.list_blobs(self.bucketName_content)
        for blob in blobs:
            pages.append(blob.name[:len(blob.name) - 4])
        return pages

    def upload(self, content, name):
        """This method uploads the content of a wiki page to the content bucket.

        Args:
            content: A string corresponding to the content of the wiki page.
            name: A string corresponding to the name of the wiki page.
        """
        blob = self.bucket_content.blob(name)
        blob.upload_from_file(content)
        # with blob.open("w") as f:
        #     f.write(content)

    def sign_up(self, username, password):
        """This methods checks that a given the user matches the hashed password in bucket_users.

        Attributes:
            username: string indicading the blob to look for.
            password: A string corresponding to the content of the blob.

        Returns:
            A boolean value indicating if the hashed password matches the user
        """
        if self.user_exists(username):
            return False

        blob = self.bucket_users.blob(username)
        # with self.writeUser( blob, "w") as f:
        with blob.open("w") as f:
            f.write(password)
        return True

    def user_exists(self, username):
        """This methods checks if an user exists in the data base in bucket_users.

        Attributes:
            username: A string indicading the blob to look for.

        Returns:
            A boolean value that indicates if the username is already registered.
        """
        blobs = self.storage_client.list_blobs(self.bucketName_users)

        for blob in blobs:
            if blob.name == username:
                return True
        return False

    def sign_in(self, username, password):
        """ This method adds a new user to the users and passwords bucket.

        Args:
            username: string corresponding to the username of the new user.
            password: A string corresponding to the hashed password of the new user.

        Returns:
            A boolean value indicating if the user was successfully added.
        """
        if not self.user_exists(username):
            return False

        blobUsers = self.bucket_users.blob(username)

        # compare passwords
        with blobUsers.open("r") as f:
            blobPassword = f.read()
            # for line in blobPassword:
            if blobPassword == password:
                return True
        return False

    def get_image(self, imageName):
        """ This method retrieves the image with the given image name from the author_images bucket.

        Args:
            imageName: A string corresponding to the name of the image to retrieve.

        Returns:
            an object representing the image file.
        """

        blob = self.bucket_images.blob(imageName)
        image = None
        with blob.open("r") as f:
            image = f.read()
        return image

    def add_comment(self, page_name, username, comment):
        """
        Add a comment to the comments bucket for the specified wiki page.

        Args:
            page_name: A string corresponding to the name of the wiki page.
            username: A string corresponding to the name of the user.
            comment: A string corresponding to the comment to be added.

        Returns:
            None.
        """
        blob_name = f"{page_name}/{username}/{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}.txt"
        blob = self.bucket_comments.blob(blob_name)
        blob.upload_from_string(comment)

    def get_comments(self, page_name):
        """
        Retrieve comments from the comments bucket for the specified wiki page.

        Args:
            page_name: A string corresponding to the name of the wiki page.

        Returns:
            A list of tuples containing the username and comment text.
        """
        blobs = self.bucket_comments.list_blobs(prefix=page_name)
        comments = []
        for blob in blobs:
            username, datetime_str = blob.name[len(page_name) + 1:].split("/")
            with blob.open("r") as f:
                comment = f.read()
                comments.append((username, datetime_str, comment))
        return comments

    def delete_comment(self, page_name, username, datetime_str):
        """
        Delete a comment from the comments bucket for the specified wiki page.

        Args:
            page_name: A string corresponding to the name of the wiki page.
            username: A string corresponding to the name of the user who posted the comment.
            datetime_str: A string corresponding to the timestamp of the comment.

        Returns:
            A boolean indicating whether the deletion was successful.
        """
        blob_name = f"{page_name}/{username}/{datetime_str}"
        blob = self.bucket_comments.blob(blob_name)
        if not blob.exists():
            return False

        blob.delete()
        return True

    def get_recently_viewed(self, username):
        blob = self.bucket_profile_pictures.blob("recently_viewed/" + username)
        blob.content_type = ".json"

        if blob.exists():
            with blob.open("r") as recent:
                data = json.load(recent)
                print(data)
                recent.close()
            return [
                data["Recent"]["First"], data["Recent"]["Second"],
                data["Recent"]["Third"]
            ]
        else:
            blob.cache_control = 0
            blob.upload_from_filename("flaskr/static/default/recent.json")
            return ["None", "None", "None"]

    def update_recent(self, page, username):
        blob = self.bucket_profile_pictures.blob("recently_viewed/" + username)
        blob.content_type = ".json"

        with blob.open("r") as recent:
            data = json.load(recent)
            recent.close()

        data["Recent"]["Third"] = data["Recent"]["Second"]
        data["Recent"]["Second"] = data["Recent"]["First"]
        data["Recent"]["First"] = page

        with blob.open("w") as recent:
            recent.write(json.dumps(data))
            recent.close()
