#!/bin/bash


cd /home/ubuntu/flask
sudo bash compiled_files_cleanup.sh
sudo chmod +x start.sh
cd /home/ubuntu/flask/common_utilities/shell_scripts
sudo chmod +x clear_discover_and_reset_matched_week.sh
sudo systemctl restart supervisor.service