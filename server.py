import os
from fastapi import FastAPI, Request, Response
from main import parse_webhook_post, run_compliance_check, create_or_update_report

KEY = os.environ.get("KEY")

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    if request.method == "POST":
        # if request.headers.get("X-Webhook-Secret") != KEY:
        #     return Response("Invalid secret", status_code=401)

        data = await request.json()

        if parsed_post := parse_webhook_post(data):
            repo_name = parsed_post
        else:
            return Response("Unable to parse webhook data", status_code=400)

        compliance_check = run_compliance_check(repo_name)
        result = create_or_update_report(compliance_check, repo_name)
        return result
