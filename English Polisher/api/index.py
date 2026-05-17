from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/polish', methods=['POST'])
def api_polish():
    data = request.get_json() or {}
    text = data.get('text') or request.form.get('text') or ''
    mode = data.get('mode', 'rules')
    tone = data.get('tone', 'neutral')
    if not isinstance(text, str):
        return jsonify({'error': 'text must be a string'}), 400
    from polisher import polish
    result = polish(text, mode=mode, tone=tone)
    return jsonify(result)
