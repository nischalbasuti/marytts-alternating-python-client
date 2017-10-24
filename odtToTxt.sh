find . -iname "*.odt" | while read f
do
    echo $f
    odt2txt --output=$f.txt $f 
done
