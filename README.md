# Wikimedia Streaming to Google Cloud Pub/Sub

This Python script connects to the Wikimedia EventStreams API to receive real-time changes (edits, page creations, etc.) and publishes them to a Google Cloud Pub/Sub topic for downstream processing.

---

## 📌 Features

- Connects to the [Wikimedia RecentChange Stream](https://stream.wikimedia.org/v2/stream/recentchange) using Server-Sent Events (SSE)
- Handles dropped connections and retries gracefully
- Transforms incoming event data
- Publishes structured JSON messages to a Google Cloud Pub/Sub topic

---

## 📁 Project Structure

```
.
├── wikimedia_streaming.py   # Main Python script
├── pp_ram_gcp_key.json      # GCP service account credentials (DO NOT commit this file)
├── README.md                # Project documentation
```

---

## 🧰 Requirements

- Python 3.12
- Google Cloud Pub/Sub enabled in your GCP project
- A service account with Pub/Sub permissions
- Required Python libraries (see below)

---

## 📦 Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Ram531/pp_wikimedia.git
   cd wikimedia-streaming
   ```

2. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install requests sseclient google-cloud-pubsub
   ```

4. **Set up Google Cloud credentials**:
   Replace the path in the script with your service account JSON key path:
   ```python
   os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/absolute/path/to/pp_ram_gcp_key.json"
   ```

5. **Create the Pub/Sub topic** (if not already created):
   ```bash
   gcloud pubsub topics create pp_wikimedia_streaming_topic
   ```

---

## 🚀 Usage

Run the script:
```bash
python wikimedia_streaming.py
```

This will:
- Open a connection to the Wikimedia SSE endpoint.
- Stream real-time events (like edits on Wikipedia).
- Publish each event to your configured Google Cloud Pub/Sub topic.

---

## 🔁 Error Handling & Retry Logic

The script includes retry handling for the common error:

```
requests.exceptions.ChunkedEncodingError: Response ended prematurely
```

This ensures the connection to the stream is re-established automatically after a failure.

---

## 🔄 Sample Pub/Sub Message Format

```json
data: 
{
"$schema":"/mediawiki/recentchange/1.0.0",
"meta":
{
"uri":"https://sr.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%98%D0%B0:Pages_with_single-entry_sister_bar",
"request_id":"f6421873-98fd-45e9-a91d-dece1d62649b",
"id":"2c5e6863-38a2-4f03-8750-4ae506ded929",
"dt":"2025-04-11T18:33:45Z",
"domain":"sr.wikipedia.org",
"stream":"mediawiki.recentchange",
"topic":"eqiad.mediawiki.recentchange",
"partition":0,
"offset":5503696246
},
"id":60804600,
"type":"categorize",
"namespace":14,
"title":"Категорија:Pages with single-entry sister bar",
"title_url":"https://sr.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%98%D0%B0:Pages_with_single-entry_sister_bar",
"comment":"[[:Јеврем Грбовић]] је додата у категорију",
"timestamp":1744396425,
"user":"FelixBot",
"bot":true,
"notify_url":"https://sr.wikipedia.org/w/index.php?diff=29247950&oldid=28528557&rcid=60804600",
"server_url":"https://sr.wikipedia.org",
"server_name":"sr.wikipedia.org",
"server_script_path":"/w",
"wiki":"srwiki",
"parsedcomment":"<a href=\"/wiki/%D0%88%D0%B5%D0%B2%D1%80%D0%B5%D0%BC_%D0%93%D1%80%D0%B1%D0%BE%D0%B2%D0%B8%D1%9B\" title=\"Јеврем Грбовић\">Јеврем Грбовић</a> је додата у категорију"
}
```

*Note: The `$schema` field from the Wikimedia event is renamed to `schema` to maintain compatibility with BigQuery processing.*

---

## 🛡️ Security

- Never commit your `pp_ram_gcp_key.json` file to version control.
- Use IAM roles to restrict access to only necessary Pub/Sub permissions.

---

## 📞 Contact

For any questions or issues, feel free to contact [Ram Ganesh Natarajan](mailto:rganesh333@gmail.com).


## 📌 Key Decisions Made

1. **Use of Server-Sent Events (SSE) for Wikimedia Stream**  
   Chose SSE over WebSockets or polling because Wikimedia provides real-time event delivery using SSE. This reduces overhead and simplifies stream handling.

2. **Use of `sseclient` Library**  
   Adopted `sseclient` to efficiently handle streaming responses and iterate over events. Native `requests` does not support SSE directly.

3. **Retry on Connection Drop (ChunkedEncodingError)**  
   Implemented a retry loop to handle long-lived connections that may fail due to `ChunkedEncodingError`. This prevents unexpected termination and supports stable streaming.

4. **Schema Field Transformation (`$schema` → `schema`)**  
   Renamed `$schema` to `schema` before publishing to Pub/Sub, as `$` is not supported in many downstream JSON parsers and databases.

5. **Direct Use of Service Account Key in Dev**  
   For development simplicity, the service account key is loaded using `os.environ["GOOGLE_APPLICATION_CREDENTIALS"]`. For production, consider using workload identity or Secret Manager.

6. **Hardcoded Topic Path for Simplicity**  
   The topic path `pp_wikimedia_streaming_topic` is currently hardcoded. This can be made configurable via environment variables or CLI arguments for flexibility.

7. **Minimal Processing Before Publishing**  
   The design intentionally avoids filtering or complex transformation before publishing. The goal is to preserve full event fidelity and handle transformation downstream if needed.

8. **PUB/SUB Pull Method Chosen Over Push**  
   Push-based ingestion into BigQuery introduced delays of over 30 minutes. The pull model ensures more control and reliability for downstream systems.

9. **Ingestion Delay in BigQuery (Push Mode)**  
   Observed ingestion latency of ~30+ minutes using push subscription to BigQuery, which did not meet near real-time needs.

10. **Use of Dataflow Template for Near Real-Time Ingestion**  
    Dataflow was selected to consume messages via pull and stream them into BigQuery in near real-time, solving the ingestion delay problem.
--