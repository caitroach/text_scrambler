import random 
import spacy 
import mistune
from nltk.corpus import wordnet 

try:
    nlp = spacy.load("en_core_web_sm") # loads pre-trained pipeline
except OSError: 
    print("model not downloaded.\n\nfix: run 'python3 -m spacy download en_core_web_sm'.")
    exit

# map spacy grammatical tags to wordnet tags for accurate dictionary lookups
def get_wordnet_pos(spacy_pos):
    mapping = { 
        "NOUN": wordnet.NOUN,
        "VERB": wordnet.VERB,
        "ADJ": wordnet.ADJ,
        "ADV": wordnet.ADV
    }
    return mapping.get(spacy_pos, None)

def scramble(text, change=0.15): # u can alter this to change it more drastically obvs 
    doc = nlp(text)
    output_words = []

    for token in doc: 
        word = token.text 
        wn_pos = get_wordnet_pos(token.pos_)

        if wn_pos and token.is_alpha and random.random() < change:
            synsets = wordnet.synsets(word, pos=wn_pos)
            synonyms = set()
            for syn in synsets: 
                for lemma in syn.lemmas():
                    lemma_name = lemma.name().replace("_", ' ')
                    if lemma_name.lower() != word.lower(): 
                        synonyms.add(lemma_name)

        if synonyms: 
            chosen = random.choice(list(synonyms))
            output_words.append(chosen.title() if token.is_title else chosen)
            continue
        output_words.append(word)

        # this is gonna be so slow LOLOLOL 

    return "".join([" " + w if not w.startswith((".", ",", "!", "?", "'", "n't")) else w for w in output_words]).strip()    

# recursively processes markdown ast modifying ONLY plain text strings
def process_md(node, change):
    if isinstance(node, dict):
        if node.get("type") == "text" and "text" in node: # only grab text that's part of a paragraph or list item
            node["text"] = scramble(node["text"], change)
    if node.get("type") not in ["block_code", "inline_code", "link"]:
        for key, value in node.items(): 
            process_md(value, change) # recursion...... auauuah,

    if isinstance(node, list):
        for item in node: 
            process_md(item, change)

def scramble_md(file_path, output_path, change=0.15):
    try:
        print(f"opening {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            md_parser = mistune.create_markdown(renderer=None)
            ast = md_parser(md_content)

            process_md(ast, change)

            md_renderer = mistune.create_markdown(renderer='ast') 

            lines = md_content.splitlines()
            scrambled_lines = []
            in_code_block = False

            for line in lines: 
                if line.strip().startswith("```"): # leave code intact hashtagyourewelcome
                    in_code_block = not in_code_block # im proud of this one idk why this always gets me 
                    # u invert it..... get it....... auuaa
                    scrambled_lines.append(line)
                    continue 
                if in_code_block or line.strip().startswith(("#","!","[")): # skip headers images etc etc 
                    scrambled_lines.append(line)
                else:
                    scrambled_lines.append(scramble(line, change))
            print("markdown file scrambled successfully.\nSaving output...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(scrambled_lines))
            print("markdown scramble saved.")


    except FileNotFoundError:
        print(f"{file_path} not found. check your file path again.")
        exit





