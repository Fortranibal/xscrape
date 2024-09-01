import os
from dotenv import load_dotenv
import pandas as pd
import openai
import time
from twikit import Client

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class TwitterScraper:
    def __init__(self):
        self.client = Client()
        # Uncomment the following lines if you need to log in
        # self.client.login(
        #     auth_info_1=os.getenv('TWITTER_USERNAME'),
        #     password=os.getenv('TWITTER_PASSWORD')
        # )

    def scrape_tweets(self, username, max_tweets=None):
        """Scrape tweets from a specific user."""
        all_tweets = []
        cursor = None
        
        while True:
            try:
                tweets = self.client.get_tweets(username, count=100, cursor=cursor)
                if not tweets:
                    break
                
                all_tweets.extend(tweets)
                cursor = tweets[-1].cursor
                
                print(f"Scraped {len(all_tweets)} tweets so far...")
                
                if max_tweets and len(all_tweets) >= max_tweets:
                    break
                
                time.sleep(2)  # Add a delay to avoid rate limiting
            except Exception as e:
                print(f"Error occurred while scraping: {e}")
                break
        
        return all_tweets[:max_tweets] if max_tweets else all_tweets

def save_tweets_to_csv(tweets, filename):
    """Save tweets to a CSV file."""
    data = [{
        'id': tweet.id,
        'created_at': tweet.created_at,
        'text': tweet.text,
        'retweet_count': tweet.retweet_count,
        'favorite_count': tweet.favorite_count,
    } for tweet in tweets]
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} tweets to {filename}")
def estimate_classification_cost(num_tweets, cost_per_1k_tokens=0.02):
    """Estimate the cost of classifying tweets using GPT-3."""
    # Assume an average of 50 tokens per tweet (including prompt)
    total_tokens = num_tweets * 50
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
    return estimated_cost

def classify_tweets_batch(tweets, batch_size=100):
    """Classify a batch of tweets using GPT-3."""
    results = []
    for i in range(0, len(tweets), batch_size):
        batch = tweets[i:i+batch_size]
        prompt = "Classify each tweet as related to PhotoAI (development, LLM models, text-to-image tools, revenue) or not. Respond with only 'Yes' or 'No' for each tweet, separated by commas.\n\n"
        prompt += "\n".join([f"Tweet {j+1}: {tweet}" for j, tweet in enumerate(batch)])
        prompt += "\n\nClassifications:"
        
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=batch_size * 5,
            n=1,
            stop=None,
            temperature=0.3,
        )
        
        classifications = response.choices[0].text.strip().split(',')
        results.extend([c.strip().lower() == 'yes' for c in classifications])
    
    return results

def sort_and_classify_tweets(input_file, output_file):
    """Sort tweets by engagement and classify them."""
    df = pd.read_csv(input_file)
    
    # Sort by engagement (assuming it's the sum of retweets and favorites)
    df['engagement'] = df['retweet_count'] + df['favorite_count']
    df = df.sort_values('engagement', ascending=False)
    
    # Estimate classification cost
    num_tweets = len(df)
    estimated_cost = estimate_classification_cost(num_tweets)
    print(f"Estimated cost to classify {num_tweets} tweets: ${estimated_cost:.2f}")
    
    # Ask for confirmation before proceeding
    proceed = input("Do you want to proceed with classification? (y/n): ").lower()
    if proceed != 'y':
        print("Classification cancelled.")
        return
    
    # Classify tweets in batches
    df['is_photoai'] = classify_tweets_batch(df['text'].tolist())
    
    # Save sorted and classified tweets
    df.to_csv(output_file, index=False)
    print(f"Saved sorted and classified tweets to {output_file}")



def main():
    username = "levelsio"  # Replace with the actual username
    max_tweets = None  # Set to None to fetch all tweets
    keyword = "PhotoAI"
    raw_file = f"{username}_x.csv"
    processed_file = f"{username}_{keyword}_x.csv"

    scraper = TwitterScraper()

    # Scrape tweets
    if not os.path.exists(raw_file):
        print(f"Scraping {username}'s X...")
        tweets = scraper.scrape_tweets(username, max_tweets)
        save_tweets_to_csv(tweets, raw_file)
    else:
        print(f"Raw tweets file {raw_file} already exists. Skipping scraping.")

    # Sort and classify tweets
    print("Sorting and classifying tweets...")
    sort_and_classify_tweets(raw_file, processed_file)

    # Display some stats
    df = pd.read_csv(processed_file)
    photoai_tweets = df[df['is_photoai']]
    print(f"\nTotal tweets: {len(df)}")
    print(f"PhotoAI tweets: {len(photoai_tweets)}")
    print("\nTop 5 PhotoAI tweets by engagement:")
    print(photoai_tweets.head()[['text', 'engagement', 'created_at']])

if __name__ == "__main__":
    main()
