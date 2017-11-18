mkdir $1_audio
for f in `ls $1_txt/femalefemale`; 
do
   python tts_unclean.py -i $1_txt/femalefemale/$f -o $1_audio/$f -c true -v1 f -v2 f -l $1
done
for f in `ls $1_txt/malefemale`; 
do
   python tts_unclean.py -i $1_txt/malefemale/$f -o $1_audio/$f -c true -v1 m -v2 f -l $1
done
for f in `ls $1_txt/femalemale`; 
do
   python tts_unclean.py -i $1_txt/femalemale/$f -o $1_audio/$f -c true -v1 f -v2 m -l $1
done
for f in `ls $1_txt/malemale`; 
do
   python tts_unclean.py -i $1_txt/malemale/$f -o $1_audio/$f -c true -v1 m -v2 m -l $1
done
