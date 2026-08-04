import os
import json
import requests
import urllib3
import webbrowser
from typing import Type
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

CLIENT_ID = os.getenv("CONFLUENCE_CLIENT_ID")
CLIENT_SECRET = os.getenv("CONFLUENCE_CLIENT_SECRET")
CONFLUENCE_DOMAIN = os.getenv("CONFLUENCE_DOMAIN")

if not all([CLIENT_ID, CLIENT_SECRET, CONFLUENCE_DOMAIN]):
    raise ValueError(
        "Missing required environment variables: CONFLUENCE_CLIENT_ID, CONFLUENCE_CLIENT_SECRET, CONFLUENCE_DOMAIN. "
        "Please set them in your .env file."
    )

REDIRECT_URI = "http://localhost:8000/callback"
TOKEN_ENDPOINT = "https://auth.atlassian.com/oauth/token"
AUTHORIZE_ENDPOINT = "https://auth.atlassian.com/authorize"
TOKEN_FILE = os.path.expanduser("~/.confluence_oauth_token.json")

_oauth_tokens = None
_callback_code = None
_server = None


class CallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Atlassian."""

    def do_GET(self):
        global _callback_code
        query_params = parse_qs(urlparse(self.path).query)
        _callback_code = query_params.get("code", [None])[0]

        if _callback_code:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Success!</h1><p>You can close this window and return to your terminal.</p></body></html>"
            )
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Error</h1><p>No authorization code received.</p></body></html>")

    def log_message(self, format, *args):
        pass


def load_tokens():
    """Load stored OAuth tokens from file."""
    global _oauth_tokens
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            _oauth_tokens = json.load(f)
            return _oauth_tokens
    return None


def save_tokens(tokens):
    """Save OAuth tokens to file."""
    global _oauth_tokens
    _oauth_tokens = tokens
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    os.chmod(TOKEN_FILE, 0o600)


def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    resp = requests.post(
        TOKEN_ENDPOINT,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        verify=False
    )
    resp.raise_for_status()
    return resp.json()


def authenticate_user():
    """Perform OAuth 2.0 Authorization Code flow."""
    global _callback_code, _server

    # Start local callback server
    _server = HTTPServer(("localhost", 8000), CallbackHandler)

    # FIX 1: Audience must be api.atlassian.com
    # FIX 2: offline_access is required to receive a refresh_token
    auth_url = (
        f"{AUTHORIZE_ENDPOINT}"
        f"?audience=api.atlassian.com"
        f"&client_id={CLIENT_ID}"
        f"&scope=offline_access write:confluence-content read:confluence-content.all read:confluence-space.summary write:confluence-space manage:confluence-configuration"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&prompt=consent"
    )

    print("\n🔐 Opening browser for authentication...")
    # ... rest of the function remains the same


    print(f"If browser doesn't open, visit: {auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for callback
    _server.handle_request()
    _server.server_close()

    if not _callback_code:
        raise RuntimeError("Failed to get authorization code from Atlassian")

    # Exchange code for tokens
    resp = requests.post(
        TOKEN_ENDPOINT,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": _callback_code,
            "redirect_uri": REDIRECT_URI,
        },
        verify=False
    )
    resp.raise_for_status()
    tokens = resp.json()
    print(f"\nDEBUG - Token response: {json.dumps(tokens, indent=2)}\n")
    save_tokens(tokens)
    return tokens


def get_oauth_client() -> requests.Session:
    """Get a requests Session with valid OAuth 2.0 access token."""
    global _oauth_tokens

    # Try loading existing tokens
    tokens = load_tokens()

    if not tokens:
        print("\n✨ First time setup: authenticating with Confluence...")
        tokens = authenticate_user()

    # Check if token needs refresh
    if "access_token" not in tokens and "refresh_token" in tokens:
        print("🔄 Refreshing access token...")
        tokens = refresh_access_token(tokens["refresh_token"])
        save_tokens(tokens)

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {tokens['access_token']}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    return session


class ConfluencePageCreatorSchema(BaseModel):
    """Input schema for ConfluencePageCreator."""
    title: str = Field(..., description="The title of the Confluence page. If it exists, content is appended; otherwise a new page is created.")
    content: str = Field(..., description="The body content to add, in Confluence storage format (XHTML). Basic tags like <p>, <h1>, <ul>, <table> are accepted.")
    space_key: str = Field(..., description="The key of the space, e.g. '~7120208dde8969e5854fbfbe0185df21567c33'.")
    base_url: str = Field(..., description="The base URL of the Confluence instance, e.g. 'https://your-domain.atlassian.net/wiki'.")


class ConfluencePageCreator(BaseTool):
    """Creates a Confluence page, or appends to it if the title already exists."""
    name: str = "Confluence Page Creator"
    description: str = "Creates a new Confluence page, or appends content to the bottom of an existing page with the same title."
    args_schema: Type[BaseModel] = ConfluencePageCreatorSchema

    def _run(self, title: str, content: str, space_key: str, base_url: str) -> str:
        # We will keep base_url to construct the human-readable web link at the end
        user_base = base_url.rstrip("/")

        try:
            client = get_oauth_client()

            # FIX 3: Fetch the Cloud ID for the OAuth token
            res_resp = client.get("https://api.atlassian.com/oauth/token/accessible-resources", verify=False)
            res_resp.raise_for_status()
            resources = res_resp.json()

            if not resources:
                return "Error: No Atlassian resources accessible with this token. Check app permissions."
            
            # Extract cloud_id (defaults to the first authorized site)
            cloud_id = resources[0]["id"]
            
            # The new base URL for all REST API calls
            api_base = f"https://api.atlassian.com/ex/confluence/{cloud_id}"

            print(f"\nDEBUG - Using Cloud ID: {cloud_id}")

            # 1. Look for an existing page with this title in the space
            # Notice we use api_base here, not user_base
            search = client.get(
                f"{api_base}/rest/api/content",
                params={
                    "spaceKey": space_key,
                    "title": title,
                    "expand": "body.storage,version",
                },
                verify=False
            )
            search.raise_for_status()
            results = search.json().get("results", [])

            if results:
                # 2a. Page exists -> append content and update
                page = results[0]
                page_id = page["id"]
                existing_body = page.get("body", {}).get("storage", {}).get("value", "")
                current_version = page.get("version", {}).get("number", 1)

                new_body = existing_body + "<p></p>" + content

                update_payload = {
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "version": {"number": current_version + 1},
                    "body": {
                        "storage": {
                            "value": new_body,
                            "representation": "storage",
                        }
                    },
                }

                update = client.put(
                    f"{api_base}/rest/api/content/{page_id}",
                    json=update_payload,
                    verify=False
                )
                update.raise_for_status()
                data = update.json()
                webui = data.get("_links", {}).get("webui", "")
                
                # Use the user_base to construct the final clickable UI link
                full_link = f"{user_base}{webui}" if webui else "(link unavailable)"
                return (
                    f"Content appended to existing page.\n"
                    f"confluence_page_id: {page_id} \nbase_url: {user_base}\nspace_key: {space_key}\n"
                    f"\nPage Title: {title}\nVersion: {current_version + 1}\nURL: {full_link}"
                )

            else:
                # 2b. Page doesn't exist -> create it
                create_payload = {
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "body": {
                        "storage": {
                            "value": content,
                            "representation": "storage",
                        }
                    },
                }
                create = client.post(
                    f"{api_base}/rest/api/content",
                    json=create_payload,
                    verify=False
                )
                create.raise_for_status()
                data = create.json()
                new_id = data.get("id", "")
                webui = data.get("_links", {}).get("webui", "")
                
                # Use the user_base to construct the final clickable UI link
                full_link = f"{user_base}{webui}" if webui else "(link unavailable)"
                return (
                    f"Page created successfully.\n"
                    f"confluence_page_id: {new_id} \nbase_url: {user_base}\nspace_key: {space_key}\n"
                    f"\nPage Title: {title}\nVersion: 1 \nURL: {full_link}"
                )

        except requests.RequestException as e:
            # ... exception handling remains the same
            body = getattr(e.response, "text", "") if getattr(e, "response", None) else ""
            try:
                error_json = json.loads(body) if body else {}
                error_msg = error_json.get("message", body)
            except:
                error_msg = body
            return f"Error writing to Confluence page: {str(e)}\nDetails: {error_msg}"


'''
Notes:
The append is a full-page rewrite. Confluence has no "append" endpoint, so the tool reads the existing storage-format body, concatenates your new content onto the end, and PUTs the whole thing back. That's why it fetches body.storage and version in the search call — both are needed to do the update.

Version bumping is mandatory. Confluence uses optimistic locking: an update must specify version.number as exactly current + 1, or it rejects the request with a 409 Conflict. The code reads the current version and increments it.

Concurrency caveat. Because it's read-modify-write, if two runs update the same page at nearly the same moment, one can fail with a version conflict (or overwrite the other). For a single agent running sequentially this won't happen, but worth knowing if you ever parallelize.

Search matches exact title within the space. The title param does an exact match, so "KB Notes" won't match "kb notes". If the title has special characters, requests handles the URL encoding for you since it's passed via params.

OAuth 2.0 Authentication:
This tool uses OAuth 2.0 Authorization Code flow (3-legged OAuth). On first run, it opens a browser
for the user to authenticate with their Atlassian account. Tokens are cached locally in ~/.confluence_oauth_token.json
with restricted permissions (0600). Each user can only edit pages they have access to in Confluence.
Tokens are automatically refreshed when expired.
'''