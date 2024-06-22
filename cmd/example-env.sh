#!/bin/bash
input_file=".env"
output_file=".env.example"

if [ ! -f "$input_file" ]; then
    echo "Error: $input_file does not exist."
    exit 1
fi

> "$output_file"

while IFS= read -r line || [ -n "$line" ]; do
    if [[ "$line" =~ ^#.* ]] || [[ -z "$line" ]]; then
        echo "$line" >> "$output_file"
    else    
        key=$(echo "$line" | cut -d '=' -f 1)
        echo "$key=" >> "$output_file"
    fi
done < <(cat "$input_file"; echo "")

echo "Successfully created $output_file from $input_file."