export ENV = PROD
cd mnt/c/Users/mina\ maher/data-wrangling-with-python/ch14\ -\ Automation\ and\ Scaling/Cron/
python hello_time.py

# crontab -e
# MAIL_TO=minamahertalaat58@gmail.com
# */5 * * * * bash cron.sh > var/log/my_cron.log 2>&1