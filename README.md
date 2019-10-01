## Maps the [sofascore](https://www.sofascore.com/de/) rating to [comunio](https://www.comunio.de/home) players
[![Build Status](https://travis-ci.org/bierschi/ComunioScore.png?branch=master)](https://travis-ci.org/bierschi/ComunioScore) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
- get live points from your comunio players
- website to visualize rating, points and different statistics from your comunio players
- messenger integration to share it in groups chat with friends

## Installation

install from source with
<pre><code>
sudo python3 setup.py install
</code></pre>

## Usage

edit the `comunioscore.ini` file with credentials for comunio and database:
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

[comunioscore_database]
schema=comunioscore
table_communityuser=communityuser
table_squad=squad
</code></pre>

execute the command line app
<pre><code>
ComunioScoreApp
</code></pre>

or start the systemd service file
<pre><code>
sudo systemctl start ComunioScoreApp.service
</code></pre>


## Changelog
All changes and versioning information can be found in the [CHANGELOG](https://github.com/bierschi/ComunioScore/blob/master/CHANGELOG.rst)

## License
Copyright (c) 2019 Bierschneider Christian. See [LICENSE](https://github.com/bierschi/ComunioScore/blob/master/LICENSE)
for details