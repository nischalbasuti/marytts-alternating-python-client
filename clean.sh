mkdir $1/clean
for f in `ls $1`; do
    echo "$f"
    sed -En 's/(^.+:)(.*$)/\2/p' $1/$f > "$1/clean/$f"
done
