import json
import random

import numpy as np
import tensorflow as tf

IGNORE_CHARS = ['\n']


def is_chinese(char):
  if char < u'\u4e00' or char > u'\u9fff':
    return False
  return True


extra_chars = ['𝑢', '𝑚', '𝑒']  # unknown, mask, end


class Tokenizer:
  def __init__(self, load=True):
    self.full_table = {}
    if load:
      self.table = json.load(tf.io.gfile.GFile('./data/tokenizer_table.json', 'r'))
      for e in extra_chars:
        self.table[e] = 0
      self.table_lookup = {k: i for i, k in enumerate(self.table.keys())}
      self.vocab_size = len(self.table_lookup)
    else:
      self.table = {}

  def call(self, text):
    idxs = []
    for char in text:
      idx = self.table_lookup[char] if char in self.table_lookup else self.vocab_size - 1
      idxs.append(idx)
    return idxs


class CharLSTM(tf.keras.Model):
  def __init__(self, model_dim=768, num_cells=3):
    super(CharLSTM, self).__init__()
    self.tokenizer = Tokenizer()
    self.char_embed = tf.keras.layers.Dense(model_dim)
    self.cells = [tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(model_dim, return_sequences=True)) for _ in range(num_cells)]
    self.pos = [tf.keras.layers.Dense(model_dim) for _ in range(num_cells)]
    self.bns = [tf.keras.layers.BatchNormalization() for _ in range(num_cells)]
    self.final_cell = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(model_dim))
    self.cls = tf.keras.layers.Dense(self.tokenizer.vocab_size)
    self.chars = list(self.tokenizer.table.keys())

  def encode_string(self, text):
    idxs = [self.tokenizer.call(text_) for text_ in text]
    oh = tf.one_hot(idxs, depth=self.tokenizer.vocab_size)
    assert tf.reduce_all(tf.reduce_sum(oh, axis=-1) == 1)
    return oh

  def call(self, text, inference=False):
    """Predict the next token
    """
    oh = self.encode_string(text)
    x = self.char_embed(oh)
    for cell in self.cells:
      x = cell(x)
      if not inference:
        x = tf.nn.dropout(x, rate=0.3)
    x = self.final_cell(x)
    x = self.cls(x)
    x = tf.nn.softmax(x, axis=-1)
    return x

  def train_step(self, text):
    """Bidirectional LSTM with teacher forcing
    """
    text = [a.decode() for a in text.numpy()]
    text_len = random.randint(12, 24)
    text = [t[:text_len] for t in text]
    mask_len = random.randint(1, 3)
    start = random.randint(0, len(text[0]) - mask_len)
    end = start + mask_len
    X = [t[:start] + '𝑚' * mask_len + t[end:] for t in text]
    X = [x + '𝑒' for x in X]
    for step in range(mask_len):
      label_string = [t[start + step] for t in text]
      labels = self.encode_string(label_string)[:, 0, :]
      # if random.randint(0, 128) == 0:
      #   print(X[0])
      #   print(label_string[0])
      #   print(text[0])
      with tf.GradientTape() as tape:
        pred = self.call(X)
        loss = self.loss(labels, pred)        
      X = [x[:start + step] + l + x[start + step:] for x, l in zip(X, label_string)]
      gradients = tape.gradient(loss, self.trainable_variables)
      self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
      mae = tf.keras.metrics.mean_absolute_error(labels, pred)
    return {
      'loss': loss,
      'mae': mae
    }

  def inference(self, sentence, k=64):
    """Get top completions for a single sentence
    """
    result = self.call([sentence], inference=True)
    ranked = tf.math.top_k(result[0], k=k)
    return {self.chars[i]: prob.numpy() for prob, i in zip(ranked.values, ranked.indices)}


# PREPARE MODELS
model = CharLSTM()
model.inference("你好")
model.load_weights('./data/bilstm-768-contd.ckpt')


def beam_search(text, num_branches=3, verbose=False):
  cands, probs = [text], [0]
  all_cands, all_probs = [], []
  while len(cands) > 0:
    cand, prob = cands.pop(), probs.pop()
    if '𝑚' not in cand:
      continue
    for next_cand, next_prob in model.inference(cand, k=num_branches).items():
      new_cand = cand.replace('𝑚', next_cand, 1)
      if verbose:
        print(cand, prob, ':', new_cand, prob + next_prob)
      if '𝑚' not in new_cand:
        all_cands.append(new_cand)
        all_probs.append(prob + next_prob)
      cands.append(new_cand)
      probs.append(prob + next_prob)
  all_cands = [c[:-1] for c in all_cands]
  idxs = np.argsort(all_probs)[::-1]
  all_cands, all_probs = select_from_lists(idxs, all_cands, all_probs)
  return {'chars': all_cands, 'probs': all_probs}


def endpoint(start='', end='', mask_len=1):
  inp = start + '𝑚' * mask_len + end + '𝑒'
  return beam_search(inp)


def select_from_lists(idxs, *lists):
  out = []
  for l_ in lists:
    out.append([l_[idx] for idx in idxs])
  return out

# endpoint(start='大', end='好', mask_len=1)
