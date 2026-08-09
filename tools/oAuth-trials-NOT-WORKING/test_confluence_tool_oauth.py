import importlib.util

# Load the OAuth version of the tool
module_path = '/Users/admin/Desktop/agent-factory/tools/api-secrets-exposed/tool-L1-confluence-page-writer-and-updater/tool-L1-confluence-page-writer-and-updater-oauth.py'
spec = importlib.util.spec_from_file_location("confluence_tool_oauth", module_path)
confluence_tool_oauth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(confluence_tool_oauth)

ConfluencePageCreator = confluence_tool_oauth.ConfluencePageCreator

# Create an instance of the tool
tool = ConfluencePageCreator()

# Test with sample inputs
result = tool._run(
    title="Test Page OAuth",
    content="<p>This is test content using OAuth 2.0 authentication.</p>",
    space_key="~7120208dde8969e5854fbfbe0185df21567c33",
    base_url="https://aava-temp-ggm.atlassian.net/wiki"
)

print("Tool Result:")
print(result)
