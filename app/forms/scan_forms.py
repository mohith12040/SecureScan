import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError

class ScanForm(FlaskForm):
    target = StringField('Scan Target', validators=[
        DataRequired(message="Target IP address, hostname, or domain is required.")
    ])
    scan_type = SelectField('Scan Mode', choices=[
        ('Quick Scan', 'Quick Scan (Fast Common Ports Check)'),
        ('Full Scan', 'Full Scan (Deep Services & Versions Check)'),
        ('Custom Ports', 'Custom Scan (Specific Port Listing)')
    ], default='Quick Scan')
    custom_ports = StringField('Custom Ports (e.g. 80,443,8080)', default='')
    submit = SubmitField('Initialize Scan')

    def validate_target(self, target):
        # Sanitize and validate target format to prevent malicious input/command injections.
        data = target.data.strip()
        
        # Allowed formats:
        # 1. IPv4: 192.168.1.1 or 127.0.0.1
        # 2. Domain / Hostname: localhost, scanme.nmap.org, google.com
        # 3. CIDR Block: 192.168.1.0/24 (only allow /24 or smaller to prevent massive network stalls)
        
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}\/(2[4-9]|3[0-2])$'
        domain_pattern = r'^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)*[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*$'
        
        if data.lower() == 'localhost':
            return
            
        is_ip = re.match(ipv4_pattern, data)
        is_cidr = re.match(cidr_pattern, data)
        is_domain = re.match(domain_pattern, data)
        
        if not (is_ip or is_cidr or is_domain):
            raise ValidationError("Invalid scan target. Must be a valid IP address, domain (e.g. google.com), or CIDR (/24 to /32).")
            
    def validate_custom_ports(self, custom_ports):
        # Only validate if Custom Ports mode is selected
        if self.scan_type.data == 'Custom Ports':
            data = custom_ports.data.strip()
            if not data:
                raise ValidationError("Please provide a comma-separated list of ports when using 'Custom Scan'.")
            
            # Match comma separated positive integers between 1 and 65535
            ports_pattern = r'^(\d+)(,\d+)*$'
            if not re.match(ports_pattern, data):
                raise ValidationError("Invalid ports list format. Examples: 80 or 80,443,8080")
            
            # Double check limits
            ports = [int(p) for p in data.split(',')]
            for p in ports:
                if p < 1 or p > 65535:
                    raise ValidationError("Port numbers must be between 1 and 65535.")
