import azure.functions as func
# import time
import requests
# from datetime import datetime, timezone
# from openai import AzureOpenAI
# import os
import json
# from typing import Optional, Union, Any, Dict
from final_chatbot import query_chatbot


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_question = req_body.get('question')

        if not user_question:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'question' in request body."}),
                status_code=400,
                mimetype="application/json"
            )

        #answer = query_chatbot(user_question)
        answer = "test"

        return func.HttpResponse(
            json.dumps({"question": user_question, "answer": answer}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
