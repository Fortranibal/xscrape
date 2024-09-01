import os
import asyncio
from dotenv import load_dotenv
import pandas as pd
import openai
from twikit.guest import GuestClient

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class TwitterScraper:
    def __init__(self):
        self.client = GuestClient()

    async def activate(self):
        await self.client.activate()

    async def scrape_tweets(self, username, max_tweets=None):
        """Scrape tweets from a specific user."""
        all_tweets = []
        
        try:
            user = await self.client.get_user_by_screen_name(username)
            if not user:
                print(f"User {username} not found.")
                return all_tweets

            tweets = await self.client.get_user_tweets(user.id)
            for tweet in tweets:
                all_tweets.append(tweet)
                print(f"Scraped {len(all_tweets)} tweets so far...")
                
                if max_tweets and len(all_tweets) >= max_tweets:
                    break
                
                await asyncio.sleep(0.5)  # Add a small delay to avoid rate limiting
        except Exception as e:
            print(f"Error occurred while scraping: {e}")
        
        return all_tweets[:max_tweets] if max_tweets else all_tweets

def save_tweets_to_csv(tweets, filename):
    """Save tweets to a CSV file."""
    if not tweets:
        print("No tweets to save.")
        return False
    
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
    return True

def estimate_classification_cost(num_tweets, cost_per_1k_tokens=0.02):
    """Estimate the cost of classifying tweets using GPT-3."""
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
    
    df['engagement'] = df['retweet_count'] + df['favorite_count']
    df = df.sort_values('engagement', ascending=False)
    
    num_tweets = len(df)
    estimated_cost = estimate_classification_cost(num_tweets)
    print(f"Estimated cost to classify {num_tweets} tweets: ${estimated_cost:.2f}")
    
    proceed = input("Do you want to proceed with classification? (y/n): ").lower()
    if proceed != 'y':
        print("Classification cancelled.")
        return
    
    df['is_photoai'] = classify_tweets_batch(df['text'].tolist())
    
    df.to_csv(output_file, index=False)
    print(f"Saved sorted and classified tweets to {output_file}")

async def main():
    username = "levelsio"  # Replace with the actual username
    max_tweets = None  # Set to None to fetch all tweets
    keyword = "PhotoAI"
    raw_file = f"{username}_x.csv"
    processed_file = f"{username}_{keyword}_x.csv"

    # Delete the CSV file if it exists but is empty
    if os.path.exists(raw_file) and os.path.getsize(raw_file) == 0:
        os.remove(raw_file)
        print(f"Deleted empty file: {raw_file}")

    scraper = TwitterScraper()
    await scraper.activate()

    if not os.path.exists(raw_file):
        print(f"Scraping {username}'s X...")
        tweets = await scraper.scrape_tweets(username, max_tweets)
        if not save_tweets_to_csv(tweets, raw_file):
            print("No tweets were scraped. Exiting.")
            return
    else:
        print(f"Raw tweets file {raw_file} already exists. Skipping scraping.")

    if os.path.exists(raw_file) and os.path.getsize(raw_file) > 0:
        print("Sorting and classifying tweets...")
        sort_and_classify_tweets(raw_file, processed_file)

        df = pd.read_csv(processed_file)
        photoai_tweets = df[df['is_photoai']]
        print(f"\nTotal tweets: {len(df)}")
        print(f"PhotoAI tweets: {len(photoai_tweets)}")
        print("\nTop 5 PhotoAI tweets by engagement:")
        print(photoai_tweets.head()[['text', 'engagement', 'created_at']])
    else:
        print("No tweets data available. Please run the scraper first.")

if __name__ == "__main__":
    asyncio.run(main())
