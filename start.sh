#!/bin/bash

# Check if there are any running tmux sessions
if tmux list-sessions &> /dev/null; then
  echo "Closing all existing tmux sessions..."
  # Kill all tmux sessions
  tmux kill-server
fi

# Start a new tmux session and run the setup and script
echo "Starting a new tmux session..."
tmux new-session -d -s mysession <<- 'EOF'
  cd ~/reposter/
  git reset --hard
  git pull
  rm -rf .venv
  python3 -m venv .venv
  source .venv/bin/activate
  python --version  # Ensure the version is Python 3.7.16+
  pip install -r requirements.txt
  python ~/reposter/reposter.py
EOF

echo "Setup and reposter.py are now running in a new tmux session named 'mysession'."
