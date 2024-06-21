import os
from predict_polarity import Polarity


def test_predict():
    text = "Biden Goes After Trump’s Felon Status at Connecticut Fund-Raiser"
    get_polarity = Polarity(model_dir=os.getcwd() + os.sep + 'ml' + os.sep + "models")
    res = get_polarity.predict(text, "2024")
    assert [{'entity': 'Biden', 'prediction': 'neutral'}, {'entity': 'Trump', 'prediction': 'negative'}] == res
