# 🌐 Network & 📑 Log Analyzer

**Description:**
This Python script analyzes data from server monitoring and logs generated during host pinging. It reads results from a **SQLite database** (`response_hosts_database.db`) and a **log file** (`response_hosts_log.log`), processes them, evaluates success rates, latency, and error occurrences. The output is a clear **report in a text file** (`report.txt`) with detailed statistics for each host.

The script uses several Python libraries such as `sqlite3`, `re`, `collections`, `datetime`, and a custom module `network_automation_module`. Through this project, I learned how to work with databases, regular expressions, log parsing, report generation, and structured output in Python.

## 🔧 Features
- Loads a list of hosts from a **SQLite database**
- Retrieves statistics on:
  - ✅ Successful responses
  - ⚠️ Slow responses
  - ❌ Failed responses
- Calculates:
  - Success rate percentage per host
  - Average, minimum, and maximum latency
- Analyzes the **log file** and displays counts by severity level (INFO, WARNING, ERROR)
- Generates a clear **text report (`report.txt`)** with results
- Outputs results to the console

## 📂 Database Structure
The `response_hosts_database.db` contains a table called **`data`** with the following columns:
- `Number` – auto-incremented ID
- `Host` – hostname or IP address
- `Status` – availability (✅ / ⚠️ / ❌)
- `Latency` – response time in milliseconds
- `Timestamp` – date and time of the ping

## 📝 Log File
The script works with the file **`response_hosts_log.log`**, which includes:
- Timestamps for each host
- Entries by logging level:
  - `INFO` – successful pings
  - `WARNING` – slow responses
  - `ERROR` – unreachable hosts

## 📑 Report
The output is a file **`report.txt`**, which contains:
- List of hosts
- Log statistics (`INFO`, `WARNING`, `ERROR`)
- Analysis per host:
  - Count and percentage of successful, slow, and failed responses
  - Average, minimum, and maximum latency

