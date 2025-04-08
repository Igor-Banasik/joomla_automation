import os
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o-mini",
    input="Write a 140–145 character metadata description for 'Events in Italy', starting with its name followed by a colon or dash."
)

print(response.output_text)

