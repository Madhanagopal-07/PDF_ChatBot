from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from secret_key import key

from langchain_community.vectorstores import FAISS


SECRET_KEY=key
vectordb_file_path = "faiss_index"

llm = ChatGroq(
    temperature=0,
    groq_api_key=SECRET_KEY,
    model_name="llama-3.1-70b-versatile",
    max_tokens=100
)

embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-large"
)



def vector_db(pdf_file):
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()
    chunks=loader.load_and_split()
    vectordb = FAISS.from_documents(documents=chunks,
                                    embedding=embeddings)

    vectordb.save_local(vectordb_file_path)



def qa_chain():
    vectordb = FAISS.load_local(vectordb_file_path,embeddings,allow_dangerous_deserialization=True)
    retriever = vectordb.as_retriever()
    prompt_template = """
                        ### INSTRUCTION:
                            Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer."
                        ### CONTEXT: {context}
                        ### QUESTION: {question}
                          
                        """
    prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
            )
    qa_chain = RetrievalQA.from_llm(
            llm, retriever=retriever, prompt=prompt
            )
    return qa_chain

'''vector_db('uploads\DS_Bootcamp_Brochure.pdf')
chain = qa_chain()
print(chain.invoke("what is nurel network")['result'])
ch='y'
while ch=='y':
    
    ques= input("Ques: ")
    chain = qa_chain()
    print(chain.invoke(ques)['result'])
    ch=input()
'''
    