import datetime
import pymysql
from decouple import config
import sys
import re
import pandas as pd

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
            from utility import extract_id
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
            from utility import parse_synopsis
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
            from utility import parse_synopsis
            return parse_synopsis(row[0][0])

        except pymysql.MySQLError as err:
            print(err)

    def extract_id_from_embed_code(self, embed_code):
        # This regex pattern captures the value of the 'id' parameter in the iframe's src URL
        match = re.search(r'id=([a-zA-Z0-9]+)', embed_code)
        if match:
            return match.group(1)
        return None

    def get_untranscripted_vdo_cipher_list(self, package):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            vdo_cipher_query = f"""
            SELECT id, embed_code FROM classroom_lecture 
            WHERE id NOT IN (SELECT lecture_id FROM lecture_transcription WHERE status=1)
            AND package = {package} AND status='Active' AND embed_code LIKE '%vdocipher.com%'
            """
            cursor = conn.cursor()
            cursor.execute(vdo_cipher_query)
            rows = cursor.fetchall()
            conn.close()

            # Process the data and extract IDs from embed codes
            data = []
            for row in rows:
                lecture_id = row[0]
                embed_code = row[1]
                extracted_id = self.extract_id_from_embed_code(embed_code)
                data.append({"lecture_id": lecture_id, "embed_code": embed_code, "extracted_id": extracted_id})

            # Convert data to a DataFrame and save to an Excel file
            df = pd.DataFrame(data)
            df.to_excel("untranscripted_lectures.xlsx", index=False)

        except pymysql.MySQLError as err:
            print(err)


    def fetch_handout_file_name_from_db(self, class_id):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            vdo_cipher_query = f"""
            Select * from lecture_notes where lecture_id = {class_id}
            """
            cursor = conn.cursor()
            cursor.execute(vdo_cipher_query)
            rows = cursor.fetchall()
            print(rows)
            conn.close()

        except pymysql.MySQLError as err:
            print(err)



if __name__ == "__main__":
    class_id = sys.argv[1:][0]
    db_ops = DBOperations()
    db_ops.fetch_handout_file_name_from_db(class_id=class_id)

    # package = sys.argv[1:][0]
    # print(package)
    # db_ops = DBOperations()
    # db_ops.get_untranscripted_vdo_cipher_list(package=package)
