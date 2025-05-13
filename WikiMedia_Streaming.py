import time

import requests
import json
import sseclient
import os
import google.cloud
from google.cloud import pubsub_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/tempranar/PycharmProjects/PP_WikiMedia/pp_ram_gcp_key.json"  #LL: Set the path to your Google Cloud credentials file
print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]) #LL: Print the path to the credentials file for debugging purposes


def transform_paload(data):
    if '$schema' in data:
        data["schema"] = data.pop("$schema")
    return data


def call_wikimedia_api():
    url = "https://stream.wikimedia.org/v2/stream/recentchange"
    headers = {"Accept": "text/event-stream"} #LL: The header should be actually compatible to the data source. Here it is not Application/JSON but text/event-stream

    publisher = pubsub_v1.PublisherClient() #LL: Create a PublisherClient instance to interact with Google Cloud Pub/Sub
    topic_path = publisher.topic_path("de-ram-ganesh-natarajan", "pp_wikimedia_streaming_topic")

    print(publisher.list_topic_subscriptions(request={"topic": topic_path})) #LL: List the subscriptions for the specified topic path

    """
    Lessons Learnt
    Below While block is the Lessons Learnt as to when the script ended prematurely due to an issue.
    Issue: requests.exceptions.ChunkedEncodingError: Response ended prematurely
    Means that the streaming connection to the Wikimedia SSE API dropped unexpectedly, and your script wasn’t prepared to handle it.
    This is normal for long-running HTTP streams, especially over the internet.
    """
    while True:
        try:
            # Make a GET request to the Wikimedia API
            response = requests.get(url, headers=headers, stream=True, verify=False) #LL:stream=True is used to keep the connection open for streaming data
            client = sseclient.SSEClient(response) #LL: sseclient is a library that allows you to handle Server-Sent Events (SSE) in Python. It provides a convenient way to read and parse the incoming stream of events.

            for event in client.events(): #LL: Iterate over the events in the stream using the object returned by sseclient.SSEClient
                if event.data:
                    try:
                        data = json.loads(event.data)
                        data = transform_paload(data)
                        publisher.publish(topic_path, json.dumps(data).encode("utf-8")) #LL: Publish the JSON data to a Pub/Sub topic
                        print(f"Published message to {topic_path}: {data}")
                    except json.JSONDecodeError:
                        print("Error decoding JSON:", event.data)
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Chunked encoding error, retrying... {e}")
            time.sleep(5)
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Chunked encoding error, retrying... {e}")
            time.sleep(10)
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"Chunked encoding error, retrying... {e}")
            time.sleep(15)

if __name__ == "__main__":
    call_wikimedia_api()