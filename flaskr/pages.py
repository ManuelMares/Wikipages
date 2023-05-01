from flask import render_template, redirect, url_for
from flask import request
from flaskr.backend import Backend
import hashlib
import os
from google.cloud import storage
from .wikimusic import get_wikipedia_articles, get_iframe_spotify_songs


def make_endpoints(app):
    loggedIn = False
    db = Backend()
    sessionUserName = ""

    @app.context_processor
    def inject_now():
        """
        This variables are known are send to all templated when used.
        Their value cannot be modified. Instead, we use a condition to decide
        what value to send.
        """
        if loggedIn:
            return {'loggedIn': True, "userName": sessionUserName}
        else:
            return {'loggedIn': False, "userName": ""}

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/home", methods=["GET"])
    @app.route("/", methods=["GET"])
    def home():
        nonlocal loggedIn
        nonlocal sessionUserName
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return render_template("home.html")

    @app.route("/<usr>")
    def user(usr, pwd):
        nonlocal loggedIn
        nonlocal sessionUserName
        # TODO(Checkpoint Requirement 2 of 3): Change this to use render_template
        # to render main.html on the home page.
        return f"<h1>{usr}</h1> <h2>{pwd}<h2>"

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        nonlocal loggedIn
        nonlocal sessionUserName

        if request.method == "POST":

            if "pfpUpload" in request.files:
                uploaded_pfp = request.files["pfpUpload"]
                if uploaded_pfp.filename != "":
                    uploaded_pfp.save(
                        os.path.join('flaskr/static/avatars',
                                     sessionUserName + ".png"))
                    db.upload_profile_picture(
                        os.path.relpath("flaskr/static/avatars/" +
                                        sessionUserName + ".png"),
                        sessionUserName)

            if "bioUpload" in request.form:
                uploaded_bio = request.form["bioUpload"]
                db.upload_user_bio(uploaded_bio, sessionUserName)

            profile_picture = db.get_user_profile_picture(sessionUserName)
            bio = db.get_user_bio(sessionUserName)
            recently_viewed = db.get_recently_viewed(sessionUserName)
            return render_template("profile.html",
                                   profile_pic=profile_picture,
                                   profile_bio=bio,
                                   recent=recently_viewed)

        profile_picture = db.get_user_profile_picture(sessionUserName)
        bio = db.get_user_bio(sessionUserName)
        recently_viewed = db.get_recently_viewed(sessionUserName)
        return render_template("profile.html",
                               profile_pic=profile_picture,
                               profile_bio=bio,
                               recent=recently_viewed)

    # uses backend to obtain list of wiki content, sends that list when rendering pages.html

    @app.route("/pages", methods=["GET"])
    def pages(page=None):
        nonlocal loggedIn
        nonlocal sessionUserName
        pages = db.get_all_page_names()
        return render_template("pages.html", listPages=pages, page=page)

    # uses backend to obtain content of a certain page, sends the content when rendering pages.html
    @app.route("/pages/<path>", methods=["GET", "POST"])
    def current_page(path):
        nonlocal loggedIn
        nonlocal sessionUserName
        page = db.get_wiki_page(path)

        # Handle comment submission
        if request.method == "POST":
            comment = request.form["comment"]
            db.add_comment(path, sessionUserName, comment)
            return redirect(url_for('current_page', path=path))

        # Get existing comments for the page
        comments = db.get_comments(path)
        return render_template('pages.html', page=page, comments=comments)

    @app.route("/about")
    def about():
        nonlocal loggedIn
        nonlocal sessionUserName
        return render_template("about.html")

    @app.route("/logout")
    def logout():
        nonlocal loggedIn
        nonlocal sessionUserName
        loggedIn = False
        return redirect(url_for('home'))

    @app.route("/login", methods=["POST", "GET"])
    def login():
        nonlocal loggedIn
        nonlocal sessionUserName
        if request.method == "POST":
            user = request.form["nm"]
            password = hashlib.blake2b(request.form["pwd"].encode()).hexdigest()

            if db.sign_in(user, password):
                loggedIn = True
                sessionUserName = user
                return redirect(url_for('home'))
            else:
                return render_template("login.html", error=True)
        else:
            return render_template("login.html", error=False)

    @app.route("/signup", methods=["POST", "GET"])
    def signup():
        nonlocal loggedIn
        nonlocal sessionUserName
        if request.method == "POST":
            user = request.form["nm"]
            password = hashlib.blake2b(request.form["pwd"].encode()).hexdigest()
            if db.sign_up(user, password):
                loggedIn = True
                sessionUserName = user
                return redirect(url_for('home'))
            else:
                return render_template("signup.html", error=True)
        else:
            return render_template("signup.html", error=False)

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        client = storage.Client()
        if request.method == "POST":
            file = request.files["fileUpload"]
            filename = file.filename
            blob = client.bucket("group_wiki_content").blob(filename)
            blob.upload_from_file(file)
            return render_template("upload.html",
                                   message="File uploaded successfully.")
        return render_template("upload.html")

    @app.route("/delete_comment", methods=["POST"])
    def delete_comment():
        page_name = request.form["page_name"]
        username = request.form["username"]
        datetime_str = request.form["datetime_str"]

        # must wait for backend method in order to work
        success = db.delete_comment(page_name, username, datetime_str)
        if success:
            return "Comment deleted successfully", 200
        else:
            return "Failed to delete comment", 400

    @app.route("/wikimusic", methods=["GET", "POST"])
    def wikiAPIRequest():
        if request.method == "POST":
            songname = request.form["songname"]
            artist = request.form["artist"]
            if songname == "" or artist == "":
                return render_template("wikimusic_notfound.html")

            iframes = get_iframe_spotify_songs(songname, artist)
            articles = get_wikipedia_articles(songname + " " + artist)

            if len(articles) == 0:
                return render_template("wikimusic_notfound.html")
            else:
                return render_template("WikiMusicAnswer.html",
                                       articles=articles,
                                       iframes_spotify=iframes)
        else:
            return render_template("WikiMusicStart.html")
