import os
import sys
from convert import main
import configparser
import logging
import sonarr, radarr

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=dir_path + '/mp4Simple.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
logging.info("Starting qBittorrent.py")
## Get config.ini values
config = configparser.ConfigParser()
config.read(dir_path + '/config.ini')
qBitDownDir = config.get('qBittorrent', "output_dir")

label = sys.argv[1].lower().strip()
root_path = str(sys.argv[2])


logging.info("Label: " + label)
logging.info("Root path: " + root_path)

try:
    filepath = []

    for file in os.listdir(root_path):
        if file.endswith(".mp4") or file.endswith(".mkv"):
            filepath.append(os.path.join(root_path, file))

    ## Convert files.
    if len(filepath) == 1: ## if single file
        main(filepath[0], logging)

        ## Once finished hit sonarr or radarr api.
        if label == "tv-sonarr":
            settings = dict(config.items("Sonarr"))
            dirName = root_path.replace(qBitDownDir, '')
            sonarr.processEpisode(dirName, settings, logging)
        elif label == "radarr":
            settings = dict(config.items("Radarr"))
            dirName = root_path.replace(qBitDownDir, '')

            radarr.processMovie(dirName, settings, logging)

    elif len(filepath) > 1: ## if multiple files
        for file in filepath:
            main(file, logging)

        ## Once finished hit sonarr or radarr api.
        if label == "tv-sonarr":
            settings = dict(config.items("Sonarr"))
            dirName = root_path.replace(qBitDownDir, '')
            sonarr.processEpisode(dirName, settings, logging)
        elif label == "radarr":
            settings = dict(config.items("Radarr"))
            dirName = root_path.replace(qBitDownDir, '')

            radarr.processMovie(dirName, settings, logging)

    else:
        logging.info('no file')
except Exception as e:
    logging.info(e)
    sys.exit(1)


# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Root Path: /mnt/Hard Disk/qbittorrent/downloads/Harry.Potter.And.The.Prisoner.Of.Azkaban.2004.1080p.BluRay.H264.AAC-RARBG.
# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Content Path: /mnt/Hard Disk/qbittorrent/downloads/Harry.Potter.And.The.Prisoner.Of.Azkaban.2004.1080p.BluRay.H264.AAC-RARBG.
# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Label: radarr.
# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Categories: ['sickbeard', 'tv-sonarr', 'radarr', 'sickrage', 'bypass'].
# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Torrent hash: 7712cd259b3d0552f49a4f02b2bc3652a4854093.
# 2022-05-28 06:15:54 - qBittorrentPostProcess - DEBUG - Torrent name: Harry.Potter.And.The.Prisoner.Of.Azkaban.2004.1080p.BluRay.H264.AAC-RARBG.