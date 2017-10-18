#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Nischal Srinvas Basuti
#Date: 2017 October 17

import httplib2
try:
    #python3
    from urllib.parse import urlencode
except:
    #python2
    from urllib import urlencode
    FileExistsError = Exception #hacky python2 support

import os
import sys
import subprocess
import argparse

def isPython2():
    if sys.version_info[0] < 3:
        return True
    return False

class TTS(object):
    """docstring for TTS"""
    def __init__(self, textFilePath, outputPrefix, toClean):
        super(TTS, self).__init__()
        self.textFilePath, self.outputPrefix, self.toClean = textFilePath, outputPrefix, toClean
        self.lines = open(textFilePath).readlines()

        # Make wav and mp3 directories with prefix
        self._makedir("./%s_wav" % outputPrefix)
        self._makedir("./%s_mp3" % outputPrefix)

        self.voices = ["cmu-slt-hsmm", "dfki-spike-hsmm", "dfki-obadiah"]

        # Mary server informations
        self.mary_host = "localhost"
        self.mary_port = "59125"
        
    # Make directory, and prompt user to overwrite if directory already exists
    def _makedir(self, dirName):
        try:
            os.makedirs(dirName)
        except FileExistsError as e:
            overwrite = ''
            while ( overwrite != 'y' ) and ( overwrite != 'n' ): 

                if isPython2():
                    overwrite = raw_input("prefix "+outputPrefix+ " already exists, do you want to over write it? (y/n): ").lower()
                else:
                    overwrite = input("prefix "+outputPrefix+ " already exists, do you want to over write it? (y/n): ").lower()

                if overwrite == 'y':
                    subprocess.call(['rm', '-r', dirName])
                    print("removed "+dirName)
                    os.makedirs(dirName)
                elif overwrite == 'n':
                    print("...did nothing...")
                    quit()

    # Build the query
    def _construct_query(self, text, voice_id):
        query_hash_voice = {"INPUT_TEXT":text,
                  "INPUT_TYPE":"TEXT", # Input text
                  "LOCALE":"en_GB",
                  "VOICE":voice_id, # Voice informations  (need to be compatible)
                  "OUTPUT_TYPE":"AUDIO",
                  "AUDIO":"WAVE", # Audio informations (need both)
                  }
        return urlencode( query_hash_voice )

    # Converts wav files to mp3 using ffmpeg
    def _wav2mp3(self, prefix, count):
        cmd = "ffmpeg -i {0}_wav/{1}.wav {0}_mp3/{1}.mp3".format(prefix, "%02d"%count)
        subprocess.call(cmd, shell=True)

    # todo
    def _concatinate_mp3(self, files):
        concatString = "\"concat:{0}_wav/00.wav".format(self.outputPrefix)

        concatString = "\"concat:%s" % ("|".join(files))
        concatString += "\""
        print(concatString)
        subprocess.call("ffmpeg -i %s -acodec copy %s.mp3" % (concatString, self.outputPrefix), shell = True)
    # todo
    def setVoices(self, voice):
        if ( voice.lower() == "male" ) or ( voice.lower() == "m" ):
            self.voices[0] = "dfki-spike-hsmm"
            self.voices[1] = "cmu-slt-hsmm"
        elif ( voice.lower() == "female" ) or ( voice.lower() == "f" ):
            self.voices[0] = "cmu-slt-hsmm"
            self.voices[1] = "dfki-spike-hsmm"
        pass

    # The self.run function() coverts text to speech
    # Alternates voices between lines and generates wav files in *prefix*_wav directory
    # The files in *prefix*_wav are then coverted to mp3 in the *prefix*_mp3 directory
    # If self.toClean is set to "True" (string), then the  *prefix*_wav directory is removed recursively
    def run(self):
        voiceSwitch = True    #boolean, used to alternate voices
        count = 0   #name files based on count

        wav_files = []
        mp3_files = []

        for line in self.lines:
            if voiceSwitch:
                voice = self.voices[0]
            else:
                voice = self.voices[1]
            voiceSwitch = not voiceSwitch

            # Run the query to mary http server
            query = self._construct_query(line, voice)
            h_mary = httplib2.Http()
            resp, content = h_mary.request("http://%s:%s/process?" % (self.mary_host, self.mary_port), "POST", query)
            print("query = \"http://%s:%s/process?%s\"" % (self.mary_host, self.mary_port, query))

            # Decode the wav file or raise an exception if no wav files
            if (resp["content-type"] == "audio/x-wav"):
                # Write the wav file
                f = open("./%s_wav/%02d.wav" % (self.outputPrefix, count), "wb")
                f.write(content)
                f.close()

                # Convert to mp3
                self._wav2mp3(self.outputPrefix, count)

                wav_files.append("./%s_wav/%02d.wav" % (self.outputPrefix, count))
                mp3_files.append("./%s_mp3/%02d.mp3" % (self.outputPrefix, count))

                count = count + 1
            else:
                raise Exception(content)
        self._concatinate_mp3(mp3_files)
        # Remove wav files and directory
        if self.toClean.lower() == "true":
            subprocess.call(['rm', '-r', "%s_wav" % (self.outputPrefix)])

if __name__ == "__main__":
    # Get prefix name to write files to 
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', required = True, help = 'input text file' )
    ap.add_argument('-o', '--output', required = True, help = 'output dir name and prefix' )
    ap.add_argument('-v1', '--voice1', required = False, help = 'set gender of first voice1, default is female/f.' )
    ap.add_argument('-c', '--clean', required = False, help = 'set True to clean wav files. default is False' )

    args = vars(ap.parse_args())
    textFilePath = args['input']
    outputPrefix = args['output']
    toClean = args['clean']
    if not toClean:
        toClean = 'false'
    voice1 = args['voice1']
    if not voice1:
        voice1 = 'f'

    tts = TTS(textFilePath, outputPrefix, toClean)
    tts.setVoices(voice1)
    tts.run()
