async function getContacts(client) {
    const contacts = await client.getContacts();

    const contactosValidos = contacts
        .filter(contact => contact.id.server !== 'lid' && contact.isMyContact && contact.number != 0)
        .map(async contact => {
            try {
                return {
                    id: contact.id._serialized,
                    name: contact.name || contact.pushname || '',
                    number: await contact.getFormattedNumber()
                };
            } catch (err) {
                console.warn(`Error con contacto ${contact.id._serialized}: ${err.message}`);
                return null;
            }
        });

    return await Promise.all(contactosValidos);
}

module.exports = { getContacts }