import azure.functions as func
import json
from final_chatbot import query_chatbot

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_query = req_body.get("question")

        if not user_query:
            return func.HttpResponse("Missing 'question' in request body.", status_code=400)

        # answer = query_chatbot(user_query)
        answer = "test"
        return func.HttpResponse(json.dumps({"response": answer}), mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
