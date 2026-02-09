#!/usr/bin/env python3
"""Helper script to update token count - run by the agent"""
import json
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: update_tokens.py <token_count>")
    sys.exit(1)

token_count = int(sys.argv[1])

data = {
    "tokens": token_count,
    "updated": datetime.now().isoformat()
}

with open('token_count.json', 'w') as f:
    json.dump(data, f)

print(f"Updated: {token_count} tokens")
