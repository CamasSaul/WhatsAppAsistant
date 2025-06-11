import sqlite3 as sql
import os

DB_PATH = 'data/data.db'


class DBManager:
    def __init__ (self):
        if not os.path.exists(DB_PATH):
            self.conn = sql.connect(DB_PATH)
            self.cur = self.conn.cursor()
            with open('data/schema.sql', 'r') as f:
                schema = f.read()
                self.cur.executescript(schema)
                self.conn.commit()
            print('Database created.')
        else:
            self.conn = sql.connect(DB_PATH)
            self.cur = self.conn.cursor()


    def __del__ (self):
        self.conn.close()


    def fetch_contacts (self, conditions:any=None) -> list:
        """conditions: str or list"""
        query = 'SELECT * FROM contacts '
        if isinstance(conditions, str):
            query += 'WHERE '
            query += conditions
        if isinstance(conditions, list):
            query += 'WHERE '
            for c in conditions:
                query += f'{c}'
        self.cur.execute(query)
        contacts = self.cur.fetchall()
        return contacts

    
    def fetch_messages (self, conditions:any=None) -> list:
        """conditions: str or list"""
        query = 'SELECT * FROM messages '
        if isinstance(conditions, str):
            query += 'WHERE '
            query += conditions
        if isinstance(conditions, list):
            query += 'WHERE '
            for c in conditions:
                query += f'{c}'
        self.cur.execute(query)
        contacts = self.cur.fetchall()
        return contacts

    
    def fetch_responses (self, conditions:any=None) -> list:
        """conditions: str or list"""
        query = 'SELECT * FROM responses '
        if isinstance(conditions, str):
            query += 'WHERE '
            query += conditions
        if isinstance(conditions, list):
            query += 'WHERE '
            for c in conditions:
                query += f'{c}'
        self.cur.execute(query)
        contacts = self.cur.fetchall()
        return contacts


    def save_contact (self, id:str, name:str, phone:str, info:str, is_checked:bool, info_boxes:str=None):
        """Params: (id, name, phone, info, is_checked, info_boxes) """
        self.cur.execute('INSERT INTO contacts (id, name, phone, info, is_checked, info_boxes) VALUES (?,?,?,?,?,?)', (id, name, phone, info, is_checked, info_boxes))
        self.conn.commit()


    def save_message (self, timestamp, sender, content, msg_type):
        self.cur.execute('INSERT INTO messages (timestamp, sender, content, type) VALUES (?,?,?,?)', (timestamp, sender, content, msg_type))
        self.conn.commit()

    def save_response (self, timestamp, contact_id, content, respond_to):
        self.cur.execute('INSERT INTO responses (timestamp, contact_id, content, respond_to) VALUES (?,?,?,?)', (timestamp, contact_id, content, respond_to))
        self.conn.commit()

if __name__ == '__main__':
    db = DBManager()