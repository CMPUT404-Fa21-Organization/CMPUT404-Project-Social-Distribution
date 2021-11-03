# CMPUT404-Project-Social-Distribution

## Team members
* jinzhou
* kar3
* mparasha
* poulomi
* xinjian

## Description of Project

The web is fundamentally interconnected and peer to peer. There’s no really great reason why we should all use facebook.com or google+ or myspace or something like that. If these social networks came up with an API you could probably link between them and use the social network you wanted. Furthermore you might gain some autonomy.

Thus in the spirit of diaspora https://diasporafoundation.org/ we want to build something like diaspora but far far simpler.

This blogging/social network platform will allow the importing of other sources of posts (github, twitter, etc.) as well allow the distributing sharing of posts and content.

An author sitting on one server can aggregate the posts of their friends on other servers.

We are going to go with an inbox model where by you share posts to your friends by sending them your posts. This is similar to activity pub: https://www.w3.org/TR/activitypub/ Activity Pub is great, but too complex for a class project.

We also won’t be adding much in the way of encryption or security to this platform. We’re keeping it simple and restful.

## Model Names

* Author
* Like
* Liked
* Followers
* Inbox
* Post

## Architecture

* Backend: SQLite3 and Django
* Frontend: Bootstrapped CSS & HTML

## References

* https://www.youtube.com/watch?v=tUqUdu0Sjyc - Login and authentication
* https://realpython.com/django-redirects/ - Redirects
* https://www.w3docs.com/snippets/html/how-to-display-base64-images-in-html.html - Displaying base64 images
* https://openclassrooms.com/en/courses/7107341-intermediate-django/7265468-create-many-to-many-relationships - Many to many relationships
* https://stackoverflow.com/questions/63135702/django-automatic-logout-and-and-after-login-it-stays-on-same-page

## Technical sources

* https://docs.djangoproject.com
* https://www.django-rest-framework.org/
* https://getbootstrap.com/docs/5.0/getting-started/introduction/
* https://docs.github.com/en/rest/reference/activity
* https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
* https://django-markdownify.readthedocs.io/en/latest/index.html
