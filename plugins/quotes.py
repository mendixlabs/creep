from plugin import Plugin
import sqlite3
import re

class Quotes(Plugin):

    provides = ['aq', 'iq', 'q', 'sq']

    def __init__(self):
        self.db = 'quotes.db'
        self.__initialize_db()

    def aq(self, message=None, origin=None):
        conn = sqlite3.connect(self.db)
        try:
            cursor = conn.cursor()
            query = 'insert into quotes (content) values (?)'
            result = cursor.execute(query, [message])
            quote_id = result.lastrowid
            cursor.close()
            conn.commit()

            return 'inserted quote \'%s\'' % quote_id

        finally:
            conn.close()

    def iq(self, message=None, origin=None):
        try:
            quote_id = int(message)
            conn = sqlite3.connect(self.db)
            with conn:
                cursor = conn.cursor()
                query = 'select content from quotes where id=?'
                result = cursor.execute(query, [quote_id]).fetchone()
                if result is None:
                    return 'quote not found'
                quote = result[0]
                cursor.close()
                conn.commit()

                return str(quote)
        except Exception as e:
            return "whoopsie: %s" % e

        except ValueError:
            return 'invalid quote_id: \'%s\'' % message

    def q(self, message=None, origin=None):
        conn = sqlite3.connect(self.db)
        with conn:
            cursor = conn.cursor()
            query = 'select content from quotes order by random() limit 1;'
            result = cursor.execute(query).fetchone()
            if result is None:
                return 'no quotes found'
            quote = result[0]
            cursor.close()
            conn.commit()

            return str(quote)

    def sq(self, message=None, origin=None):
        conn = sqlite3.connect(self.db)
        with conn:
            cursor = conn.cursor()
            query = 'select content from quotes where content like ?  \
                    limit 3'
            result = cursor.execute(query, ['%%%s%%' % message]).fetchall()
            if len(result) == 0:
                return 'no quotes found'
            result = map(lambda x: x[0], result)
            quote = '\n'.join(result)
            cursor.close()
            conn.commit()

            return str(quote)

    def __initialize_db(self):
        conn = sqlite3.connect(self.db)
        with conn:
            cursor = conn.cursor()
            query = 'SELECT name FROM sqlite_master  \
                WHERE type=\'table\' \
                ORDER BY name;'
            if not len(list(cursor.execute(query))):
                cursor.execute('''CREATE TABLE quotes
                     ( id INTEGER PRIMARY KEY AUTOINCREMENT, content text)''')

            cursor.close()
            conn.commit()
    def __str__(self):
        return "Quotes plugin"
