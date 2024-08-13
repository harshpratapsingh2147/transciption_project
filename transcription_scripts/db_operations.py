import datetime
import pymysql
from decouple import config
from utility import extract_id, parse_synopsis
import re

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

    def extract_id(self, embed_code):
        pattern = r'id=([a-f0-9]{32})'
        match = re.search(pattern, embed_code)

        # Extract the matched value if found
        if match:
            video_id = match.group(1)
            return video_id
        else:
            print("No match found.")
    #
    # def get_all_lecture_ids(self):
    #     try:
    #         conn = pymysql.connect(
    #             host=self.host,
    #             user=self.user,
    #             passwd=self.password,
    #             db=self.name,
    #             connect_timeout=5
    #         )
    #         q = f"""
    #         Select id, embed_code from classroom_lecture where package=5661 and status='Active'"""
    #         cursor = conn.cursor()
    #         cursor.execute(q)
    #         rows = cursor.fetchall()
    #         class_id_list = [{"id": row[0], "embed_code": self.extract_id(row[1])} for row in rows]
    #         print(class_id_list)
    #         print(len(class_id_list))
    #         conn.close()
    #         return class_id_list
    #
    #     except pymysql.MySQLError as err:
    #         print(err)
    #
    # def find_all_vids_that_are_not_transcripted(self, transcripted_list):
    #     class_id_list = self.get_all_lecture_ids()
    #     non_transcripted_list = []
    #     for id_ in class_id_list:
    #         if id_ not in transcripted_list:
    #             non_transcripted_list.append(id_)
    #     print(non_transcripted_list)

    def get_all_embed_ids(self, lecture_ids):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            q = f"""Select id, embed_code from classroom_lecture where id in ({lecture_ids})"""

            cursor = conn.cursor()
            cursor.execute(q)
            rows = cursor.fetchall()
            result_list = [{"id": row[0], "embed_code": self.extract_id(row[1])} for row in rows]
            conn.close()
            print(result_list)

        except pymysql.MySQLError as err:
            print(err)



if __name__ == "__main__":

    dp_ops = DBOperations()
    transcripted_list = [95583, 95592, 95606, 95613, 95623, 98409, 98413, 98456, 98459, 98463, 99464, 99516, 99524, 99528, 99557, 99560, 101234]
    dp_ops.get_all_embed_ids(transcripted_list)