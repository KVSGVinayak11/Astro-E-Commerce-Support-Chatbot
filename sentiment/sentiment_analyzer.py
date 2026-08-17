from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        """
        Initializes the sentiment analysis pipeline using a pre-trained model.
        """
        print("Initializing Sentiment Analyzer...")
        # This model is specifically trained on tweets and is great for customer feedback.
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model=model_name, 
            tokenizer=model_name
        )
        print("Sentiment Analyzer initialized successfully.")

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyzes the sentiment of a given text.
        
        Args:
            text (str): The user's query.

        Returns:
            str: The detected sentiment ('positive', 'negative', 'neutral').
        """
        try:
            result = self.sentiment_pipeline(text)
            # The pipeline returns a list of dictionaries, e.g., [{'label': 'positive', 'score': 0.9...}]
            return result[0]['label']
        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            return "neutral" # Default to neutral in case of an error