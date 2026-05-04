#!/bin/bash

# Script to monitor Redmine and restart if down
# Run this script in the background: nohup ./monitor_redmine.sh &

REDMINE_DIR="/opt/redmine"
REDMINE_URL="http://localhost:3000"
CHECK_INTERVAL=60  # seconds

echo "Starting Redmine monitor..."
echo "Checking every $CHECK_INTERVAL seconds"

while true; do
    if curl -f --max-time 10 "$REDMINE_URL" > /dev/null 2>&1; then
        echo "$(date): Redmine is up"
    else
        echo "$(date): Redmine is down, restarting..."
        cd "$REDMINE_DIR"
        # Kill any existing rails server processes
        pkill -f "rails server" || true
        # Start the server
        bundle exec rails server -e production -d
        sleep 10  # Wait a bit for it to start
    fi
    sleep $CHECK_INTERVAL
done