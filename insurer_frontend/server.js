
const https = require('https');
const fs = require('fs');
const path = require('path');
const express = require('express');

const app = express();

app.use(express.static(path.join(__dirname, 'build')));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const options = {
  key: fs.readFileSync('/etc/letsencrypt/live/ims.icp-insurance-system.ru/privkey.pem'), // Путь к приватному ключу
  cert: fs.readFileSync('/etc/letsencrypt/live/ims.icp-insurance-system.ru/fullchain.pem'), // Путь к сертификату
};

const port = 4000;
https.createServer(options, app).listen(port, '0.0.0.0', () => {
  console.log(`HTTPS сервер запущен на https://0.0.0.0:${port}`);
});
