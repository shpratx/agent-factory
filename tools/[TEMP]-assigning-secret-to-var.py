import json
from typing import Type, Dict, Any
from pydantic import BaseModel
from crewai.tools import BaseTool
import boto3
from botocore.exceptions import ClientError




class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity. No user inputs — everything is hardcoded."""
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads a hardcoded AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Hardcoded — edit directly in code
    SECRET_NAME: str = "aava-secret-manager-sfi-credentials"


    def _run(self) -> Dict[str, Any]:
        try:

            # region = us-east-1 for client side, us-east-2 for internal and staging
            client = boto3.client('secretsmanager', region_name='us-east-1')
            get_secret_value_response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = get_secret_value_response.get('SecretString', '{}')
            secret_dict = json.loads(secret_string)

            if not isinstance(secret_dict, dict):
                raise ValueError(f"Secret value is not a JSON object: {secret_dict}")

            return secret_dict

        except ClientError as e:
            raise RuntimeError(f"Error retrieving secret: {str(e)}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error: {str(ex)}")


reader = AWSSecretReaderPodIdentity()
secrets = reader._run()  

# Now assign specific keys to variables outside the tool
redis_password = secrets.get("redis_password")
rds_password = secrets.get("rds_password")
