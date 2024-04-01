import pymysql
import re
from decouple import config

HOST = config('DB_HOST')
NAME = config('DB_NAME')
USER = config('DB_USER')
PASS = config('DB_PASS')

print(USER)
print(NAME)
print(USER)
print(PASS)

def get_id_from_embed_code(class_id):
    try:
        conn = pymysql.connect(host=HOST, user=USER, passwd=PASS, db=NAME, connect_timeout=5)
        q = "Select embed_code from classroom_lecture where id='%s'" % class_id
        cursor = conn.cursor()
        cursor.execute(q)
        row = cursor.fetchall()
        print(row)
        return extract_id(row[0][0])

    except pymysql.MySQLError as err:
        print(err)


def extract_id(embed_code):
    # Define a regular expression pattern to extract the ID
    pattern = r'id=(\d+)'
    match = re.search(pattern, embed_code)

    if match:
        # Extract the ID from the matched group
        id_value = match.group(1)
        return id_value
    else:
        return None


