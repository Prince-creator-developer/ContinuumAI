"""
ContinuumAI - Zero-Trust Sanitizer & Redaction Module
Protects organizational privacy, API tokens, passwords, and executive compensation data
prior to embedding or presentation.
"""

import re
from typing import Dict, Any, Tuple

class DataSanitizer:
    def __init__(self):
        # High-precision deterministic regex rules for credentials and secrets
        self.secret_patterns = [
            (r'(?:sk_live_|sk_mock_|sk_test_)[0-9a-zA-Z_]{16,}', '[REDACTED_STRIPE_SECRET_KEY]'),
            (r'whsec_[0-9a-zA-Z]{16,}', '[REDACTED_WEBHOOK_SIGNING_SECRET]'),
            (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_ACCESS_KEY]'),
            (r'(?i)(?:password|passwd|secret|token)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', r'\1: [REDACTED_CREDENTIAL]'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[REDACTED_EMAIL]'),
            (r'\$\d{1,3}(?:,\d{3})*(?:k|K|\/mo|\/yr)?', '[REDACTED_FINANCIAL_FIGURE]')
        ]

    def sanitize_text(self, text: str, role: str = "engineering") -> Tuple[str, int]:
        """
        Sanitizes raw text and returns (sanitized_text, redactions_count).
        If role == 'contractor', strictly masks all internal financial & executive discussions.
        """
        if not text:
            return "", 0

        redacted_count = 0
        cleaned = text

        for pattern, replacement in self.secret_patterns:
            matches = re.findall(pattern, cleaned)
            if matches:
                redacted_count += len(matches)
                cleaned = re.sub(pattern, replacement, cleaned)

        # Contractor Role additional boundary masking
        if role == "contractor":
            confidential_patterns = [
                (r'(?i)salary.*', '[REDACTED_EXECUTIVE_DATA]'),
                (r'(?i)budget.*', '[REDACTED_FINANCIAL_BUDGET]'),
                (r'(?i)confidential.*', '[REDACTED_RESTRICTED_ACCESS]')
            ]
            for pattern, replacement in confidential_patterns:
                if re.search(pattern, cleaned):
                    redacted_count += 1
                    cleaned = re.sub(pattern, replacement, cleaned)

        return cleaned, redacted_count

sanitizer = DataSanitizer()
