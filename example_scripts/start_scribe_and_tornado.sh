nohup scribed -c scribe/scribe.conf >> logs/scribe.log 2>&1 &
sudo nohup python tornado/catch_logs.py >> logs/tornado.log 2>&1 &
