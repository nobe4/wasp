# WASP Challenge

> Perfectly insecure web application that sting !

This challenge was written for a [London Sectalks](http://www.sectalks.org/london/) event organised in July 2017.

You can find a fully-working docker-compose file in `docker-compose.yml`, you only need to run `docker-compose up` to run it.

If you want to roll this on a server/VM, I recommend a Debian 8, and the `setup.sh` script should be able to install everything needed.

**The README is heavily spoiling the challenge, don't look at it if you want to try to solve the challenge !**

# How does it work?

The application is a simple [Flask](http://flask.pocoo.org/) server, using [SQLAlchemy](http://www.sqlalchemy.org/) for the database interactions. 

There is a [MySQL](https://www.mysql.com/) server running and an [nginx](https://www.nginx.com/) proxy configured.

A [phantom.js](http://phantomjs.org/) bot will look at flagged posts and mark them as checked every 5 seconds.

If you want to customize it, look at `.env` which contains most of the key data for the challenge config.

# Challenge setup

```
Good evening fellow hackers, your task is simple: find the password used by the user "sectalk" to register on the website.

What you need:
- A web browser
- Some programming knowledge
- Your brain

What you don't need:
- Scan the application
- Bruteforce the application
- Spam the application
(seriously, you don't need that)

The challenge lives here: http://HOSTNAME:PORT/
Using `user`/`th1s1ss0s3c_r3` to auth.
```

# Where to look? (aka the interesting pieces)

To create the challenge I had to manually add vulnerabilities to the code, here is a list of the places where I put a vulnerability:

- `web/templates/post.html` l1 and `web/templates/home.html` l16

This is the first vulnerability the user will see. The [`safe` filter](http://jinja.pocoo.org/docs/2.9/templates/#html-escaping) will let the content of the post to be display verbatim on the web page. This is useful if you want to include images, videos, ... But can also cause horrible security issues if you don't check for malicious scripts, for more information look at the [OWASP XSS wiki](https://www.owasp.org/index.php/Cross-site_Scripting_(XSS)).

- `web/server.py` l152 and l141

This one is more subtle, it's using a `GET` request parameter as a verification token to do some admin stuff. Because of the previous vulnerability, the keys can be extracted if a user can see an incoming request from the admin (namely using the [`referer`](https://en.wikipedia.org/wiki/HTTP_referer) header of the `HTTP` request). For this challenge, the keys are ~unique, but still, this is giving away a lot of information.

- `phantom/phantom.js` l15-27 and `web/server.py` l99-136

Without knowing a way to generate the admin key, the previous vulnerability can't lead to any further exploitations, but it's using an custom-made "cryptographic" key. [Never use your own cryptographic function](https://security.stackexchange.com/a/18198). For this exercise it was possible to reverse the process, quite easily as long as you could generate multiple keys (you would see at some point the number wrapping around at 999).

- `web/server.py` l173-178

This one is maybe the worst of all, it's a typical [SQL Injection](https://www.owasp.org/index.php/SQL_injection). By looking around the `post_id` of the request, you could inject you own commands in the SQL engine directly, and giving access to the whole database.

- `web/models.py` l19

While storing plaintext passwords is a [very-very bad idea](https://stackoverflow.com/a/1054033/2558252) using a function as "simple" as MD5 is quite adventurous. [There](https://crackstation.net/) [are](https://md5.gromweb.com/) [numerous](http://reversemd5.com/) [websites](https://isc.sans.edu/tools/reversehash.html) that provides a `md5` reverse lookup service. In the case of this challenge, the password is so simple than any of these tools will find it.

# Results

It was a really fun challenge to run and to create, the `XSS` flaws was clearly going to cause users to mess with other's people browser, and the story tells that everybody in the room got RickRolled!

While looking at the logs and restarting the server from time to time, we discovered some unknown issues:

1. If you inject something like `<script>while(1){}</script>` it will make the phantomjs bot hang, trapped in the loop.
2. You can create multiple users with the same username.
3. You can make the login/signup form crash if you pass too much data in the fields.

# Leaderboard

1. [taw](https://github.com/taw)
2. [blinken](https://github.com/blinken) & [npny](https://github.com/npny)
