import dbfunctions
from pprint import pprint

if __name__ == '__main__':
    dbfunctions.set_dbpath("C:/Users/jorge/tangerine/estancia/hotline/resources/hotline.db")
    conn = dbfunctions.get_connection()
    conn.close()
