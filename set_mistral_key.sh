#!/bin/bash

# Script to securely set your Mistral API key
# Usage: ./set_mistral_key.sh YOUR_ACTUAL_API_KEY

if [ -z "$1" ]; then
    echo "Usage: $0 <your-mistral-api-key>"
    echo "Example: $0 a8zh3krcxy8FHvP2RmzxJDO5YWcwVg0I"
    exit 1
fi

API_KEY="$1"

# Update the .env file
if [ -f ".env" ]; then
    # Use sed to replace the placeholder with the actual key
    sed -i.bak "s/MISTRAL_API_KEY=your-mistral-api-key-here/MISTRAL_API_KEY=$API_KEY/" .env
    echo "✅ Mistral API key updated in .env file"
    echo "🔒 Your API key is now securely stored in the .env file"
    echo "⚠️  Remember: Never commit .env files to version control!"
else
    echo "❌ .env file not found. Please copy .env.example to .env first."
    exit 1
fi