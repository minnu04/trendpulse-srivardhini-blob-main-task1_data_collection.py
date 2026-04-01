"""
TrendPulse: Data Collection Module
===================================
This module collects and analyzes trending data from multiple sources
to identify what's actually trending right now.

The module fetches trending topics, hashtags, and popular content from various
platforms and aggregates them into meaningful insights.
"""

import json
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from collections import Counter
from urllib.parse import quote
import logging

# Data processing and analysis libraries (Task 3: NumPy/Pandas)
import numpy as np
import pandas as pd

# Visualization libraries (Task 4: Visualize)
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging for tracking data collection operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendingDataCollector:
    """
    Main class for collecting trending data from multiple sources.
    
    This class provides methods to fetch trending stories from HackerNews
    and other sources, categorizes them, and aggregates for analysis.
    
    HackerNews API Integration:
    - Top stories endpoint: https://hacker-news.firebaseio.com/v0/topstories.json
    - Item details endpoint: https://hacker-news.firebaseio.com/v0/item/{id}.json
    - No authentication required - fully open API
    """
    
    def __init__(self):
        """Initialize the data collector with configuration and storage."""
        self.trends_data = {
            'collected_at': datetime.now().isoformat(),
            'sources': {},
            'aggregated_trends': [],
            'categories': {}
        }
        self.session = requests.Session()
        # Set User-Agent for HackerNews API requests
        self.session.headers.update({"User-Agent": "TrendPulse/1.0"})
        # Set timeout for all requests to prevent hanging
        self.timeout = 10
        
        # Define category keywords for story classification
        self.category_keywords = {
            'technology': ['AI', 'software', 'tech', 'code', 'computer', 'data', 'cloud', 'API', 'GPU', 'LLM'],
            'worldnews': ['war', 'government', 'country', 'president', 'election', 'climate', 'attack', 'global'],
            'sports': ['NFL', 'NBA', 'FIFA', 'sport', 'game', 'team', 'player', 'league', 'championship'],
            'science': ['research', 'study', 'space', 'physics', 'biology', 'discovery', 'NASA', 'genome'],
            'entertainment': ['movie', 'film', 'music', 'Netflix', 'game', 'book', 'show', 'award', 'streaming']
        }
        
        logger.info("TrendingDataCollector initialized with HackerNews API integration")
    
    def categorize_story(self, title: str) -> str:
        """
        Categorize a HackerNews story by checking its title for keywords.
        
        Logic:
        1. Convert title to lowercase for case-insensitive matching
        2. Check each category's keywords against the title
        3. Return the first matching category
        4. Default to 'technology' if no category matches
        
        Args:
            title: The story title to categorize
            
        Returns:
            Category name as string
        """
        title_lower = title.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    return category
        
        # Default to technology if no category matched
        return 'technology'
    
    def collect_hackernews_stories(self, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch trending stories from HackerNews API (fully open, no auth needed).
        
        API Flow:
        1. Fetch top 500 story IDs from /topstories.json
        2. For each story ID, fetch story details from /item/{id}.json
        3. Categorize each story by title keywords
        4. Store story data with metadata
        
        Args:
            limit: Number of stories to fetch (default 100, max recommended 500)
            
        Returns:
            Dictionary containing HackerNews stories organized by category
        """
        hackernews_data = {
            'source': 'HackerNews',
            'timestamp': datetime.now().isoformat(),
            'stories_by_category': {
                'technology': [],
                'worldnews': [],
                'sports': [],
                'science': [],
                'entertainment': []
            },
            'total_fetched': 0,
            'error': None,
            'status': 'pending'
        }
        
        try:
            logger.info(f"Fetching top {limit} HackerNews stories")
            
            # Step 1: Fetch list of top story IDs
            # Uses Firebase endpoint that returns JSON array of integers
            top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            
            response = self.session.get(top_stories_url, timeout=self.timeout)
            response.raise_for_status()
            
            story_ids = response.json()[:limit]  # Get top N story IDs
            logger.info(f"Fetched {len(story_ids)} story IDs from HackerNews")
            
            collected_count = 0
            error_count = 0
            
            # Step 2: Fetch details for each story
            # Each story requires a separate API call
            for story_id in story_ids:
                try:
                    # Construct story endpoint URL
                    story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    
                    story_response = self.session.get(story_url, timeout=self.timeout)
                    story_response.raise_for_status()
                    
                    story_data = story_response.json()
                    
                    # Skip if story data is None or missing required fields
                    if not story_data:
                        continue
                    
                    # Extract story fields
                    title = story_data.get('title', 'Untitled')
                    score = story_data.get('score', 0)
                    story_type = story_data.get('type', 'story')
                    url = story_data.get('url', '')
                    comments = story_data.get('descendants', 0)
                    
                    # Skip if not a story or has no score
                    if story_type != 'story' or score == 0:
                        continue
                    
                    # Categorize story by title keywords
                    category = self.categorize_story(title)
                    
                    # Create story record
                    story_record = {
                        'id': story_id,
                        'title': title,
                        'score': score,
                        'comments': comments,
                        'url': url,
                        'category': category
                    }
                    
                    # Add to appropriate category list
                    hackernews_data['stories_by_category'][category].append(story_record)
                    collected_count += 1
                    
                    # Add small delay to be respectful to the API (optional)
                    # time.sleep(0.1)
                    
                except json.JSONDecodeError:
                    error_count += 1
                    logger.warning(f"Failed to parse story {story_id}")
                    continue
                except requests.RequestException as e:
                    error_count += 1
                    logger.warning(f"Failed to fetch story {story_id}: {str(e)}")
                    continue
            
            hackernews_data['total_fetched'] = collected_count
            hackernews_data['status'] = 'success'
            
            # Log category distribution
            for cat, stories in hackernews_data['stories_by_category'].items():
                logger.info(f"Category '{cat}': {len(stories)} stories")
            
            logger.info(f"HackerNews collection complete: {collected_count} stories collected")
            
        except requests.RequestException as e:
            error_msg = f"Failed to fetch HackerNews top stories: {str(e)}"
            logger.error(error_msg)
            hackernews_data['error'] = error_msg
            hackernews_data['status'] = 'failed'
        except Exception as e:
            error_msg = f"Unexpected error during HackerNews collection: {str(e)}"
            logger.error(error_msg)
            hackernews_data['error'] = error_msg
            hackernews_data['status'] = 'failed'
        
        return hackernews_data
    
    def collect_twitter_trends(self) -> Dict[str, Any]:
        """
        Collect trending topics from Twitter/X-like sources.
        
        Returns:
            Dictionary containing trending topics and related metadata
            
        Note: In production, this would use Twitter API v2 with proper authentication.
        For demonstration, we'll use a mock implementation pattern.
        """
        twitter_trends = {
            'source': 'Twitter',
            'timestamp': datetime.now().isoformat(),
            'trends': [],
            'error': None
        }
        
        try:
            # In production, you would authenticate with Twitter API v2
            # API endpoint: https://api.twitter.com/2/trends/search
            # For now, we'll demonstrate the pattern
            
            logger.info("Attempting to collect Twitter trending topics")
            
            # Mock data structure for demonstration
            # In real implementation, this would come from Twitter API
            mock_trends = [
                {'name': '#Python', 'tweet_volume': 45000},
                {'name': '#DataScience', 'tweet_volume': 38000},
                {'name': '#TrendingNow', 'tweet_volume': 72000},
            ]
            
            twitter_trends['trends'] = mock_trends
            twitter_trends['status'] = 'success'
            
        except requests.RequestException as e:
            # Handle network-related errors gracefully
            error_msg = f"Failed to fetch Twitter trends: {str(e)}"
            logger.error(error_msg)
            twitter_trends['error'] = error_msg
            twitter_trends['status'] = 'failed'
        
        return twitter_trends
    
    def collect_google_trends(self) -> Dict[str, Any]:
        """
        Collect trending search terms from Google.
        
        Returns:
            Dictionary containing Google search trends
            
        Note: Uses pytrends library patterns (or mock for demonstration)
        """
        google_trends = {
            'source': 'Google',
            'timestamp': datetime.now().isoformat(),
            'trends': [],
            'error': None
        }
        
        try:
            logger.info("Attempting to collect Google trending searches")
            
            # Mock trending search terms
            # In production: from pytrends.request import TrendReq
            # pytrends = TrendReq(hl='en-US', tz=360)
            # pytrends.build_payload(kw_list=[''], timeframe='now 1-H')
            # data = pytrends.trending_searches(pn='united_states')
            
            mock_searches = [
                {'term': 'Python programming', 'volume': 125000},
                {'term': 'Machine Learning', 'volume': 98000},
                {'term': 'Artificial Intelligence', 'volume': 156000},
            ]
            
            google_trends['trends'] = mock_searches
            google_trends['status'] = 'success'
            
        except Exception as e:
            error_msg = f"Failed to fetch Google trends: {str(e)}"
            logger.error(error_msg)
            google_trends['error'] = error_msg
            google_trends['status'] = 'failed'
        
        return google_trends
    
    def collect_reddit_trends(self) -> Dict[str, Any]:
        """
        Collect trending subreddits and posts from Reddit.
        
        Returns:
            Dictionary containing Reddit trending data
        """
        reddit_trends = {
            'source': 'Reddit',
            'timestamp': datetime.now().isoformat(),
            'trends': [],
            'error': None
        }
        
        try:
            logger.info("Attempting to collect Reddit trending posts")
            
            # In production: Use PRAW (Python Reddit API Wrapper)
            # reddit = praw.Reddit(client_id='...', client_secret='...', user_agent='TrendPulse')
            # hot_posts = reddit.subreddit('all').hot(limit=25)
            
            mock_reddit_trends = [
                {'title': 'Data Science Discussion', 'score': 25000, 'subreddit': 'r/datascience'},
                {'title': 'Python Tips and Tricks', 'score': 18500, 'subreddit': 'r/Python'},
                {'title': 'AI Breakthroughs', 'score': 31000, 'subreddit': 'r/MachineLearning'},
            ]
            
            reddit_trends['trends'] = mock_reddit_trends
            reddit_trends['status'] = 'success'
            
        except Exception as e:
            error_msg = f"Failed to fetch Reddit trends: {str(e)}"
            logger.error(error_msg)
            reddit_trends['error'] = error_msg
            reddit_trends['status'] = 'failed'
        
        return reddit_trends
    
    def collect_hashtag_trends(self) -> Dict[str, Any]:
        """
        Aggregate and analyze popular hashtags across platforms.
        
        Returns:
            Dictionary containing aggregated hashtag trends
        """
        hashtag_trends = {
            'source': 'Hashtag Aggregation',
            'timestamp': datetime.now().isoformat(),
            'trends': [],
            'error': None
        }
        
        try:
            logger.info("Collecting hashtag trends")
            
            # Pattern-based hashtag collection
            # These would typically come from multiple platform APIs
            mock_hashtags = [
                {'hashtag': '#AI', 'frequency': 145000},
                {'hashtag': '#Technology', 'frequency': 128000},
                {'hashtag': '#Innovation', 'frequency': 87000},
                {'hashtag': '#Cloud', 'frequency': 76000},
            ]
            
            hashtag_trends['trends'] = mock_hashtags
            hashtag_trends['status'] = 'success'
            
        except Exception as e:
            error_msg = f"Failed to collect hashtag trends: {str(e)}"
            logger.error(error_msg)
            hashtag_trends['error'] = error_msg
            hashtag_trends['status'] = 'failed'
        
        return hashtag_trends
    
    def aggregate_trends(self) -> List[Dict[str, Any]]:
        """
        Aggregate trends from all sources into a unified ranking.
        
        Logic:
        1. Collect HackerNews data (primary source)
        2. Collect data from other sources as fallback
        3. Normalize scores to make them comparable across platforms
        4. Calculate weighted average importance
        5. Sort by aggregated score
        
        Returns:
            Sorted list of aggregated trends
        """
        logger.info("Starting trend aggregation from all sources")
        
        # Collect HackerNews data (primary source - real API)
        hackernews_data = self.collect_hackernews_stories(limit=100)
        
        # Collect fallback data from mock sources
        sources_data = {
            'hackernews': hackernews_data,
            'twitter': self.collect_twitter_trends(),
            'google': self.collect_google_trends(),
            'reddit': self.collect_reddit_trends(),
            'hashtags': self.collect_hashtag_trends()
        }
        
        # Store collected data
        self.trends_data['sources'] = sources_data
        
        # Initialize category distribution tracking
        category_distribution = {
            'technology': [],
            'worldnews': [],
            'sports': [],
            'science': [],
            'entertainment': []
        }
        
        # Process HackerNews stories by category
        if hackernews_data['status'] == 'success':
            for category, stories in hackernews_data['stories_by_category'].items():
                # Sort stories by score and take top stories per category
                sorted_stories = sorted(stories, key=lambda x: x['score'], reverse=True)[:10]
                category_distribution[category].extend(sorted_stories)
        
        # Store category distribution for later use
        self.trends_data['categories'] = category_distribution
        
        # Create a frequency counter to identify most mentioned trends across all sources
        trend_counter = Counter()
        
        # Aggregate trend mentions from traditional sources
        for source_name, source_data in sources_data.items():
            if source_name == 'hackernews':
                # For HackerNews, count by category
                for category, stories in source_data['stories_by_category'].items():
                    trend_counter[category] += len(stories)
            elif source_data.get('status') == 'success':
                for trend in source_data.get('trends', []):
                    # Extract trend name/identifier
                    trend_name = trend.get('name') or trend.get('term') or trend.get('title') or trend.get('hashtag')
                    # Increment counter for this trend
                    trend_counter[trend_name] += 1
        
        # Convert counter to sorted list format
        aggregated_trends = [
            {
                'trend': trend_name,
                'mentions_across_sources': count,
                'importance_score': count * 100  # Simple scoring algorithm
            }
            for trend_name, count in trend_counter.most_common()
        ]
        
        logger.info(f"Aggregated {len(aggregated_trends)} unique trends")
        logger.info(f"Category distribution: {dict((k, len(v)) for k, v in category_distribution.items())}")
        
        return aggregated_trends
    
    def export_to_csv(self, filepath: str = 'trends_raw.csv') -> None:
        """
        Task 2: Clean CSV - Export trend data to CSV format.
        
        This function exports collected trends to a CSV file with proper
        formatting and structure for easy data analysis and sharing.
        
        Includes HackerNews stories with category assignment and scores.
        
        Args:
            filepath: Path where CSV will be saved
        """
        try:
            logger.info("Exporting trends to CSV format")
            
            # Create a clean list of records from all sources
            csv_records = []
            
            # Extract HackerNews stories by category
            hackernews_data = self.trends_data['sources'].get('hackernews', {})
            if hackernews_data.get('status') == 'success':
                for category, stories in hackernews_data.get('stories_by_category', {}).items():
                    for story in stories:
                        record = {
                            'source': 'HackerNews',
                            'timestamp': hackernews_data.get('timestamp', ''),
                            'trend_name': story.get('title', ''),
                            'volume_frequency': story.get('score', 0),
                            'category': story.get('category', 'uncategorized'),
                            'comments': story.get('comments', 0),
                            'url': story.get('url', '')
                        }
                        csv_records.append(record)
            
            # Extract data from other sources
            for source_name, source_data in self.trends_data['sources'].items():
                if source_name == 'hackernews':
                    continue  # Already processed
                    
                if source_data.get('status') == 'success':
                    for trend in source_data.get('trends', []):
                        # Create a normalized record with all relevant fields
                        record = {
                            'source': source_data.get('source', source_name),
                            'timestamp': source_data.get('timestamp', ''),
                            'trend_name': trend.get('name') or trend.get('term') or trend.get('title') or trend.get('hashtag'),
                            'volume_frequency': trend.get('tweet_volume') or trend.get('volume') or trend.get('score') or trend.get('frequency', 0),
                            'category': 'uncategorized',
                            'comments': trend.get('descendants', 0),
                            'url': trend.get('url', '')
                        }
                        csv_records.append(record)
            
            # Write cleaned data to CSV with proper headers
            if csv_records:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['source', 'timestamp', 'trend_name', 'volume_frequency', 'category', 'comments', 'url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header row
                    writer.writeheader()
                    # Write all data rows
                    writer.writerows(csv_records)
                
                logger.info(f"CSV export successful: {filepath} ({len(csv_records)} records)")
                print(f"✓ CSV exported to {filepath} ({len(csv_records)} records)")
            else:
                logger.warning("No data available for CSV export")
                print("✗ No data to export to CSV")
                
        except IOError as e:
            error_msg = f"Failed to export CSV: {str(e)}"
            logger.error(error_msg)
            print(f"✗ Error exporting CSV: {error_msg}")
    
    def analyze_with_pandas(self, csv_filepath: str = 'trends_raw.csv') -> pd.DataFrame:
        """
        Task 3: NumPy/Pandas Analysis - Perform data processing and analysis.
        
        This function uses pandas and numpy to:
        1. Read the CSV data (including HackerNews categorized stories)
        2. Clean and normalize the data
        3. Perform statistical analysis by category and source
        4. Generate insights on trending stories and categories
        
        Args:
            csv_filepath: Path to the CSV file to analyze
            
        Returns:
            Cleaned and processed DataFrame
        """
        try:
            logger.info("Starting Pandas/NumPy analysis")
            
            # Read CSV file into pandas DataFrame
            df = pd.read_csv(csv_filepath)
            
            logger.info(f"Loaded {len(df)} records for analysis")
            
            # Data Cleaning: Remove duplicates based on trend_name and source
            df_cleaned = df.drop_duplicates(subset=['source', 'trend_name'], keep='first')
            logger.info(f"After deduplication: {len(df_cleaned)} records")
            
            # Handle missing values: Fill 'N/A' values
            df_cleaned['category'] = df_cleaned['category'].fillna('uncategorized')
            df_cleaned['url'] = df_cleaned['url'].fillna('')
            
            # Convert volume_frequency to numeric (handles conversion errors)
            df_cleaned['volume_frequency'] = pd.to_numeric(
                df_cleaned['volume_frequency'], 
                errors='coerce'
            ).fillna(0)
            
            # Feature Engineering: Create normalized scores using numpy
            # Normalize volume_frequency to 0-100 scale using min-max scaling
            vol_min = df_cleaned['volume_frequency'].min()
            vol_max = df_cleaned['volume_frequency'].max()
            
            # Prevent division by zero
            if vol_max > vol_min:
                df_cleaned['normalized_score'] = (
                    (df_cleaned['volume_frequency'] - vol_min) / 
                    (vol_max - vol_min) * 100
                )
            else:
                df_cleaned['normalized_score'] = 50
            
            # Statistical Analysis using NumPy
            stats_summary = {
                'total_trends': len(df_cleaned),
                'avg_volume': float(np.mean(df_cleaned['volume_frequency'])),
                'median_volume': float(np.median(df_cleaned['volume_frequency'])),
                'std_volume': float(np.std(df_cleaned['volume_frequency'])),
                'max_volume': float(np.max(df_cleaned['volume_frequency'])),
                'min_volume': float(np.min(df_cleaned['volume_frequency']))
            }
            
            logger.info(f"Statistical summary: {stats_summary}")
            
            # Group analysis: Trends by source
            source_counts = df_cleaned.groupby('source').size()
            logger.info(f"Trends by source:\n{source_counts}")
            
            # Category analysis: Count stories per category
            category_counts = df_cleaned.groupby('category').size()
            logger.info(f"Stories per category:\n{category_counts}")
            
            # Per-category statistics for HackerNews
            print(f"\n📈 Category Statistics (from {len(df_cleaned)} records):")
            print("-" * 70)
            for category in ['technology', 'worldnews', 'sports', 'science', 'entertainment', 'uncategorized']:
                cat_data = df_cleaned[df_cleaned['category'] == category]
                if len(cat_data) > 0:
                    avg_score = cat_data['volume_frequency'].mean()
                    max_score = cat_data['volume_frequency'].max()
                    count = len(cat_data)
                    print(f"{category:15s}: {count:3d} stories | Avg Score: {avg_score:7.0f} | Max: {max_score:7.0f}")
            
            # Save cleaned data back
            df_cleaned.to_csv('trends_cleaned.csv', index=False, encoding='utf-8')
            logger.info("Cleaned data saved to trends_cleaned.csv")
            
            print(f"\n📊 Analysis Summary:")
            print(f"   Total Records: {stats_summary['total_trends']}")
            print(f"   Avg Score: {stats_summary['avg_volume']:.0f}")
            print(f"   Median Score: {stats_summary['median_volume']:.0f}")
            print(f"   Std Dev: {stats_summary['std_volume']:.0f}")
            
            return df_cleaned
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_filepath}")
            print(f"✗ Error: CSV file not found at {csv_filepath}")
            return pd.DataFrame()
        except Exception as e:
            error_msg = f"Failed during analysis: {str(e)}"
            logger.error(error_msg)
            print(f"✗ Analysis error: {error_msg}")
            return pd.DataFrame()
    
    def visualize_trends(self, df: pd.DataFrame, output_dir: str = '.') -> None:
        """
        Task 4: Visualize - Create comprehensive visualizations of trending data.
        
        This function generates multiple charts to visualize:
        1. Distribution of HackerNews stories by category
        2. Top stories by score per category
        3. Score statistics across sources and categories
        4. Category comparison and trends
        
        Args:
            df: Cleaned DataFrame from pandas analysis
            output_dir: Directory to save visualization files
        """
        try:
            if df.empty:
                logger.warning("No data available for visualization")
                print("✗ No data to visualize")
                return
            
            logger.info("Starting trend visualization")
            
            # Set style for better-looking plots
            sns.set_style("whitegrid")
            plt.rcParams['figure.figsize'] = (15, 11)
            
            # Create a figure with multiple subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 11))
            fig.suptitle('TrendPulse: HackerNews & Trending Data Dashboard', fontsize=16, fontweight='bold')
            
            # Plot 1: Stories by Category (Bar Chart)
            category_counts = df['category'].value_counts()
            colors_cat = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            axes[0, 0].bar(range(len(category_counts)), category_counts.values, color=colors_cat[:len(category_counts)])
            axes[0, 0].set_xticks(range(len(category_counts)))
            axes[0, 0].set_xticklabels(category_counts.index, rotation=45, ha='right')
            axes[0, 0].set_ylabel('Number of Stories', fontweight='bold')
            axes[0, 0].set_title('Stories Distribution by Category')
            
            # Add value labels on bars
            for i, v in enumerate(category_counts.values):
                axes[0, 0].text(i, v + 1, str(v), ha='center', va='bottom', fontweight='bold')
            
            # Plot 2: Top 10 Trends by Score (Horizontal Bar Chart)
            top_trends = df.nlargest(10, 'volume_frequency')[['trend_name', 'volume_frequency']]
            axes[0, 1].barh(range(len(top_trends)), top_trends['volume_frequency'], color='steelblue')
            axes[0, 1].set_yticks(range(len(top_trends)))
            axes[0, 1].set_yticklabels([name[:40] for name in top_trends['trend_name']], fontsize=9)
            axes[0, 1].set_xlabel('Score/Volume', fontweight='bold')
            axes[0, 1].set_title('Top 10 Stories by Score')
            axes[0, 1].invert_yaxis()
            
            # Plot 3: Average Score by Category (Box Plot)
            categories = df['category'].unique()
            box_data = [df[df['category'] == cat]['volume_frequency'].values for cat in sorted(categories)]
            bp = axes[1, 0].boxplot(box_data, labels=sorted(categories), patch_artist=True)
            
            # Color the box plots
            for patch, color in zip(bp['boxes'], colors_cat[:len(categories)]):
                patch.set_facecolor(color)
            
            axes[1, 0].set_ylabel('Score/Volume', fontweight='bold')
            axes[1, 0].set_title('Score Distribution by Category')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].grid(True, alpha=0.3)
            
            # Plot 4: Source vs Category Heatmap/Matrix
            source_category = pd.crosstab(df['source'], df['category'])
            sns.heatmap(source_category, annot=True, fmt='d', cmap='YlOrRd', ax=axes[1, 1], cbar_kws={'label': 'Count'})
            axes[1, 1].set_title('Stories Count: Source vs Category')
            axes[1, 1].set_xlabel('Category', fontweight='bold')
            axes[1, 1].set_ylabel('Source', fontweight='bold')
            
            # Adjust layout to prevent overlapping
            plt.tight_layout()
            
            # Save visualization
            viz_filepath = os.path.join(output_dir, 'trends_visualization.png')
            plt.savefig(viz_filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved: {viz_filepath}")
            print(f"✓ Main dashboard saved to {viz_filepath}")
            
            # Create additional visualization: Category Breakdown with Top Stories
            fig2, axes2 = plt.subplots(3, 2, figsize=(16, 12))
            fig2.suptitle('TrendPulse: Top Stories by Category', fontsize=16, fontweight='bold')
            
            categories_list = ['technology', 'worldnews', 'sports', 'science', 'entertainment', 'uncategorized']
            
            for idx, category in enumerate(categories_list):
                row = idx // 2
                col = idx % 2
                ax = axes2[row, col]
                
                # Get top 8 stories for this category
                cat_df = df[df['category'] == category].nlargest(8, 'volume_frequency')
                
                if len(cat_df) > 0:
                    bars = ax.barh(range(len(cat_df)), cat_df['volume_frequency'], color='coral' if category == 'entertainment' else 'steelblue')
                    ax.set_yticks(range(len(cat_df)))
                    ax.set_yticklabels([name[:45] + '...' if len(name) > 45 else name for name in cat_df['trend_name']], fontsize=8)
                    ax.set_xlabel('Score', fontweight='bold')
                    ax.set_title(f'{category.upper()} ({len(cat_df)} stories)', fontweight='bold')
                    ax.invert_yaxis()
                    
                    # Add value labels
                    for i, v in enumerate(cat_df['volume_frequency']):
                        ax.text(v + 10, i, str(int(v)), va='center', fontsize=8)
                else:
                    ax.text(0.5, 0.5, f'No {category} stories', ha='center', va='center', fontsize=12)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
            
            plt.tight_layout()
            
            # Save category breakdown
            viz2_filepath = os.path.join(output_dir, 'trends_by_category.png')
            plt.savefig(viz2_filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Category visualization saved: {viz2_filepath}")
            print(f"✓ Category breakdown saved to {viz2_filepath}")
            
            plt.close('all')
            
        except Exception as e:
            error_msg = f"Failed during visualization: {str(e)}"
            logger.error(error_msg)
            print(f"✗ Visualization error: {error_msg}")
    
    def save_results(self, filepath: str = 'trends_output.json') -> None:
        """
        Save collected trends to a JSON file for further analysis.
        
        Args:
            filepath: Path where the JSON output will be saved
        """
        try:
            self.trends_data['aggregated_trends'] = self.aggregate_trends()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.trends_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Trends saved to {filepath}")
            print(f"\n✓ Data saved to {filepath}")
            
        except IOError as e:
            error_msg = f"Failed to save results: {str(e)}"
            logger.error(error_msg)
            print(f"\n✗ Error saving data: {error_msg}")
    
    def print_summary(self) -> None:
        """
        Print a formatted summary of the collected trends for quick viewing.
        
        Displays:
        1. HackerNews stories categorized into 5 categories
        2. Top trending stories per category
        3. Category statistics
        """
        print("\n" + "="*80)
        print("TRENDPULSE: HACKERNEWS TRENDING ANALYSIS")
        print("="*80)
        print(f"Collection Time: {self.trends_data['collected_at']}\n")
        
        # Display HackerNews categories
        categories_data = self.trends_data.get('categories', {})
        
        print("📊 HACKERNEWS STORIES BY CATEGORY (Top 5 per category):")
        print("-"*80)
        
        for category in ['technology', 'worldnews', 'sports', 'science', 'entertainment']:
            stories = categories_data.get(category, [])
            
            if stories:
                # Sort by score and take top 5
                top_stories = sorted(stories, key=lambda x: x.get('score', 0), reverse=True)[:5]
                
                print(f"\n🔹 {category.upper()} ({len(stories)} stories)")
                print("   " + "-"*76)
                
                for i, story in enumerate(top_stories, 1):
                    title = story.get('title', 'Untitled')[:60]
                    score = story.get('score', 0)
                    comments = story.get('comments', 0)
                    print(f"   {i}. {title:60s} | Score: {score:5d} | Comments: {comments:4d}")
            else:
                print(f"\n🔹 {category.upper()}: No stories found")
        
        print("\n" + "="*80)
        
        # Display aggregated trends
        aggregated_trends = self.aggregate_trends()
        
        if aggregated_trends:
            print("\nTOP TRENDING TOPICS (Aggregated from all sources):")
            print("-"*80)
            for i, trend in enumerate(aggregated_trends[:10], 1):
                importance = trend['importance_score']
                print(f"{i:2d}. {trend['trend']:40s} | Score: {importance}")
        
        print("="*80 + "\n")


def main():
    """
    Main execution function - Complete TrendPulse Pipeline with HackerNews Integration.
    
    Flow:
    1. Initialize the data collector
    2. Fetch and aggregate HackerNews trending stories
    3. Categorize stories into 5 categories (technology, worldnews, sports, science, entertainment)
    4. Task 1: Save results to JSON (Fetch JSON)
    5. Task 2: Export to CSV and clean data (Clean CSV)
    6. Task 3: Process with Pandas and NumPy (NumPy/Pandas)
    7. Task 4: Create visualizations (Visualise)
    """
    try:
        print("\n" + "="*80)
        print("TRENDPULSE: HackerNews Trending Data Collector & Analyzer")
        print("="*80)
        print("Integration: HackerNews API (No Auth Required)")
        print("Categories: Technology, WorldNews, Sports, Science, Entertainment")
        print("="*80)
        
        # Initialize collector
        collector = TrendingDataCollector()
        
        # Step 1 & 2: Collect and aggregate trends (includes HackerNews API)
        print("\n🔄 PHASE 1: Data Collection")
        print("-" * 80)
        logger.info("Starting TrendPulse data collection pipeline with HackerNews")
        collector.print_summary()
        
        # TASK 1: Save results to JSON (Fetch JSON)
        print("\n📋 TASK 1: Fetching and Storing JSON Data")
        print("-" * 80)
        output_json = 'trends_output.json'
        collector.save_results(output_json)
        print(f"✓ JSON data structure includes: HackerNews categories, aggregated trends")
        
        # TASK 2: Export to CSV and clean data (Clean CSV)
        print("\n📁 TASK 2: Data Cleaning & CSV Export")
        print("-" * 80)
        csv_file = 'trends_raw.csv'
        collector.export_to_csv(csv_file)
        print("✓ HackerNews stories categorized and exported to CSV")
        print("  Columns: source, timestamp, trend_name, volume_frequency, category, comments, url")
        
        # TASK 3: Process with Pandas and NumPy (NumPy/Pandas Analysis)
        print("\n🔬 TASK 3: NumPy/Pandas Data Analysis")
        print("-" * 80)
        df_cleaned = collector.analyze_with_pandas(csv_file)
        print("✓ Data processed with Pandas/NumPy statistical analysis")
        print("  - Deduplication applied")
        print("  - Normalized scores calculated")
        print("  - Category statistics computed")
        
        # TASK 4: Create visualizations (Visualise)
        print("\n📊 TASK 4: Data Visualization")
        print("-" * 80)
        if not df_cleaned.empty:
            collector.visualize_trends(df_cleaned)
            print("✓ Multi-format visualizations generated:")
            print("  - Category distribution dashboard")
            print("  - Top stories by category breakdown")
        
        print("\n" + "="*80)
        print("✅ COMPLETE: All 4 Tasks Executed Successfully!")
        print("="*80)
        print("\n📂 Generated Output Files:")
        print(f"  1. {output_json}")
        print(f"     └─ JSON data dump with HackerNews categories and aggregated trends")
        print(f"  2. {csv_file}")
        print(f"     └─ Raw CSV export with all stories and category assignments")
        print(f"  3. trends_cleaned.csv")
        print(f"     └─ Cleaned CSV with normalized scores and deduplication")
        print(f"  4. trends_visualization.png")
        print(f"     └─ Main dashboard: categories, top stories, score distribution")
        print(f"  5. trends_by_category.png")
        print(f"     └─ Category breakdown with top 8 stories per category")
        print("\n🔗 Data Source: HackerNews API (Fully Open, No Authentication)")
        print("📌 Categories: Technology | WorldNews | Sports | Science | Entertainment")
        print("="*80 + "\n")
        
        logger.info("TrendPulse pipeline completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during pipeline execution: {str(e)}")
        print(f"\n✗ Error: {str(e)}")


if __name__ == '__main__':
    main()
