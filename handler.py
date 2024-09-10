import json
import datetime
from ProgressiveMotorcycleBot.spiders.Motorcycle_Bot import run_bot

def main(event, context):
    print(event, context)
    if 'body' not in event or not event['body']:
        print("Error: No body found in the request.")
        raise ValueError("No body found in the request.")

    # Extract the body from the event
    body = event['body']
    print("*** Received body: ", body)

    # Check if body is a string, and if so, parse it as JSON
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError as e:
            print("Error: Failed to parse body as JSON.")
            raise ValueError("Failed to parse body as JSON.") from e

    # Check if the actual data is nested inside another dictionary
    if 'body' in body:
        body = body['body']

    result = run_bot(body)
    print('RESULT', result)
    if isinstance(result, str):
        return {
            'statusCode': 500,
            'error': result
        }

    return result
