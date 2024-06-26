from fake2 import faker


def test_faker():
    # Test health check endpoint
    text = faker()
    assert text == "coucouuuuuguuuuuuuuu"



