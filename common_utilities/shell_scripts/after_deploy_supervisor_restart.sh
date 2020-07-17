#!/bin/bash

cd /var/flaskapp/flask
sudo bash compiled_files_cleanup.sh
sudo chmod +x start.sh
cd  /var/flaskapp/flask/common_utilities/scripts
sudo chmod +x secondary_upgrade.sh
sudo chmod +x secondary_replicate.sh
sudo systemctl restart supervisor.service