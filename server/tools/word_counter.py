"""
Word counter tool
"""
import re
from collections import Counter

def count_words(text):
    """
    Count words, characters, paragraphs, and sentences in the given text
    
    Args:
        text (str): Input text to analyze
        
    Returns:
        dict: Dictionary containing various text statistics
    """
    if not text:
        return {
            'words': 0,
            'characters': 0,
            'characters_no_spaces': 0,
            'paragraphs': 0,
            'sentences': 0,
            'lines': 0,
            'average_words_per_sentence': 0,
            'most_common_words': [],
            'reading_time_minutes': 0
        }
    
    # Basic counts
    characters = len(text)
    characters_no_spaces = len(text.replace(' ', '').replace('\t', '').replace('\n', ''))
    
    # Count lines
    lines = len(text.split('\n'))
    
    # Count paragraphs (separated by double newlines or single newlines with content)
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    if paragraphs == 0:  # If no double newlines, count non-empty lines as paragraphs
        paragraphs = len([line for line in text.split('\n') if line.strip()])
    
    # Count sentences (basic sentence detection)
    sentence_endings = re.findall(r'[.!?]+', text)
    sentences = len(sentence_endings)
    if sentences == 0 and text.strip():  # If no sentence endings found but text exists
        sentences = 1
    
    # Count words (split by whitespace and filter out empty strings)
    words_list = [word.strip() for word in re.findall(r'\b\w+\b', text.lower())]
    words = len(words_list)
    
    # Calculate average words per sentence
    average_words_per_sentence = round(words / sentences, 1) if sentences > 0 else 0
    
    # Find most common words (excluding very short words)
    meaningful_words = [word for word in words_list if len(word) > 2]
    word_counter = Counter(meaningful_words)
    most_common_words = [
        {'word': word, 'count': count} 
        for word, count in word_counter.most_common(10)
    ]
    
    # Estimate reading time (average 200 words per minute)
    reading_time_minutes = round(words / 200, 1) if words > 0 else 0
    
    return {
        'words': words,
        'characters': characters,
        'characters_no_spaces': characters_no_spaces,
        'paragraphs': paragraphs,
        'sentences': sentences,
        'lines': lines,
        'average_words_per_sentence': average_words_per_sentence,
        'most_common_words': most_common_words,
        'reading_time_minutes': reading_time_minutes
    }
