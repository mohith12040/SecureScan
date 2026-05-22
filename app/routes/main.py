from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.forms.scan_forms import ScanForm
from app.utils.security import SecurityUtils

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch all scans belonging to current user
    user_scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.created_at.desc()).all()
    
    # Calculate operational metrics
    total_scans = len(user_scans)
    
    # Compute counts across completed scans
    completed_scans = [s for s in user_scans if s.status == 'Completed']
    total_vulnerabilities = sum(len(s.vulnerabilities) for s in completed_scans)
    
    # High risk targets (Unique hosts with Critical/High predicted severity or risk score >= 50)
    high_risk_hosts = set()
    for s in completed_scans:
        if s.predicted_severity in ['High', 'Critical'] or s.risk_score >= 50.0:
            high_risk_hosts.add(s.target)
    high_risk_targets_count = len(high_risk_hosts)
    
    # Severity distribution
    severity_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    for s in completed_scans:
        severity_counts[s.predicted_severity] = severity_counts.get(s.predicted_severity, 0) + 1
        
    recent_scans = user_scans[:5]
    
    # Instantiate WTForm for scanner modal
    scan_form = ScanForm()
    
    return render_template(
        'dashboard.html',
        title='Dashboard | SecureScan Operations',
        total_scans=total_scans,
        total_vulnerabilities=total_vulnerabilities,
        high_risk_targets=high_risk_targets_count,
        severity_counts=severity_counts,
        recent_scans=recent_scans,
        form=scan_form
    )


@main_bp.route('/scan/<int:scan_id>')
@login_required
def scan_detail(scan_id):
    # Fetch scan, checking owner safety
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    # Structure vulnerability data
    vulns = Vulnerability.query.filter_by(scan_id=scan.id).all()
    
    # Format open ports list for risk analysis engine
    ports_list = []
    for v in vulns:
        ports_list.append({
            'port': v.port,
            'protocol': v.protocol,
            'service': v.service,
            'version': v.version
        })
        
    # Recompute remediations and details on-the-fly to prevent double writes
    risk_analysis = SecurityUtils.calculate_risk_and_remediations(ports_list)
    
    return render_template(
        'scan_detail.html',
        title=f"Scan Details: {scan.target} | SecureScan",
        scan=scan,
        vulns=vulns,
        risk_analysis=risk_analysis
    )


@main_bp.route('/history')
@login_required
def history():
    # Setup search, filtering, sorting, and pagination parameters
    search_query = request.args.get('search', '').strip()
    severity_filter = request.args.get('severity', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()
    page = request.args.get('page', 1, type=int)
    
    query = Scan.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search_query:
        query = query.filter(Scan.target.like(f"%{search_query}%"))
        
    # Apply severity filter
    if severity_filter and severity_filter in ['Low', 'Medium', 'High', 'Critical']:
        query = query.filter_by(predicted_severity=severity_filter)
        
    # Apply sorting
    if sort_by == 'oldest':
        query = query.order_by(Scan.created_at.asc())
    elif sort_by == 'risk_desc':
        query = query.order_by(Scan.risk_score.desc())
    elif sort_by == 'risk_asc':
        query = query.order_by(Scan.risk_score.asc())
    else: # default: newest
        query = query.order_by(Scan.created_at.desc())
        
    # Pagination
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    scans = pagination.items
    
    return render_template(
        'history.html',
        title='Scan History Archives | SecureScan',
        scans=scans,
        pagination=pagination,
        search=search_query,
        severity=severity_filter,
        sort=sort_by
    )


@main_bp.route('/analytics')
@login_required
def analytics():
    # Fetch all completed scans for user
    scans = Scan.query.filter_by(user_id=current_user.id, status='Completed').order_by(Scan.created_at.asc()).all()
    
    # Calculate trending data
    scan_dates = [(s.created_at + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d') for s in scans]
    risk_trends = [s.risk_score for s in scans]
    ports_trends = [s.open_ports_count for s in scans]
    
    # Calculate service distribution
    services_counts = {}
    severity_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
    
    for s in scans:
        severity_counts[s.predicted_severity] += 1
        for v in s.vulnerabilities:
            services_counts[v.service] = services_counts.get(v.service, 0) + 1
            
    # Take top 5 exposed services
    top_services = sorted(services_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_services_labels = [x[0] for x in top_services]
    top_services_values = [x[1] for x in top_services]
    
    return render_template(
        'analytics.html',
        title='Vulnerability Analytics Matrix | SecureScan',
        scan_dates=scan_dates,
        risk_trends=risk_trends,
        ports_trends=ports_trends,
        severity_counts=severity_counts,
        top_services_labels=top_services_labels,
        top_services_values=top_services_values,
        has_data=len(scans) > 0
    )
