from plugin import Plugin
import sqlite3
import re
from threading import Lock

class Quotes(Plugin):

    provides = ['aq', 'iq', 'q', 'sq']

    def __init__(self, xmpp, config=None):
        self.__initialize_db()
        self.lock = Lock()

    def aq(self, message=None, origin=None):
        with self.lock:
            cursor = self.db.cursor()
            query = 'insert into quotes (content) values (?)'
            result = cursor.execute(query, [message])
            quote_id = result.lastrowid
            cursor.close()
            self.db.commit()

            return 'inserted quote \'%s\'' % quote_id

    def iq(self, message=None, origin=None):
        with self.lock:
            try:
                quote_id = int(message)
                cursor = self.db.cursor()
                query = 'select content from quotes where id=?'
                result = cursor.execute(query, [quote_id]).fetchone()
                if result is None:
                    return 'quote not found'
                quote = result[0]
                cursor.close()
                self.db.commit()

                return str(quote)
            except ValueError:
                return 'invalid quote_id: \'%s\'' % message

    def q(self, message=None, origin=None):
        with self.lock:
            cursor = self.db.cursor()
            query = 'select content from quotes order by random() limit 1;'
            result = cursor.execute(query).fetchone()
            if result is None:
                return 'no quotes found'
            quote = result[0]
            cursor.close()
            self.db.commit()

            return str(quote)

    def sq(self, message=None, origin=None):
        with self.lock:
            cursor = self.db.cursor()
            query = 'select content from quotes where content like ?  \
                    limit 3'
            result = cursor.execute(query, ['%%%s%%' % message]).fetchall()
            if len(result) == 0:
                return 'no quotes found'
            result = map(lambda x: x[0], result)
            quote = '\n'.join(result)
            cursor.close()
            self.db.commit()

            return str(quote)

    def __initialize_db(self):
        db = sqlite3.connect('quotes.db', check_same_thread = False)
        cursor = db.cursor()
        query = 'SELECT name FROM sqlite_master  \
            WHERE type=\'table\' \
            ORDER BY name;'
        if not len(list(cursor.execute(query))):
            cursor.execute('''CREATE TABLE quotes
                 ( id INTEGER PRIMARY KEY AUTOINCREMENT, content text)''')

        cursor.close()
        db.commit()
        self.db = db
    
    def shutdown(self):
        with self.lock:
            self.db.close()

    def __str__(self):
        return "Quotes plugin"