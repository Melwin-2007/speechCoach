import string

def parse_transcript(text: str) -> list[dict]:
    """
    Convert raw text into a list of structured word dictionaries.
    
    The output word dict must have the following keys:
    - i: int (0-based index)
    - raw: str (the raw word with punctuation attached)
    - norm: str (lowercase word, stripped of punctuation)
    - punct: str (the punctuation character attached after the word, if any)
    
    Valid punctuation characters to extract: "", ",", ".", ";", ":", "?", "!"
    """
    words = []
    raw_tokens = text.split()
    valid_punct = {",", ".", ";", ":", "?", "!"}
    
    for i, token in enumerate(raw_tokens):
        punct = ""
        # Check if the last character is a valid punctuation
        if token and token[-1] in valid_punct:
            punct = token[-1]
            raw_word_no_punct = token[:-1]
        else:
            raw_word_no_punct = token
            
        # Lowercase and strip any remaining non-alphanumeric chars at the ends
        # We use a specific set of chars to strip to preserve internal apostrophes like "don't"
        norm = raw_word_no_punct.lower().strip("""'",.;:?!”“"()""")
        
        words.append({
            "i": i,
            "raw": token,
            "norm": norm,
            "punct": punct
        })
        
    return words
