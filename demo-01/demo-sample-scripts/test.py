import spacy
nlp = spacy.load("en_core_web_sm")

def extract_named_entities_test(text):
    """
    Extract named entities categorized as physical places from the text.

    NER Tag Descriptions:
    FAC:         Buildings, airports, highways, bridges, etc.
    ORG:         Companies, agencies, institutions, etc.
    GPE:         Countries, cities, states.
    LOC:         Non-GPE locations, mountain ranges, bodies of water.
    PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
    """
    doc = nlp(text)
    location_entities = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC", "FAC", "PRODUCT"}]

    return location_entities


sample = "The Golden Gate Bridge is a suspension bridge in links the U.S. city of San Francisco."
print("\n\nSample line: ", sample, "\n")
print("\n", extract_named_entities_test(sample), "\n\n")