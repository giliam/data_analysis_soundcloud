for f in data/*; do 
	if [[ -d $f ]]; then 
        echo "in folder $f"
        for file in `find $f -type f` ; do
            echo "file $file"
            filename=$file
            if [[ $file =~ \.mp3$ ]]; then
                IFS='.' read -ra filedata <<< "$file"
                filename="${filedata[0]}.wav"
                echo "filename $filename"
                avconv -i $file $filename
            fi
            IFS='/' read -ra tags <<< "$f"
            IFS='/' read -ra titles <<< "$filename"
            tag=${tags[1]}
            echo "tag $tag"
            echo "title ${titles[2]}"
            python processor.py -i $filename -t $tag -o "$f.csv" -u ${titles[2]}
            if [[ $file =~ \.mp3$ ]]; then
                rm $filename
            fi
        done;
    fi
done;
