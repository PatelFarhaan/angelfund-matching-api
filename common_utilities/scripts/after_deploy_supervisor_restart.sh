cd /var/flaskapp/flask
sudo bash compiled_files_cleanup.sh
sudo chmod +x start.sh
sudo supervisorctl start backend
sudo systemctl restart supervisor.service