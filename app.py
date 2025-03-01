import tweepy
from textblob import TextBlob
import plotly.express as px
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

# --- Setup & Security Check ---
try:
    # Try Streamlit Cloud secrets first
    credentials = {
        "api_key": st.secrets["TWITTER_API_KEY"],
        "api_secret": st.secrets["TWITTER_API_SECRET"],
        "bearer_token": st.secrets["TWITTER_BEARER_TOKEN"]
    }
except (KeyError, FileNotFoundError):
    # Fallback to local/Codespaces
    load_dotenv()
    credentials = {
        "api_key": os.getenv("TWITTER_API_KEY"),
        "api_secret": os.getenv("TWITTER_API_SECRET"),
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
    }

if not all(credentials.values()):
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
                bearer_token=credentials["bearer_token"],
                consumer_key=credentials["api_key"],
                consumer_secret=credentials["api_secret"],
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
                return "Positive 😊" if polarity > 0.2 else "Negative 😠" if polarity < -0.2 else "Neutral 😐"

            sentiments = [analyze_sentiment(text) for text in tweets]
            df = pd.DataFrame({"Tweet": tweets, "Sentiment": sentiments})

            # --- Visualizations ---
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(df, names="Sentiment", title="Sentiment Breakdown",
                            color="Sentiment",
                            color_discrete_map={
                                "Positive 😊": "#2E8B57",
                                "Negative 😠": "#DC143C",
                                "Neutral 😐": "#FFD700"
                            })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                avg_polarity = sum(TextBlob(text).sentiment.polarity for text in tweets)/len(tweets)
                st.metric("Average Sentiment Score", f"{avg_polarity:.2f}", 
                         delta="Positive 😊" if avg_polarity > 0 else "Negative 😠")
                st.write("**Sample Tweet:**")
                st.caption(tweets[0][:100] + "...")

            # --- Alert System ---
            negative_tweets = df[df["Sentiment"] == "Negative 😠"]
            if len(negative_tweets) > 5:
                st.error(f"🚨 Alert: {len(negative_tweets)} negative tweets detected!")
                st.snow()

        st.success("Analysis complete! ✅")

    except Exception as e:
        st.error(f"Error: {str(e)}")  # Show full error message