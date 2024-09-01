# XScrape

# X (Twitter) Scraper and Classifier

This project allows you to scrape tweets from any X (formerly Twitter) user, classify them based on a specified keyword, and analyze the results.

## Features

- Scrape tweets from any X user
- Classify tweets based on any specified keyword
- Sort tweets by engagement
- Estimate classification costs before proceeding
- Save raw and processed tweets to CSV files

## Prerequisites

- Python 3.12.5 or later
- An OpenAI API key for tweet classification

## Setup

1. Ensure you have Python 3.12.5 or later installed.
2. Clone this repository.
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment:
- Windows: `.\.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Create a `.env` file in the project root and add your OpenAI API key: `OPENAI_API_KEY=your_openai_api_key_here` 

## Usage

1. Activate the virtual environment (if not already activated):
- Windows: `.\.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

2. Open `main.py` and modify the following variables in the `main()` function:
- `username`: The X username you want to scrape tweets from
- `max_tweets`: Maximum number of tweets to scrape (set to `None` for all tweets)
- `keyword`: The keyword you want to classify tweets by

3. Run the script: `python main.py`

4. The script will:
- Scrape tweets from the specified user
- Save raw tweets to a CSV file
- Estimate the cost of classification
- Ask for confirmation before proceeding with classification
- Classify tweets based on the specified keyword
- Save processed tweets to a new CSV file
- Display statistics about the classified tweets

## Output

- Raw tweets: `{username}_x.csv`
- Processed tweets: `{username}_{keyword}_x.csv`

## Notes

- Be mindful of X's rate limits and terms of service when scraping tweets.
- Classification using OpenAI's API incurs costs. The script will provide an estimate before proceeding.
- Ensure your OpenAI API key has sufficient credits for the classification task.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.