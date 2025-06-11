from source.db_manager import DBManager

if __name__ == '__main__':
    #App().run()
    #App().run(debug=True)
    db = DBManager('data/data.db')
    #db.save_contact(('456@us.c', 'Juan', '123456789', 'Edad:19', False))
    db.save_message((223456789, '123@us.c', 'Hola', 'TEXT', ))
    print(db.fetch_messages())