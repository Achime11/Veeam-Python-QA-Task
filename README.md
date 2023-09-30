# Veeam-Python-QA-Task
### Description
Python script that synchronizes two folders one-way: source to the replica.

    usage: main.py [-h] -s SOURCE_PATH -r REPLICA_PATH -i SYNCHRONIZATION_INTERVAL -l LOG_PATH
    
    Python script that synchronizes two folders one-way: source to the replica.
    
    options:
      -h, --help            show this help message and exit
      -s SOURCE_PATH, --source_path SOURCE_PATH
                            Source path for synchronization.
      -r REPLICA_PATH, --replica_path REPLICA_PATH
                            Replica path for synchronization.
      -i SYNCHRONIZATION_INTERVAL, --synchronization_interval SYNCHRONIZATION_INTERVAL
                            An integer for synchronization interval in seconds
      -l LOG_PATH, --log_path LOG_PATH
                            Path for synchronization logs.
