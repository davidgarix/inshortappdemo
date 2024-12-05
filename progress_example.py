import logging
from tqdm import tqdm
import time
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def long_running_task():
    logging.info("Starting long-running task")
    for i in tqdm(range(100), desc="Processing", file=sys.stdout):
        time.sleep(0.1)  # Simulate work
    logging.info("Task completed")

if __name__ == "__main__":
    logging.debug("Debug mode: on")
    long_running_task()
