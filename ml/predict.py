from transformers import pipeline
import re


class Polarity:
    def __init__(self, model_name="trainer_seq2seq", device='cpu'):
        self.model = pipeline("text2text-generation", model=model_name, max_new_tokens=1, device=device)
        # TODO : to complete
        self.entities = [{"date": 2024,
                         "candidates": ["Biden", "Trump"]},
                         {"date": 2020,
                         "candidates": ["Biden", "Trump"]},
                         {"date": 2016,
                          "candidates": ["Clinton", "Trump"]},
                         {"date": 2012,
                          "candidates": ["Obama", "Romney"]},
                         {"date": 2008,
                          "candidates": ["Obama", "McCain"]}]

    def predict(self, text, year, verbose=False):
        text = "Is this text about /ENTITY/ is 'neutral', 'positive' or 'negative' ? text : " + text
        entities = [x['candidates'] for x in self.entities if x['date'] == int(year)][0]
        res = []

        for entity in entities:
            pred = None
            if re.search(r'(^' + entity + r'|\s+' + entity + r'\s|' + entity + '$)', text):
                _input = re.sub('/ENTITY/', entity, text)
                pred = self.model(_input)[0]['generated_text']
                if verbose:
                    print("Entity :", entity)
                    print("Prediction :", pred)

            res.append({'entity': entity, 'prediction': pred})
        return res


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="headline from NYT")
    parser.add_argument("-y", "--year", help="year in yyyy format")
    parser.add_argument("-v", "--verbose", help="verbosity", action="store_true")
    args = parser.parse_args()

    device = 'cpu'
    models = ["trainer_seq2seq", "trainer_flan"]
    if args.verbose:
        print("Titre :", args.text)
    for m in models:
        if args.verbose:
            print("\nModel :", m)
        get_polarity = Polarity(m, device)
        if args.verbose:
            print(get_polarity.predict(args.text, args.year, args.verbose))
