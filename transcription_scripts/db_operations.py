import datetime
import pymysql
from decouple import config
from utility import extract_id, parse_synopsis


class DBOperations:

    def __init__(self):
        self.host = config('DB_HOST')
        self.name = config('DB_NAME')
        self.user = config('DB_USER')
        self.password = config('DB_PASS')

    def update_transcription_status(self, class_id, status):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            created_at = datetime.datetime.now()
            updated_at = datetime.datetime.now()
            q = """
             INSERT INTO lecture_transcription (lecture_id, status, created_at, updated_at)
             VALUES (%s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE
                 status = VALUES(status),
                 updated_at = VALUES(updated_at)
             """
            curr = conn.cursor()
            curr.execute(q, (class_id, status, created_at, updated_at))
            conn.commit()
            conn.close()
        except pymysql.MySQLError as err:
            print("Here is the problem in pymysql........", err)
        except Exception as err:
            print("some other error...........", err)

    def get_id_from_embed_code(self, class_id):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            q = "Select embed_code from classroom_lecture where id='%s'" % class_id
            cursor = conn.cursor()
            cursor.execute(q)
            row = cursor.fetchall()
            conn.close()
            return extract_id(row[0][0])

        except pymysql.MySQLError as err:
            print(err)

    def get_synopsis_from_db(self, class_id):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            q = "Select content from classroom_lecture where id='%s'" % class_id
            cursor = conn.cursor()
            cursor.execute(q)
            row = cursor.fetchall()
            conn.close()
            return parse_synopsis(row[0][0])

        except pymysql.MySQLError as err:
            print(err)

    def get_section_id(self, class_id):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            q = f"""SELECT section_name 
            FROM section 
            WHERE section_id IN ( 
                SELECT section_id 
                FROM classroom_lecture 
                WHERE id = {class_id} 
            )"""
            cursor = conn.cursor()
            cursor.execute(q)
            row = cursor.fetchall()
            conn.close()
            return parse_synopsis(row[0][0])

        except pymysql.MySQLError as err:
            print(err)


# if __name__ == "__main__":
#     # List of class_ids for the videos to transcribe
#     class_ids = sys.argv[1:]
#     dp_ops = DBOperations()
#     print(dp_ops.get_section_id(class_id=class_ids[0]))

