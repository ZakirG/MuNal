#!/bin/bash
#Input: folder containing music
#Output: text file containing list of song names and artists
#Be sure to include full paths in command line arguments.
#The optional -r flag will perform recursive search.
#Example usage: sh library_to_text.sh -r ~/Desktop/Music/ ~/grp-275-cs122-win-14/src/output.txt

if [[ $# -lt 2 ]]; then
	echo "You must pass arguments to the script."
	exit 0
fi

recursive=false
folder=$1
output_file=$2
while getopts ":r:" opt; do
	case $opt in
		r) 
			echo "Recursive folder search enabled."
			unset recursive
			recursive=true
			unset folder
			unset output_file
			folder=$2
			output_file=$3
		;;
	esac
done



#check that the folder exists and is a directory
if [ ! -d "$folder" ]
then
	echo "Invalid command line arguments."
	exit 0
fi

#if output file does not exist, create it
if [ ! -e "$output_file" ]
then
	touch "${output_file}"
fi

cd "${folder}"

if [[ ! recursive ]]; then
	for file in *.mp3
	do
		echo "${file}" >> "${output_file}"
	done
	for file in *.m4a
	do
		echo "${file}" >> "${output_file}"
	done
	echo "Process complete."
	exit 1
fi

if [[ recursive ]]; then
	find "${folder}" -name "*.mp3" >> "${output_file}"
	find "${folder}" -name "*.m4a" >> "${output_file}"
	echo "Process complete."
	exit 1
fi