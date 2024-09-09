import os
import json
from openai import OpenAI
from dotenv import load_dotenv

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def prompt_openai(prompt):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content



def get_tracklist(input_text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts tracklists to structured data."},
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

    return json.loads(response.choices[0].message.function_call.arguments)

# # Use the function to process the input_tracklist
# processed_tracklist = get_tracklist(input_tracklist)
