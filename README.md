# 🧾 Athenys - Intelligent Invoice Query System

Athenys is a smart document processing pipeline designed to extract structured financial data from raw invoices and enable natural language queries using LLMs. It allows you to ask questions like:

> “How much did Acme Corp spend on software in July 2025?”

And get accurate answers by parsing, embedding, and searching thousands of invoices using vector stores and metadata filters.

---

## 📁 Project Structure

├── invoices/ # Raw invoice text files
├── structured_output/ # Generated structured JSONs & Chroma vectorstore
├── config.py # Env & API config
├── parser.py # Extract structured data from invoice text using LLM
├── embedder.py # Embeds structured data to Chroma vectorstore
├── retriever.py # Handles metadata extraction, retrieval, fuzzy boosting, answer generation
├── streamlit_app.py # Streamlit interface for querying
├── main.py # Entry point to run parsing + embedding pipeline
├── empty_collection.py # Script to clear the Chroma vectorstore
├── utils.py # Utility functions
└── queries.txt # Sample queries

## 🚀 Setup Instructions

1. **Clone the Repository**

git clone https://github.com/your-username/athenys.git
cd athenys

python -m venv athenyx_env
source athenyx_env/bin/activate


2. **Install Dependencies**
pip install -r requirements.txt

3. **Set Environment Variables**

Create a .env file in the root directory with your Azure OpenAI credentials:

AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
OPENAI_API_VERSION=2023-05-15
OPENAI_API_TYPE=azure

4. **Add Raw Invoices**
Place your invoice text files in the invoices/ folder. As of now all invoices are text files.
We will eventually replace with a method to get the invoices from a database or cloud and will also extend capability to extract from pdfs and other input formats.

## 🧪 How to Run

1. **Convert Invoices to Embeddable Vectors**

python main.py


2. **Run the Query App**

streamlit run streamlit_app.py

Enter any natural language question based on your invoices.
Answers are retrieved using metadata + semantic boosting + LLM generation.

3. **Clear Existing Vectorstore (optional)**

Perform this step only if you want to alter the starutured data creation prompt or have made any other changes to the flow. 

python empty_collection.py

## 🗂️ Example Queries
"Show all software expenses paid by Acme Corp in 2025"
"How much did John Doe spend on hardware?"
"List logistics payments in June over ₹10,000"
"What were the education-related expenses last month?"

## 📌 Todo (Future scope)
 Add PDF → Markdown preprocessor
 Add support for image-based OCR
 Improve category classification
 Add agent-based query planner

## 📫 Contact
Made with ❤️ by Yaswanthi. For questions or collaboration, reach out at yaswanthi2001@gmail.com.

