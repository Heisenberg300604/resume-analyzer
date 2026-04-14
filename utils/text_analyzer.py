import streamlit as st
import spacy

# Load the small English model from spaCy.
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")

# ADD THIS LINE RIGHT HERE!
# This actually runs the function and saves the cached dictionary to the 'nlp' variable
nlp = load_spacy_model()


# =============================================================================
# SKILLS DATABASE
# This is our "knowledge base". The analyzer can ONLY detect skills listed here.
# A real-world system would load this from a database or a config file.
# =============================================================================
SKILLS_DB = [
    'python', 'java', 'sql', 'c++', 'react', 'javascript',
    'machine learning', 'aws', 'docker', 'git', 'html', 'css',
    'data analysis', 'linux', 'node.js', 'typescript', 'mongodb',
    'flask', 'django', 'kubernetes', 'tableau', 'power bi', 'excel'
]


def _clean_text(text: str) -> str:
    """
    Private helper function to clean and normalize raw text.

    Uses spaCy to tokenize the text and filters out punctuation and
    whitespace-only tokens. The result is a clean, lowercased string.

    Args:
        text: The raw input string (from PDF or text area).

    Returns:
        A lowercased, cleaned string ready for keyword matching.
    """
    # Process the text through spaCy's NLP pipeline
    doc = nlp(text.lower())

    # Keep only meaningful tokens (ignore punctuation and whitespace)
    clean_tokens = [token.text for token in doc if not token.is_punct and not token.is_space]

    # Rejoin tokens into a single string for phrase matching (e.g., "machine learning")
    return " ".join(clean_tokens)


def extract_skills(text: str) -> list:
    """
    Scans the given text and returns all skills found in SKILLS_DB.

    This is a rule-based approach: we simply check if each skill keyword
    (or phrase) appears as a substring in the cleaned text.

    Args:
        text: Raw text extracted from the resume PDF.

    Returns:
        A sorted list of unique skill strings found in the text.
        Example: ['aws', 'docker', 'git', 'python', 'sql']
    """
    # Step 1: Clean and normalize the input text
    cleaned_text = _clean_text(text)

    found_skills = []

    # Step 2: Check each skill in our database against the cleaned text
    for skill in SKILLS_DB:
        # We use 'in' for substring matching. This correctly handles
        # multi-word phrases like 'machine learning' or 'data analysis'.
        if skill in cleaned_text:
            found_skills.append(skill)

    # Return a sorted list of unique found skills
    return sorted(list(set(found_skills)))


def match_with_jd(resume_skills: list, jd_text: str) -> tuple:
    """
    Compares the resume's skills against the skills required in a Job Description.

    Args:
        resume_skills: A list of skills already extracted from the resume.
        jd_text:       The raw Job Description text pasted by the user.

    Returns:
        A tuple of (match_percentage, missing_skills):
            - match_percentage (float): A value from 0.0 to 100.0
            - missing_skills (list):    Skills in the JD but NOT in the resume
    """
    # Step 1: Extract required skills from the Job Description using the same function
    jd_skills = extract_skills(jd_text)

    # Edge case: If the JD has no recognizable skills, we can't compute a match.
    if not jd_skills:
        return 0.0, []

    # Step 2: Find skills that are in the JD but MISSING from the resume
    # We use Python's set difference for this: JD skills - Resume skills
    resume_skills_set = set(resume_skills)
    jd_skills_set = set(jd_skills)

    missing_skills = sorted(list(jd_skills_set - resume_skills_set))

    # Step 3: Calculate how many JD skills the resume has covered
    matched_skills_count = len(jd_skills_set.intersection(resume_skills_set))

    # Step 4: Calculate the match percentage
    # Formula: (Number of JD skills found in resume / Total JD skills) * 100
    match_percentage = (matched_skills_count / len(jd_skills_set)) * 100

    return round(match_percentage, 2), missing_skills