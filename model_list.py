import os
from openai import OpenAI
import re

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)
models = client.models.list()
for model in models:
    model_id=model.id

    if re.search(r"o4", model_id):
        print(model_id)
