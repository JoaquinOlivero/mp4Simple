import logging
import os
import sys
from convert import main


dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=dir_path + '/mp4Simple.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
logging.info("Starting batch.py")


try:
    batch_dir = sys.argv[1]
    filepath = []

    for file in os.listdir(batch_dir):
        if file.endswith(".mp4") or file.endswith(".mkv"):
            filepath.append(os.path.join(batch_dir, file))

    if len(filepath) == 1: ## if single file
        main(filepath[0], logging)
    elif len(filepath) > 1: ## if multiple files
        for file in filepath:
            main(file, logging)
except Exception as e:
    logging.info(e)
    sys.exit(1)