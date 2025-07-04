import azure.functions as func
import json
import time
import os
import requests
from datetime import datetime, timezone
from openai import AzureOpenAI
from typing import Optional, Union, Any, Dict

# Constants (should ideally come from environment variables)
AZURE_SERVICE_NAME = "starlink-aisearch-nprd"
AZURE_SEARCH_API_VERSION = "2020-06-30"
AZURE_SEARCH_INDEX = "shipment-data-index"
AZURE_SEARCH_ENDPOINT_C = f"https://{AZURE_SERVICE_NAME}.search.windows.net/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version={AZURE_SEARCH_API_VERSION}"

AZURE_OPENAI_API_KEY = "rEgv1GQVyOg1JjyskTQd2twIRroog6lVfrIkRMTUHstO8lxTCTaOJQQJ99BFACHYHv6XJ3w3AAABACOG41dX"
AZURE_OPENAI_ENDPOINT = "https://starlink-openai-nprd.openai.azure.com/openai/deployments/gpt-35-turbo-starlink/chat/completions?api-version=2025-01-01-preview"
AZURE_OPENAI_DEPLOYMENT = "gpt-35-turbo-starlink"
AZURE_OPENAI_API_VERSION = "2023-12-01-preview"
SECRET_1 = "EtbxI75wdOgVThA39ziNcN21rsbIOO2738rzV5VImjAzSeAOLkHy"

log_file = "chatbot_logs.jsonl"

def log_interaction(user_query: str, bot_response: str, latency: float, is_correct: Optional[bool]=None) -> None:
    log_entry: dict[str, Union[str, float, bool, None]] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": user_query,
        "response": bot_response,
        "latency_sec": latency,
        "correct": is_correct
    }
    try:
        with open(log_file, "a") as file:
            file.write(json.dumps(log_entry) + "\n")
    except IOError as e:
        print(f"Error writing to log file: {e}")

def query_azure_search(user_query: str) -> Dict[str, Any]:
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "api-key": SECRET_1
    }
    payload: Dict[str, Union[str, int]] = {
        "search": user_query,
        "queryType": "simple",
        "top": 5
    }
    response = requests.post(AZURE_SEARCH_ENDPOINT_C, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_system_prompt() -> str:
    fields = "ContainerNo, ContainerTy, DestinationSer, LoadPort, FinalLoadPort, DischargePort, LastCyLoc"
    return (
        "You are an AI-powered logistics assistant specializing in shipment data. "
        "Answer questions ONLY using the provided data from Azure AI Search. "
        "If you don’t know, say 'I don’t have that information but still learning.'\n\n"
        f"Use only the following fields: {fields}.\n"
        "Never invent details.\n"
        "Format dates as DD-MMM-YYYY (e.g., 13-Jan-2025)."
    )

def query_chatbot(user_query: str) -> Union[str, Any]:
    start_time = time.time()
    try:
        system_prompt = get_system_prompt()
        search_results = query_azure_search(user_query)
        documents = [doc.get("content", "") for doc in search_results.get("value", [])]
        context = "\n\n".join(documents)

        openai_client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            _strict_response_validation=False
        )

        response = openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
            ]
        )

        bot_response = response.choices[0].message.content
        latency = time.time() - start_time
        log_interaction(user_query, bot_response, latency)
        return bot_response

    except Exception as err:
        print(f"System encountered an error: {err}")
        return None

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_query = req_body.get("question")

        if not user_query:
            return func.HttpResponse("Missing 'question' in request body.", status_code=400)

        answer = query_chatbot(user_query)
        if answer is None:
            return func.HttpResponse("Internal error occurred during chatbot execution.", status_code=500)

        return func.HttpResponse(json.dumps({"response": answer}), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Unhandled error: {str(e)}", status_code=500)
