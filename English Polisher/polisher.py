import re
from typing import List, Dict, Tuple

# A small, conservative rule-based polisher.
# It returns a dict with keys: original, improved, corrections (list).

COMMON_SINGULARS = {
    "informations": "information",
    "advices": "advice",
    "furnitures": "furniture",
}

CONTRACTIONS = {
    "I am": "I'm",
    "I will": "I'll",
    "do not": "don't",
    "does not": "doesn't",
    "did not": "didn't",
    "we are": "we're",
    "they are": "they're",
}

def _fix_articles(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
    # a -> an before vowel sound (simple vowel check)
    def repl(match):
        a = match.group(0)
        next_char = match.group(1)
        if next_char.lower() in 'aeiou':
            suggestion = 'an ' + next_char
            corrections.append({
                'orig': a + next_char,
                'suggestion': suggestion,
                'explanation_es': "Se usa 'an' antes de sonidos vocálicos; aquí suena mejor 'an'.",
                'type': 'grammar'
            })
            return 'an ' + next_char
        return a + next_char

    # This is conservative: only replace when pattern 'a [vowel]' (space kept)
    text = re.sub(r"\ba (\w)", repl, text)
    return text, corrections


def _capitalize_i(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
    # capitalize standalone i -> I
    def repl(match):
        orig = match.group(0)
        if orig == ' i ':
            corrections.append({
                'orig': ' i ',
                'suggestion': ' I ',
                'explanation_es': "La primera persona singular siempre se escribe 'I' en mayúscula en inglés.",
                'type': 'grammar'
            })
            return ' I '
        return orig

    # Surround with spaces to be conservative
    new_text = re.sub(r"\bi\b", lambda m: 'I' if m.group(0) == 'i' else m.group(0), text)
    if new_text != text:
        corrections.append({
            'orig': 'i (minúscula)',
            'suggestion': 'I (mayúscula)',
            'explanation_es': "La primera persona singular debe ser 'I' en mayúscula.",
            'type': 'grammar'
        })
    return new_text, corrections


def _fix_common_singulars(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
    for wrong, right in COMMON_SINGULARS.items():
        if wrong in text:
            corrections.append({
                'orig': wrong,
                'suggestion': right,
                'explanation_es': f"'{wrong}' no es correcto en inglés; se usa '{right}' como no contable o singular.",
                'type': 'grammar'
            })
            text = text.replace(wrong, right)
    return text, corrections


def _apply_contractions(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
    for long, short in CONTRACTIONS.items():
        # case-insensitive replace, but preserve case when at start of sentence naive
        pattern = re.compile(re.escape(long), re.IGNORECASE)
        def repl(m):
            orig = m.group(0)
            # preserve capitalization
            if orig[0].isupper():
                sug = short[0].upper() + short[1:]
            else:
                sug = short
            corrections.append({
                'orig': orig,
                'suggestion': sug,
                'explanation_es': "Contratón sugerido para un registro más coloquial.",
                'type': 'style'
            })
            return sug
        text = pattern.sub(repl, text)
    return text, corrections


def _simplify_that(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
    # remove optional 'that' after verbs like 'think that' -> 'think'
    pattern = re.compile(r"\b(think|believe|say|feel|hope) that\b", re.IGNORECASE)
    def repl(m):
        verb = m.group(1)
        corrections.append({
            'orig': m.group(0),
            'suggestion': verb,
            'explanation_es': "Eliminar 'that' hace la oración más natural y coloquial en muchos casos.",
            'type': 'style'
        })
        return verb
    new_text = pattern.sub(repl, text)
    return new_text, corrections


def polish(text: str) -> Dict:
    """Return a conservative polished version and list of corrections with Spanish explanations.

    Output shape:
    {
        'original': str,
        'improved': str,
        'corrections': [ {orig, suggestion, explanation_es, type}... ]
    }
    """
    orig = text
    corrections = []

    # Normalize whitespace
    text = text.strip()

    t, c = _capitalize_i(text)
    text = t
    corrections.extend(c)

    t, c = _fix_common_singulars(text)
    text = t
    corrections.extend(c)

    t, c = _fix_articles(text)
    text = t
    corrections.extend(c)

    t, c = _apply_contractions(text)
    text = t
    corrections.extend(c)

    t, c = _simplify_that(text)
    text = t
    corrections.extend(c)

    # Simple punctuation fixes: collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return {
        'original': orig,
        'improved': text,
        'corrections': corrections
    }


if __name__ == '__main__':
    sample = "i am a student and i have informations about a hour. I think that we are ready."
    print(polish(sample))
