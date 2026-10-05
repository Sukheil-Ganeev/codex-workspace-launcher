#!/bin/bash
# Быстрая публикация текстового поста в Threads

if [ $# -lt 3 ]; then
  echo "Usage: $0 <text> <user_id> <access_token>"
  echo "Example: $0 'Amazing Dubai tour!' 17841400123456789 IGQWRPZD3..."
  exit 1
fi

TEXT="$1"
USER_ID="$2"
ACCESS_TOKEN="$3"

curl -X POST "https://graph.threads.net/v1.0/$USER_ID/threads" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$TEXT\", \"auto_publish_text\": true}"

echo ""
echo "Post published!"
