import azure.functions as func
import json
import time
import os
import requests
from datetime import datetime, timezone
from openai import AzureOpenAI
from typing import Optional, Union, Any, Dict


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_query = req_body.get("question")

        if not user_query:
            return func.HttpResponse("Missing 'question' in request body.", status_code=400)

        #answer = query_chatbot(user_query)
        answer = "test"
        if answer is None:
            return func.HttpResponse("Internal error occurred during chatbot execution.", status_code=500)

        return func.HttpResponse(json.dumps({"response": answer}), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Unhandled error: {str(e)}", status_code=500)
