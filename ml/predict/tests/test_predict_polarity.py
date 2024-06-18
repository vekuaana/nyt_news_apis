import pytest
import os
from predict_polarity import Polarity


@pytest.mark.parametrize(("text", "year"), [("Biden Goes After Trump’s Felon Status at Connecticut Fund-Raiser", "2024")])
def test_predict(text, year):
    print(os.getcwd())
    get_polarity = Polarity(model_dir=os.getcwd() + os.sep + 'ml' + os.sep + "models")
    res = get_polarity.predict(text, year)
    assert [{'entity': 'Biden', 'prediction': 'neutral'}, {'entity': 'Trump', 'prediction': 'negative'}] == res
