#!/usr/bin/env python
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
    def __init__(self, textFilePath, outputPrefix, toClean, language='en', outDir='./'):
        super(TTS, self).__init__()
        self.textFilePath, self.outputPrefix, self.toClean = textFilePath, outputPrefix, toClean
        self.outDir = outDir
        #ignore blank lines
        self.lines = []
        lineCount = 0
        with open(textFilePath) as file:
            for line in file:
                if not line.strip():
                    pass
                else:
                    self.lines.append(line)
                    lineCount += 1


        # Make wav and mp3 directories with prefix
        self._makedir("./%s_wav" % outputPrefix)
        self._makedir("./%s_mp3" % outputPrefix)

        # Default voices
        self.voice = 'f'
        self.voices = ["cmu-slt-hsmm", "dfki-spike-hsmm"]
        self.locale = 'en_GB'

        self.maleRate = 1
        self.femaleRate = 1

        # Set the voices
        if language.lower() == 'fr':
            # French
            self.locale = 'fr'
            self.maleVoices     = ['enst-dennys-hsmm', 'upmc-pierre-hsmm']
            self.femaleVoices   = ['enst-camille','enst-camille-hsmm','upmc-jessica-hsmm']
            self.maleIndex      = 1;
            self.femaleIndex    = 0;
            self.maleRate = 1.3
            self.femaleRate = 0.8
        elif language.lower() == 'de':
            # German
            self.locale = 'de'
            self.maleVoices     = ['bits3-hsmm','dfki-pavoque-neutral-hsmm','dfki-pavoque-styles']
            self.femaleVoices   = ['bits1-hsmm','bits-4']
            self.maleIndex      = 0;
            self.femaleIndex    = 0;
            self.maleRate = 1
            self.femaleRate = 1
        else: #elif language.lower() == 'en':
            # English
            self.maleVoices     = ['dfki-obadiah-hsmm','dfki-spike-hsmm','cmu-dbl-hsmm','cmu-rms-hsmm'];
            self.femaleVoices   = ['dfki-poppy-hsmm','dfki-prudence-hsmm','cmu-slt-hsmm'];
            self.maleIndex      = 3;
            self.femaleIndex    = 2;
            self.maleRate = 1.3
            self.femaleRate = 0.8

        self.setVoices(self.voice)

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
    def _construct_query(self, text, voice_id,locale='en_GB'):
        query_hash_voice = {"INPUT_TEXT":text,
                  "INPUT_TYPE":"TEXT", # Input text
                  "LOCALE":locale,
                  "VOICE":voice_id, # Voice informations  (need to be compatible)
                  "OUTPUT_TYPE":"AUDIO",
                  "AUDIO":"WAVE", # Audio informations (need both)
                  }
        print(text)
        return urlencode( query_hash_voice )

    # Converts wav files to mp3 using ffmpeg as subprocess
    def _wav2mp3(self, prefix, count, rate = 1):
        cmd = "ffmpeg -i  {0}_wav/{1}.wav   -filter:a \"atempo={2}\" {0}_mp3/{1}.mp3".format(prefix, "%02d"%count, rate)
        subprocess.call(cmd, shell=True)

    # TODO: working as expected server, not on laptop, make sure it's working properly.
    # Concatinate the generated mp3 files
    def _concatinate_mp3(self, files):
        concatString = "\"concat:{0}_wav/00.wav".format(self.outputPrefix)

        concatString = "\"concat:%s" % ("|".join(files))
        concatString += "\""
        print(concatString)
        #subprocess.call("ffmpeg -i %s -acodec copy %s.mp3" % (concatString, self.outputPrefix), shell = True)
        subprocess.call("mp3wrap {1}/{0}.mp3 {0}_mp3/*.mp3".format(self.outputPrefix, self.outDir), shell = True)

    # Set's the gender of the first voice based on argument, and set's second voice as opposite gender
    def setVoices(self, voice):
        self.voice = voice
        if ( voice.lower() == "male" ) or ( voice.lower() == "m" ):
            self.voices[0] = self.maleVoices[self.maleIndex]
            self.voices[1] = self.femaleVoices[self.femaleIndex]
        elif ( voice.lower() == "female" ) or ( voice.lower() == "f" ):
            self.voices[0] = self.femaleVoices[self.femaleIndex]
            self.voices[1] = self.maleVoices[self.maleIndex]

    # The self.run function() coverts text to speech
    # Alternates voices between lines and generates wav files in *prefix*_wav directory
    # The files in *prefix*_wav are then coverted to mp3 in the *prefix*_mp3 directory
    # If self.toClean is set to "True" (string), then the  *prefix*_wav directory is removed recursively
    def run(self):
        voiceSwitch = True    #boolean, used to alternate voices
        count = 0   #name temporary wav and mp3 files based on count

        # TODO check if useful
        # Being used in self._concatinate_mp3(mp3_files) if use ffmpeg
        wav_files = []
        mp3_files = []

        for line in self.lines:
            if voiceSwitch:
                voice = self.voices[0]
            else:
                voice = self.voices[1]
            voiceSwitch = not voiceSwitch

            # Run the query to mary http server
            query = self._construct_query(line, voice, self.locale)
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
                if(self.voice == 'f') or (self.voice == 'female'):
                    if (count % 2 == 0):
                        self._wav2mp3(self.outputPrefix, count,self.femaleRate)
                    else:
                        self._wav2mp3(self.outputPrefix, count,self.maleRate)
                elif(self.voice == 'm') or (self.voice == 'male'):
                    if (count % 2 == 0):
                        self._wav2mp3(self.outputPrefix, count,self.maleRate)
                    else:
                        self._wav2mp3(self.outputPrefix, count,self.femaleRate)

                # TODO check if useful
                wav_files.append("./%s_wav/%02d.wav" % (self.outputPrefix, count))
                mp3_files.append("./%s_mp3/%02d.mp3" % (self.outputPrefix, count))

                count = count + 1
            else:
                raise Exception(content)
        self._concatinate_mp3(mp3_files)
        # Remove wav and individual mp3 files and directories
        if self.toClean.lower() == "true":
            subprocess.call(['rm', '-r', "%s_wav" % (self.outputPrefix)])
            subprocess.call(['rm', '-r', "%s_mp3" % (self.outputPrefix)])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', required = True, help = 'input text file')
    ap.add_argument('-o', '--output', required = True, help = 'output dir name and prefix')
    ap.add_argument('-v1', '--voice1', required = False, help = 'set gender of first voice1, default is female/f.')
    ap.add_argument('-c', '--clean', required = False, help = 'set True to clean wav files. default is False')
    ap.add_argument('-l', '--language', required = False, help = 'set the language(en, fr, de), default en')

    # Get arguments
    args = vars(ap.parse_args())
    textFilePath = args['input']
    outputPrefix = args['output']
    toClean = args['clean']
    language = args['language']

    # Set default arguments
    if not language:
        language = 'en'
    if not toClean:
        toClean = 'false'
    voice1 = args['voice1']
    if not voice1:
        voice1 = 'f'

    tts = TTS(textFilePath, outputPrefix, toClean, language, language+"_audio")
    tts.setVoices(voice1)
    tts.run()
