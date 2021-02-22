from speedtest import Speedtest
import sqlite3

conn = sqlite3.connect('speed.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS speedtest(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                download INTEGER, 
                upload INTEGER, 
                ping INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )''')
conn.commit()

s = Speedtest()
mbps = 1000000

def speeddb():
    """runs a speedtest to the closest server 
    and then inserts the value to the database"""
    s.get_best_server()
    s.download(threads=64)
    s.upload(threads=64)
    data = (int(s.results.download//mbps),
            int(s.results.upload//mbps),
            int(s.results.ping))
    c.execute('''INSERT INTO speedtest 
                (download, upload, ping) 
                VALUES (?,?,?)''',
                 data)
    conn.commit()
    conn.close()

speeddb()