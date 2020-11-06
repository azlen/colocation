from dragonmapper import hanzi
import pinyin
import json

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from nlp import endpoint, is_chinese
# from prob import get3

verbose = False

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'

@app.route('/')
def index():
  return 'Server Works!'
  
@app.route('/pinyin/number/<chinese>')
@cross_origin()
def get_pinyin_number(chinese):
  return pinyin.get(chinese, format="numerical", delimiter=" ")

@app.route('/pinyin/tone/<chinese>')
@cross_origin()
def get_pinyin_tone(chinese):
  return pinyin.get(chinese, delimiter=" ")

# @app.route('/prob/<template>')
# @cross_origin()
# def get_probabilities(template):
#   return json.dumps(get3(template))

@app.route('/prob/<template>')
@cross_origin()
def get_nlp_probabilities(template):
  out_chars = []
  chunks = []
  cur_mask = None
  if verbose: print(f'Template: {template}')
  for char in template:
    if char == '_':
      if cur_mask is not True:
        chunks.append(char)
        cur_mask = True
        continue
    else:
      if cur_mask is not False:
        chunks.append(char)
        cur_mask = False
        continue
    chunks[-1] += char
  if verbose: print(f'Chunks: {chunks}')
  for i, chunk in enumerate(chunks):
    if chunk.startswith('_'):
      # let's do some inference
      start = chunks[i - 1] if i != 0 else ''
      end = chunks[i + 1] if i < len(chunks) - 1 else ''
      mask_len = len(chunk)
      if verbose: print(f'start: {start}, end: {end}, mask_len: {mask_len}')
      fill = endpoint(start, end, mask_len)['chars'][:8]
      if verbose: print(f'fill: {fill}')
      for i in range(mask_len):
        out_chars.append([])
        for sentence in fill:
          out_chars[-1].append(sentence[i + len(start)])
        char_set = []
        for char in out_chars[-1]:
          if char not in char_set and is_chinese(char): char_set.append(char)
        out_chars[-1] = char_set
      if verbose: print(out_chars)
    else:
      for char in chunk:
        out_chars.append([char])
      if verbose: print(out_chars)
  return jsonify(
    out_chars
  )


app.run('0.0.0.0', port=5000)
