## Maps the [sofascore](https://www.sofascore.com/de/) rating to [comunio](https://www.comunio.de/home) players
[![Build Status](https://travis-ci.org/bierschi/ComunioScore.png?branch=master)](https://travis-ci.org/bierschi/ComunioScore) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
- get live points from your comunio players
- website to visualize rating, points and different statistics from your comunio players
- messenger integration to share it in groups chat with friends


## Installation

install package from source with
<pre><code>
sudo python3 setup.py install
</code></pre>

## Usage

edit the `comunioscore.ini` file with credentials for comunio and postgres database:
<pre><code>
[comunio]
username=
password=

[database]
host=
port=
username=
password=
dbname=

[comunioscore]
schema=comunioscore
table_auth=auth
table_communityuser=communityuser
table_squad=squad
table_season=season

[telegram]
token=
</code></pre>

execute the console script
<pre><code>
ComunioScoreApp
</code></pre>

or start the systemd service file
<pre><code>
sudo systemctl start ComunioScoreApp.service
</code></pre>

## Deployment on server

create a wheel for server deployment
<pre><code>
sudo python3 setup.py bdist_wheel
</code></pre>

install wheel with
<pre><code>
pip3 install ComunioScore-1.0.0-py3-none-any.whl
</code></pre>

uninstall wheel with
<pre><code>
pip3 uninstall ComunioScore
</code></pre>

## Troubleshooting
add your current user to group `syslog`, this allows the application to create a folder in
`/var/log`. Replace `<user>` with your current user
<pre><code>
sudo adduser &lt;user&gt; syslog
</code></pre>
to apply this change, log out and log in again and check with the command `groups`

## Changelog
All changes and versioning information can be found in the [CHANGELOG](https://github.com/bierschi/ComunioScore/blob/master/CHANGELOG.rst)

## License
Copyright (c) 2019 Bierschneider Christian. See [LICENSE](https://github.com/bierschi/ComunioScore/blob/master/LICENSE)
for details
