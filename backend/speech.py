
from lmnt.api import Speech
import os 
from dotenv import load_dotenv

load_dotenv()

speech_client = Speech(os.getenv("LMNT_API_KEY"))