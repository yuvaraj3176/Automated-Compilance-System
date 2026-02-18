import json
import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Any

class ComplianceEngine:
    def __init__(self):
        self.rules = []
    
    def evaluate_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single rule against provided data
        """
        result = {
            'rule_name': rule.get('name'),
            'rule_type': rule.get('rule_type'),
            'passed': False,
            'details': [],
            'severity': rule.get('severity', 'medium')
        }
        
        try:
            condition = json.loads(rule.get('condition', '{}'))
            
            if rule.get('rule_type') == 'data_quality':
                result = self._check_data_quality(condition, data, result)
            elif rule.get('rule_type') == 'security':
                result = self._check_security(condition, data, result)
            elif rule.get('rule_type') == 'access':
                result = self._check_access_control(condition, data, result)
            elif rule.get('rule_type') == 'privacy':
                result = self._check_privacy(condition, data, result)
            
        except Exception as e:
            result['details'].append(f"Error evaluating rule: {str(e)}")
            result['passed'] = False
        
        return result
    
    def _check_data_quality(self, condition: Dict, data: Dict, result: Dict) -> Dict:
        """
        Check data quality rules
        """
        required_fields = condition.get('required_fields', [])
        data_types = condition.get('data_types', {})
        value_ranges = condition.get('value_ranges', {})
        
        all_passed = True
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                result['details'].append(f"Missing required field: {field}")
                all_passed = False
        
        # Check data types
        for field, expected_type in data_types.items():
            if field in data:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type:
                    result['details'].append(f"Field {field} should be {expected_type}, got {actual_type}")
                    all_passed = False
        
        result['passed'] = all_passed
        return result
    
    def _check_security(self, condition: Dict, data: Dict, result: Dict) -> Dict:
        """
        Check security rules
        """
        sensitive_patterns = condition.get('sensitive_patterns', [])
        encryption_required = condition.get('encryption_required', False)
        
        all_passed = True
        
        # Check for sensitive data exposure
        if isinstance(data, dict):
            data_str = json.dumps(data)
            for pattern in sensitive_patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    result['details'].append(f"Sensitive pattern detected: {pattern}")
                    all_passed = False
        
        result['passed'] = all_passed
        return result
    
    def _check_access_control(self, condition: Dict, data: Dict, result: Dict) -> Dict:
        """
        Check access control rules
        """
        allowed_roles = condition.get('allowed_roles', [])
        user_role = data.get('user_role', '')
        
        if user_role not in allowed_roles:
            result['details'].append(f"User role '{user_role}' not in allowed roles: {allowed_roles}")
            result['passed'] = False
        else:
            result['passed'] = True
        
        return result
    
    def _check_privacy(self, condition: Dict, data: Dict, result: Dict) -> Dict:
        """
        Check privacy rules
        """
        pii_fields = condition.get('pii_fields', [])
        anonymization_required = condition.get('anonymization_required', False)
        
        all_passed = True
        
        for field in pii_fields:
            if field in data and data[field]:
                result['details'].append(f"PII field '{field}' contains data that may need anonymization")
                all_passed = False
        
        result['passed'] = all_passed
        return result

class LogAnalyzer:
    @staticmethod
    def analyze_log_file(log_content: str, patterns: List[str] = None) -> Dict[str, Any]:
        """
        Analyze log file for issues
        """
        if patterns is None:
            patterns = [
                r'error|exception|failed|failure',
                r'unauthorized|forbidden|access denied',
                r'invalid|illegal|malformed',
                r'timeout|expired|deadlock'
            ]
        
        lines = log_content.split('\n')
        issues = []
        issue_count = 0
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i + 1,
                        'content': line.strip(),
                        'pattern': pattern
                    })
                    issue_count += 1
                    break
        
        return {
            'total_lines': len(lines),
            'issues_found': issue_count,
            'issues': issues[:50],  # Limit to first 50 issues
            'analysis_time': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_report(analysis_results: List[Dict]) -> pd.DataFrame:
        """
        Generate a report from analysis results
        """
        report_data = []
        for result in analysis_results:
            report_data.append({
                'filename': result.get('filename', 'Unknown'),
                'total_lines': result.get('total_lines', 0),
                'issues_found': result.get('issues_found', 0),
                'analysis_time': result.get('analysis_time', ''),
                'top_issues': ', '.join([i['pattern'] for i in result.get('issues', [])[:3]])
            })
        
        return pd.DataFrame(report_data)