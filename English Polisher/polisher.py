import re
import os
from typing import List, Dict, Tuple
from json import loads

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

SYSTEM_PROMPTS = {
    "casual": """Eres un experto lingüista y editor especializado en inglés. Tu tarea es analizar, mejorar y corregir el texto en inglés que te proporcione el usuario, enfocándote en hacerlo más natural y coloquial.

Pautas de tono casual:
- Usa contracciones frecuentemente
- Incorpora jerga o expresiones coloquiales cuando sea apropiado
- Usa estructuras de oraciones variadas para darle ritmo
- Añade detalles específicos que demuestren autenticidad
- El tono debe sentirse conversacional y cercano""",
    "neutral": """Eres un experto lingüista y editor especializado en inglés. Tu tarea es analizar, mejorar y corregir el texto en inglés que te proporcione el usuario, enfocándote en hacerlo más natural.

Pautas de tono neutral:
- Equilibrio entre formal e informal
- Usa contracciones cuando suene natural
- Evita lenguaje demasiado técnico o demasiado coloquial
- Mantén un tono claro, directo y amigable""",
    "formal": """Eres un experto lingüista y editor especializado en inglés. Tu tarea es analizar, mejorar y corregir el texto en inglés que te proporcione el usuario, enfocándote en un registro formal y profesional.

Pautas de tono formal:
- Evita contracciones
- Usa vocabulario preciso y sofisticado
- Estructuras gramaticales completas y correctas
- Mantén un tono profesional y respetuoso"""
}

USER_PROMPT_SUFFIX = """

Output ONLY valid JSON with this exact format, no markdown, no explanation:
{
  "original": "texto original del usuario",
  "improved": "texto mejorado y pulido",
  "corrections": [
    {
      "orig": "texto original",
      "suggestion": "texto corregido",
      "explanation_es": "explicación en español",
      "type": "grammar|style"
    }
  ]
}

Reglas:
- Explica las correcciones gramaticales en español
- Evita negritas en el texto mejorado
- Mantén el significado original
- Palabras a evitar en el texto mejorado: "ahondar", "sumergirse", "discutible", "ciertamente", "consecuentemente", "por ende", "sin embargo", "de hecho", "además", "no obstante", "por lo tanto", "sin lugar a dudas", "hábil", "loable", "dinámico", "eficiente", "en constante evolución", "emocionante", "ejemplar", "innovador", "invaluable", "robusto", "fluido", "sinérgico", "que hace pensar", "en consonancia", "ampliar", "emprender", "facilitar", "maximizar", "resalta", "utilizar", "un testimonio de", "en conclusión", "en resumen", "es importante señalar", "vale la pena mencionar", "por el contrario", "esta no es una lista exhaustiva", "proporcionar ideas prácticas a través de un análisis profundo", "impulsar decisiones informadas", "aprovechar ideas"."""


def _fix_articles(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
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
    text = re.sub(r"\ba (\w)", repl, text)
    return text, corrections


def _capitalize_i(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
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
        pattern = re.compile(re.escape(long), re.IGNORECASE)
        def repl(m):
            orig = m.group(0)
            if orig[0].isupper():
                sug = short[0].upper() + short[1:]
            else:
                sug = short
            corrections.append({
                'orig': orig,
                'suggestion': sug,
                'explanation_es': "Contracción sugerida para un registro más coloquial.",
                'type': 'style'
            })
            return sug
        text = pattern.sub(repl, text)
    return text, corrections


def _simplify_that(text: str) -> Tuple[str, List[Dict]]:
    corrections = []
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


def polish_rules(text: str) -> Dict:
    orig = text
    corrections = []
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

    text = re.sub(r"\s+", " ", text)

    return {
        'original': orig,
        'improved': text,
        'corrections': corrections
    }


def polish_llm(text: str, tone: str = 'neutral') -> Dict:
    try:
        from openai import OpenAI
    except ImportError:
        return {
            'original': text,
            'improved': text,
            'corrections': [],
            'error': 'OpenAI package not installed. Run: pip install openai'
        }

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {
            'original': text,
            'improved': text,
            'corrections': [],
            'error': 'OPENAI_API_KEY environment variable not set.'
        }

    client = OpenAI(api_key=api_key)
    system_prompt = SYSTEM_PROMPTS.get(tone, SYSTEM_PROMPTS['neutral'])

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text + USER_PROMPT_SUFFIX}
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        content = content.strip('`').lstrip('json').strip()

        try:
            result = loads(content)
            result['original'] = text
            return result
        except Exception:
            return {
                'original': text,
                'improved': content,
                'corrections': [],
                'error': 'Could not parse LLM response as JSON.'
            }

    except Exception as e:
        return {
            'original': text,
            'improved': text,
            'corrections': [],
            'error': f'OpenAI API error: {str(e)}'
        }


def polish(text: str, mode: str = 'rules', tone: str = 'neutral') -> Dict:
    if mode == 'llm':
        return polish_llm(text, tone)
    return polish_rules(text)


if __name__ == '__main__':
    sample = "i am a student and i have informations about a hour. I think that we are ready."
    print(polish(sample))
