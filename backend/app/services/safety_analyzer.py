import re
from typing import Dict, List, Optional, Tuple

# Cyberbullying and dangerous keyword lists categorized by severity
CYBERBULLYING_KEYWORDS = {
    "hate_speech": ["hate you", "kill yourself", "die", "loser", "ugly", "freak", "nobody likes you", "go away"],
    "threats": ["i will hurt you", "punch you", "watch your back", "beat you up"],
    "self_harm": ["suicide", "want to die", "hurt myself", "cut myself", "end my life"],
    "inappropriate": ["porn", "xxx", "gambling", "casino", "betting", "drugs", "buy pills", "weed"],
}

SUSPICIOUS_URL_PATTERNS = [
    r".*porn.*",
    r".*xxx.*",
    r".*casino.*",
    r".*betting.*",
    r".*torrent.*",
    r".*darkweb.*",
    r".*phishing.*",
]


class SafetyAnalyzer:
    @staticmethod
    def inspect_text(text: str) -> Optional[Dict[str, str]]:
        if not text:
            return None
        lowered = text.lower()
        for category, keywords in CYBERBULLYING_KEYWORDS.items():
            for kw in keywords:
                if kw in lowered:
                    severity = "critical" if category in ["threats", "self_harm"] else "warning"
                    return {
                        "category": category,
                        "matched_keyword": kw,
                        "severity": severity,
                        "description": f"Potential {category.replace('_', ' ')} detected: '{kw}'"
                    }
        return None

    @staticmethod
    def inspect_url(url: str) -> Optional[Dict[str, str]]:
        if not url:
            return None
        lowered = url.lower()
        for pattern in SUSPICIOUS_URL_PATTERNS:
            if re.search(pattern, lowered):
                return {
                    "category": "inappropriate_web",
                    "matched_keyword": pattern.replace(".*", ""),
                    "severity": "warning",
                    "description": f"Access to restricted or suspicious web domain: {url}"
                }
        return None


safety_analyzer = SafetyAnalyzer()

