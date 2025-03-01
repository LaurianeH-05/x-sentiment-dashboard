import tweepy
from textblob import TextBlob
import plotly.express as px
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Setup & Security Check ---
required_keys = ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_BEARER_TOKEN"]
if not all(os.getenv(key) for key in required_keys):
    st.error("🔐 Missing API credentials - contact admin")
    st.stop()

# --- Streamlit App ---
st.title("🚀 Real-Time Brand Sentiment Tracker")
st.write("Track customer sentiment for any brand or product!")

# --- Main Input ---
search_term = st.text_input("Enter a brand, hashtag, or product:")

if search_term:
    try:
        with st.status("🔍 Scanning Twitter...", expanded=True):
            # --- Connect to Twitter API ---
            client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                wait_on_rate_limit=True
            )

            # --- Get Recent Tweets ---
            response = client.search_recent_tweets(
                query=f"{search_term} lang:en -is:retweet",
                max_results=100,
                tweet_fields=["text"]
            )
            
            if not response.data:
                st.warning(f"No tweets found for '{search_term}'")
                st.stop()
            
            tweets = [tweet.text for tweet in response.data]

            # --- Sentiment Analysis ---
            def analyze_sentiment(text):
                analysis = TextBlob(text)
                polarity = analysis.sentiment.polarity
                if polarity > 0.2: return "Positive 😊"
                if polarity < -0.2: return "Negative 😠"
                return "Neutral 😐"

            sentiments = [analyze_sentiment(text) for text in tweets]
            df = pd.DataFrame({"Tweet": tweets, "Sentiment": sentiments})

            # --- Visualizations ---
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment Distribution
                fig = px.pie(df, names="Sentiment", title="Sentiment Breakdown",
                             color="Sentiment",
                             color_discrete_map={
                                 "Positive 😊": "#2E8B57",
                                 "Negative 😠": "#DC143C",
                                 "Neutral 😐": "#FFD700"
                             })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Average Polarity
                avg_polarity = sum(TextBlob(text).sentiment.polarity for text in tweets)/len(tweets)
                st.metric("Average Sentiment Score", f"{avg_polarity:.2f}", 
                         delta="Positive 😊" if avg_polarity > 0 else "Negative 😠")
                
                # Top Tweet Preview
                st.write("**Sample Tweet:**")
                st.caption(tweets[0][:100] + "...")

            # --- Alert System ---
            negative_tweets = df[df["Sentiment"] == "Negative 😠"]
            if len(negative_tweets) > 5:  # More than 5 negative tweets
                st.error(f"🚨 Alert: {len(negative_tweets)} negative tweets detected!")
                st.snow()

        st.success("Analysis complete! ✅")

    except Exception as e:
        st.error(f"Error: {str(e)[:200]}")