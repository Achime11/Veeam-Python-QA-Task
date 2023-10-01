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
def copy_file_lib(source_file, destination_file):
    try:
        with open(source_file, 'rb') as source, open(destination_file, 'wb') as destination:
            shutil.copyfileobj(source, destination)
    except FileNotFoundError:
        logger.warning(f"Source file '{source_file}' not found.")
    except Exception as e:
        logger.critical(f"An error occurred: {str(e)}")


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
        logger.info(f"File '{source_file}' copied to '{destination_file}'")
    except FileNotFoundError:
        logger.warning(f"Source file '{source_file}' not found.")
    except Exception as e:
        logger.critical(f"An error occurred: {str(e)}")


# function that generate MD5 hash for a file given as file_path
def generate_file_md5(file_path, block_size=2 ** 18):
    md5 = hashlib.md5()
    with open(os.path.join(file_path), "rb") as file:
        while True:
            buf = file.read(block_size)
            if not buf:
                break
            md5.update(buf)
    return md5.hexdigest()


# function that generate SHA1 hash for a file given as file_path
def generate_file_sha1(file_path, block_size=2 ** 18):
    sha1 = hashlib.sha1()
    with open(os.path.join(file_path), "rb") as file:
        while True:
            buf = file.read(block_size)
            if not buf:
                break
            sha1.update(buf)
    return sha1.hexdigest()


# function that generate SHA256 hash for a file given as file_path
def generate_file_sha256(file_path, block_size=2 ** 18):
    sha256 = hashlib.sha256()
    with open(os.path.join(file_path), "rb") as file:
        while True:
            buf = file.read(block_size)
            if not buf:
                break
            sha256.update(buf)
    return sha256.hexdigest()


# function that initialize the logger and returns it to use it later
def logger_init(log_file):
    # Configure the logger
    logger_instance = logging.getLogger("Sync One-Way")
    logger_instance.setLevel(logging.DEBUG)

    # Create a file handler to log to a file
    file_handler = logging.FileHandler(log_file)
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
    logger_instance.addHandler(file_handler)
    logger_instance.addHandler(console_handler)

    # Return logger
    return logger_instance


# a recursive function that sync folders from source to replica,
# remove files and folder that are not in source but in replica they are present
def synchronize_folders(source_folder, replica_folder):
    logger.info(f"Syncing \"{source_folder}\" to \"{replica_folder}\" !")

    # check if the source folder exist
    if not os.path.exists(source_folder):
        logger.critical(f"Source folder '{source_folder}' does not exist!")
        return

    # check if replica folder exit, if not create one
    if not os.path.exists(replica_folder):
        logger.info(f"Creating '{replica_folder}'!")
        os.makedirs(replica_folder)

    # take every file/directory in first tree of source folder and sync with replica
    for item in os.listdir(source_folder):
        # Creating full item path
        source_item = os.path.join(source_folder, item)
        replica_item = os.path.join(replica_folder, item)

        # Checking if item is a folder to recall sync for folders
        if os.path.isdir(source_item):
            synchronize_folders(source_item, replica_item)
        # else check for file in replica folder, if exist or time is different or size is different copy file
        elif (not os.path.exists(replica_item) or
              os.path.getsize(source_item) != os.path.getsize(replica_item) or
              generate_file_sha1(source_item) != generate_file_sha1(replica_item)):
            logger.info(f"Copying '{source_item}' to '{replica_item}'")
            copy_file(source_item, replica_item)

    # Remove files in replica folder that don't exist in source folder
    for item in os.listdir(replica_folder):
        # create path for items in replica folder
        replica_item = os.path.join(replica_folder, item)
        source_item = os.path.join(source_folder, item)

        # check if the item is a folder or item and need to be removed because is not in source folder
        if not os.path.exists(source_item):
            if os.path.isfile(replica_item):
                logger.info(f"Removing '{replica_item}' file (not in source folder)")
                os.remove(replica_item)
            elif os.path.isdir(replica_item):
                logger.info(f"Removing '{replica_item}' folder (not in source folder)")
                shutil.rmtree(replica_item)


# main sync function where it logs sync start/finish and restart the sync process after sync interval
# and check after every sync if the user has input something to stop the script
def sync(scheduler_param, source_folder, replica_folder):
    logger.info("Sync started!")

    start_time = time.time()

    # call the function to start the sync between the source and replica folders
    synchronize_folders(source_folder, replica_folder)

    logger.info(f"Sync finished after {time.time() - start_time} seconds!")

    # add event for resync at x seconds interval of time
    event = scheduler_param.enter(args.synchronization_interval,
                                  1,
                                  sync,
                                  (scheduler_param, source_folder, replica_folder,))

    # check for any inputs after the sync is done to let the user stop the script in a safe way
    if input() != '':
        scheduler_param.cancel(event)


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

# init logger
logger = logger_init(args.log_path)

# init scheduler
scheduler = sched.scheduler(time.time, time.sleep)

# add event for first sync between source folder and replica folder
scheduler.enter(0, 1, sync, (scheduler, args.source_path.replace('/', '\\'), args.replica_path.replace('/', '\\'),))
# start the scheduler
scheduler.run()
