import pymysql
from decouple import config

HOST = config('DB_HOST')
NAME = config('DB_NAME')
USER = config('DB_USER')
PASS = config('DB_PASS')


def update_transcription_status(class_id):
    try:
        conn = pymysql.connect(host=HOST, user=USER, passwd=PASS, db=NAME, connect_timeout=5)
        q = "UPDATE classroom_lecture SET transcription_status = %s WHERE id = %s" % (1, class_id)
        curr = conn.cursor()
        curr.execute(q)
        conn.commit()
        conn.close()
    except pymysql.MySQLError as err:
        print(err)


