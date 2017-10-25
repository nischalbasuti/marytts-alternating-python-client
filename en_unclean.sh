mkdir en_audio
for f in `ls en_txt/clean`; 
do
   python tts_unclean.py -i en_txt/$f -o f_$f -c true -v1 f -l en
   python tts_unclean.py -i en_txt/$f -o m_$f -c true -v1 m -l en
   break
done
