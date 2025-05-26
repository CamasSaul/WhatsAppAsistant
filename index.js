const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const client = new Client({ authStrategy: new LocalAuth() });

client.on('qr', qr => qrcode.generate(qr, { small: true }));
client.on('ready', async () => {
    console.log('Conectado a WhatsApp');

    const contacts = await client.getContacts();

    // Filtrar solo contactos con número real
    const contactosValidos = contacts
        .filter(contact => contact.isMyContact && contact.id.user.startsWith('521'))
        .map(contact => ({
            nombre: contact.name || contact.pushname || '',
            numero: contact.number
        }));

    // Exportar a CSV
    const csvWriter = createCsvWriter({
        path: 'contactos_whatsapp.csv',
        header: [
            { id: 'nombre', title: 'Nombre' },
            { id: 'numero', title: 'Número' },
        ]
    });

    await csvWriter.writeRecords(contactosValidos);
    console.log(`Exportados ${contactosValidos.length} contactos a 'contactos_whatsapp.csv'`);

    const chats = await client.getChats();
    for (const chat of chats) {
        //console.log(`Contacto no válido: ${chat.name}`)
        const contacto = contactosValidos.find(c => c.nombre === chat.name)
        if (contacto) {
            chat_path = `chats/${chat.name}/${chat.name}.txt`
            if (fs.existsSync(chat_path)) {
                fs.writeFileSync(chat_path, '', 'utf8');
                console.log(`Chat encontrado con: ${chat.name || chat.id.user}`);
                const messages = await chat.fetchMessages({ limit: 50 });
                messages.forEach(msg => {
                    const autor = msg.fromMe ? 'Yo' : chat.name;
                    console.log(`[${new Date(msg.timestamp * 1000).toLocaleString()}] ${autor}: ${msg.body}`);
                    fs.appendFileSync(
                        `chats/${chat.name}/${chat.name}.txt`,
                        `[${new Date(msg.timestamp * 1000).toLocaleString()}] ${autor}: ${msg.body}\n`,
                        'utf8'
                    );
                });
            }
        }
    }
});

client.on('message', async msg => {
    console.log(`Mensaje de ${msg.from}: ${msg.body}`);

    try {
        console.log('Conectando con localhost...')
        const res = await axios.post('http://localhost:8000/analyze', {
            from_: msg.from,
            body: msg.body
        });

        if (res.data && res.data.reply) {
            await msg.reply(res.data.reply);
            console.log(`Respuesta enviada: ${res.data.reply}`);
        }
    } catch (error) {
        console.error("Error en la API:", error.message);
    }
});

client.initialize();