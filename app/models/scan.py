from datetime import datetime
from app import db

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target = db.Column(db.String(255), nullable=False)
    scan_type = db.Column(db.String(50), default="Quick Scan")  # Quick Scan, Full Scan, Port Custom
    status = db.Column(db.String(50), default="Pending")         # Pending, Scanning, Completed, Failed
    risk_score = db.Column(db.Float, default=0.0)                # Score from 0 - 100
    predicted_severity = db.Column(db.String(50), default="Low") # Low, Medium, High, Critical (predicted by ML)
    confidence_score = db.Column(db.Float, default=0.0)          # Confidence rating from ML model
    open_ports_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    vulnerabilities = db.relationship('Vulnerability', backref='scan', lazy=True, cascade="all, delete-orphan")
    reports = db.relationship('Report', backref='scan', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan {self.id} for {self.target} - {self.status}>"
