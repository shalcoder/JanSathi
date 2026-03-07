import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agentcore.tools import retrieve_knowledge
from app.api import create_app

app = create_app()

with app.app_context():
    result = retrieve_knowledge("PM-KISAN, PM Awas, e-Shram, Ayushman Bharat", language="en")
    print(result)
