import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        name = req.params.get('name')
        if not name:
            req_body = req.get_json()
            name = req_body.get('name')

        return func.HttpResponse(
            json.dumps({"message": f"Hello, {name}!"}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
