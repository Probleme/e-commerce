#!/bin/bash

# Function to get IP address for macOS
get_ip_macos() {
    ifconfig | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1
}

# Function to get IP address for Linux
get_ip_linux() {
    ip addr show | grep 'inet ' | grep -v 127.0.0.1 | awk '{print $2}' | cut -d'/' -f1 | head -n 1
}

# Determine the operating system and get the IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
    ip=$(get_ip_macos)
    sed_command="sed -i ''"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ip=$(get_ip_linux)
    sed_command="sed -i"
else
    echo "Unsupported OS type: $OSTYPE"
    exit 1
fi

# Remove existing HOST_IP line if it exists
if [ -f .env ]; then
    $sed_command '/^HOST_IP=/d' .env
    
    # Add newline if file doesn't end with one
    if [ -s .env ] && [ "$(tail -c1 .env)" != "" ]; then
        echo "" >> .env
    fi
fi

# Append the IP address to the .env file
echo "HOST_IP=$ip" >> .env
echo "Updated HOST_IP to $ip in .env"