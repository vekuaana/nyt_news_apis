from fake import faker


def test_faker():
    # Test health check endpoint
    text = faker()
    assert text == "coucouuuuuguuuuuuuuu"



