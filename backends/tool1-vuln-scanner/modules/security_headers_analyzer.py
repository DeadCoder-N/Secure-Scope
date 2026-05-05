"""Enhanced Security Headers Analyzer Module"""

class SecurityHeadersAnalyzer:
    def __init__(self):
        self.name = "Security Headers Analyzer"
    
    def analyze_headers(self, url):
        """Comprehensive security headers analysis with grading"""
        import requests
        
        results = {
            'score': 0,
            'grade': 'F',
            'headers': {},
            'vulnerabilities': []
        }
        
        try:
            response = requests.get(url, timeout=10)
            headers = response.headers
            
            # Check 9 critical headers
            header_checks = {
                'Content-Security-Policy': {'weight': 25, 'severity': 'CRITICAL'},
                'Strict-Transport-Security': {'weight': 20, 'severity': 'HIGH'},
                'X-Frame-Options': {'weight': 15, 'severity': 'HIGH'},
                'X-Content-Type-Options': {'weight': 10, 'severity': 'MEDIUM'},
                'Referrer-Policy': {'weight': 10, 'severity': 'MEDIUM'},
                'Permissions-Policy': {'weight': 10, 'severity': 'LOW'},
                'X-XSS-Protection': {'weight': 5, 'severity': 'LOW'},
                'Cache-Control': {'weight': 3, 'severity': 'LOW'},
                'X-Permitted-Cross-Domain-Policies': {'weight': 2, 'severity': 'LOW'}
            }
            
            for header, config in header_checks.items():
                value = headers.get(header, '')
                results['headers'][header] = value
                
                if value:
                    results['score'] += config['weight']
                else:
                    results['vulnerabilities'].append({
                        'type': f'Missing {header}',
                        'severity': config['severity'],
                        'description': f'{header} header not set',
                        'evidence': 'Header missing'
                    })
            
            # Grade calculation
            if results['score'] >= 90:
                results['grade'] = 'A+'
            elif results['score'] >= 80:
                results['grade'] = 'A'
            elif results['score'] >= 70:
                results['grade'] = 'B'
            elif results['score'] >= 60:
                results['grade'] = 'C'
            elif results['score'] >= 50:
                results['grade'] = 'D'
            else:
                results['grade'] = 'F'
            
            # CSP analysis
            if 'Content-Security-Policy' in headers:
                csp = headers['Content-Security-Policy']
                if 'unsafe-inline' in csp:
                    results['vulnerabilities'].append({
                        'type': 'Weak CSP - unsafe-inline',
                        'severity': 'HIGH',
                        'description': 'CSP allows unsafe-inline scripts',
                        'evidence': csp
                    })
                if 'unsafe-eval' in csp:
                    results['vulnerabilities'].append({
                        'type': 'Weak CSP - unsafe-eval',
                        'severity': 'HIGH',
                        'description': 'CSP allows unsafe-eval',
                        'evidence': csp
                    })
            
            # HSTS validation
            if 'Strict-Transport-Security' in headers:
                hsts = headers['Strict-Transport-Security']
                if 'max-age' not in hsts:
                    results['vulnerabilities'].append({
                        'type': 'Weak HSTS - No max-age',
                        'severity': 'MEDIUM',
                        'description': 'HSTS missing max-age directive',
                        'evidence': hsts
                    })
                elif 'max-age=0' in hsts or 'max-age=1' in hsts:
                    results['vulnerabilities'].append({
                        'type': 'Weak HSTS - Short max-age',
                        'severity': 'MEDIUM',
                        'description': 'HSTS max-age too short',
                        'evidence': hsts
                    })
            
            # Cookie security
            set_cookie = headers.get('Set-Cookie', '')
            if set_cookie:
                if 'Secure' not in set_cookie:
                    results['vulnerabilities'].append({
                        'type': 'Insecure Cookie - Missing Secure',
                        'severity': 'HIGH',
                        'description': 'Cookie missing Secure flag',
                        'evidence': set_cookie
                    })
                if 'HttpOnly' not in set_cookie:
                    results['vulnerabilities'].append({
                        'type': 'Insecure Cookie - Missing HttpOnly',
                        'severity': 'HIGH',
                        'description': 'Cookie missing HttpOnly flag',
                        'evidence': set_cookie
                    })
                if 'SameSite' not in set_cookie:
                    results['vulnerabilities'].append({
                        'type': 'Insecure Cookie - Missing SameSite',
                        'severity': 'MEDIUM',
                        'description': 'Cookie missing SameSite attribute',
                        'evidence': set_cookie
                    })
            
            # Information disclosure
            server = headers.get('Server', '')
            if server and any(v in server.lower() for v in ['apache', 'nginx', 'iis', 'tomcat']):
                results['vulnerabilities'].append({
                    'type': 'Information Disclosure - Server Header',
                    'severity': 'LOW',
                    'description': 'Server header exposes version information',
                    'evidence': server
                })
            
            x_powered_by = headers.get('X-Powered-By', '')
            if x_powered_by:
                results['vulnerabilities'].append({
                    'type': 'Information Disclosure - X-Powered-By',
                    'severity': 'LOW',
                    'description': 'X-Powered-By header exposes technology stack',
                    'evidence': x_powered_by
                })
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
