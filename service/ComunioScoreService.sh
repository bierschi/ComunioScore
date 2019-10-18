#!/bin/bash

SYSTEMD_SCRIPT_DIR=$( cd  $(dirname "${BASH_SOURCE:=$0}") && pwd)
sudo chown root:root "$SYSTEMD_SCRIPT_DIR/ComunioScoreApp.service"
sudo cp -f "$SYSTEMD_SCRIPT_DIR/ComunioScoreApp.service" /etc/systemd/system

sudo systemctl daemon-reload
sudo systemctl enable ComunioScoreApp.service
sudo systemctl start ComunioScoreApp.service