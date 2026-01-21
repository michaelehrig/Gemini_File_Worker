import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from creations.Gemini_File_Worker.config import model_name

def get_file_list(extension_list: list = []) -> list[str]:
    """
    Generates list of all files in the directory.

    Returns
    -------
    list[str]
        list of all file names in directory
    """
    file_list = []
    directory_content = os.listdir(os.path.abspath('source/'))
    for content in directory_content:
        content_source = os.path.join('source/', content)
        if os.path.isfile(content_source):
            base, extension = os.path.splitext(content)
            if extension in extension_list:
                file_list.append(content)
    file_list.sort(key=str.lower)
    return file_list


def main():
    load_dotenv()

    # Lits all supported file types
    file_types = ['.md', '.txt', '.pdf', '.jpg']
    
    # Obtain API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None:
        raise RuntimeError("Api key not found!")

    # Initiate client
    client = genai.Client(api_key=api_key)

    # Lits all acceptable files in source/ directory
    file_list = get_file_list(file_types)
    if file_list == []:
        print('No files available in \'source/\' .')
        sys.exit(0)
    else:
        while True:
            print('\033[91m'+'--------'+'\033[0m')
            print("Available files:")
            for i,file in enumerate(file_list):
                print(f'{i}: {file}')
            print('\033[91m'+'--------'+'\033[0m')
            number = input('Which file (input the number or \X to exit)? ')
            if number == '\X':
                print('Exiting')
                sys.exit(0)
            if number.isdigit():
                if 0 <= int(number) < len(file_list):
                    file_name = file_list[int(number)]
                    break
    file_path = "source/" + file_name
    
    _, extension = os.path.splitext(file_path)
    if extension == '.md' or extension == '.txt':
        config_dict={"mime_type": "text/plain"}
    elif extension == '.pdf':
        config_dict={"mime_type": "application/pdf"}
    elif extension == '.jpg':
        config_dict={"mime_type": "image/jpeg"}
        
        
    # Uploads file to the client
    try:
        print(f'Uploading: {file_path}')
        upload_file = client.files.upload(file=file_path, config=config_dict)
    except Exception as e:
        print(f'Error: {e}')
    except:
        print('Could not upload and analyze file.')
        sys.exit(1)
        
    # Asks for prompt, if none given it summarizes
    
    prompt = input('What should be done with the file? (blank for summarize) ')
    if prompt == '':
        prompt = "Summarize and return in markdown format."
    else:
        prompt += " Return your response in markdown format."

    print(f'Working on: {file_path}')

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt, upload_file]
    )
    md_file_name = file_name.split('.')[0] + '.md'
    
    # Saves response result as results/result_<original file name>.md
    try:
        with open("results/result_"+md_file_name, "w") as f:
            print(f'Writing: results/result_{md_file_name}')
            f.write(response.text)
    except:
        print('Could not write summary.')

    # Delete uploaded file again
    try:
        print(f'Deleting uploaded file')
        client.files.delete(name=upload_file.name)
    except Exception as e:
        print(f"Error deleting file online: {e}")
    
if __name__ == "__main__":
    main()
