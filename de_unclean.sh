mkdir de_audio
for f in `ls de_txt/clean`; 
do
   python tts.py -i de_txt/clean/$f -o f_$f -c true -v1 f -l de
   python tts.py -i de_txt/clean/$f -o m_$f -c true -v1 m -l de
done
