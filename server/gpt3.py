import openai
import pandas as pd
import csv
import numpy as np
from transformers import GPT2TokenizerFast
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
OPENAI_API_KEY = "####################################"
DOC_EMBEDDINGS_MODEL, QUERY_EMBEDDINGS_MODEL = "text-embedding-ada-002"
COMPLETIONS_MODEL = "text-curie-001"
SEPARATOR = "\n* "
MAX_SECTION_LENGTH = 500
COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.0,
    "max_tokens": 300,
    "model": COMPLETIONS_MODEL,
}

openai.api_key = OPENAI_API_KEY
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
separator_len = len(tokenizer.tokenize(SEPARATOR))

def get_embedding(text: str, model: str) -> list[float]:
    result = openai.Embedding.create(
      model=model,
      input=text
    )
    return result["data"][0]["embedding"]

def get_doc_embedding(text: str) -> list[float]:
    return get_embedding(text, DOC_EMBEDDINGS_MODEL)

def get_query_embedding(query: str) -> list[float]:
    return get_embedding(query,QUERY_EMBEDDINGS_MODEL)

def compute_doc_embeddings(df: list[dict]) -> dict[tuple[str, str], list[float]]:
    return {
        (r["title"], r["heading"]): get_doc_embedding(r["content"].replace("\n", " ")) for r in df
    }

def write_embedding_to_csv(filename: str, data: dict[int,list[float]], header: list[str] = None):
    if header is None:
        header = ["Index"]
        max_val = max([len(values) for values in data.values()])
        for i in range(max_val):
            header.append(i)
    
    with open(filename+'.csv','w',encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for i in data:
            print(i)
            writer.writerow([i,*data[i]])

def load_embeddings(filename: str) -> dict[int,list[float]]:
    df = pd.read_csv(filename,header=0)
    max_val = max([int(c) for c in df.columns if c != 'Index'])
    return {
        idx : [r[str(i)] for i in range(max_val+1)] for idx, r in df.iterrows()
    }

def vector_similarity(x: list[float], y: list[float]) -> float:
    return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query: str, context: dict[int,np.array]) -> list[(float, int)]:
    query_embedding = get_query_embedding(query)

    doc_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index,doc_embedding in context.items()],reverse=True)
    return doc_similarities

def construct_prompt(question: str, context_embedding: dict, df: pd.DataFrame) -> str:
    most_relevant_doc_sections = order_document_sections_by_query_similarity(question,context_embedding)

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_doc_sections:
        doc_section = df.iloc[section_index]

        chosen_sections_len += doc_section.Tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LENGTH:
            break

        chosen_sections.append(SEPARATOR + doc_section.Content.replace("\n"," "))
        chosen_sections_indexes.append(str(section_index)) 

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))  

    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""
    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"

def answer_query_with_context(
    query: str,
    df: pd.DataFrame,
    document_embeddings: dict[int,np.array],
    show_prompt: bool = True
    ) -> str:

    prompt = construct_prompt(query,document_embeddings,df)
    if show_prompt:
        print(prompt)

    response = openai.Completion.create(prompt=prompt, **COMPLETIONS_API_PARAMS)

    return response["choices"][0]["text"].strip(' \n')

def main():

    df = pd.read_csv('FScience.csv',header=0)
    document_embeddings = load_embeddings("FScience_embed.csv")
    question = "Prerequisite of COMP 2007?"
    answer = answer_query_with_context(question,df,document_embeddings)
    print(f"\nQ: {question}\nA: {answer}")

def answer_query(query:str) -> str:
    df = pd.read_csv("test.csv", header=0)
    df.index = df["heading"]
    document_embeddings = load_embeddings("embedded.csv")
    answer = answer_query_with_context(query, df, document_embeddings)  
    print(f"\nQ: {query}\nA: {answer}")
    return answer

if __name__ == '__main__':
    main()
