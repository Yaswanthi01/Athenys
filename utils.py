
import json
import re
import ast
from langchain_openai import AzureOpenAIEmbeddings
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION,OPENAI_API_TYPE

def get_embedding():
    """Get the embedding model."""
    return AzureOpenAIEmbeddings(
        chunk_size=1,
        azure_deployment="text-embedding-ada-002",
        api_version=OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_type=OPENAI_API_TYPE,
    )


def extract_json_str(text):
	"""
	Extracts the JSON substring from the given text by locating the first
	'{' and the last '}' to capture the JSON object.
	"""
	# Replace double {{ and }} with single braces
	text = text.replace("{{", "{").replace("}}", "}")
	start_index = text.find("{")
	end_index = text.rfind("}") + 1  # +1 to include the closing brace in the slice

	if start_index == -1 or end_index == -1 or start_index > end_index:
		return "{}"
	return text[start_index:end_index]


def remove_trailing_commas(json_str):
	"""
	Removes trailing commas before closing braces or brackets.
	For example: {"key1": "value1",} -> {"key1": "value1"}
	"""
	# Regex to find trailing commas before } or ]
	pattern = r",\s*([}\]])"
	cleaned_str = re.sub(pattern, r"\1", json_str)
	return cleaned_str


def fix_quotes(json_str):
	"""
	Replaces single quotes with double quotes to conform to JSON standards.
	It ensures that only quotes around keys and string values are replaced.
	"""
	# This regex finds single-quoted keys or string values
	pattern = r"\'([^']*)\'"
	cleaned_str = re.sub(pattern, r'"\1"', json_str)
	return cleaned_str


def balance_braces(json_str):
	"""
	Balances the number of opening and closing braces/brackets by adding
	missing closing braces/brackets at the end of the string.
	"""
	braces = {"{": "}", "[": "]"}
	stack = []
	for char in json_str:
		if char in braces:
			stack.append(braces[char])
		elif char in braces.values():
			if stack and char == stack[-1]:
				stack.pop()
			else:
				# Unexpected closing brace/bracket
				pass  # You might want to handle this case differently
	# Add the necessary closing braces/brackets
	balanced_str = json_str + "".join(stack)
	return balanced_str


def load_json(text):
	"""
	Extracts and parses a JSON object from the given text.
	It attempts to fix common JSON errors by removing trailing commas,
	fixing quotes, and balancing braces/brackets before parsing.
	"""
	# Extract the JSON substring from the text
	json_str = extract_json_str(text)

	# Attempt initial parsing
	try:
		json_dict = json.loads(json_str)
		return json_dict
	except json.JSONDecodeError:
		pass  # Proceed to attempt fixing the JSON

	# Step 1: Remove trailing commas
	json_str = remove_trailing_commas(json_str)

	# Step 2: Fix quotes
	json_str = fix_quotes(json_str)

	# Step 3: Balance braces/brackets
	json_str = balance_braces(json_str)

	# Attempt parsing again
	try:
		json_dict = json.loads(json_str)
		return json_dict
	except json.JSONDecodeError:
		pass  # Proceed to the next attempt

	# Step 4: Attempt using ast.literal_eval as a fallback
	try:
		# ast.literal_eval can handle single quotes and other Python literals
		json_data = json.dumps(ast.literal_eval(json_str))
		json_dict = json.loads(json_data)
		return json_dict
	except Exception:
		# If all attempts fail, return an error dictionary
		return {"Error": "JSON conversion error", "text": text}
