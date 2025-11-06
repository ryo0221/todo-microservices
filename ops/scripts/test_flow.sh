#!/bin/bash
set -e

BASE=http://localhost:8080
EMAIL="alice@example.com"
PASS="password123"

echo "1️⃣ Register..."
TOKEN=$(curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" | jq -r .access_token)

echo "✅ Token issued: $TOKEN"

echo "2️⃣ Get current user..."
curl -s -X GET $BASE/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq

echo "3️⃣ Create ToDo..."
curl -s -X POST $BASE/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Build JWT Gateway Integration"}' | jq

echo "4️⃣ List ToDos..."
curl -s -X GET $BASE/todos \
  -H "Authorization: Bearer $TOKEN" | jq
