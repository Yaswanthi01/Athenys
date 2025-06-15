import json
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION
from utils import load_json


llm = AzureChatOpenAI(
    model="gpt-4o",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)

prompt = ChatPromptTemplate.from_template("""
You are an intelligent invoice parser.

Your task is to convert raw invoice text into structured JSON with two sections:

---

1. **"metadata"**: This is a fixed structure used solely for indexing and filtering.
It must include:
- invoice_id
- company_name (entity being billed)
- payer (entity paying)
- recipient (vendor/service provider)
- year (from invoice or payment date)
- month
- category (e.g., infrastructure, marketing, travel, legal, software, hardware, logistics, HR, events, consulting — pick the most specific category based on the invoice content)
---

2. **"expenditures"**: This is a list of detailed entries, one per line item in the invoice.
Each entry should:
- Include all useful information about that item or service
- Also include relevant invoice-level context such as:
  - invoice_id
  - company_name
  - payer
  - recipient
  - date / service_period
  - category
- Include keys like description, amount, unit_price, quantity, tax, total, service_period, notes, etc.
- Include only keys that are actually present (omit nulls or empty fields)
- NOT rely on metadata to infer context — all necessary context should be repeated inside each entry

---

Respond only with a JSON object with the following keys:

  "metadata":  a dictionary,
  "expenditures": a list of dictionaries


Do not add explanations, formatting, or placeholders.

---

Invoice ID: {invoice_id}

Invoice Text:
\"\"\"
{invoice_text}
\"\"\"
""")


chain = LLMChain(llm=llm, prompt=prompt)

def parse_invoice(text: str, invoice_id: str):
    try:
        result = chain.run(invoice_text=text, invoice_id=invoice_id)
        #cleaning json
        result = load_json(result)
        try : 
            structured = json.loads(result)
        except Exception as _:
            structured = result
        expenditures = structured.get("expenditures", [])
        metadata = structured.get("metadata", {})

        # Attach metadata to each item
        for exp in expenditures:
            exp["metadata"] = metadata
        return expenditures
    except Exception as e:
        print(f"LLM parsing failed for {invoice_id}: {e}")
        return []
    
if __name__ == "__main__":
    # Example usage
    #call the fucntion 
    output = parse_invoice("Sample invoice text", "INV-12345")  
    print(output)                                
