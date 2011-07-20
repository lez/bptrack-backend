#!/bin/zsh

if [ $# -lt 1 ]; then
    echo "$0 <kml> - Downloads .kml track into <kml> file"
    exit 1
fi
FILE=$1

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\"><Document>" > $FILE
echo "Opened $FILE for kml writing..."
curl "budapestcycletrack.appspot.com/stats/kml?cursor=start" >> $FILE
OLD_SIZE="zero"
for i in {1..199}; do
    curl "budapestcycletrack.appspot.com/stats/kml?cursor=more" >> $FILE
    echo -ne "Tracks downloaded: "; grep "<Placemark>" $FILE | wc -l
    NEW_SIZE=`ls -l $FILE|cut -d" " -f 5`
    if [ "$NEW_SIZE" = "$OLD_SIZE" ]; then
        echo "downloaded all."
        break
    fi
    OLD_SIZE=$NEW_SIZE
done
echo "</Document></kml>" >> $FILE
echo "Done."

