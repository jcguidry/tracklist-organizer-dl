import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def prompt_openai(prompt):
    """
    Send a prompt to OpenAI and get a response.
    """
    logging.info("Sending prompt to OpenAI")

    try:
        completion = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        logging.info("Received response from OpenAI")
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error in prompt_openai: {str(e)}")
        raise

def get_tracklist(input_text):
    """
    Convert a tracklist to a structured format using OpenAI.
    Leverages OpenAI's function calling capabilities to return structured data.
    """

    base_prompt = """
    You are a helpful assistant that converts tracklists to structured data.
    You will be given a tracklist and you will need to convert it to a list of dictionaries with artist and title.
    If the name of a track is unclear, you can completely omit it from the list.
    If a track is listed, and you are not able to recognize the name of the artist, you can use "Unknown Artist".
    If a track is listed, and you are able to recognize the name of the artist, you can use their name.
    """

    logging.info("Converting tracklist to structured data")

    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": f"Convert this tracklist to a list of dictionaries: {input_text}"}
            ],
            functions=[
                {
                    "name": "process_tracklist",
                    "description": "Convert a tracklist to a list of dictionaries with artist and title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tracks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "artist": {"type": "string"},
                                        "title": {"type": "string"}
                                    },
                                    "required": ["artist", "title"]
                                }
                            }
                        },
                        "required": ["tracks"]
                    }
                }
            ],
            function_call={"name": "process_tracklist"}
        )

        structured_data = json.loads(response.choices[0].message.function_call.arguments)
        logging.debug(f"Structured tracklist: {structured_data}")
        logging.info("Tracklist conversion completed")
        return structured_data
    except Exception as e:
        logging.error(f"Error in get_tracklist: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    sample_tracklist = """
    1. Artist A - Song X
    2. Artist B - Song Y
    3. Artist C - Song Z
    """
    result = get_tracklist(sample_tracklist)
    print(json.dumps(result, indent=2))
