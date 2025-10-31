from aibasic.aibasic_intent import determine_intent

def test_load_csv():
    h = determine_intent("read the file customers.csv into a dataframe")
    assert h.intent == "load_csv"
    assert h.filename == "customers.csv"
    assert h.confidence >= 0.8
