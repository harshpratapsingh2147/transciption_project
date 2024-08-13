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

    def get_all_lecture_ids(self):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.name,
                connect_timeout=5
            )
            q = f"""
            Select id from classroom_lecture where package=5661 and status='Active'"""
            cursor = conn.cursor()
            cursor.execute(q)
            rows = cursor.fetchall()
            class_id_list = [row[0] for row in rows]
            print(class_id_list)
            print(len(class_id_list))
            conn.close()
            return class_id_list

        except pymysql.MySQLError as err:
            print(err)

    def find_all_vids_that_are_not_transcripted(self, transcripted_list):
        class_id_list = self.get_all_lecture_ids()
        non_transcripted_list = []
        for id_ in class_id_list:
            if id_ not in transcripted_list:
                non_transcripted_list.append(id_)
        print(non_transcripted_list)


if __name__ == "__main__":

    dp_ops = DBOperations()
    transcripted_list = [73994, 72223,70966,72004,73550,80063,80470,73532,73533,73993,73394,74506,77005,77408,77415,78088,72222,72233,72749,73167,75225,75227,75229,75753,75754,75755,75226,75756,76316,76318,76321,69361,69362,69932,69935,69937,70157,70158,70701,70705,71145,71146,72050,72051,72221,79195,79196,80067,80473,81174,81988,82511,82512,82514,73545,73548,74001,74004,74497,74494,74504,77004,77410,77411,77412,77413,78083,78653,78654,79191,79192,80064,80065,80066,80068,80474,80475,81140,81144,81163,81965,81972,81980,81984,82513,82515,78351,75221,75223,75751,76324,76326,77001,77002,70151,70153,70155,70710,70713,70717,71148,71149,72219,72220,72747,72959,73157,73160,78084,78085,78086,78650,78651,78652,79194,80467,81154,70141,70663,71133,71159,72003,72005,72224,72225,73169,73564,73996,74508,75233,75752,75757,77006,77409,77414,72750,69360,96622,85311,85323,86029,86035,86043,86051,87345,87346,87347,87349,87350,87354,88243,88247,88238,88252,88257,88260,89452,82983,83485,83489,83493,83499,83501,83509,84103,84104,84106,84107,84109,84110,85188,85189,85190,85191,85803,85806,85809,85812,85814,85817,87313,87315,87317,87319,87322,88269,88277,88281,88299,89292,89294,89296,89298,89826,90182,89830,89832,89834,89824,90790,90791,90792,90793,90794,90797,91487,91489,91491,91493,91494,91894,91895,91896,91897,91898,91899,92602,92604,92606,92609,92610,92612,92613,93019,93021,93022,93046,93052,93076,93380,93383,93384,93387,93391,93394,93395,93909,93910,93911,93912,93913,93914,93915,93916,94344,94345,94351,94353,94356,98406,98404,97284,97261,97252,97247,97240,97236,97229,96632,96630,96628,96625,85311,85323,86029,86035,86043,86051,87345,87346,87347,87349,87350,87354,88243,88247,88238,88252,88257,88260,89452]
    dp_ops.find_all_vids_that_are_not_transcripted(transcripted_list=transcripted_list)

