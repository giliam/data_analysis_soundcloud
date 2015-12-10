for f in *; do 
	if [[-d $f ]]; then 
        for file in $f/; do
            filename = $file
            if [[ $file =~ \.mp3$ ]]; then
                IFS='.' read -ra filedata <<< "$file"
                $filename = "$filedata[0].wav"
                avconv -i $file filename
            fi
            python processor.py -i filename
            if [[ $file =~ \.mp3$ ]]; then
                rm filename
            fi
        done;
    fi
done;
