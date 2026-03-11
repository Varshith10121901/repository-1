import nltk
nltk.download('maxent_ne_chunker_tab')
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    nltk.data.find('chunkers/maxent_ne_chunker')
    nltk.data.find('chunkers/maxent_ne_chunker_tab')
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('maxent_ne_chunker')
    nltk.download('maxent_ne_chunker_tab')
    nltk.download('words')

def process_text(text):
    # Tokenize the input text
    tokens = word_tokenize(text)
    print("\nTokens:")
    print(tokens)
    
    # Perform POS tagging
    pos_tags = pos_tag(tokens)
    print("\nPart-of-Speech Tags:")
    print(pos_tags)
    
    # Perform Named Entity Recognition
    ner_tree = ne_chunk(pos_tags)
    print("\nNamed Entities:")
    entities = []
    for subtree in ner_tree:
        if hasattr(subtree, 'label'):  # Check if it's a named entity
            entity = " ".join([leaf[0] for leaf in subtree.leaves()])
            label = subtree.label()
            entities.append((entity, label))
    if entities:
        for entity, label in entities:
            print(f"Entity: {entity}, Label: {label}")
    else:
        print("No named entities found.")

# Main function to get user input and process it
def main():
    print("Basic NLP Program using NLTK")
    print("Enter a sentence to analyze (or 'quit' to exit):")
    
    while True:
        user_input = input("> ")
        
        if user_input.lower() == 'quit':
            print("Exiting program.")
            break
        
        if not user_input.strip():
            print("Please enter a valid sentence.")
            continue
        
        # Process the input text
        process_text(user_input)

if __name__ == "__main__":
    main()



