import os
import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings (only when JIRA_VERIFY_SSL=false, i.e. local dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JIRACommentPublisherSchema(BaseModel):
    '''Input schema for JIRACommentPublisher.'''
    issue_key: str = Field(..., description="JIRA issue key (e.g., PROJECT-123)")
    body: str = Field(..., description="Comment text. JIRA wiki markup is supported (h3. heading, *bold*, {code}...{code}, || table headers ||). Not markdown.")


class JIRACommentPublisher(BaseTool):
    '''
    JIRACommentPublisher - A tool to post a comment onto a JIRA issue via API.

    Companion to JIRAUserStoryRetriever. Used by agents that must write their
    verdict, review packet or evidence bundle back onto the ticket so the
    ticket remains the audit record.

    Comments are posted unrestricted — visible to everyone who can see the
    issue. This is deliberate: the comment IS the audit record and must reach
    the PM who wrote the story and the architect who approves the design.
    Restricting it is not supported by this tool.
    '''

    name: str = "JIRA Comment Publisher"
    description: str = "A tool to post a comment on a JIRA issue."
    args_schema: Type[BaseModel] = JIRACommentPublisherSchema
    jira_url: str = "https://worktejasc.atlassian.net"

    def _run(self, issue_key: str, body: str) -> Any:
        try:
            print(f"Posting comment to JIRA issue: {issue_key}")

            # Retrieve API token and username from secret manager / environment.
            # Never hardcode credentials in the tool body.
            username = "work.tejasc@gmail.com"
            api_token = '[Redacted]'
            if not username or not api_token:
                return {
                    "success": False,
                    "error": "Missing credentials. Set JIRA_USERNAME and JIRA_API_TOKEN."
                }

            if not body or not body.strip():
                return {
                    "success": False,
                    "error": "Comment body is empty. Refusing to post an empty comment."
                }

            # Construct the API endpoint URL
            self.jira_url = "https://worktejasc.atlassian.net"
            api_endpoint = f"{self.jira_url.rstrip('/')}/rest/api/2/issue/{issue_key}/comment"

            # Set up the authentication
            auth = HTTPBasicAuth(username, api_token)

            # Set headers
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # API v2 takes wiki markup as a plain string.
            # No "visibility" key -> comment is visible to everyone with issue access.
            payload = {"body": body}

            verify_ssl = os.environ.get("JIRA_VERIFY_SSL", "true").lower() != "false"

            response = requests.post(
                api_endpoint,
                headers=headers,
                auth=auth,
                json=payload,
                verify=verify_ssl,
                timeout=30
            )

            # Surface JIRA's own error messages rather than a bare status code
            if response.status_code >= 400:
                detail = response.text
                try:
                    err = response.json()
                    detail = "; ".join(
                        err.get("errorMessages", []) +
                        [f"{k}: {v}" for k, v in err.get("errors", {}).items()]
                    ) or response.text
                except ValueError:
                    pass
                return {
                    "success": False,
                    "issue_key": issue_key,
                    "status_code": response.status_code,
                    "error": f"Error posting comment: {detail}"
                }

            comment = response.json()
            author = comment.get("author") or {}
            comment_id = comment.get("id")

            return {
                "success": True,
                "issue_key": issue_key,
                "comment_id": comment_id,
                "comment_url": f"{self.jira_url.rstrip('/')}/browse/{issue_key}?focusedCommentId={comment_id}",
                "created": comment.get("created"),
                "author": author.get("displayName"),
                "body_preview": (body[:200] + "...") if len(body) > 200 else body
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "issue_key": issue_key,
                "error": f"Error posting comment: {str(e)}"
            }

            

           