# Python server pinger with latency logger
# Author: DusanB98

import subprocess
import platform
import sqlite3
import logging
import datetime

# File location
database_file = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/response_hosts_database.db"
log_file = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/response_hosts_log.log"
hosts_file = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/hosts.txt"

# Function for creating database
def database_init(database_file):

    # creating connection with database (if doesn't exist, it will create new)
    database = sqlite3.connect(database_file)
    
    # creating SQL cursor, cmds are executed through this cursor
    cursor = database.cursor()

    # commadns for executing, first variable is name of column and capital words are commands, (data is variable)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data (
            Number INTEGER PRIMARY KEY AUTOINCREMENT,
            Host TEXT,
            Status INTEGER,
            Latency REAL,
            Timestamp TEXT)
    """)

    # saving all changes and closing .db file
    database.commit()
    database.close()

def log_init(log_file):
    logging.basicConfig(                                        # configuration of function log
        filename=log_file,                                      # name of file "path"
        level=logging.INFO,                                     # minimal level info of log
        format="%(asctime)s [%(levelname)s] %(message)s",       # time, info about (INFO, WARNING, ERROR), insert message which is defined by me
        datefmt="%Y-%m-%d %H:%M:%S"                             # modification of timestamp for right ISO format
    )

# Function for reading file of hosts with error notification
def read_hosts(hosts_file):
    print()
    try:
        with open(file=hosts_file, mode="r") as file:
            hosts = file.read()
            print("🌐 List of Hosts:")
            print("─" * 80)
            print(hosts)
            print("─" * 80 + "\n")
            hosts = hosts.splitlines()        # split a string into a list of lines at each newline character (\n)
            return hosts
    except FileNotFoundError:
        print("──────────────────────")
        print("This file wasn't found")
        print("──────────────────────")
        return []                             # returning empty list if the file can't be read, so code can continiu without crash
    except PermissionError:
        print("───────────────────────────────────────────")
        print("You don't have permission to read this file")
        print("───────────────────────────────────────────")
        return []                             # returning empty list if the file can't be read, so code can continiu without crash
    print()

# Function for pinging availability of hosts
def pinging_hosts_latency(host):
    # what system is user using
    os = platform.system().lower()

    if os == "linux":
        cmd = ["ping", "-c", "1", host]        # -c for linux/macOS
    else:
        cmd = ["ping", "-n", "1", host]        # -n for windows

    try:
        data_out = subprocess.run(
            cmd,                               # commands for pinging system
            capture_output=True,               # capture data from pinging
            text=True,                         # convert output data from bytes to string to process it with split() function
            check=True                         # ensures that a failed ping throws an exception
        ).stdout

        for data in data_out.split():          # using split() to find time of pinging (whole word)
            if "time=" in data:
                return float(data.replace("time=", ""))
    
    except subprocess.CalledProcessError:  
        return False                           # host is unavailable

# Function for saving data to databse
def save_data(database_file, host, status, latency):

    # creating connection with database (if doesn't exist, it will create new)
    database = sqlite3.connect(database_file)
    
    # creating SQL cursor, cmds are executed through this cursor
    cursor = database.cursor()

    # datetime customization for the right time format
    date_now = datetime.datetime.now()
    date_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
    
    # rounding latency time to 2 decimal places and adding ms
    latency = f"{latency:.2f} ms"

    # writing collected data to variable (data) which contains (Host, Status, Latency, Timestamp), "?" is position where are data written down
    cursor.execute("INSERT INTO data (Host, Status, Latency, Timestamp) VALUES (?, ?, ?, ?)",
                   (host, status, latency, date_now))

    # saving all changes and closing .db file
    database.commit()
    database.close()

# Function for main logic
def server_ping():
    
    # creating and initializing database
    database_init(database_file)

    # configuration for log file
    log_init(log_file)
    
    # opening and reading file of hosts to ping
    hosts = read_hosts(hosts_file)

    print("📡 Pinging Hosts:")
    print("─" * 80)
    for host in hosts:
        # pinging hosts according to what system is user using
        latency = pinging_hosts_latency(host)

        # console, database and log status check
        if latency >= 0.01 and latency <= 99.99:
            status = "✅"
            logging.info(f"{host} is available, latency {latency:.2f} ms")
            print(f"✅ Host '{host}' is available, latency {latency:.2f} ms")
        elif latency >= 100:
            status = "⚠️"
            logging.warning(f"{host} is available, slower response, latency {latency:.2f} ms")
            print(f"⚠️ Host '{host}' is available, slower response, latency {latency:.2f} ms")
        elif latency == 0.00:
            status = "❌"
            logging.error(f"{host} no response, latency {latency:.2f} ms")
            print(f"❌ Host '{host}' is unavailable, latency {latency:.2f} ms")

        # saving data to database
        save_data(database_file, host, status, latency)
    
    print("─" * 80)
    print()

# Calling functions and printing results
if __name__ == '__main__':
    server_ping()