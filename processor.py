from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import PyPDF2
import os

maximum_grade = 100
feedback_marker = True
document_directory = r"/Users/vgowda/Desktop/BoltGrader/streamlit/data"
graded_feedback = None
strictness_level = 0

load_dotenv()
api_key = os.getenv('api_key')
os.environ["OPENAI_API_KEY"] = api_key

def count_characters_in_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_characters = 0
        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text()
            if page_text:
                total_characters += len(page_text)
        return total_characters

class MetadataPDFLoader(PyPDFLoader):
    def load(self):
        docs = super().load()
        for doc in docs:
            pdf_reader = doc.metadata.get('pdf_reader')
            if pdf_reader:
                doc.metadata.update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', ''),
                })
        return docs

# Global variables to store the QA chain and retriever
qa_chain = None
retriever = None

def load_documents():
    global qa_chain, retriever
    loader = DirectoryLoader(document_directory, glob="**/*.pdf", loader_cls=MetadataPDFLoader)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
    splits = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": len(documents)})

    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
        
    )
    print(retriever)

def ask_question(question):
    if qa_chain is None:
        load_documents()
    result = qa_chain.invoke({"query": question})
    return result["result"]

def grade_assignments():
    question = f"""
    You are a helpful and critically grading educator. Please analyze the documents provided:
    1. Identify which document is the rubric.
    2. Identify any documents that appear to be student assignments.
    3. If there are both a rubric and at least one assignment, grade the assignment(s) based on the rubric criteria.
    4. If there's only a rubric, or only assignments, or neither, please report what you found and explain that grading cannot be completed without both a rubric and assignments.
    5. If there are multiple assignments, give separate feedback for them.
    6. The grading strictness parameter references how closely an assignment should be graded to the criteria of the rubric. 1 stands for the least strictness while 5 is the most. The current strictness level is {strictness_level}
    Provide a detailed explanation of your findings and any grading you were able to do.
    """
    answer = ask_question(question)
    return answer

def quiz_doc(text_inputs):
    question = f"{text_inputs}"
    answer = ask_question(question)
    return answer

def list_documents():
    files = os.listdir(document_directory)
    return [f for f in files if f.endswith('.pdf')]


print(strictness_level)
