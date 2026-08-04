import importlib.util

# Load the module with hyphens in the name
module_path = '/Users/admin/Desktop/agent-factory/tools/api-secrets-exposed/tool-L1-confluence-page-writer-and-updater/tool-L1-confluence-page-writer-and-updater.py'
spec = importlib.util.spec_from_file_location("confluence_tool", module_path)
confluence_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(confluence_tool)

ConfluencePageCreator = confluence_tool.ConfluencePageCreator

# Create an instance of the tool
tool = ConfluencePageCreator()

# Test with sample inputs
result = tool._run(
    title="New Banana",
    content="<p>This is test content for the Confluence page.</p>",
    space_key="~7120208dde8969e5854fbfbe0185df21567c33",  # Replace with actual space key
    base_url="https://aava-temp-ggm.atlassian.net/wiki"  # Replace with actual URL
)

print("Tool Result:")
print(result)
