import re

class DroughtPickyKeywordClassifier:
    """
    Classifier by picky regular expresion:
    - sequia OR ((lluv OR llov OR llue) AND (asez OR gadi OR ricc) ) AND NOT (gole OR debu OR unfo)
    """

    drought_regex = r"(sequia|sequía)+"
    drought_regex_not_keyword = [r"(lluv|llov|llue)+", r"(asez|gadi|ricc)+"]
    negative_regex = r"(gole|debu|unfo)+"

    def __init__(self):
        self.drought_regex = re.compile(self.drought_regex, re.IGNORECASE)
        self.drought_regex_not_keyword = [re.compile(regex, re.IGNORECASE) for regex in self.drought_regex_not_keyword]
        self.negative_regex = re.compile(self.negative_regex, re.IGNORECASE)

    def classify(self, text: str) -> bool:
        """
        Classify the text to determine if it is related to drought.
        is related to drought if .
        OR (sequia | sequía) AND NOT (gole | debu | unfo)
        OR ((lluv | llov | llue) AND (asez | gadi | ricc)) AND NOT (gole | debu | unfo)
        :param text: The text to classify.
        :return: True if the text is related to drought, False otherwise.
        :rtype: bool

        """

        if not text:
            return None
        
        # En cualquier caso, si hay negativos no se clasifica como sequía
        if self.negative_regex.search(text):
            return False

        # Si hay la palabra sequía, se clasifica como sequía
        if self.drought_regex.search(text):
            return True
        
        # Check if any of the 
        if all(regex.search(text) for regex in self.drought_regex_not_keyword):
            return True

        return False