cd /var/flaskapp/flask
sudo bash compiled_files_cleanup.sh
sudo git checkout test_server
sudo bash compiled_files_cleanup.sh
sudo systemctl restart supervisor.service