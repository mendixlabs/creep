from plugin import Plugin
import sqlite3
from threading import Lock


class Quotes(Plugin):

    provides = ['aq', 'iq', 'q', 'sq', 'lq', 'dq']

    def __init__(self, creep, config=None):
        self.__initialize_db()
        self.lock = Lock()
        if 'admins' in config:
            self.admins = config['admins']
        else:
            self.admins = []

    def aq(self, message=None, origin=None):
        '''Add a quote. For example: "aq this is my quote"'''
        with self.lock:
            cursor = self.db.cursor()
            query = 'insert into quotes (content) values (?)'
            result = cursor.execute(query, [message])
            quote_id = result.lastrowid
            cursor.close()
            self.db.commit()

            return 'inserted quote \'%s\'' % quote_id

    def iq(self, message=None, origin=None):
        '''Query for a quote. For example: "iq 123"'''
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
        '''Retrieve a random quote. For example: "q"'''
        with self.lock:
            cursor = self.db.cursor()
            query = 'select content from quotes order by random() limit 1;'
            result = cursor.execute(query).fetchone()
            if result is None:
                return 'no quotes found'
            quote = result[0]
            cursor.close()

            return str(quote)

    def lq(self, message=None, origin=None):
        '''List the last 10 quotes'''
        with self.lock:
            cursor = self.db.cursor()
            query = 'select id, content from quotes order by id desc limit 10'
            result = cursor.execute(query).fetchall()
            if len(result) == 0:
                return 'no quotes found'
            result = map(lambda x: "%d - %s" % (x[0], x[1].strip()), result)
            quote = '\n'.join(result)
            cursor.close()

            return str(quote)

    def sq(self, message=None, origin=None):
        '''Search for a quote. For example: "sq name"'''
        with self.lock:
            cursor = self.db.cursor()
            query = 'select id, content from quotes where content like ?  \
                    order by random() limit 3'
            result = cursor.execute(query, ['%%%s%%' % message]).fetchall()
            if len(result) == 0:
                return 'no quotes found'
            result = map(lambda x: "%d - %s" % (x[0], x[1].strip()), result)
            quote = '\n'.join(result)
            cursor.close()
            self.db.commit()

            return str(quote)

    def dq(self, message=None, origin=None):
        '''Delete a quote. Only available for admins'''
        origin_bare = str(origin).split('/')[0]
        if origin_bare not in self.admins:
            return "You're not an admin"

        with self.lock:
            try:
                quote_id = int(message)
                cursor = self.db.cursor()

                query = 'select content from quotes where id=?'
                result = cursor.execute(query, [quote_id]).fetchone()
                if result is None:
                    return 'quote not found'

                query = 'delete from quotes where id=?'
                cursor.execute(query, [quote_id])
                cursor.close()
                self.db.commit()

                return "'%s' deleted" % quote_id
            except ValueError:
                return 'invalid quote_id: \'%s\'' % message
                result = cursor.execute(query, [quote_id]).fetchone()

    def __initialize_db(self):
        db = sqlite3.connect('quotes.db', check_same_thread=False)
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
        return 'quotes'
