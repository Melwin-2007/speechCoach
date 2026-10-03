import re

try:
    import cmudict
    cmu = cmudict.dict()
except ImportError:
    cmu = None

def count_syllables(word: str) -> int:
    """
    Count syllables using cmudict with a regex fallback.
    """
    word = word.lower()
    # Remove punctuation
    word = re.sub(r'[^a-z]', '', word)
    
    if not word:
        return 0
        
    if cmu is not None and word in cmu:
        # cmudict gives list of phoneme lists. We take the first pronunciation.
        # Syllables correspond to phonemes ending with a digit (stress marker).
        phonemes = cmu[word][0]
        return len([p for p in phonemes if p[-1].isdigit()])
        
    # Regex fallback heuristic
    # Remove trailing 'e' (usually silent, except for small words like 'the')
    if len(word) > 2 and word.endswith('e') and not word.endswith('le'):
        word = word[:-1]
        
    vowels = re.findall(r'[aeiouy]+', word)
    return max(1, len(vowels))
