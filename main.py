import os
import json
from parser import parse_invoice
from embedder import embed_expenditures

INVOICE_DIR = "invoices"
OUTPUT_JSON = "structured_output/parsed_expenditures.json"

def main():
    structured = []

    for fname in os.listdir(INVOICE_DIR):
        if fname.endswith(".txt"):
            path = os.path.join(INVOICE_DIR, fname)
            with open(path, "r") as f:
                raw_text = f.read()
                invoice_id = fname.replace(".txt", "") #hash this
                entries = parse_invoice(raw_text, invoice_id)
                structured.extend(entries)

    os.makedirs("structured_output", exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(structured, f, indent=2)

    embed_expenditures(structured)

if __name__ == "__main__":
    main()
