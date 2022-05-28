import requests

def processMovie(dirName, settings, logging):
    logging.info("Sending request to Radarr api")
    try:
        url = "http://" + settings["url"] + ":" + str(settings["port"]) + "/api/v3/command"
        payload = {'name': 'DownloadedMoviesScan', 'path': settings["download_dir"] + dirName}
        headers = {
            'X-Api-Key': settings["api_key"]
        }

        r = requests.post(url, json=payload, headers=headers)
        res = r.json()
        logging.info(res)
    except Exception as e:
        print(e)
        return False