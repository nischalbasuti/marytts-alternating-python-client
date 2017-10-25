mkdir $1_audio
for f in `ls $1_txt/clean`; 
do
   python tts_unclean.py -i $1_txt/$f -o f_$f -c true -v1 f -l $1
   python tts_unclean.py -i $1_txt/$f -o m_$f -c true -v1 m -l $1
   break
done
