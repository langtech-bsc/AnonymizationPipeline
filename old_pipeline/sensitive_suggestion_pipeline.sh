#!/bin/bash

#############################################################
# Default values
#############################################################


#############################################################
# Help
#############################################################
Help()
{
        echo "This script generates labeled suggestions in Conll format to be imported in Doccano"
        echo 
        echo "Syntax: anonymize [-h] [arguments]"
        echo "options:"
        echo "h       Print this Help."
        echo "arguments:"
        echo "d         Wether the script will run in the docker container or not (important for the relative paths)"
        echo "f <path>  Name of the file to be anonymized (if running on docker it must be only the name inside the volume)"
        echo "o <path>  Name of the output directory (if not specified the directory of the input will be used)"
        echo 
        echo "Author: Joaquin Dario Silveira Ocampo"
        echo 

}

# Get the options
while getopts ":hdf:o:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      d) # Running inside the Docker container
         DOCKER=true
         ;;
      f) # env name
         FILE_PATH=$OPTARG
         ;;
      o) # env name
         DIRECTORY=$OPTARG
         ;;
     \?) # incorrect option
         echo "Error: Invalid option"
         echo ;
         Help 
         exit;;
   esac
done

if [ -z "$FILE_PATH" ]; then
        echo "A path to the file to be anonymized must be set";
        echo ;
        Help 
        exit ;
fi

if [ "$DOCKER" = true ]; then
        echo "Running in the Docker anonym_pipeline container (the mounted volume is located in ../vol1/";
        DIRECTORY=../vol1 ;
        FILE_PATH=$DIRECTORY/$FILE_PATH ;
        echo ;
else
        if [ ! -d "venvAnon" ]; then
            python3 -m venv --system-site-packages venvAnon
            echo "Created virtual environment for execution"
            source venvAnon/bin/activate
            pip install -r requirements.txt
            # deactivate
        fi
        source venvAnon/bin/activate
        echo "Running in local setup" ;
        echo ;
fi

if [ -z "$DIRECTORY" ]; then
        echo "Using the input file directory as output directory";
        DIRECTORY="$(dirname "$FILE_PATH")" ;
        echo ;
fi

# echo $FILE_PATH
# echo $DIRECTORY

# PROCESS:
#---------
# Regex over original text and generate brat output
# Convert brat to conll 
# Execute Name identification over the conll and generate a new conll (only change the labels)


#Run the identification of regular expressions (Telephones, Bank accounts, Identification numbers, E-mail addresses, credit cards, etc)
python3 sensitive_data_identification.py -f $FILE_PATH

#Copy the original text to the folder in which the BRAT result of the previous step is located so that we can transform the BRAT into CONLL
cp $FILE_PATH output/tmp/sensitive_identification.txt

#Transform the result of the regular expression identification from BRAT format to CONLL format with added span information
python3 brat_to_conll.py -i output/tmp/ -o output/text_brat_to_conll.conll

#Run the identification of common names in Spain (from list of names)
# python3 name_identification.py # Seems that with ROBERTa name identificatio I don't need the regex names anymore
python3 cleanConllForDoccano.py
# cp output/text_brat_to_conll.conll output/suggestion.conll

#Copy the suggestion conll file to the directory that contains the original text
cp output/suggestion.conll $DIRECTORY/suggestion.txt