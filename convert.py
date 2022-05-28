import os
from os import walk
import pathlib
import ffmpeg
from pprint import pprint
import subprocess


def subtitles(streamIndex, lang, media_file):
    logging.info('Extracting subs', lang, media_file)
    outputSub = os.path.splitext(media_file)[0] ## remove extension from filepath
    filepath = pathlib.Path().resolve() ## get media_file's parent directory
    parentDirFiles = next(walk(filepath), (None, None, []))[2] ## get all files in media_file's parent directory

    ## change "spa" to "es" for the .srt file language code
    if lang == "spa":
        lang = "es"
    
    defaultSubs = os.path.splitext(os.path.basename(media_file))[0] + "." + lang + ".default.srt" ## example: filenames ending with .eng.default.srt
    otherSubs = os.path.splitext(os.path.basename(media_file))[0] + "." + lang + ".srt" ## example: filenames ending with .eng.srt

    # Extract subtitles to .srt files
    if len(parentDirFiles) == 0:
        subprocess.call(["ffmpeg", "-y", "-i", media_file, "-map", "0:s:" + str(streamIndex), outputSub + "." + lang + ".srt"],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif defaultSubs not in parentDirFiles:
        subprocess.call(["ffmpeg",  "-y", "-i", media_file, "-map", "0:s:" + str(streamIndex), outputSub + "." + lang + ".default.srt"],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    elif otherSubs not in parentDirFiles:
        subprocess.call(["ffmpeg", "-y", "-i", media_file, "-map", "0:s:" + str(streamIndex), outputSub + "." + lang + ".srt"],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    else: 
        subprocess.call(["ffmpeg", "-y", "-i", media_file, "-map", "0:s:" + str(streamIndex), outputSub + "." + lang + "." + str(streamIndex) + ".srt"],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


## Convert audio streams and containers as needed. There can only be one audio stream, because some devices do not support track switching. This can be changed if I find out how to make aac 2.0 the default stream and leave untouched other audio streams in the container.
def convert(fileContainer, fileAudioStreams, media_file, logging):
    
    ## Check container format.
    isCorrectContainer = False 
    if "mp4" in fileContainer:
        isCorrectContainer = True

   ## Check if there is an aac 2.0 audio stream.
    def isStereoDefault(item):
                if item["aac 2.0"]:
                        return True
                else:
                        return False

    aacAudioStream = list(filter(isStereoDefault, fileAudioStreams))

    if len(aacAudioStream) > 0 and isCorrectContainer == True:

        if aacAudioStream[0]["default"] != 1 and len(fileAudioStreams) > 1:
            os.rename(media_file, media_file + '.original')
            audioMapping = []
            for i in range(len(fileAudioStreams)):
                audioMapping.append('-map')
                audioMapping.append('0:a:' + str(i))

            audioDisposition = []
            for i in range(len(fileAudioStreams)):
                streamIndex = fileAudioStreams[i]["index"]
                streamDefault = fileAudioStreams[i]["default"]
                streamAac = fileAudioStreams[i]["aac 2.0"]
                if streamAac == True:
                    audioDisposition.append("-disposition:a:" + str(i))
                    audioDisposition.append(" default")
                elif streamDefault == 1:
                    audioDisposition.append("-disposition:a:" + str(i))
                    audioDisposition.append(" 0")

            # ffmpeg -i Severance.S01E01.mp4 -map 0:v:0 -map 0:a:2 -metadata:s:a:0 handler_name='Stereo' -c copy -c:a aac -ac 2 test.mp4
            logging.info('AAC 2.0 stream found in ' + media_file + ' . Setting it as default audio stream')
            subprocess.call(["ffmpeg", "-y", "-i", media_file + ".original", "-map", "0:v:0"] + audioMapping + ["-c", "copy"] + audioDisposition + ["-movflags", "+faststart", media_file],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            os.remove(media_file + ".original")
        else: 
            logging.info("AAC 2.0 is the default audio stream and the container is MP4. Conversion not needed. Skipping... " + media_file)
    elif len(aacAudioStream) == 0 and isCorrectContainer == True:
        logging.info("AAC 2.0 stream NOT found in " + media_file + " . Converting first available audio stream to aac 2.0 and removing other audio streams.")
        os.rename(media_file, media_file + '.original')
        subprocess.call(["ffmpeg", "-y", "-i", media_file + ".original", "-map", "0:v:0", "-map", "0:a:0", "-metadata:s:a:0", "handler_name='Stereo'", "-c", "copy", "-c:a", "aac", "-ac", "2","-movflags", "+faststart", media_file],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        os.remove(media_file + ".original")
    else:
        logging.info(media_file + "'s container is not mp4. Converting the container to mp4 and the first available audio stream to aac 2.0. Removing other audio streams. ")
        outputfile = os.path.splitext(media_file)[0]
        subprocess.call(["ffmpeg", "-y", "-i", media_file, "-map", "0:v:0", "-map", "0:a:0", "-metadata:s:a:0", "handler_name='Stereo'", "-c", "copy", "-c:a", "aac", "-ac", "2","-movflags", "+faststart", outputfile + ".mp4"],  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        os.remove(media_file)



def main(filepath, logging):
    media_file = str(filepath)
    
    try:
        ## List with container names
        fileContainer = list(ffmpeg.probe(media_file)["format"]["format_name"].split(","))
        ## List of file streams
        fileStreams = ffmpeg.probe(media_file)["streams"]

        ## Subtitles
        fileSubtitlesStreams = []
        wantedSubtitlesStreams = []

        for index in range(len(fileStreams)):
            if "codec_type" in fileStreams[index] and fileStreams[index]["codec_type"] == "subtitle":
                fileSubtitlesStreams.append(fileStreams[index])

        if len(fileSubtitlesStreams) > 0:
            for index in range(len(fileSubtitlesStreams)):
                if "codec_type" in fileSubtitlesStreams[index] and fileSubtitlesStreams[index]["codec_type"] == "subtitle":
                    if fileSubtitlesStreams[index]["tags"]["language"] == "eng" or fileSubtitlesStreams[index]["tags"]["language"] == "spa":
                        wantedSubtitlesStreams.append({"index": index, "lang": fileSubtitlesStreams[index]["tags"]["language"], "codec_name": fileSubtitlesStreams[index]["codec_name"]})

            ## Subtitle extraction
            # !!!! UNCOMMENT THE CODE BELOW. ## Code below is commented out to avoid subs extraction while testing other functionalities.
            # for index in range(len(wantedSubtitlesStreams)):
            #     subtitles(wantedSubtitlesStreams[index]["index"], wantedSubtitlesStreams[index]["lang"], media_file)
            for sub in wantedSubtitlesStreams:
                subtitles(sub["index"], sub["lang"], media_file)
        else:
            logging.info('No subtitles available.')

        ## Audio streams
        fileAudioStreams = []
        for index in range(len(fileStreams)):
            if "codec_type" in fileStreams[index] and fileStreams[index]["codec_type"] == "audio":
                if fileStreams[index]["codec_name"] == "aac" and fileStreams[index]["channels"] == 2:
                    fileAudioStreams.append({"aac 2.0": True, "index": index, "default": fileStreams[index]["disposition"]["default"]})
                else:
                    fileAudioStreams.append({"aac 2.0": False, "index": index, "default": fileStreams[index]["disposition"]["default"]})

        ## Final converting function.
        logging.info("Converting file: " + media_file)
        convert(fileContainer, fileAudioStreams, media_file, logging)
    except Exception as e:
        logging.info(e)


## Check for container
## Check for audio streams
## 
## If present, extract subs in spanish and english. And convert them to .srt ## ffmpeg -i Movie.mkv -map 0:s:0 subs.srt
## If not present, convert audio to AAC 2.0. If AAC 5.1 is present prioritize for conversion to stereo. ## convert from acc 5.1 to acc 2.0 ffmpeg -i Severance.S01E01.mp4 -map 0:v:0 -map 0:a:2 -metadata:s:a:0 handler_name='Stereo' -c copy -c:a aac -ac 2 test.mp4
## if the container is not mp4 convert to mp4

## move_text subtitles (usually found in .mp4 containers)
#  'avg_frame_rate': '0/0',
#  'bit_rate': '63',
#  'codec_long_name': 'MOV text',
#  'codec_name': 'mov_text',
#  'codec_tag': '0x67337874',
#  'codec_tag_string': 'tx3g',
#  'codec_time_base': '0/1',
#  'codec_type': 'subtitle',

## srt subtitles (usually embedded in .mkv containers. Can't be embedded in .mp4 containers)
#  'avg_frame_rate': '0/0',
#  'codec_long_name': 'SubRip subtitle',
#  'codec_name': 'subrip',
#  'codec_tag': '0x0000',
#  'codec_tag_string': '[0][0][0][0]',
#  'codec_time_base': '0/1',
#  'codec_type': 'subtitle',
#  'tags':{'language': 'eng'}