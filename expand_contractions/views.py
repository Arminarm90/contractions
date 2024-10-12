from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re

# Define a map for common contractions (excluding "I'd" since it has special handling)
contractions_map = {
    "he's": ["he is", "he has"],
    "she's": ["she is", "she has"],
    "it's": ["it is", "it has"],
    "you'd": ["you had", "you would"],
    "he'd": ["he had", "he would"],
    "she'd": ["she had", "she would"],
    "it'd": ["it had", "it would"],
    "we'd": ["we had", "we would"],
    "they'd": ["they had", "they would"],
    "that's": ["that is", "that has"],
    "there's": ["there is", "there has"],
    "who's": ["who is", "who has"],
    "what's": ["what is", "what has"],
    "where's": ["where is", "where has"],
    "when's": ["when is", "when has"],
    "why's": ["why is", "why has"],
    "how's": ["how is", "how has"],
}

# Dictionary of common contractions and their full forms (all lowercased)
contractions_dict = {
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "won't": "will not",
    "wouldn't": "would not",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "can't": "cannot",
    "couldn't": "could not",
    "shouldn't": "should not",
    "mustn't": "must not",
    "shan't": "shall not",
    "let's": "let us",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "o'clock": "of the clock",
    "haven't" : "have not",
}


# Adverbs that often appear before past participles but can be tricky
adverbs_before_past_participle = ["always", "never", "often", "already", "just"]


def handle_I_d(sentence):
    """
    Function to expand "I'd" into either 'I had' or 'I would' based on the following word.
    """
    words = sentence.split()  # Split sentence into words
    result = []

    for i, word in enumerate(words):
        if word.lower() == "i'd":
            if i < len(words) - 1:  # Check if there's a word after "I'd"
                next_word = words[i + 1].lower()

                # Detect if next word is likely a past participle (for "I had")
                if re.match(r"\b\w+(ed|en)\b", next_word):  # Common past participles
                    result.append("I had")
                else:
                    result.append("I would")
            else:
                # If there's no next word, default to "I would"
                result.append("I would")
        else:
            result.append(word)  # For other words, keep them the same

    return " ".join(result)


def handle_other_contractions(sentence):
    """
    Function to expand other contractions (excluding "I'd") based on a predefined map.
    """
    words = sentence.split()  # Split sentence into words
    result = []

    for i, word in enumerate(words):
        lowercase_word = word.lower()

        if lowercase_word in contractions_map:
            expansions = contractions_map[lowercase_word]

            # Handle tricky adverbs like "always", "never" that often follow "has"
            if (
                i < len(words) - 1
                and words[i + 1].lower() in adverbs_before_past_participle
            ):
                result.append(
                    expansions[1].capitalize() if word[0].isupper() else expansions[1]
                )  # Use "has"
            # For contractions like "he's", "she's", "it's", etc.
            elif lowercase_word in [
                "he's",
                "she's",
                "it's",
                "that's",
                "there's",
                "who's",
                "what's",
                "where's",
                "when's",
                "why's",
                "how's",
            ]:
                if i < len(words) - 1 and re.match(
                    r"\b\w+(ed|en)\b", words[i + 1]
                ):  # If next word is past participle
                    result.append(
                        expansions[1].capitalize()
                        if word[0].isupper()
                        else expansions[1]
                    )  # Use "has"
                else:
                    result.append(
                        expansions[0].capitalize()
                        if word[0].isupper()
                        else expansions[0]
                    )  # Use "is"
            # For contractions like "he'd", "she'd", "it'd", etc.
            else:
                if i < len(words) - 1 and re.match(
                    r"\b\w+(ed|en)\b", words[i + 1]
                ):  # If next word is past participle
                    result.append(
                        expansions[0].capitalize()
                        if word[0].isupper()
                        else expansions[0]
                    )  # Use "had"
                else:
                    result.append(
                        expansions[1].capitalize()
                        if word[0].isupper()
                        else expansions[1]
                    )  # Use "would"
        else:
            result.append(word)  # For other words, keep them the same

    return " ".join(result)


# Function to expand contractions
def expand_other_contractions(sentence):
    # Create a case-insensitive pattern for contractions
    contractions_pattern = re.compile(
        "(%s)" % "|".join(re.escape(key) for key in contractions_dict.keys()),
        flags=re.IGNORECASE,
    )

    def replace(match):
        contraction = match.group(0)
        expanded_form = contractions_dict[contraction.lower()]

        # Preserve case - match the case of the first letter in the contraction
        if contraction[0].isupper():
            expanded_form = expanded_form.capitalize()

        return expanded_form

    # Replace contractions with their expanded forms
    expanded_text = contractions_pattern.sub(replace, sentence)
    return expanded_text


def expand_contractions(sentence):
    """
    Main function that applies both "I'd" and other contraction handlers.
    """
    # First handle "I'd" separately
    sentence_with_id_expanded = handle_I_d(sentence)

    sentence_other_contractions = expand_other_contractions(sentence_with_id_expanded)

    # Then handle other contractions
    final_sentence = handle_other_contractions(sentence_other_contractions)

    return final_sentence


# API View to handle POST requests and return expanded contractions
class ExpandContractionsAPIView(APIView):
    def post(self, request):
        # Get the input sentence from the request body
        sentence = request.data.get("sentence", "")

        if not sentence:
            return Response(
                {"error": "No sentence provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Expand contractions in the sentence
        expanded_sentence = expand_contractions(sentence)

        # Return the expanded sentence
        return Response(
            {"original_sentence": sentence, "expanded_sentence": expanded_sentence},
            status=status.HTTP_200_OK,
        )
