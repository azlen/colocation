import json

with open('data.json', 'r') as f:
  data = json.loads(f.read())

context = 6

avg = {}
n = 0

for charA in data:
  for key in data[charA]:
    if key not in avg:
      avg[key] = {}
      for character in data:
        avg[key][character] = 0
        avg[key]['BLANK'] = 0
    
    if key != 'n':
      for charB in data[charA][key]:
        avg[key][charB] += data[charA][key][charB] * data[charA]['n']
    else:
      n += data[charA]['n']


for key in avg:
  for character in avg[key]:
    avg[key][character] /= float(n)


def get(char, pos):
  items = list(data[char][pos].items())
  items = list(map(lambda x: (x[0], x[1] ), items))
  items.sort(key=lambda x: x[1], reverse=True)

  for item in items[:30]:
    print(item)

# - avg[pos][char] * avg[pos][char] * 50
# / avg[pos][char]

#get('中', 'r2')
#get('国', 'r1')

def get2(query):
  output = list(map(lambda x: {} if x=='_' else {x:1.0}, query))
  for index in range(len(query)):
    if query[index] == '_':
      
      # for i in range(1, context + 1):
      #   key = 'r' + str(i)
      #   if index - i >= 0:
      #     char = query[index - i]
      #     if char != '_':
      #       for char2 in data[char][key]:
      #         if char2 not in output[index]:
      #           output[index][char2] = data[char][key][char2]
      #         else:
      #           output[index][char2] *= data[char][key][char2]
      for i in range(1, context + 1):
        for direction in [('l', i), ('r', -i)]:
          key = direction[0] + str(i)
          if index + direction[1] < len(query) and index + direction[1] >= 0:
            char = query[index + direction[1]]
            if char != '_':
              diff = set(output[index].keys()) ^ set(data[char][key].keys())

              #average = 0
              median = data[char][key][list(data[char][key].keys())[int(len(data[char][key])/2)]]

              if len(output[index].items()) == 0:
                for char2 in data[char][key]:

                  opposite = {'l':'r','r':'l'}[direction[0]] + str(i)
                  if char2 in data and char in data[char2][opposite]:
                    mult = data[char2][opposite][char]
                  else:
                    mult = 0.01
                  
                  #output[index][char2] = data[char][key][char2] * mult - avg[key][char2] / i
                  output[index][char2] = data[char][key][char2] * mult / median
              else:
                marked = []
                for char2 in output[index]:
                  
                  opposite = {'l':'r','r':'l'}[direction[0]] + str(i)
                  if char2 in data and char in data[char2][opposite]:
                    mult = data[char2][opposite][char]
                  else:
                    mult = 0.01

                  if char2 in data[char][key]:
                    #average = avg[key][char2]
                    #output[index][char2] *= data[char][key][char2] * mult - avg[key][char2] / i
                    output[index][char2] *= data[char][key][char2] * mult / median
                  else:
                    marked.append(char2)
                
                for x in marked:
                  # del output[index][x]
                  output[index][x] *= 0.001
            # print(diff)
            # for x in diff:
            #   del output[index][x]
  return output

def get3(query):
  output = get2(query)
  for i in range(len(output)):
    prediction = output[i]
    items = list(prediction.items())
    items.sort(key=lambda x: x[1], reverse=True)
    output[i] = list(map(lambda x: x[0], items[:5]))
  return output