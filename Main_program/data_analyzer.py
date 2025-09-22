# Python script for Database and Logging Analysis
# Author: DusanB98

import network_automation_module
import sqlite3
import re
from collections import Counter
import datetime

database_path = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/response_hosts_database.db"
log_path = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/response_hosts_log.log"
report_path = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/report.txt"
host_path = "/home/dusan/Desktop/Github/Python_projects/Data_analyzer/Main_program/hosts.txt"

def select_hosts(database_path):
    
    # creating connection with database (if doesn't exist, it will create new)
    database = sqlite3.connect(database_path)

    # creating SQL cursor, cmds are executed through this cursor
    cursor = database.cursor()

    # command line for sq3lite, select not repetetive Host(column) from data(table)
    sql_cmd = "SELECT DISTINCT Host FROM data"

    # execute command fro sql_cmd
    cursor.execute(sql_cmd)

    # get all hosts e.x. [('myanimelist.net',), ('facebook.com',), ('google.com',)], it returns list of tuples!!!! not list of strings!!!
    hosts = cursor.fetchall()

    # saving all changes and closing .db file
    database.commit()
    database.close()

    # returning aquired lists
    return hosts

def select_status_latency_timestamp(database_path, hosts):

    # creating connection with database (if doesn't exist, it will create new)
    database = sqlite3.connect(database_path)

    # creating SQL cursor, cmds are executed through this cursor
    cursor = database.cursor()

    dic_data_host = {}

    # Need for loop to select one at the time, because hosts contains list of 10 tuples(hosts)
    for tuple_host in hosts:

        # converting tuple to string, google.com not ('google.com',)
        string_host = tuple_host[0]

        # command line for sq3lite, select columns Status, Latency, Timestamp from data(table) where hosts
        sql_cmd = "SELECT Status, Latency, Timestamp FROM data WHERE Host = ?"  
        
        # execute command for sql_cmd
        cursor.execute(sql_cmd, tuple_host)
        
        # get all all status, latency, timestamp ... -||-
        list_rows = cursor.fetchall()

        # for each paramater list
        status = []
        latency = []
        timestamp = []

        # add all measured data from database to the list
        for row in list_rows:
            status.append(row[0])
            latency.append(row[1])
            timestamp.append(row[2])

        # saving all sorted data
        dic_data_host[string_host] = {
            "status": status,
            "latency": latency,
            "timestamp": timestamp
        }

    # saving all changes and closing .db file
    database.commit()
    database.close()

    # returning sorted data
    return dic_data_host

def analyze_data(database_path, hosts):
    
    # calling function to get sorted data
    dic_data_host = select_status_latency_timestamp(database_path, hosts)

    # creating dictionary to divide data for each host
    hosts_results = {}

    for host_key, data_value in dic_data_host.items():
        
        # counting emoji marks from database
        count_succes = data_value["status"].count('✅')
        count_warning = data_value["status"].count('⚠️')
        count_error = data_value["status"].count('❌')

        total_count = count_succes + count_warning + count_error
        success_rate = (count_succes / total_count) * 100
        warning_rate = (count_warning / total_count) * 100
        error_rate = (count_error / total_count) * 100

        # finding only numbers in latency without units "ms" (variables, for loop)
        latency_group = 0
        count_numb_avg = 0
        latency_values = []

        for input in data_value["latency"]:
            find_number = re.search(r"\d+\.\d+", input)  # regex from library "re" to find numbers, when in string is more than one expression
            value = float(find_number.group())           # group() takes back aquired numbers from regex
            latency_values.append(value)                 # add numbers from regex to list to find min. and max.
            latency_group += value
            count_numb_avg += 1                          # counting how many numbers are in a list

        # avg, min, max, filter zero
        filter_zero = list(filter(lambda zero: zero > 0.00, latency_values))
        avg_latency = latency_group / count_numb_avg

        if filter_zero:
            min_latency = min(filter_zero)
            max_latency = max(filter_zero)
        else:
            min_latency = None
            max_latency = None
        
        hosts_results[host_key] = {                 # to get all hosts and data
            "host_key": host_key,
            "count_succes": count_succes,
            "success_rate": success_rate,
            "count_warning": count_warning,
            "warning_rate": warning_rate,
            "count_error": count_error,
            "error_rate": error_rate,
            "avg_latency": avg_latency,
            "max_latency": max_latency,
            "min_latency": min_latency
        }

    return hosts_results                        # return data for every host

def select_log(log_path):
    
    log_count = Counter()       # library 'collections', when you search for more than one expression and you need to just count them separatly
    
    try:
        with open(file=log_path, mode="r") as log:
            for line in log:
                find_status = re.search(r"\[(INFO|WARNING|ERROR)\]", line)
                type = find_status.group()
                log_count[type] += 1
    except FileNotFoundError:
        print("──────────────────────")
        print("This file wasn't found")
        print("──────────────────────")
        return None
    except PermissionError:
        print("───────────────────────────────────────────")
        print("You don't have permission to read this file")
        print("───────────────────────────────────────────")
        return None
    
    return log_count

def report_txt(report_path, hosts_results, log_count):

    date_now = datetime.datetime.now()
    date_now = date_now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(file=report_path, mode="w") as txt:
            txt.write("*" * 80 + "\n")
            txt.write("🌐 Network & 📑 Log Analyzer Report\n")
            txt.write(f"⚙️ Generated: {date_now}\n")
            txt.write("*" * 80 + "\n\n")
            try:
                with open(file=host_path, mode="r") as list:
                    hosts = list.read()
            except FileNotFoundError:
                print("──────────────────────")
                print("This file wasn't found")
                print("──────────────────────")
                return None
            except PermissionError:
                print("───────────────────────────────────────────")
                print("You don't have permission to read this file")
                print("───────────────────────────────────────────")
                return None
            txt.write("🌐 List of Hosts:\n")
            txt.write("─" * 80 + "\n")
            txt.write(hosts + "\n")
            txt.write("─" * 80 + "\n\n")
            hosts = hosts.splitlines()        # split a string into a list of lines at each newline character (\n)
            txt.write("📑 Log Analysis:\n")
            txt.write("─" * 80 + "\n")
            for status, occurrenece in log_count.items():
                 txt.write(f"{status}: {occurrenece}x\n")
            txt.write("─" * 80 + "\n\n")
            txt.write("🌐 Host Analysis:\n")
            txt.write("─" * 80 + "\n")
            for host_key, value in hosts_results.items():
                txt.write(f"🌐 {host_key}:\n")
                txt.write(f"✅ Success: {value['count_succes']}x, {value['success_rate']:.2f} %\n")
                txt.write(f"⚠️ Slow: {value['count_warning']}x, {value['warning_rate']:.2f} %\n")
                txt.write(f"❌ Error: {value['count_error']}x, {value['error_rate']:.2f} %\n")
                if value['min_latency'] and value['max_latency'] and value['avg_latency'] is not None:
                    txt.write(f"🕒 Avg. latency: {value['avg_latency']:.2f} ms\n")
                    txt.write(f"⬆️ Max. latency: {value['max_latency']:.2f} ms\n")
                    txt.write(f"⬇️ Min. latency: {value['min_latency']:.2f} ms\n")
                else:
                    txt.write(f"🕒 Avg. latency: N/A\n")
                    txt.write(f"⬆️ Max. latency: N/A\n")
                    txt.write(f"⬇️ Min. latency: N/A\n")
                txt.write("─" * 80 + "\n")
    except FileNotFoundError:
        print("──────────────────────")
        print("This file wasn't found")
        print("──────────────────────")
        return None
    except PermissionError:
        print("────────────────────────────────────────────────────")
        print("You don't have permission to write down to this file")
        print("────────────────────────────────────────────────────")
        return None
    
    print(f"\n✅ Report was exported to the text file!\n")

def main():
    network_automation_module.server_ping()
    
    get_hosts = select_hosts(database_path)
    select_status_latency_timestamp(database_path, get_hosts)
    
    data = analyze_data(database_path, get_hosts)

    count_status = select_log(log_path)
    
    print("📑 Log Analysis:")
    print("─" * 80)
    for status, occurrenece in count_status.items():
        print(f"{status}: {occurrenece}x")
    print("─" * 80)
    print()

    print("🌐 Host Analysis: ")
    print(f"─" * 80)
    for host_key, value in data.items():
        print(f"🌐 {host_key}:")
        print(f"✅ Success: {value['count_succes']}x, {value['success_rate']:.2f} %")
        print(f"⚠️  Slow: {value['count_warning']}x, {value['warning_rate']:.2f} %")
        print(f"❌ Error: {value['count_error']}x, {value['error_rate']:.2f} %")
        if value['min_latency'] and value['max_latency'] and value['avg_latency'] is not None:
            print(f"🕒 Avg. latency: {value['avg_latency']:.2f} ms")
            print(f"⬆️  Max. latency: {value['max_latency']:.2f} ms")
            print(f"⬇️  Min. latency: {value['min_latency']:.2f} ms")
        else:
            print(f"🕒 Avg. latency: N/A")
            print(f"⬆️  Max. latency: N/A")
            print(f"⬇️  Min. latency: N/A")
        print("─" * 80)

    hosts_results = analyze_data(database_path, get_hosts)
    log_count = select_log(log_path)
    report_txt(report_path, hosts_results, log_count)

# calling functions
if __name__ == '__main__':
    main()