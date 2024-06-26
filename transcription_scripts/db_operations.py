import pymysql
from decouple import config
from utility import extract_id, parse_synopsis


class DBOperations:

    def __init__(self):
        self.host = config('DB_HOST')
        self.name = config('DB_NAME')
        self.user = config('DB_USER')
        self.password = config('DB_PASS')
        self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )

    def update_transcription_status(self, class_id):
        try:
            q = "UPDATE classroom_lecture SET transcription_status = %s WHERE id = %s" % (1, class_id)
            curr = self.conn.cursor()
            curr.execute(q)
            self.conn.commit()
            self.conn.close()
        except pymysql.MySQLError as err:
            print(err)

    def get_id_from_embed_code(self, class_id):
        try:
            q = "Select embed_code from classroom_lecture where id='%s'" % class_id
            cursor = self.conn.cursor()
            cursor.execute(q)
            row = cursor.fetchall()
            self.conn.close()
            return extract_id(row[0][0])

        except pymysql.MySQLError as err:
            print(err)

    def get_synopsis_from_db(self, class_id):
        try:
            q = "Select content from classroom_lecture where id='%s'" % class_id
            cursor = self.conn.cursor()
            cursor.execute(q)
            row = cursor.fetchall()
            self.conn.close()
            return parse_synopsis(row[0][0])

        except pymysql.MySQLError as err:
            print(err)
