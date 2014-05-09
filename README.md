Desire2Login
============

Desire2Login is a local client with a simple GUI to check the status of classes hosted on the
desire2learn (D2L) platform.  Current support is simply the login protocols and a rough parse of HTML
to determine the number of unread emails, dropbox feedback, and discussions.

The program is targeted to automate checking for class updates at Regis University's deployment
of D2L, but it should be portable to other schools (use the current `urls.json` file as a template,
and swap icons in `config.json`).

It's a bit dirty coding, but was quick to meet a short term need.

Non-Standard Modules Required
-----------------------------

[keyring](https://pypi.python.org/pypi/keyring)
* Supports keyrings in Windows, OSX, Gnome, KDE (some non-standard as well)
