import os
import csv
import random
import pandas as pd
import numpy as np

def generate_vulnerability_dataset(output_path, num_samples=2500):
    """
    Generates a realistic, synthetic vulnerability scanning dataset
    for severity classification using Scikit-Learn.
    """
    print(f"Generating synthetic cybersecurity dataset: {num_samples} samples...")
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for _ in range(num_samples):
        # Generate raw security features
        open_ports_count = random.randint(1, 20)
        
        # Dangerous ports exposed: FTP(21), Telnet(23), SMTP(25), NetBIOS(139), SMB(445), RDP(3389)
        dangerous_ports_count = random.choices([0, 1, 2, 3, 4, 5], weights=[60, 25, 10, 3, 1.5, 0.5])[0]
        # Cap dangerous ports to open ports
        dangerous_ports_count = min(dangerous_ports_count, open_ports_count)
        
        exposed_services_count = random.randint(1, min(open_ports_count + 1, 10))
        
        # Risk score calculation
        base_risk = open_ports_count * 2.0 + dangerous_ports_count * 15.0 + exposed_services_count * 2.5
        # Outdated services count
        outdated_services_count = random.choices([0, 1, 2, 3, 4], weights=[50, 30, 15, 4, 1])[0]
        outdated_services_count = min(outdated_services_count, exposed_services_count)
        base_risk += outdated_services_count * 8.0
        
        # Critical ports indicator
        has_critical_port = 1 if (dangerous_ports_count > 0 and random.random() > 0.4) else 0
        if has_critical_port:
            base_risk += 20.0
            
        # Add random noise
        noise = np.random.normal(0, 4.0)
        risk_score = np.clip(base_risk + noise, 0.0, 100.0)
        
        # Determine logical severity class
        # 0 = Low, 1 = Medium, 2 = High, 3 = Critical
        if risk_score >= 70.0:
            severity = 3
        elif risk_score >= 45.0:
            severity = 2
        elif risk_score >= 20.0:
            severity = 1
        else:
            severity = 0
            
        # Add a tiny bit of random label noise (e.g. 3% flip chance) to represent real-world exceptions
        if random.random() < 0.03:
            severity = random.randint(0, 3)
            
        data.append({
            'open_ports_count': open_ports_count,
            'dangerous_ports_count': dangerous_ports_count,
            'exposed_services_count': exposed_services_count,
            'risk_score': round(risk_score, 2),
            'has_critical_port': has_critical_port,
            'outdated_services_count': outdated_services_count,
            'severity': severity
        })
        
    # Write to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully at: {output_path}")
    print(df['severity'].value_counts())
    
if __name__ == '__main__':
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dataset'))
    output_file = os.path.join(output_dir, 'vulnerability_dataset.csv')
    generate_vulnerability_dataset(output_file)
