from transformers import pipeline, T5Tokenizer
import re
import os


class Polarity:
    def __init__(self, model_name: str = "flan_seq2seq_model", device: str = 'cpu'):
        """
            Init Polarity class

            Args:
                model_name (str): name of the model to use for text generation.
                device (str): device between 'cuda' and 'cpu'
        """
        self.model = pipeline("text2text-generation", model='..' + os.sep + 'models' + os.sep + model_name, max_new_tokens=1, device=device)
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
                          "candidates": ["Obama", "McCain"]},
                         {"date": 2004,
                          "candidates": ["Bush", "Kerry"]},
                         {"date": 2000,
                          "candidates": ["Bush", "Gore"]},
                         {"date": 1996,
                          "candidates": ["Clinton", "Dole"]},
                         {"date": 1992,
                          "candidates": ["Clinton", "Bush"]},
                         {"date": 1988,
                          "candidates": ["Bush", "Dukakis"]},
                         {"date": 1984,
                          "candidates": ["Reagan", "Mondale"]},
                         {"date": 1980,
                          "candidates": ["Reagan", "Carter"]},
                         {"date": 1976,
                          "candidates": ["Carter", "Ford"]},
                         {"date": 1972,
                          "candidates": ["Nixon", "McGovern"]},
                         {"date": 1968,
                          "candidates": ["Nixon", "Humphrey"]},
                         {"date": 1964,
                          "candidates": ["Johnson", "Goldwater"]},
                         {"date": 1960,
                          "candidates": ["Kennedy", "Nixon"]},
                         {"date": 1956,
                          "candidates": ["Eisenhower", "Stevenson"]},
                         {"date": 1952,
                          "candidates": ["Eisenhower", "Stevenson"]},
                         {"date": 1948,
                          "candidates": ["Truman", "Dewey"]},
                         {"date": 1944,
                          "candidates": ["Roosevelt", "Dewey"]},
                         {"date": 1940,
                          "candidates": ["Roosevelt", "Willkie"]},
                         {"date": 1936,
                          "candidates": ["Roosevelt", "Landon"]},
                         {"date": 1932,
                          "candidates": ["Roosevelt", "Hoover"]},
                         {"date": 1928,
                          "candidates": ["Smith", "Hoover"]},
                         {"date": 1924,
                          "candidates": ["Coolidge", "Davis"]},
                         {"date": 1920,
                          "candidates": ["Harding", "Cox"]},
                         {"date": 1916,
                          "candidates": ["Wilson", "Hughes"]},
                         {"date": 1912,
                          "candidates": ["Wilson", "Roosevelt"]},
                         {"date": 1908,
                          "candidates": ["Taft", "Bryan"]},
                         {"date": 1904,
                          "candidates": ["Roosevelt", "Parker"]},
                         {"date": 1900,
                          "candidates": ["McKinley", "Bryan"]},
                         {"date": 1896,
                          "candidates": ["McKinley", "Bryan"]},
                         {"date": 1892,
                          "candidates": ["Cleveland", "Harrison"]},
                         {"date": 1888,
                          "candidates": ["Harrison", "Cleveland"]},
                         {"date": 1884,
                          "candidates": ["Cleveland", "Blaine"]},
                         {"date": 1880,
                          "candidates": ["Garfield", "Hancock"]},
                         {"date": 1876,
                          "candidates": ["Hayes", "Tilden"]},
                         {"date": 1872,
                          "candidates": ["Grant", "Greeley"]},
                         {"date": 1868,
                          "candidates": ["Grant", "Seymour"]},
                         {"date": 1864,
                          "candidates": ["Lincoln", "McClellan"]},
                         {"date": 1860,
                          "candidates": ["Lincoln", "Douglas"]},
                         {"date": 1856,
                          "candidates": ["Frémont", "Buchanan"]},
                         {"date": 1852,
                          "candidates": ["Scott", "Pierce"]}
                         ]

    def predict(self, text: str, year: str, verbose: bool = False):
        """
        Predict the  polarity of entity mentioned in the text for a given year.

        Args:
            text (str): input text
            year (int): year of election
            verbose (bool)

        Returns:
            List[Dict]: A list of dit containing the entity and polarity
        """
        text = "Is this text about /ENTITY/ is 'neutral', 'positive' or 'negative' ? text : " + text
        entities = [x['candidates'] for x in self.entities if x['date'] == int(year)][0]
        res = []

        for entity in entities:
            pred = None
            if re.search(r'(^' + entity + r'|\s+' + entity + r'(\s|[’\']s)|' + entity + '$)', text):
                formatted_text = re.sub('/ENTITY/', entity, text)
                pred = self.model(formatted_text)[0]['generated_text']
                if verbose:
                    print("Entity :", entity)
                    print("Prediction :", pred)

            res.append({'entity': entity, 'prediction': pred})
        return res


if __name__ == '__main__':
    import argparse

    # example : Biden Goes After Trump’s Felon Status at Connecticut Fund-Raiser

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="headline from NYT")
    parser.add_argument("-y", "--year", help="year in yyyy format")
    parser.add_argument("-v", "--verbose", help="verbosity", action="store_true")
    args = parser.parse_args()

    device = 'cpu'
    model = "flan_seq2seq_model"
    if args.verbose:
        print("Titre :", args.text)
    if args.verbose:
        print("\nModel :", model)
    get_polarity = Polarity(model, device)
    if args.verbose:
        print(get_polarity.predict(args.text, args.year, args.verbose))
