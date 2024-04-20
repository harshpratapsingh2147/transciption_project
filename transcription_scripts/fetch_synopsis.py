import pymysql
from bs4 import BeautifulSoup
from decouple import config

HOST = config('DB_HOST')
NAME = config('DB_NAME')
USER = config('DB_USER')
PASS = config('DB_PASS')


def parse_synopsis(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()


def get_synopsis_from_db(class_id):
    try:
        conn = pymysql.connect(host=HOST, user=USER, passwd=PASS, db=NAME, connect_timeout=5)
        q = "Select content from classroom_lecture where id='%s'" % class_id
        cursor = conn.cursor()
        cursor.execute(q)
        row = cursor.fetchall()
        conn.close()
        return parse_synopsis(row[0][0])

    except pymysql.MySQLError as err:
        print(err)


