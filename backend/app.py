"""
Flask Backend for Plagiarism Checker
API Endpoints for text similarity analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from algorithms import PlagiarismAlgorithms
from utils import TextUtils
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize algorithms
plagiarism_checker = PlagiarismAlgorithms()
text_utils = TextUtils()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Plagiarism Checker API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    Main analysis endpoint
    Accepts: { text1: string, text2: string, mode: 'compare'|'single' }
    Returns: Similarity analysis results
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text1 = data.get('text1', '').strip()
        mode = data.get('mode', 'compare')
        
        if not text1:
            return jsonify({'error': 'Text1 is required'}), 400
        
        if mode == 'single':
            # In single mode, compare against a database of common phrases
            common_phrases = [
                "in conclusion", "on the other hand", "for example",
                "as a result", "furthermore", "moreover",
                "it is important to note", "research shows that",
                "studies have found", "according to experts"
            ]
            # Create simulated text from common phrases
            text2 = '. '.join(common_phrases) + '. ' + text1[:100]
            results = plagiarism_checker.calculate_plagiarism_score(text1, text2)
            # Adjust score for single mode (lower threshold)
            results['similarity'] = round(results['similarity'] * 0.7, 2)
            results['mode'] = 'single'
            
        else:
            text2 = data.get('text2', '').strip()
            
            if not text2:
                return jsonify({'error': 'Both texts are required for comparison'}), 400
            
            results = plagiarism_checker.calculate_plagiarism_score(text1, text2)
            results['mode'] = 'compare'
        
        # Add text utilities
        results['text_stats'] = {
            'text1_chars': text_utils.get_character_count(text1),
            'text1_words': text_utils.get_word_count(text1),
            'text2_chars': text_utils.get_character_count(data.get('text2', '')),
            'text2_words': text_utils.get_word_count(data.get('text2', ''))
        }
        
        # Generate highlighted versions if in compare mode
        if mode == 'compare':
            matches = results.get('matches', [])
            results['highlighted_text1'] = text_utils.highlight_matches(
                text1, matches, True
            )
            results['highlighted_text2'] = text_utils.highlight_matches(
                data.get('text2', ''), matches, False
            )
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': str(e.__traceback__)}), 500


@app.route('/api/detailed-analysis', methods=['POST'])
def detailed_analysis():
    """
    Detailed phrase-level analysis
    Returns: List of matching phrases with context
    """
    try:
        data = request.get_json()
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()
        
        if not text1 or not text2:
            return jsonify({'error': 'Both texts required'}), 400
        
        # Get detailed matches
        matches = plagiarism_checker.find_matching_phrases(text1, text2, min_length=3)
        
        # Add context to each match
        detailed_matches = []
        sentences1 = text1.split('. ')
        sentences2 = text2.split('. ')
        
        for match in matches:
            detailed_matches.append({
                'phrase': match['text'],
                'matched_phrase': match['matched_text'],
                'similarity_score': match['similarity'],
                'match_type': match['type'],
                'context_before': '...',
                'context_after': '...'
            })
        
        return jsonify({
            'matches': detailed_matches,
            'total_matches': len(matches),
            'analysis_timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file-upload', methods=['POST'])
def file_upload():
    """Handle file uploads and extract text"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Read file content
        try:
            if file.filename.endswith('.pdf'):
                return jsonify({
                    'error': 'PDF processing requires PyPDF2. Install: pip install PyPDF2'
                }), 400
            
            elif file.filename.endswith(('.doc', '.docx')):
                return jsonify({
                    'error': 'Word document processing requires python-docx. Install: pip install python-docx'
                }), 400
            
            else:
                content = file.read().decode('utf-8')
                return jsonify({
                    'filename': file.filename,
                    'content': content,
                    'length': len(content)
                })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
