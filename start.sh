#!/bin/zsh
cd "$(dirname "$0")"
IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
echo "On your iPhone (same Wi-Fi), open:  http://$IP:8000"
python3 -m http.server 8000
