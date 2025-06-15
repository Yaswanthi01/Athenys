from langchain_community.vectorstores import Chroma
from utils import get_embedding

PERSIST_DIR = "structured_output/chroma_invoice_store"
vectorstore = Chroma(
    collection_name="invoice_expenditures",
    embedding_function=get_embedding(),
    persist_directory=PERSIST_DIR
)

# Deletes all documents in the collection
all_ids = vectorstore._collection.get()["ids"]


if all_ids:
    vectorstore._collection.delete(ids=all_ids)
    vectorstore.persist() 
    print(f"✅ Deleted {len(all_ids)} documents.")
else:
    print("ℹ️ Collection already empty. Nothing to delete.")


collection_data = vectorstore._collection.get()
is_empty = len(collection_data["ids"]) == 0

if is_empty:
    print("✅ Collection is now empty.")
else:
    print("❌ Collection still has documents:", collection_data["ids"])