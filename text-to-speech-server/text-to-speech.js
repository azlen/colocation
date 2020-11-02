// Imports the Google Cloud client library
const textToSpeech = require('@google-cloud/text-to-speech');

// Import other required libraries
const fs = require('fs');
const util = require('util');

const express = require('express')
const cors = require('cors')
const app = express()
const port = 3000
const bodyParser = require('body-parser');

app.use(cors())

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static('public'))

app.post('/speak', (req, res) => {
  let text = req.body.text;
  let speakingRate = req.body.speakingRate || 0.7;
  console.log(speakingRate)
  getSpeech(text).then(filename => res.send(filename));
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})


// Creates a client
const client = new textToSpeech.TextToSpeechClient();
async function getSpeech(text, speakingRate) {
  // Construct the request
  const request = {
    input: {text: text},
    // Select the language and SSML voice gender (optional)
    voice: {languageCode: 'cmn-CN', ssmlGender: 'NEUTRAL'},
    // select the type of audio encoding
    audioConfig: {audioEncoding: 'MP3', speakingRate: speakingRate},
  };

  // Performs the text-to-speech request
  const [response] = await client.synthesizeSpeech(request);
  // Write the binary audio content to a local file
  const writeFile = util.promisify(fs.writeFile);
  
  let filename = new Date().getTime().toString() + '.mp3';
  await writeFile('public/' + filename, response.audioContent, 'binary');
  console.log('Audio content written to file: ' + filename);
  return filename;
}
// getSpeech('你好，我叫拉菲');