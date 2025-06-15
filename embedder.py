from langchain.vectorstores import Chroma
from langchain.schema import Document
import os
import json
from utils import get_embedding


PERSIST_DIR = "structured_output/chroma_invoice_store"
COLLECTION_NAME = "invoice_expenditures"



def embed_expenditures(expenditures: list[dict]):
    embedding_function = get_embedding()

    # Load or create collection
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=PERSIST_DIR
    )

    documents = []
    for item in expenditures:
        metadata = item.get("metadata", {})
        content_dict = {k: v for k, v in item.items() if k != "metadata"}
        doc = Document(
            page_content=json.dumps(content_dict, indent=2),
            metadata=metadata
        )
        documents.append(doc)

    vectorstore.add_documents(documents)
    vectorstore.persist()
    print(f"✅ Added {len(documents)} items to Chroma collection '{COLLECTION_NAME}'")
