import os
import re
import sys
import time
import random
import socket
import subprocess

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

class VulnerabilityScanner:
    def __init__(self):
        self.nmap_path = '/opt/homebrew/bin/nmap' if os.path.exists('/opt/homebrew/bin/nmap') else 'nmap'
        
    def check_nmap_installed(self):
        """Checks if Nmap CLI is available in the system."""
        try:
            subprocess.run([self.nmap_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            try:
                subprocess.run(['nmap', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except FileNotFoundError:
                return False

    def run_live_scan(self, target, scan_type, custom_ports=None):
        """
        Executes a live network scan on the target using Nmap.
        Does not require sudo because it uses standard TCP Connect Scan (-sT) or simple port check.
        """
        if not NMAP_AVAILABLE or not self.check_nmap_installed():
            raise RuntimeError("Nmap utility or python-nmap library is not installed on this system.")
            
        print(f"Executing Live Nmap Scan on {target} ({scan_type})...")
        
        nm = nmap.PortScanner()
        
        # Build scan arguments
        # -sT: TCP Connect scan (doesn't require root)
        # -sV: Service version detection
        # -F: Fast scan (top 100 ports)
        arguments = '-sT -sV'
        
        ports = '1-1000' # default port range
        if scan_type == 'Quick Scan':
            arguments += ' -F'
            ports = None
        elif scan_type == 'Custom Ports' and custom_ports:
            ports = custom_ports
            
        try:
            # Run scan
            scan_data = nm.scan(hosts=target, ports=ports, arguments=arguments, timeout=120)
            
            # Parse scan data
            results = []
            hosts = nm.all_hosts()
            
            if not hosts:
                return {
                    'status': 'Completed',
                    'logs': f"Nmap scan completed. Target {target} appeared to be down or blocking port scans.",
                    'ports': []
                }
                
            for host in hosts:
                for proto in nm[host].all_protocols():
                    lport = sorted(nm[host][proto].keys())
                    for port in lport:
                        port_info = nm[host][proto][port]
                        results.append({
                            'port': int(port),
                            'protocol': proto,
                            'service': port_info.get('name', 'unknown'),
                            'version': f"{port_info.get('product', '')} {port_info.get('version', '')}".strip() or 'unknown',
                            'state': port_info.get('state', 'closed')
                        })
                        
            # Format output logs
            logs = f"Nmap Scan Report for {target}\n"
            logs += f"Host: {target} is UP.\n"
            logs += f"Scan Type: {scan_type}\n"
            logs += f"Total open ports found: {len(results)}\n\n"
            for r in results:
                logs += f"Port: {r['port']}/{r['protocol']} | State: {r['state']} | Service: {r['service']} ({r['version']})\n"
                
            return {
                'status': 'Completed',
                'logs': logs,
                'ports': results
            }
            
        except Exception as e:
            print(f"Live Nmap Scan encountered error: {e}")
            raise e

    def run_simulated_scan(self, target, scan_type, custom_ports=None):
        """
        Generates a highly realistic simulated cybersecurity port scan.
        Perfect for offline demonstrations, student portfolios, and speed testing.
        """
        print(f"Initializing simulated scan engine for target: {target}...")
        
        # Setup specific templates based on target name
        target_lower = target.lower()
        
        simulated_ports = []
        
        # Predefined mock vulnerability profiles
        if 'db' in target_lower or 'sql' in target_lower or 'data' in target_lower:
            # Database vulnerability profile
            profile_name = "SecureScan Internal Database Server Audit"
            candidates = [
                {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (outdated)', 'state': 'open'},
                {'port': 80, 'service': 'http', 'version': 'Apache httpd 2.4.18 (outdated)', 'state': 'open'},
                {'port': 139, 'service': 'netbios-ssn', 'version': 'Samba netbios-ssn (Workgroup: WORKGROUP)', 'state': 'open'},
                {'port': 445, 'service': 'microsoft-ds', 'version': 'Windows Server 2008 SMBv1 exposed', 'state': 'open'},
                {'port': 1433, 'service': 'ms-sql-s', 'version': 'Microsoft SQL Server 2012 SP1', 'state': 'open'},
                {'port': 3306, 'service': 'mysql', 'version': 'MySQL 5.5.47-0ubuntu0.14.04.1 (vulnerable)', 'state': 'open'},
                {'port': 8080, 'service': 'http-proxy', 'version': 'Squid Proxy 3.5.12', 'state': 'open'}
            ]
        elif 'web' in target_lower or 'prod' in target_lower or 'www' in target_lower or 'com' in target_lower:
            # Web server vulnerability profile
            profile_name = "Enterprise Production Web Server Gateway Audit"
            candidates = [
                {'port': 21, 'service': 'ftp', 'version': 'vsftpd 2.3.4 (backdoored)', 'state': 'open'},
                {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 8.4p1 Debian', 'state': 'open'},
                {'port': 23, 'service': 'telnet', 'version': 'Linux telnetd (unencrypted)', 'state': 'open'},
                {'port': 25, 'service': 'smtp', 'version': 'Postfix smtpd', 'state': 'open'},
                {'port': 80, 'service': 'http', 'version': 'Nginx 1.10.3 (vulnerable reverse proxy)', 'state': 'open'},
                {'port': 443, 'service': 'https', 'version': 'Nginx 1.10.3 (SSLv3 enabled)', 'state': 'open'},
                {'port': 3389, 'service': 'ms-wbt-server', 'version': 'Microsoft Remote Desktop (RDP) exposed', 'state': 'open'}
            ]
        elif 'localhost' in target_lower or '127.0.0.1' in target_lower:
            # Localhost loopback audit
            profile_name = "Localhost Development Node Self-Audit"
            candidates = [
                {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 9.0p1', 'state': 'open'},
                {'port': 80, 'service': 'http', 'version': 'SimpleHTTPServer (Python 3.x)', 'state': 'open'},
                {'port': 3000, 'service': 'node-web', 'version': 'Express.js backend server (development)', 'state': 'open'},
                {'port': 5000, 'service': 'flask-app', 'version': 'Werkzeug WSGI backend (debug mode ON)', 'state': 'open'},
                {'port': 6379, 'service': 'redis', 'version': 'Redis key-value store (no auth)', 'state': 'open'},
                {'port': 27017, 'service': 'mongodb', 'version': 'MongoDB 4.4.1 (unauthenticated)', 'state': 'open'}
            ]
        else:
            # Generic endpoint profile
            profile_name = "Standard Network Client Device Assessment"
            candidates = [
                {'port': 22, 'service': 'ssh', 'version': 'OpenSSH 8.9p1', 'state': 'open'},
                {'port': 80, 'service': 'http', 'version': 'Apache httpd 2.4.41', 'state': 'open'},
                {'port': 443, 'service': 'https', 'version': 'Apache httpd 2.4.41', 'state': 'open'},
                {'port': 139, 'service': 'netbios-ssn', 'version': 'Samba', 'state': 'open'},
                {'port': 445, 'service': 'microsoft-ds', 'version': 'Samba 4.15.2 (SMBv2)', 'state': 'open'},
                {'port': 8080, 'service': 'http-alt', 'version': 'Apache Tomcat 8.5.5', 'state': 'open'}
            ]
            
        # Select ports based on scan type and custom parameters
        if scan_type == 'Quick Scan':
            # Take a subset of 3-4 ports
            simulated_ports = candidates[:random.randint(3, 5)]
        elif scan_type == 'Custom Ports' and custom_ports:
            # Parse custom ports and pick matching ones or generate custom ones
            requested_ports = [int(p) for p in custom_ports.split(',')]
            for p in requested_ports:
                match = next((item for item in candidates if item['port'] == p), None)
                if match:
                    simulated_ports.append(match)
                else:
                    # Generate a custom dummy service
                    simulated_ports.append({
                        'port': p,
                        'service': f'service-{p}',
                        'version': 'Generic service version 1.0.4',
                        'state': 'open'
                    })
        else:
            # Full Scan: take all
            simulated_ports = candidates
            
        return {
            'status': 'Completed',
            'profile_name': profile_name,
            'ports': simulated_ports
        }
