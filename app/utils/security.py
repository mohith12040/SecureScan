import re
import socket

class SecurityUtils:
    @staticmethod
    def sanitize_target(target):
        """Sanitizes target string and returns validated clean address."""
        if not target:
            return None
        target = target.strip()
        # Keep alphanumeric, dots, hyphens, slashes for domains, IPs, and CIDRs
        cleaned = re.sub(r'[^a-zA-Z0-9\.\-\/]', '', target)
        return cleaned

    @staticmethod
    def calculate_risk_and_remediations(open_ports):
        """
        Custom risk scoring algorithm.
        Evaluates discovered open ports and service headers.
        
        Returns:
            dict containing:
                risk_score (float): Calculated score (0.0 to 100.0)
                risk_level (str): 'Low', 'Medium', 'High', 'Critical'
                dangerous_ports_count (int)
                has_critical_port (int)
                outdated_services_count (int)
                remediations (list of dict)
        """
        # Critical entry points list
        critical_ports = {21, 23, 139, 445, 3389}
        
        dangerous_ports = {
            21: ("FTP", 18.0, "Disable FTP services and transition to SFTP or secure HTTPS-based file transfers."),
            23: ("Telnet", 22.0, "Disable the unencrypted Telnet service immediately. Enforce SSH (Port 22) for remote command administration."),
            25: ("SMTP", 8.0, "Verify SMTP relays are secure. Restrict public access, block open relay configurations, and enforce STARTTLS."),
            80: ("HTTP", 6.0, "Enforce SSL/TLS encryption. Redirect unencrypted HTTP traffic on Port 80 to HTTPS (Port 443) and enable HSTS."),
            139: ("NetBIOS", 12.0, "Disable NetBIOS over TCP/IP and restrict ports 137-139 at host and edge firewalls."),
            445: ("SMB", 25.0, "CRITICAL: Disable SMBv1. Restrict SMB (Port 445) exposure to internal corporate networks and require SMBv3 signing."),
            1433: ("MSSQL", 15.0, "Database server exposed. Block public access at firewalls and enforce strong AD/SQL authentication and TLS."),
            3306: ("MySQL", 15.0, "Exposed SQL database service. Restrict binding to 127.0.0.1, restrict inbound IPs, and enforce strong user passwords."),
            3389: ("RDP", 20.0, "Remote Desktop exposed. Disable public access. Restrict RDP behind a secure VPN gateway and require Multi-Factor Authentication (MFA)."),
            6379: ("Redis", 15.0, "Insecure key-value database. Require Redis password authentication, bind to loopback, and disable dangerous commands."),
            8080: ("HTTP-Alt", 10.0, "Ensure admin portals (e.g. Tomcat Web Manager) are locked down behind strong passwords, SSL, and restricted IP access."),
            27017: ("MongoDB", 15.0, "Database exposed. Enable MongoDB auth, restrict access to authorized app servers, and enable TLS.")
        }
        
        risk_score = 0.0
        dangerous_ports_count = 0
        has_critical_port = 0
        outdated_services_count = 0
        remediations = []
        
        if not open_ports:
            return {
                'risk_score': 0.0,
                'risk_level': 'Low',
                'dangerous_ports_count': 0,
                'has_critical_port': 0,
                'outdated_services_count': 0,
                'remediations': [{
                    'port': 'N/A',
                    'service': 'General',
                    'priority': 'Low',
                    'remediation': 'No open ports detected. Continue periodic audits and monitor firewall logs.'
                }]
            }
            
        # 1. Evaluate individual ports
        for p_info in open_ports:
            port = p_info['port']
            service = p_info.get('service', 'unknown')
            version = p_info.get('version', '')
            
            # Base score for any open port
            port_weight = 3.0
            
            # Outdated version checks
            is_outdated = False
            version_lower = version.lower()
            if any(word in version_lower for word in ['outdated', 'vulnerable', 'backdoor', 'ubuntu2.8', '5.5.47', '2.3.4', '2008', '2012']):
                is_outdated = True
                outdated_services_count += 1
                port_weight += 8.0
                remediations.append({
                    'port': port,
                    'service': service,
                    'priority': 'High',
                    'remediation': f"Update outdated or vulnerable version of '{service}' ({version}) to the latest secure vendor patch."
                })
                
            # Dangerous port checks
            if port in dangerous_ports:
                name, score, rec = dangerous_ports[port]
                dangerous_ports_count += 1
                port_weight += score
                
                priority = 'Critical' if port in critical_ports else 'High'
                if port in critical_ports:
                    has_critical_port = 1
                    
                remediations.append({
                    'port': port,
                    'service': service,
                    'priority': priority,
                    'remediation': rec
                })
            else:
                # Standard recommendation for custom/other open ports
                remediations.append({
                    'port': port,
                    'service': service,
                    'priority': 'Medium' if is_outdated else 'Low',
                    'remediation': f"Apply Least-Privileged Access. Ensure service is authenticated and block public access on port {port} if unused."
                })
                
            risk_score += port_weight
            
        # Add factor for exposed service variety
        risk_score += len(open_ports) * 1.5
        
        # Cap final risk score at 100.0
        risk_score = round(min(risk_score, 100.0), 2)
        
        # Classify Risk Level
        if risk_score >= 75.0:
            risk_level = 'Critical'
        elif risk_score >= 50.0:
            risk_level = 'High'
        elif risk_score >= 20.0:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
            
        # Sort remediations so highest priority items are displayed first
        priority_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        remediations.sort(key=lambda x: priority_weights.get(x['priority'], 1), reverse=True)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'dangerous_ports_count': dangerous_ports_count,
            'has_critical_port': has_critical_port,
            'outdated_services_count': outdated_services_count,
            'remediations': remediations
        }
