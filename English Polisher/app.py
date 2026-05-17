from flask import Flask, render_template, request, jsonify
from polisher import polish

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/polish', methods=['POST'])
def api_polish():
    data = request.get_json() or {}
    text = data.get('text') or request.form.get('text') or ''
    if not isinstance(text, str):
        return jsonify({'error': 'text must be a string'}), 400
    result = polish(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
