from datetime import datetime
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CurrentDateFetcherSchema(BaseModel):
    """Input schema for CurrentDateFetcher."""
    timezone: str = Field(..., description="Timezone for which the current date is fetched (e.g., UTC, EST, PST). Default is UTC.")


class CurrentDateFetcher(BaseTool):
    """
    CurrentDateFetcher - A tool to fetch the current date.
    """

    name: str = "Current Date Fetcher"
    description: str = "A tool to fetch the current date based on the provided timezone."
    args_schema: Type[BaseModel] = CurrentDateFetcherSchema

    def _run(self, timezone: str = "UTC") -> str:
        try:
            print(f"Fetching current date for timezone: {timezone}")
            # For simplicity, we assume UTC as the default timezone.
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            return f"Current date in {timezone}: {current_date}"

        except Exception as e:
            return f"Error fetching current date: {str(e)}"
