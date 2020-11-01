from dragonmapper import hanzi
import pinyin
from prob import get3
import json

from flask import Flask
from flask_cors import CORS, cross_origin
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

@app.route('/prob/<template>')
@cross_origin()
def get_probabilities(template):
  return json.dumps(get3(template))