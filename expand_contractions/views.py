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
                if re.match(r'\b\w+(ed|en)\b', next_word):  # Common past participles
                    result.append("I had")
                else:
                    result.append("I would")
            else:
                # If there's no next word, default to "I would"
                result.append("I would")
        else:
            result.append(word)  # For other words, keep them the same
    
    return ' '.join(result)

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
            if i < len(words) - 1 and words[i + 1].lower() in adverbs_before_past_participle:
                result.append(expansions[1].capitalize() if word[0].isupper() else expansions[1])  # Use "has"
            # For contractions like "he's", "she's", "it's", etc.
            elif lowercase_word in ["he's", "she's", "it's", "that's", "there's", "who's", "what's", "where's", "when's", "why's", "how's"]:
                if i < len(words) - 1 and re.match(r'\b\w+(ed|en)\b', words[i + 1]):  # If next word is past participle
                    result.append(expansions[1].capitalize() if word[0].isupper() else expansions[1])  # Use "has"
                else:
                    result.append(expansions[0].capitalize() if word[0].isupper() else expansions[0])  # Use "is"
            # For contractions like "he'd", "she'd", "it'd", etc.
            else:
                if i < len(words) - 1 and re.match(r'\b\w+(ed|en)\b', words[i + 1]):  # If next word is past participle
                    result.append(expansions[0].capitalize() if word[0].isupper() else expansions[0])  # Use "had"
                else:
                    result.append(expansions[1].capitalize() if word[0].isupper() else expansions[1])  # Use "would"
        else:
            result.append(word)  # For other words, keep them the same
    
    return ' '.join(result)

def expand_contractions(sentence):
    """
    Main function that applies both "I'd" and other contraction handlers.
    """
    # First handle "I'd" separately
    sentence_with_id_expanded = handle_I_d(sentence)
    
    # Then handle other contractions
    final_sentence = handle_other_contractions(sentence_with_id_expanded)
    
    return final_sentence

# API View to handle POST requests and return expanded contractions
class ExpandContractionsAPIView(APIView):
    def post(self, request):
        # Get the input sentence from the request body
        sentence = request.data.get('sentence', '')

        if not sentence:
            return Response({"error": "No sentence provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Expand contractions in the sentence
        expanded_sentence = expand_contractions(sentence)

        # Return the expanded sentence
        return Response({"original_sentence": sentence, "expanded_sentence": expanded_sentence}, status=status.HTTP_200_OK)
