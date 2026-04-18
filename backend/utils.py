"""
Utility functions for text processing and analysis
"""

import re
from typing import List


class TextUtils:
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extra whitespace and normalize"""
        return re.sub(r'\s+', ' ', text.strip())
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """Get word count"""
        return len(text.split())
    
    @staticmethod
    def get_character_count(text: str) -> int:
        """Get character count"""
        return len(text)
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def highlight_matches(text: str, matches: List[dict], is_primary: bool = True) -> str:
        """Highlight matching phrases in text"""
        if not matches:
            return text
        
        highlighted = text
        color = "style='background: rgba(239, 68, 68, 0.2); border-bottom: 2px solid #ef4444; padding: 2px 4px; border-radius: 4px;'"
        
        # Sort matches by length (longest first) to avoid nested highlighting issues
        sorted_matches = sorted(matches, key=lambda x: len(x['text']), reverse=True)
        
        used_ranges = []
        
        for match in sorted_matches:
            pattern = re.escape(match['text'])
            # Find all occurrences
            for m in re.finditer(pattern, highlighted, re.IGNORECASE):
                start = m.start()
                end = m.end()
                
                # Check for overlaps
                overlap = any(start < r['end'] and end > r['start'] for r in used_ranges)
                
                if not overlap:
                    used_ranges.append({'start': start, 'end': end})
                    before = highlighted[:start]
                    matched = highlighted[start:end]
                    after = highlighted[end:]
                    highlighted = f"{before}<{color}>{matched}</span>{after}"
        
        return highlighted