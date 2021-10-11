#!/bin/bash

#############################################################
# Default values
#############################################################


#############################################################
# Help
#############################################################
Help()
{
        echo "This script anonymizes a JsonL file with sensitive span annotations keeping the labels and the context"
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

python substitution_of_sensitive_data.py -f $FILE_PATH -o $DIRECTORY

