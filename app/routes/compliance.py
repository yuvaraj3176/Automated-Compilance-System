import json
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Rule, ComplianceCheck, LogEntry
from app.forms import RuleForm, ComplianceCheckForm
from app.utils import ComplianceEngine, LogAnalyzer

compliance = Blueprint('compliance', __name__)

@compliance.route('/rules')
@login_required
def rules():
    all_rules = Rule.query.filter_by(user_id=current_user.id).all()
    return render_template('rules.html', rules=all_rules, title='Compliance Rules')

@compliance.route('/rules/new', methods=['GET', 'POST'])
@login_required
def new_rule():
    form = RuleForm()
    if form.validate_on_submit():
        rule = Rule(
            name=form.name.data,
            description=form.description.data,
            rule_type=form.rule_type.data,
            condition=form.condition.data,
            severity=form.severity.data,
            user_id=current_user.id
        )
        db.session.add(rule)
        db.session.commit()
        flash('Your rule has been created!', 'success')
        return redirect(url_for('compliance.rules'))
    return render_template('create_rule.html', form=form, title='New Rule')

@compliance.route('/rules/<int:rule_id>')
@login_required
def view_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    if rule.user_id != current_user.id:
        flash('You do not have permission to view this rule.', 'danger')
        return redirect(url_for('compliance.rules'))
    return render_template('view_rule.html', rule=rule, title=rule.name)

@compliance.route('/rules/<int:rule_id>/delete', methods=['POST'])
@login_required
def delete_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    if rule.user_id != current_user.id:
        flash('You do not have permission to delete this rule.', 'danger')
        return redirect(url_for('compliance.rules'))
    
    db.session.delete(rule)
    db.session.commit()
    flash('Rule has been deleted.', 'success')
    return redirect(url_for('compliance.rules'))

@compliance.route('/checks')
@login_required
def checks():
    all_checks = ComplianceCheck.query.filter_by(user_id=current_user.id)\
        .order_by(ComplianceCheck.checked_at.desc()).all()
    return render_template('compliance_check.html', checks=all_checks, title='Compliance Checks')

@compliance.route('/checks/new', methods=['GET', 'POST'])
@login_required
def new_check():
    form = ComplianceCheckForm()
    form.rule_id.choices = [(r.id, r.name) for r in Rule.query.filter_by(user_id=current_user.id, is_active=True).all()]
    
    if form.validate_on_submit():
        rule = Rule.query.get(form.rule_id.data)
        
        # Sample data for compliance check (in real app, this would come from your data sources)
        sample_data = {
            'user_role': 'admin',
            'email': 'user@example.com',
            'phone': '+1234567890',
            'ssn': '123-45-6789',
            'amount': 1500,
            'transaction_date': '2024-01-15'
        }
        
        engine = ComplianceEngine()
        rule_dict = {
            'name': rule.name,
            'rule_type': rule.rule_type,
            'condition': rule.condition,
            'severity': rule.severity
        }
        
        result = engine.evaluate_rule(rule_dict, sample_data)
        
        check = ComplianceCheck(
            name=form.name.data,
            status='passed' if result['passed'] else 'failed',
            result=json.dumps(result),
            user_id=current_user.id,
            rule_id=rule.id
        )
        
        db.session.add(check)
        db.session.commit()
        
        flash(f'Compliance check completed. Status: {check.status}', 'success')
        return redirect(url_for('compliance.checks'))
    
    return render_template('run_check.html', form=form, title='New Compliance Check')

@compliance.route('/checks/<int:check_id>')
@login_required
def view_check(check_id):
    check = ComplianceCheck.query.get_or_404(check_id)
    if check.user_id != current_user.id:
        flash('You do not have permission to view this check.', 'danger')
        return redirect(url_for('compliance.checks'))
    
    result = json.loads(check.result) if check.result else {}
    return render_template('view_check.html', check=check, result=result, title='Check Result')

@compliance.route('/logs')
@login_required
def logs():
    all_logs = LogEntry.query.filter_by(user_id=current_user.id)\
        .order_by(LogEntry.analyzed_at.desc()).all()
    return render_template('logs.html', logs=all_logs, title='Log Analysis')

@compliance.route('/logs/upload', methods=['POST'])
@login_required
def upload_log():
    if 'log_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('compliance.logs'))
    
    file = request.files['log_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('compliance.logs'))
    
    if file:
        filename = secure_filename(file.filename)
        content = file.read().decode('utf-8')
        
        analyzer = LogAnalyzer()
        result = analyzer.analyze_log_file(content)
        
        log_entry = LogEntry(
            filename=filename,
            content=content[:1000],  # Store first 1000 chars
            issues_found=result['issues_found'],
            user_id=current_user.id
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        flash(f'Log file analyzed. Found {result["issues_found"]} issues.', 'info')
        return redirect(url_for('compliance.view_log', log_id=log_entry.id))
    
    return redirect(url_for('compliance.logs'))

@compliance.route('/logs/<int:log_id>')
@login_required
def view_log(log_id):
    log = LogEntry.query.get_or_404(log_id)
    if log.user_id != current_user.id:
        flash('You do not have permission to view this log.', 'danger')
        return redirect(url_for('compliance.logs'))
    
    analyzer = LogAnalyzer()
    result = analyzer.analyze_log_file(log.content)
    
    return render_template('view_log.html', log=log, result=result, title='Log Analysis Result')

@compliance.route('/reports')
@login_required
def reports():
    checks = ComplianceCheck.query.filter_by(user_id=current_user.id).all()
    logs = LogEntry.query.filter_by(user_id=current_user.id).all()
    
    # Generate summary statistics
    total_checks = len(checks)
    passed_checks = sum(1 for c in checks if c.status == 'passed')
    failed_checks = sum(1 for c in checks if c.status == 'failed')
    total_issues = sum(l.issues_found for l in logs)
    
    return render_template('reports.html', 
                         title='Reports',
                         total_checks=total_checks,
                         passed_checks=passed_checks,
                         failed_checks=failed_checks,
                         total_issues=total_issues,
                         checks=checks[:10],
                         logs=logs[:10])