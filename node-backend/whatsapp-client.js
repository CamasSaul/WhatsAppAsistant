const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const app = express();
app.use(express.json());
const { getContacts } = require('./whatsapp-normalizer');

const client = new Client({ authStrategy: new LocalAuth() });
let QRcode = '';
let ready = false;

client.on('qr', (qr) => {
  QRcode = qr;
  console.log('QR code generated.');
});

client.on('ready', () => {
  console.log('Client ready.');
  ready = true;
});

client.on('message', (msg) => {
  console.log('Message received:', msg.body);
  // Send message to FastAPI server
  fetch('http://0.0.0.0:3701/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        content: msg.body,
        from: msg.from,
        type: msg.type,
        timestamp: msg.timestamp
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    console.log('Message sent to FastAPI server:', data);
  })
  .catch(error => {
    console.error('Error sending message to FastAPI server:', error);
  });
});


// Root endpoint
app.get('/', (req, res) => {
  if (ready) {
    return res.send({ status: 'READY' });
  }
  if (QRcode) {
    return res.status(503).send({ status : 'WAITING FOR LOGIN', reason: 'Waiting for QR code to be scanned.'});
  }
  return res.status(503).send({ status : 'NOT READY', reason: 'QR code not generated yet.'});
});


app.get('/contacts', async (req, res) => {
  /**
   * Returns a list of all contacts registered in the connected WhatsApp account.
   * Each contact contains basic information like name, phone number and profile details.
   */
  if (!ready) {
        res.send('Client not ready.');
        return;
    }
    const contacts = await getContacts(client);
    res.send(contacts);
});


// Return de message history from an especific contact
app.get('/messages', async (req, res) => {
    if (!ready) {
        res.send('Client not ready.');
        return;
    }
    const id = req.query.id;
    const length = req.query.length || 10;
    const chat = await (await client.getChatById(id)).fetchMessages({ limit: parseInt(length) });
    let messages = [];
    chat.forEach(message => {
        messages.push({
            content: message.body,
            _from: message.from,
            type: message.type,
            timestamp: message.timestamp
        });
    });
    res.send(messages);
});



// Get temporal pic_url
app.get('/pic', async (req, res) => {
    if (!ready) {
        res.send('Client not ready.');
        return;
    }
    const id = req.query.id;
    const contact = await client.getContactById(id);
    const pic_url = await contact.getProfilePicUrl();
    res.send(pic_url);
})



// Get raw QR code to login
app.get('/qr', (req, res) => {
  if (!QRcode) {
    res.status(404).send('No QR code generated yet.');
    return;
  }
  res.send(QRcode);
});


// POST send a message to an especific contact
app.post('/send', async (req, res) => {
    if (!ready) {
        res.send('Client not ready.');
        return;
    }
    try {
      const id = req.body.id;
      const content = req.body.content;
      const chat = await client.getChatById(id);
      chat.sendMessage(content);
      return res.send('Message sent.');
    } catch (error) {
      return res.status(500).send({status : 'Error sending message.', reason: error.message});
    }
});

client.initialize();
app.listen(3700);