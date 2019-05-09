#!/usr/bin/python3

import time
import board
import busio
import adafruit_sgp30
import psycopg2
#import SimpleHTTPServer
#import SocketServer
from http.server import BaseHTTPRequestHandler, HTTPServer
import _thread


CURRENT_CO = 0
CURRENT_TVOC = 0
 
print("Delaying startup for 30 seconds", flush=True)
#time.sleep(30)
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
 
# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
 
print("SGP30 serial #", [hex(i) for i in sgp30.serial], flush=True)
 
sgp30.iaq_init()
#sgp30.set_iaq_baseline(0x8973, 0x8aae)

basefileName = "/home/pi/baseline.txt"
basefile = open(basefileName, "r")
baseCO2 = basefile.readline().rstrip()
baseTVOC = basefile.readline().rstrip()
basefile.close()

if baseCO2 != "" and baseTVOC != "":
    sgp30.set_iaq_baseline(int(baseCO2.lstrip('0x'), 16), int(baseTVOC.lstrip('0x'), 16))
 
print("**** Initial Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (sgp30.baseline_eCO2, sgp30.baseline_TVOC), flush=True)
eprom_sec = 0

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(bytes("{ \"co2\": " + str(CURRENT_CO) + ", \"tvoc\": " + str(CURRENT_TVOC) + "}", "utf-8"))
        return

def start_server():
    print("starting http server")
    server = HTTPServer(("", 8080), myHandler)
    server.serve_forever()

_thread.start_new_thread(start_server, ())

 
while True:
    #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC), flush=True)
    eprom_sec += 1
    if eprom_sec >= 360: # 30 minutes
        eprom_sec = 0
        print("**** Setting Baseline values: eCO2 = 0x%x, TVOC = 0x%x"  % (sgp30.baseline_eCO2, sgp30.baseline_TVOC), flush=True)
        #sgp30.set_iaq_baseline(sgp30.baseline_eCO2, sgp30.baseline_TVOC)
        basefile = open(basefileName, "w")
        basefile.write("0x%x\n0x%x\n" % (sgp30.baseline_eCO2, sgp30.baseline_TVOC))
        basefile.close()

    CURRENT_CO = sgp30.eCO2
    CURRENT_TVOC = sgp30.TVOC
    conn = psycopg2.connect("host=127.0.0.1 dbname=gas user=postgres")
    cur = conn.cursor()
    cur.execute("SET TIME ZONE 'America/Chicago'")
    cur.execute("INSERT INTO readings VALUES(to_timestamp(%s), %s, %s)", (int(time.time()), sgp30.eCO2, sgp30.TVOC))      
    conn.commit()
    cur.close()
    conn.close()
    time.sleep(5)
