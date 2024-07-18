#!/bin/bash

LOGFILE=~/reposter/reposter.log

# Check if there are any running tmux sessions
if tmux list-sessions &> /dev/null; then
  echo "Closing all existing tmux sessions..."
  # Kill all tmux sessions
  tmux kill-server
fi

# Start a new tmux session and run the setup and script
echo "Starting a new tmux session..."
tmux new-session -d -s mysession <<- 'EOF'
  cd ~/reposter/ || { echo "Failed to change directory to ~/reposter/" | tee -a $LOGFILE; exit 1; }
  git reset --hard || { echo "Git reset failed" | tee -a $LOGFILE; exit 1; }
  git pull || { echo "Git pull failed" | tee -a $LOGFILE; exit 1; }
  rm -rf .venv || { echo "Failed to remove existing virtual environment" | tee -a $LOGFILE; exit 1; }
  python3 -m venv .venv || { echo "Failed to create virtual environment" | tee -a $LOGFILE; exit 1; }
  source .venv/bin/activate || { echo "Failed to activate virtual environment" | tee -a $LOGFILE; exit 1; }
  python --version | tee -a $LOGFILE  # Ensure the version is Python 3.7.16+
  pip install -r requirements.txt || { echo "Failed to install requirements" | tee -a $LOGFILE; exit 1; }
  python ~/reposter/reposter.py >> $LOGFILE 2>&1 || { echo "Failed to start reposter.py" | tee -a $LOGFILE; exit 1; }
EOF

echo "Setup and reposter.py are now running in a new tmux session named 'mysession'."
