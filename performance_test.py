import time
from textblob import TextBlob

# Mock tweets
mock_tweets = [
    "Loving the new features! 😍",
    "Customer service is terrible 😤",
    "Meh, it's okay I guess 😐",
    "This product is a game-changer! 🚀",
    "Worst experience ever! 😠",
    "Needs improvement, but not bad 🤔",
    "Absolutely brilliant! 🌟",
    "I regret buying this 😩",
    "Solid performance overall 👍",
    "Could be better, could be worse 🤷‍♀️"
]

# Measure sentiment analysis time
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "Positive 😊" if polarity > 0.2 else "Negative 😠" if polarity < -0.2 else "Neutral 😐"

# Start timer
start_time = time.time()

# Analyze all tweets
sentiments = [analyze_sentiment(tweet) for tweet in mock_tweets]

# End timer
end_time = time.time()

# Calculate metrics
total_time = end_time - start_time
per_tweet_time = total_time / len(mock_tweets)

# Print results
print(f"Total time: {total_time:.4f} seconds")
print(f"Per-tweet time: {per_tweet_time:.4f} seconds")
print(f"Sentiments: {sentiments}")