## Maps the [sofascore](https://www.sofascore.com/de/) rating to [comunio](https://www.comunio.de/home) players
[![Build Status](https://travis-ci.org/bierschi/ComunioScore.png?branch=master)](https://travis-ci.org/bierschi/ComunioScore) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
- get live points from your comunio players
- website to visualize rating, points and different statistics from your comunio players
- messenger integration to share it in groups chat with friends


## Installation

install [ComunioScore](https://pypi.org/project/ComunioScore/) with pip
<pre><code>
pip3 install ComunioScore
</code></pre>

or from source
<pre><code>
sudo python3 setup.py install
</code></pre>


## Usage and Examples

Print the available arguments for ComunioScore
<pre><code>
ComunioScore --help
</code></pre>

Use it with pure command line arguments
<pre><code>
ComunioScore args --host 127.0.0.1 --port 8086 --dbhost 127.0.01 --dbport 5432 --dbuser john --dbpassword jane --dbname comunioscore --comunio_user john --comunio_pass jane --token adfefad
</code></pre>

Or with a configuration file
<pre><code>
ComunioScore config --file /etc/comunioscore/comunioscore.ini
</code></pre>


edit the `comunioscore.ini` file and add credentials from comunio and postgres database:
<pre><code>
[comunio]
username=
password=

[database]
host=
port=5432
username=
password=
dbname=

[server]
host='0.0.0.0'
port=8086

[telegram]
token=
</code></pre>


## Build Debian package

change into directory `dist_package` and execute:
<pre><code>
./build_package.sh --debian
</code></pre>

## Logs

logs can be found in `/var/log/ComunioScore`

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
