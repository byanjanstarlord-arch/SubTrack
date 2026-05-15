"""Regex-based Gmail subscription detection engine.

This module provides regex-based email parsing for subscription detection.
Structured to allow easy integration of NLP (spaCy) later.
"""
import re
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple


# =============================================================================
# PRICE PATTERNS
# =============================================================================

PRICE_PATTERNS = [
    # $19.99, $ 19.99, USD 19.99
    r'(?:\$|USD|US\$)\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
    # €19.99, EUR 19.99
    r'(?:€|EUR|EUR\s)\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
    # £19.99, GBP 19.99
    r'(?:£|GBP|GBP\s)\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
    # ₹199, INR 199
    r'(?:₹|INR|Rs\.?)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
    # ¥199, JPY 199
    r'(?:¥|JPY)\s*(\d{1,3}(?:,\d{3})*)',
    # Generic: charged X.XX, amount: X.XX, total: X.XX
    r'(?:charged|amount|total|price|cost|payment)\s*(?:of|is|:)?\s*(?:\$|€|£|₹)?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',
    # X.XX/month, X.XX per month
    r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*(?:/|per)\s*(?:month|mo)',
    # X.XX/year, X.XX per year
    r'(\d{1,3}(?:,\d{3})*\.\d{2})\s*(?:/|per)\s*(?:year|yr)',
]

CURRENCY_MAP = {
    '$': 'USD', 'USD': 'USD', 'US$': 'USD',
    '€': 'EUR', 'EUR': 'EUR',
    '£': 'GBP', 'GBP': 'GBP',
    '₹': 'INR', 'INR': 'INR', 'Rs': 'INR', 'Rs.': 'INR',
    '¥': 'JPY', 'JPY': 'JPY',
    'C$': 'CAD', 'CAD': 'CAD',
    'A$': 'AUD', 'AUD': 'AUD',
}


# =============================================================================
# SUBSCRIPTION SERVICE PATTERNS
# =============================================================================

SUBSCRIPTION_KEYWORDS = [
    'subscription', 'renewal', 'recurring', 'billing', 'invoice',
    'payment', 'charged', 'auto-renew', 'membership', 'plan',
    'premium', 'pro plan', 'upgrade', 'monthly', 'yearly',
    'trial', 'free trial', 'subscription confirmed',
]

KNOWN_SERVICES = {
    'netflix': 'Netflix',
    'spotify': 'Spotify',
    'apple': 'Apple',
    'google': 'Google',
    'amazon': 'Amazon',
    'microsoft': 'Microsoft',
    'adobe': 'Adobe',
    'slack': 'Slack',
    'notion': 'Notion',
    'figma': 'Figma',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'zoom': 'Zoom',
    'dropbox': 'Dropbox',
    'icloud': 'iCloud',
    'youtube': 'YouTube',
    'disney': 'Disney',
    'hulu': 'Hulu',
    'hbo': 'HBO',
    'prime': 'Amazon Prime',
    'paramount': 'Paramount',
    'peacock': 'Peacock',
    'crunchyroll': 'Crunchyroll',
    'twitch': 'Twitch',
    'patreon': 'Patreon',
    'substack': 'Substack',
    'nyt': 'New York Times',
    'washington post': 'Washington Post',
    'medium': 'Medium',
    'duolingo': 'Duolingo',
    'coursera': 'Coursera',
    'udemy': 'Udemy',
    'skillshare': 'Skillshare',
    'linkedin': 'LinkedIn',
    'canva': 'Canva',
    'grammarly': 'Grammarly',
    'lastpass': 'LastPass',
    '1password': '1Password',
    'nordvpn': 'NordVPN',
    'expressvpn': 'ExpressVPN',
    'dashlane': 'Dashlane',
    'evernote': 'Evernote',
    'todoist': 'Todoist',
    'trello': 'Trello',
    'asana': 'Asana',
    'monday': 'Monday.com',
    'clickup': 'ClickUp',
    'notion': 'Notion',
    'obsidian': 'Obsidian',
    'roam': 'Roam Research',
    'linear': 'Linear',
    'vercel': 'Vercel',
    'heroku': 'Heroku',
    'digitalocean': 'DigitalOcean',
    'aws': 'AWS',
    'azure': 'Azure',
    'gcp': 'Google Cloud',
    'twilio': 'Twilio',
    'sendgrid': 'SendGrid',
    'mailchimp': 'Mailchimp',
    'convertkit': 'ConvertKit',
    'hubspot': 'HubSpot',
    'salesforce': 'Salesforce',
    'shopify': 'Shopify',
    'stripe': 'Stripe',
    'paddle': 'Paddle',
    'lemonsqueezy': 'Lemon Squeezy',
    'fastly': 'Fastly',
    'cloudflare': 'Cloudflare',
    'datadog': 'Datadog',
    'sentry': 'Sentry',
    'logrocket': 'LogRocket',
    'algolia': 'Algolia',
    'mapbox': 'Mapbox',
}


# =============================================================================
# BILLING CYCLE PATTERNS
# =============================================================================

BILLING_CYCLE_PATTERNS = {
    'monthly': [r'\bmonthly\b', r'\bper\s+month\b', r'\b/month\b', r'\bmo\b'],
    'yearly': [r'\byearly\b', r'\bannual\b', r'\bper\s+year\b', r'\b/year\b', r'\byr\b'],
    'quarterly': [r'\bquarterly\b', r'\bper\s+quarter\b'],
    'weekly': [r'\bweekly\b', r'\bper\s+week\b'],
}


# =============================================================================
# DATE EXTRACTION
# =============================================================================

DATE_PATTERNS = [
    # Jan 15, 2024
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})\b',
    # 15 Jan 2024
    r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{4})\b',
    # 2024-01-15, 2024/01/15
    r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',
    # 01-15-2024, 01/15/2024
    r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b',
    # Jan 2024 (first day of month)
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{4})\b',
]


# =============================================================================
# DETECTION ENGINE
# =============================================================================

class SubscriptionDetector:
    """Main subscription detection engine using regex patterns."""
    
    def __init__(self):
        self.confidence = 0.0
    
    def is_subscription_email(self, subject: str, body: str, sender: str) -> bool:
        """Check if an email is likely a subscription-related email."""
        text = f"{subject} {body} {sender}".lower()
        
        keyword_matches = sum(1 for kw in SUBSCRIPTION_KEYWORDS if kw in text)
        
        # Check for price patterns
        has_price = any(re.search(pattern, text, re.IGNORECASE) for pattern in PRICE_PATTERNS)
        
        # Check for known services
        has_known_service = any(service in text for service in KNOWN_SERVICES.keys())
        
        # Scoring
        score = 0
        if keyword_matches >= 2:
            score += 30
        if has_price:
            score += 40
        if has_known_service:
            score += 30
        
        return score >= 50
    
    def extract_price(self, text: str) -> Optional[Tuple[Decimal, str]]:
        """Extract price and currency from text."""
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract price
                price_str = match.group(1).replace(',', '')
                try:
                    price = Decimal(price_str)
                except:
                    continue
                
                # Detect currency from match
                currency = 'USD'  # default
                matched_text = match.group(0)
                for symbol, code in CURRENCY_MAP.items():
                    if symbol in matched_text:
                        currency = code
                        break
                
                return (price, currency)
        return None
    
    def detect_service(self, subject: str, body: str, sender: str) -> Optional[str]:
        """Detect the service name from email content."""
        text = f"{subject} {body} {sender}".lower()
        
        # Check known services first
        for keyword, name in KNOWN_SERVICES.items():
            if keyword in text:
                return name
        
        # Try to extract from sender domain
        domain_match = re.search(r'from\s+([\w\-]+)@([\w\-]+\.\w+)', text)
        if domain_match:
            domain = domain_match.group(2).split('.')[0]
            return domain.title()
        
        # Try subject line patterns
        subject_patterns = [
            r'Your\s+(.+?)\s+(?:subscription|receipt|invoice|payment)',
            r'(.+?)\s+(?:billing|payment|charge|receipt)',
        ]
        for pattern in subject_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        return None
    
    def detect_billing_cycle(self, text: str) -> Optional[str]:
        """Detect billing cycle from text."""
        text_lower = text.lower()
        
        for cycle, patterns in BILLING_CYCLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return cycle
        
        return 'monthly'  # default assumption
    
    def detect_date(self, text: str) -> Optional[date]:
        """Extract date from text."""
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    
                    # Try different date formats
                    if len(groups) == 3:
                        # Check if first group is month name
                        month_names = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
                        }
                        
                        first = groups[0].lower()[:3]
                        if first in month_names:
                            # Format: Jan 15, 2024
                            month = month_names[first]
                            day = int(groups[1])
                            year = int(groups[2])
                            return date(year, month, day)
                        else:
                            # Format: 2024-01-15
                            year = int(groups[0])
                            month = int(groups[1])
                            day = int(groups[2])
                            return date(year, month, day)
                    
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def calculate_confidence(self, has_price: bool, has_service: bool, has_date: bool,
                           has_cycle: bool, keyword_matches: int) -> float:
        """Calculate confidence score for detection."""
        score = 0.0
        
        if has_price:
            score += 0.35
        if has_service:
            score += 0.30
        if has_date:
            score += 0.15
        if has_cycle:
            score += 0.10
        
        # Bonus for multiple keyword matches
        if keyword_matches >= 3:
            score += 0.10
        elif keyword_matches >= 2:
            score += 0.05
        
        return min(score, 1.0)
    
    def analyze_email(self, subject: str, body: str, sender: str, 
                     email_date: datetime, message_id: str) -> Optional[Dict]:
        """Analyze a single email and return detection results."""
        full_text = f"{subject} {body}"
        
        # Check if subscription-related
        if not self.is_subscription_email(subject, body, sender):
            return None
        
        # Extract data
        price_result = self.extract_price(full_text)
        service = self.detect_service(subject, body, sender)
        cycle = self.detect_billing_cycle(full_text)
        detected_date = self.detect_date(full_text)
        
        # Count keyword matches
        text_lower = full_text.lower()
        keyword_matches = sum(1 for kw in SUBSCRIPTION_KEYWORDS if kw in text_lower)
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            has_price=price_result is not None,
            has_service=service is not None,
            has_date=detected_date is not None,
            has_cycle=cycle is not None,
            keyword_matches=keyword_matches,
        )
        
        if confidence < 0.3:
            return None
        
        return {
            'detected_service': service or 'Unknown Service',
            'detected_amount': price_result[0] if price_result else None,
            'detected_currency': price_result[1] if price_result else 'USD',
            'detected_billing_cycle': cycle or 'monthly',
            'detected_date': detected_date or email_date.date(),
            'confidence_score': round(confidence, 2),
            'detection_method': 'regex',
        }
    
    def analyze_email_batch(self, emails: List[Dict]) -> List[Dict]:
        """Analyze a batch of emails."""
        results = []
        
        for email in emails:
            result = self.analyze_email(
                subject=email.get('subject', ''),
                body=email.get('body', ''),
                sender=email.get('sender', ''),
                email_date=email.get('date', datetime.now()),
                message_id=email.get('message_id', ''),
            )
            
            if result:
                result.update({
                    'email_sender': email.get('sender'),
                    'email_subject': email.get('subject'),
                    'email_date': email.get('date'),
                    'email_message_id': email.get('message_id'),
                    'raw_email_snippet': email.get('snippet', ''),
                })
                results.append(result)
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return results


def get_detector():
    """Factory function to get detector instance."""
    return SubscriptionDetector()
