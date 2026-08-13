"""
md scrambler! swaps words for synonyms while preserving meaning, leaves code alone 

usage:  python3 scramble_md.py input.md output.md 
"""

import random
import re
import sys

import spacy
from nltk.corpus import wordnet

# setup here
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    sys.exit("model not downloaded.\n\nfix: python3 -m spacy download en_core_web_sm")

try:
    wordnet.ensure_loaded()
except LookupError:
    sys.exit("wordnet not downloaded.\n\nfix: python3 -c \"import nltk; nltk.download('wordnet')\"")

POS_MAP = {
    "NOUN": wordnet.NOUN,
    "VERB": wordnet.VERB,
    "ADJ": wordnet.ADJ,
    "ADV": wordnet.ADV,
}

# things we never touch mid-line: `inline code`, link/image targets, html tags
PROTECTED = re.compile(r"(`[^`]*`|\]\([^)]*\)|<[^>]+>)")

# whole lines we never touch: headers, images, link-only lines, hr/frontmatter
SKIP_LINE = ("#", "!", "[", "---", "***", "|")


def synonyms_for(word, wn_pos):
    found = set()
    for syn in wordnet.synsets(word, pos=wn_pos):
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ")
            if name.lower() != word.lower():
                found.add(name)
    return found


def scramble_doc(doc, change): # keep original spacing
    out = [] 
    for token in doc:
        word = token.text
        wn_pos = POS_MAP.get(token.pos_)

        if wn_pos and token.is_alpha and random.random() < change:
            options = synonyms_for(word, wn_pos)
            if options:
                chosen = random.choice(sorted(options))
                if token.is_title:
                    chosen = chosen[0].upper() + chosen[1:]
                elif token.is_upper and len(word) > 1:
                    chosen = chosen.upper()
                word = chosen

        out.append(word + token.whitespace_)  
    return "".join(out)


def scramble_md(file_path, output_path, change=0.01):
    print(f"opening {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        sys.exit(f"{file_path} not found. check your file path again.")

    # pass 1: work out which chunks of which lines are scramble-able
    jobs = []        # the actual text to feed spacy
    plan = []        # per line: list of (is_job, value)
    in_code_block = False

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block  # u invert it..... get it....... auuaa
            plan.append([(False, line)])
            continue

        if in_code_block or not stripped or stripped.startswith(SKIP_LINE):
            plan.append([(False, line)])
            continue

        indent = line[: len(line) - len(stripped)]
        pieces = [(False, indent)]
        for chunk in PROTECTED.split(line):
            if not chunk:
                continue
            if PROTECTED.fullmatch(chunk):
                pieces.append((False, chunk))
            else:
                if chunk == indent and len(pieces) == 1:
                    continue
                pieces.append((True, len(jobs)))
                jobs.append(chunk.lstrip() if len(pieces) == 2 else chunk)
        plan.append(pieces)

    # pass 2: one batched spacy run instead of one call per line (way faster)
    print(f"scrambling {len(jobs)} chunks...")
    done = [scramble_doc(doc, change) for doc in nlp.pipe(jobs, batch_size=64)]

    result = "\n".join(
        "".join(done[val] if is_job else val for is_job, val in pieces)
        for pieces in plan
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result + "\n")
    print(f"saved to {output_path} :3")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python3 scramble_md.py input.md output.md [change]")
    amount = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
    scramble_md(sys.argv[1], sys.argv[2], amount)