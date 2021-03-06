# CMPUT404-Project-Social-Distribution

## Team members
* jinzhou
* kar3
* mparasha
* poulomi
* xinjian
* bholm

## Description of Project

The web is fundamentally interconnected and peer to peer. There’s no really great reason why we should all use facebook.com or google+ or myspace or something like that. If these social networks came up with an API you could probably link between them and use the social network you wanted. Furthermore you might gain some autonomy.

Thus in the spirit of diaspora https://diasporafoundation.org/ we want to build something like diaspora but far far simpler.

This blogging/social network platform will allow the importing of other sources of posts (github, twitter, etc.) as well allow the distributing sharing of posts and content.

An author sitting on one server can aggregate the posts of their friends on other servers.

We are going to go with an inbox model where by you share posts to your friends by sending them your posts. This is similar to activity pub: https://www.w3.org/TR/activitypub/ Activity Pub is great, but too complex for a class project.

We also won’t be adding much in the way of encryption or security to this platform. We’re keeping it simple and restful.

## Installation and local deployment instructions:

1. Clone repository `git clone https://github.com/CMPUT404-Fa21-Organization/CMPUT404-Project-Social-Distribution.git`
2. Move to project directory with `cd CMPUT404-Project-Social-Distribution.git`
3. Create a virtual env with `virtualenv venv --python=python3` and activate it using `source venv/bin/activate`
4. Install requirements after `cd CMPUT404Project` with `pip install -r requirements.txt`
5. Run `python manage.py makemigrations` and `python manage.py migrate` to make migrations.
6. To run locally, run `python manage.py runserver` and view site on 127.0.0.1:8000/

## API Documentation (WIP)

Can be found on [Wiki -> API Documentation](https://github.com/CMPUT404-Fa21-Organization/CMPUT404-Project-Social-Distribution/wiki/API-Documentation)

## Model Names

* Author
* Like
* Liked
* Followers
* FriendRequest
* Inbox
* Post
* Comment

## Architecture

* Backend: SQLite3 and Django
* Frontend: Bootstrapped CSS & HTML

## References

* https://www.youtube.com/watch?v=tUqUdu0Sjyc - Login and authentication
* https://realpython.com/django-redirects/ - Redirects
* https://www.w3docs.com/snippets/html/how-to-display-base64-images-in-html.html - Displaying base64 images
* https://openclassrooms.com/en/courses/7107341-intermediate-django/7265468-create-many-to-many-relationships - Many to many relationships
* https://stackoverflow.com/questions/63135702/django-automatic-logout-and-and-after-login-it-stays-on-same-page
* https://stackoverflow.com/questions/53594745/what-is-the-use-of-cleaned-data-in-django
* [Add actions to admin panel](https://simpleisbetterthancomplex.com/tutorial/2017/03/14/how-to-create-django-admin-list-actions.html)
* [Restrict server access to admin approved users](https://stackoverflow.com/questions/49553511/why-authenticate-return-none-for-inactive-users)
* [Adding flags/tags to Toast messages](https://docs.djangoproject.com/en/3.2/ref/contrib/messages/#adding-extra-message-tags)

## Technical sources

* https://docs.djangoproject.com
* https://www.django-rest-framework.org/
* https://getbootstrap.com/docs/5.0/getting-started/introduction/
* https://docs.github.com/en/rest/reference/activity
* https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
* https://django-markdownify.readthedocs.io/en/latest/index.html
