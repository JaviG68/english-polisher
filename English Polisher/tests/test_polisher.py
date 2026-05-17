from polisher import polish


def test_simple_corrections():
    text = "i am a student and i have informations about a hour. I think that we are ready."
    result = polish(text)
    assert 'improved' in result
    assert result['improved'] != text
    # Expect at least capitalization and singular fix
    assert any(c['type'] == 'grammar' for c in result['corrections'])


def test_contractions_and_style():
    text = "I am sure we are going to do not worry."
    result = polish(text)
    assert any(c['type'] == 'style' for c in result['corrections'])
