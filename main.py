# Python script that synchronizes two folders one-way: source to the replica.

# imports
import argparse
import hashlib
import logging
import os
import sched
import shutil
import time


# copy function with shutil library
def copy_file_lib(src, dst):
    with open(src, 'rb') as source_file, open(dst, 'wb') as dest_file:
        shutil.copyfileobj(source_file, dest_file)


# copy function with read/write chunks of data
def copy_file(source_file, destination_file):
    try:
        with open(source_file, 'rb') as source:
            with open(destination_file, 'wb') as destination:
                while True:
                    data = source.read(2 ** 20)  # Read in 1MB chunks
                    if not data:
                        break
                    destination.write(data)
        print(f"File '{source_file}' copied to '{destination_file}'")
    except FileNotFoundError:
        print(f"Source file '{source_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def generate_file_md5(file_path, filename, blocksize=2 ** 20):
    md5 = hashlib.md5()
    with open(os.path.join(file_path, filename), "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            md5.update(buf)
    return md5.hexdigest()


def logger_init():
    # Configure the logger
    logger = logging.getLogger("Sync One-Way")
    logger.setLevel(logging.DEBUG)

    # Create a file handler to log to a file
    file_handler = logging.FileHandler('example.log')
    file_handler.setLevel(logging.INFO)

    # Create a console handler to log to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter to specify the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set the formatter
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Return logger
    return logger


def synchronize_folders(source_folder, replica_folder):
    logger.info(f"Syncing \"{source_folder}\" to \"{replica_folder}\" !")

    if not os.path.exists(source_folder):
        logger.critical(f"Source folder '{source_folder}' does not exist!")
        return

    if not os.path.exists(replica_folder):
        logger.info(f"Creating '{replica_folder}'!")
        os.makedirs(replica_folder)

    for item in os.listdir(source_folder):
        # Creating full item path
        source_item = os.path.join(source_folder, item)
        replica_item = os.path.join(replica_folder, item)

        # Checking if item is a folder to recall sync for folders
        if os.path.isdir(source_item):
            synchronize_folders(source_item, replica_item)
        # else check for file in replica folder, if exist or time is different or size is different copy file
        elif (not os.path.exists(replica_item) or
              os.path.getmtime(source_item) != os.path.getmtime(replica_item) or
              os.path.getsize(source_item) != os.path.getsize(replica_item) or
              generate_file_md5(source_item) != generate_file_md5(replica_item)):
            logger.info(f"Copying '{source_item}' to '{replica_item}'")
            copy_file(source_item, replica_item)

    # Remove files in replica folder that don't exist in source folder
    for item in os.listdir(replica_folder):
        replica_item = os.path.join(replica_folder, item)
        source_item = os.path.join(source_folder, item)

        if not os.path.exists(source_item) and os.path.isfile(replica_item):
            logger.info(f"Removing '{replica_item}' (not in source folder)")
            os.remove(replica_item)


def sync(scheduler_param, source_folder, replica_folder):
    logger.info("Sync started!")

    start_time = time.time()

    synchronize_folders(source_folder, replica_folder)

    logger.info(f"Sync finished after {time.time() - start_time} seconds!")

    scheduler_param.enter(args.synchronization_interval, 1, sync, (scheduler_param, source_folder, replica_folder,))


# Create the parser
parser = argparse.ArgumentParser(
    description='Python script that synchronizes two folders one-way: source to the replica.')

# Add arguments
parser.add_argument("-s", '--source_path', type=str, help='Source path for synchronization.', required=True)
parser.add_argument("-r", '--replica_path', type=str, help='Replica path for synchronization.', required=True)
parser.add_argument('-i', '--synchronization_interval', help='An integer for synchronization interval in seconds',
                    type=int, required=True)
parser.add_argument('-l', '--log_path', type=str, help='Path for synchronization logs.', required=True)

# Parse the arguments
args = parser.parse_args()

# Print "Hello" + the user input arguments
print('Hello,', args.source_path, args.replica_path, args.synchronization_interval, args.log_path)

logger = logger_init()

# Test log types
logger.debug('Debug test message')
logger.info('Info test message')
logger.error('Error test message')

scheduler = sched.scheduler(time.time, time.sleep)

scheduler.enter(0, 1, sync, (scheduler, args.source_path, args.replica_path,))
scheduler.run()
