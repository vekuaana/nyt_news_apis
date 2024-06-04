# coding:utf-8
import json
import pickle

from sentence_transformers import SentenceTransformer, util


def search_books(query, se, use_dot_score, num_top, model_name='multi-qa-MiniLM-L6-cos-v1'):
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_tensor=True)
    if use_dot_score:
        se = util.normalize_embeddings(se)
        query_embedding = util.normalize_embeddings(query_embedding)
        res = util.semantic_search(query_embedding, se, top_k=num_top, score_function=util.dot_score)
    else:
        res = util.semantic_search(query_embedding, se, top_k=num_top)
    res = res[0]

    print("Requête utilisateur : ", user_request)
    print("\n---Top des ", num_top, " livres recommandés ---")
    for r in res:
        # print(hit)
        book = data_list[r["corpus_id"]]
        print("-----------------------\ntitre : {}\nauteur : {}\nrésumé : {}\nscore: {:.2f}".format(
            book["title"], book["author"], book["abstract"], r["score"]))


# Load data from json
# TODO: import json in MongoDB collection + load from MongoDB
with open('data_books.json', encoding='utf-8') as f:
    data_list = json.load(f)

summary_list = [item['abstract'] for item in data_list]

# Load embeddings from pfl file
# TODO: import json in MongoDB collection + load from MongoDB
with open('summary_embeddings.pkl', "rb") as fIn:
    cache_data = pickle.load(fIn)
    summary_embeddings = cache_data['embeddings']

# user request
user_request = "2008 gun control"
search_books(user_request, summary_embeddings, True, 5)
