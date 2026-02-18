from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import ComplianceCheck, Rule, LogEntry

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Home')

@main.route('/dashboard')
@login_required
def dashboard():
    # Get statistics for dashboard
    total_checks = ComplianceCheck.query.filter_by(user_id=current_user.id).count()
    passed_checks = ComplianceCheck.query.filter_by(user_id=current_user.id, status='passed').count()
    failed_checks = ComplianceCheck.query.filter_by(user_id=current_user.id, status='failed').count()
    total_rules = Rule.query.filter_by(user_id=current_user.id).count()
    total_logs = LogEntry.query.filter_by(user_id=current_user.id).count()
    
    recent_checks = ComplianceCheck.query.filter_by(user_id=current_user.id)\
        .order_by(ComplianceCheck.checked_at.desc()).limit(5).all()
    
    recent_rules = Rule.query.filter_by(user_id=current_user.id)\
        .order_by(Rule.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         title='Dashboard',
                         total_checks=total_checks,
                         passed_checks=passed_checks,
                         failed_checks=failed_checks,
                         total_rules=total_rules,
                         total_logs=total_logs,
                         recent_checks=recent_checks,
                         recent_rules=recent_rules)