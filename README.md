# Messaging Assistant for WhatsApp Web

## How does it work?
This is a prototype of a messaging assistant for WhatsApp Web.  
It acts as an intermediary between you and your contacts.  
Provide the assistant with information so it knows what to do and how to respond to the messages it receives.

## How to use:
- Once the system is running, log in by scanning the QR code with the WhatsApp mobile app.
- Currently, there is no user interface. To add a contact for automation, you must manually add it in the source code at:  
  `/sources/server.py`, line 73.

### Installation:
- Install or create a __Python 3.11__ environment (it’s very important to use a version between 3.8 and 3.11).
- Install Node.js on your system.
- Clone the repository and run the following commands:

```bash
npm install --prefix node-backend
```

```bash
pip install -r requirements.txt
```
- You’ll need your own Google GenAI API key for the system to work.
- Finally, run ``main.py``:

```bash
python main.py
```

### Screenshots:
- Interacción breve con el asistente:



### Notes
- This project is still under development.
- It only works on Windows.
- There are still many bugs.