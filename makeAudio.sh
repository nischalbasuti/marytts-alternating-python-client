mkdir $1_audio
for f in `ls $1_txt/clean`; 
do
   python tts.py -i $1_txt/clean/$f -o f_$f -c true -v1 f -l $1
   python tts.py -i $1_txt/clean/$f -o m_$f -c true -v1 m -l $1
   break
done
