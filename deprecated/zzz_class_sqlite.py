import sqlite3

class Sqlite:
    db = None

    def __init__(self, pad: str):
        try:
            self.db = sqlite3.connect(pad)
            self.db.row_factory = sqlite3.Row
            self.cur = self.db.cursor()
        except Exception as e:
            print("Connector mislukt", e)
            self.cur = None
            self.db = None
            return

        # print("DB VERBONDEN")

    def isValid(self):
        return True  #not self.cur is None

    def createfromdict(self, tablename, dicto, ignore=True):
        if not self.isValid:
            return False
        # maakt van een dict een sql + args voor create
        veldnamen = ''
        placeholders = ''
        komma = ''
        for ding in dicto.keys():
            veldnamen += komma + ding
            placeholders += komma + '?'
            komma = ', '

        sql = ""
        if ignore:
            sql += "INSERT INTO "
        else:
            sql += "REPLACE "

        sql += tablename + " (" + veldnamen + ") VALUES (" + placeholders + ")"
        args = list(dicto.values())
        # print('INSERT SQL: ', sql)
        # print('INSERT ARGS: ', args)
        return self.create(sql, args)

    def create(self, sql, args=()):
        try:
            self.cur.execute(sql, args)
            self.db.commit()
            lastid = self.cur.lastrowid
            # print('LASTID ', lastid)
            return lastid
        except Exception as err:
            print("DB CREATE:", err)
            return False

    def updatefromdict(self, tablename, setdicto, wheredicto):
        if not self.isValid:
            return False
        # beperking: where fieldname=value, enkelvoudig
        setreeks = ''
        komma = ''
        for ding in setdicto.keys():
            setreeks += komma + ding + "=? "
            komma = ','

        sql = "UPDATE " + tablename + " SET " + setreeks + " WHERE " + wheredicto[
            'key'] + "=? "
        args = list(setdicto.values())
        args.append(wheredicto['value'])
        return self.update(sql, args)

    def update(self, sql, args=()):
        try:
            self.cur.execute(sql, args)
            self.db.commit()
            rows = self.cur.rowcount
            return True
        except Exception as err:
            print("DB UPDATE:",err)
            return False

    # SELECT
    def read(self, sql, args=()):
        if '%s' in str(sql):
            sql = sql.replace('%s', '?')
        if not self.isValid:
            print("DB READ not valid cur")
            return None
        try:
            self.cur.execute(sql, args)
            records = self.cur.fetchall()
            if records is None:
                return None
            elif len(records) == 0:
                return []
            else:
                return [dict(row) for row in records]
        except Exception as err:
            print("DB READ:", err)
            return None

    # DELETE
    def deletefromdict(self, tablename, wheredicto):
        if not self.isValid:
            return False
        sql = "DELETE FROM " + tablename + " WHERE " + wheredicto['key'] + "=? "
        args = []
        args.append(wheredicto['value'])
        return self.delete(sql, args)

    def delete(self, sql, args=()):
        try:
            self.cur.execute(sql, args)
            self.db.commit()
            rows = self.cur.rowcount
            return True
        except Exception as err:
            print("DB DELETE:", err)
            return False

    def close(self):
        try:
            self.cur.close()
            return True
        except Exception as err:
            print("DB CLOSE:", err)
            return False
