from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
# from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION
from rapidfuzz import fuzz
from utils import get_embedding, load_json
from datetime import datetime as Datetime
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')  
import json

COLLECTION_NAME = "invoice_expenditures"
PERSIST_DIR = "structured_output/chroma_invoice_store"

# Define fields you want to extract
METADATA_FIELDS = ["invoice_id", "company_name", "payer", "recipient", "year", "month", "category"]
METADATA_FIELDS_STR = ', '.join(METADATA_FIELDS)

def extract_metadata_from_query(query: str) -> dict:
    
    prompt = prompt = ChatPromptTemplate.from_template("""
You are an intelligent metadata extractor for invoice-based finance queries.
The current date is {current_date}.

Extract the following fields from this query:
invoice_id, company_name, payer, recipient, year, month, category

Each field may have multiple possible values, so return a list for each field.
If the field is not present, ignore it.    

Try to derive values while extracting metadata from the query.
For example, if the query mentions "invoices from 2022", extract year = 2022.
If the query mentions "invoices in the last two months", extract year = year before two months based on current date and month = month before 2 months from the current date.

Try to cover as many cases as possible , for example, if the query mentions "invoices from 01/04/2022", extract year = 2022.  extact month = [4, "April"].   
Identify such cases and return all possible values for each field.                                                 

Respond ONLY with a JSON dictionary. If a field is not present, omit it.

Query:
\"\"\"{query}\"\"\"
""")
    llm = AzureChatOpenAI(
    model="gpt-4o",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)
    chain = LLMChain(prompt=prompt, llm=llm)
    current_date = Datetime.now().strftime("%Y-%m-%d")
    response = chain.run(query = query, current_date = current_date) 
    try:
        response_output  = load_json(response)

    except Exception as _:
        response_output = response
    return response_output

def semantic_similarity(a: str, b: str) -> float:
    emb1 = model.encode(a, convert_to_tensor=True)
    emb2 = model.encode(b, convert_to_tensor=True)
    return float(util.pytorch_cos_sim(emb1, emb2).item())

def boost_score(doc: Document, extracted_meta: dict) -> float:
    score = 0
    m = doc.metadata
    per_match_score = 1.0 / len(extracted_meta) if extracted_meta else 0

    for key, query_val in extracted_meta.items():
        doc_val = m.get(key)
        if not doc_val:
            continue

        values_to_check = doc_val if isinstance(doc_val, list) else [doc_val]
        for val in values_to_check:
            val_str = str(val).lower()
            query_str = str(query_val).lower()

            fuzzy = fuzz.partial_ratio(val_str, query_str) / 100
            semantic = semantic_similarity(val_str, query_str)

            combined_score = max(fuzzy, semantic)  # Or average them
            if combined_score > 0.85:  # Threshold
                score += per_match_score
                break  # Only one match per field needed
    return score


def retrieve_docs(extracted_meta: dict) -> list[Document]:
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding(),
        persist_directory=PERSIST_DIR
    )

    # Retrieve all documents from the vectorstore
    raw = vectorstore._collection.get(include=["documents", "metadatas"])
    docs = [
        Document(page_content=doc, metadata=meta)
        for doc, meta in zip(raw["documents"], raw["metadatas"])
    ]

    scored = [(doc, boost_score(doc, extracted_meta)) for doc in docs]
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    print(f"Retrieved {len(scored)} documents matching the query metadata.")
    print(scored)
    print(scored[0])  # Print top 5 scored documents for debugging
    # Return top documents
    return [doc for doc, _ in scored]


def generate_answer(query: str, docs: list[Document]) -> str:
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = ChatPromptTemplate.from_template("""
    Given the following financial records and a user query, answer concisely.

    Context:
    "{context}"

    Query:
    "{query}"

    Answer:
    """)
    llm = AzureChatOpenAI(
    model="gpt-4o",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)
    chain = LLMChain(prompt=prompt, llm=llm)
    return chain.run({"context": context, "query": query})


def handle_user_query(query: str) -> str:
    extracted_meta = extract_metadata_from_query(query)
    print(extracted_meta)
    docs = retrieve_docs( extracted_meta) 
    print(len(docs))
    print(docs) # You should implement this using filter + fuzzy + boosting
    return generate_answer(query, docs)

def debug_query(query: str):
    meta = extract_metadata_from_query(query)
    docs = retrieve_docs(meta)
    for doc in docs:
        print("-" * 80)
        print(doc.page_content)
        print("Metadata:", doc.metadata)
    print("\nAnswer:")
    print(generate_answer(query, docs))


