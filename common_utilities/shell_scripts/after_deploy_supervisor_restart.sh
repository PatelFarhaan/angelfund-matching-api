#!/bin/bash


cd /home/ubuntu/flask
sudo bash compiled_files_cleanup.sh
sudo chmod +x start.sh

cd /home/ubuntu/flask/common_utilities/shell_scripts
sudo chmod +x secondary_upgrade.sh
sudo chmod +x monday_notifications_script.sh

sudo systemctl restart supervisor.service