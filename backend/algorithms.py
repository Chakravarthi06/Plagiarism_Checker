"""
Core Plagiarism Detection Algorithms
Implements multiple algorithms for accurate similarity detection
"""

import re
import math
from typing import List, Dict, Set
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class PlagiarismAlgorithms:
    def __init__(self):
        self.ngram_size = 3  # Trigrams for shingling
    
    def preprocess_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation but keep sentence structure
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def create_shingles(self, text: str, n: int = None) -> Set[str]:
        """Create n-grams (shingles) from text"""
        if n is None:
            n = self.ngram_size
            
        words = text.split()
        if len(words) < n:
            return set(words)
        
        shingles = set()
        for i in range(len(words) - n + 1):
            shingle = ' '.join(words[i:i + n])
            shingles.add(shingle)
        return shingles
    
    def jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity using n-grams"""
        shingles1 = self.create_shingles(text1)
        shingles2 = self.create_shingles(text2)
        
        if not shingles1 or not shingles2:
            return 0.0
        
        intersection = shingles1.intersection(shingles2)
        union = shingles1.union(shingles2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def longest_common_subsequence(self, str1: str, str2: str) -> str:
        """Find longest common subsequence between two strings"""
        words1 = str1.split()
        words2 = str2.split()
        
        m, n = len(words1), len(words2)
        
        # Create DP table
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if words1[i - 1] == words2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        # Reconstruct LCS
        lcs = []
        i, j = m, n
        while i > 0 and j > 0:
            if words1[i - 1] == words2[j - 1]:
                lcs.append(words1[i - 1])
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
        
        return ' '.join(reversed(lcs))
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        # Tokenize and filter words
        words1 = [w for w in word_tokenize(text1.lower()) if w.isalpha() and len(w) > 2]
        words2 = [w for w in word_tokenize(text2.lower()) if w.isalpha() and len(w) > 2]
        
        if not words1 or not words2:
            return 0.0
        
        # Create frequency vectors
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(freq1.keys()) | set(freq2.keys())
        
        # Calculate dot product and magnitudes
        dot_product = sum(freq1.get(w, 0) * freq2.get(w, 0) for w in all_words)
        mag1 = math.sqrt(sum(f ** 2 for f in freq1.values()))
        mag2 = math.sqrt(sum(f ** 2 for f in freq2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def find_matching_phrases(self, text1: str, text2: str, min_length: int = 4) -> List[Dict]:
        """Find exact and partial matching phrases"""
        matches = []
        sentences1 = sent_tokenize(text1)
        sentences2 = sent_tokenize(text2)
        
        # Check for sentence-level matches
        for i, sent1 in enumerate(sentences1):
            clean1 = self.preprocess_text(sent1)
            if len(clean1) < min_length:
                continue
                
            for j, sent2 in enumerate(sentences2):
                clean2 = self.preprocess_text(sent2)
                if len(clean2) < min_length:
                    continue
                
                # Check for exact match
                if clean1 == clean2:
                    similarity = 100.0
                    matches.append({
                        'text': sent1,
                        'matched_text': sent2,
                        'type': 'exact',
                        'similarity': round(similarity, 2),
                        'position': {'text1': i, 'text2': j}
                    })
                    break
                
                # Check for partial containment (one contains the other)
                elif clean1 in clean2 or clean2 in clean1:
                    # Determine which is the container
                    if clean1 in clean2:
                        longer_len = len(clean2)
                        shorter_len = len(clean1)
                    else:
                        longer_len = len(clean1)
                        shorter_len = len(clean2)
                    
                    similarity = (shorter_len / longer_len) * 100
                    matches.append({
                        'text': sent1,
                        'matched_text': sent2,
                        'type': 'partial',
                        'similarity': round(similarity, 2),
                        'position': {'text1': i, 'text2': j}
                    })
        
        # Sort by similarity (highest first) and limit to top 10
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches[:10]
    
    def calculate_plagiarism_score(self, text1: str, text2: str) -> Dict:
        """Main method combining multiple algorithms"""
        # Preprocess texts
        clean1 = self.preprocess_text(text1)
        clean2 = self.preprocess_text(text2)
        
        if not clean1 or not clean2:
            return {
                'similarity': 0,
                'matches': [],
                'algorithm_scores': {},
                'metadata': {}
            }
        
        # Calculate individual scores
        jaccard = self.jaccard_similarity(clean1, clean2)
        lcs = self.longest_common_subsequence(clean1, clean2)
        cosine = self.cosine_similarity(clean1, clean2)
        
        # Weighted combination
        # Jaccard: 40%, LCS: 40%, Cosine: 20%
        lcs_score = len(lcs) / max(len(clean1), len(clean2)) if clean1 and clean2 else 0
        
        combined_score = (
            jaccard * 0.4 + 
            lcs_score * 0.4 + 
            cosine * 0.2
        )
        
        # Find matching phrases
        matches = self.find_matching_phrases(text1, text2)
        
        return {
            'similarity': round(min(combined_score * 100, 100), 2),
            'matches': matches,
            'algorithm_scores': {
                'jaccard': round(jaccard * 100, 2),
                'lcs': round(lcs_score * 100, 2),
                'cosine': round(cosine * 100, 2)
            },
            'metadata': {
                'text1_length': len(text1),
                'text2_length': len(text2),
                'text1_words': len(clean1.split()),
                'text2_words': len(clean2.split())
            }
        }