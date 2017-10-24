mkdir fr_audio
for f in `ls fr_txt/clean`; 
do
   python tts.py -i fr_txt/clean/$f -o f_$f -c true -v1 f -l fr
   python tts.py -i fr_txt/clean/$f -o m_$f -c true -v1 m -l fr
   break
done
