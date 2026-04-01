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
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from collections import Counter
from urllib.parse import quote
import logging

# Configure logging for tracking data collection operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendingDataCollector:
    """
    Main class for collecting trending data from multiple sources.
    
    This class provides methods to fetch trending topics, hashtags, and
    keywords from different platforms and aggregates them for analysis.
    """
    
    def __init__(self):
        """Initialize the data collector with configuration and storage."""
        self.trends_data = {
            'collected_at': datetime.now().isoformat(),
            'sources': {},
            'aggregated_trends': []
        }
        self.session = requests.Session()
        # Set timeout for all requests to prevent hanging
        self.timeout = 10
        logger.info("TrendingDataCollector initialized")
    
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
        1. Collect data from all sources
        2. Normalize scores to make them comparable across platforms
        3. Calculate weighted average importance
        4. Sort by aggregated score
        
        Returns:
            Sorted list of aggregated trends
        """
        logger.info("Starting trend aggregation from all sources")
        
        # Collect data from all sources
        sources_data = {
            'twitter': self.collect_twitter_trends(),
            'google': self.collect_google_trends(),
            'reddit': self.collect_reddit_trends(),
            'hashtags': self.collect_hashtag_trends()
        }
        
        # Store collected data
        self.trends_data['sources'] = sources_data
        
        # Create a frequency counter to identify most mentioned trends
        trend_counter = Counter()
        
        # Aggregate trend mentions from all sources
        for source_name, source_data in sources_data.items():
            if source_data['status'] == 'success':
                for trend in source_data['trends']:
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
        return aggregated_trends
    
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
        """
        print("\n" + "="*60)
        print("TRENDPULSE: CURRENT TRENDING ANALYSIS")
        print("="*60)
        print(f"Collection Time: {self.trends_data['collected_at']}\n")
        
        aggregated_trends = self.aggregate_trends()
        
        if aggregated_trends:
            print("TOP TRENDING TOPICS:")
            print("-"*60)
            for i, trend in enumerate(aggregated_trends[:10], 1):
                importance = trend['importance_score']
                print(f"{i:2d}. {trend['trend']:30s} | Score: {importance}")
        else:
            print("No trends could be aggregated.")
        
        print("="*60 + "\n")


def main():
    """
    Main execution function.
    
    Flow:
    1. Initialize the data collector
    2. Aggregate trends from all available sources
    3. Display summary of findings
    4. Save results to file
    """
    try:
        # Initialize collector
        collector = TrendingDataCollector()
        
        # Collect and aggregate all trends
        logger.info("Starting TrendPulse data collection pipeline")
        collector.print_summary()
        
        # Save results to output file
        output_file = 'trends_output.json'
        collector.save_results(output_file)
        
        logger.info("TrendPulse data collection completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Data collection interrupted by user")
        print("\n\nData collection interrupted.")
    except Exception as e:
        logger.error(f"Unexpected error during data collection: {str(e)}")
        print(f"\n✗ Error: {str(e)}")


if __name__ == '__main__':
    main()
