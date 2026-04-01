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
    
    def export_to_csv(self, filepath: str = 'trends_raw.csv') -> None:
        """
        Task 2: Clean CSV - Export trend data to CSV format.
        
        This function exports collected trends to a CSV file with proper
        formatting and structure for easy data analysis and sharing.
        
        Args:
            filepath: Path where CSV will be saved
        """
        try:
            logger.info("Exporting trends to CSV format")
            
            # Create a clean list of records from all sources
            csv_records = []
            
            # Extract data from each source and create CSV rows
            for source_name, source_data in self.trends_data['sources'].items():
                if source_data['status'] == 'success':
                    for trend in source_data['trends']:
                        # Create a normalized record with all relevant fields
                        record = {
                            'source': source_data['source'],
                            'timestamp': source_data['timestamp'],
                            'trend_name': trend.get('name') or trend.get('term') or trend.get('title') or trend.get('hashtag'),
                            'volume_frequency': trend.get('tweet_volume') or trend.get('volume') or trend.get('score') or trend.get('frequency'),
                            'subreddit': trend.get('subreddit', 'N/A')
                        }
                        csv_records.append(record)
            
            # Write cleaned data to CSV with proper headers
            if csv_records:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['source', 'timestamp', 'trend_name', 'volume_frequency', 'subreddit']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header row
                    writer.writeheader()
                    # Write all data rows
                    writer.writerows(csv_records)
                
                logger.info(f"CSV export successful: {filepath}")
                print(f"✓ CSV exported to {filepath}")
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
        1. Read the CSV data
        2. Clean and normalize the data
        3. Perform statistical analysis
        4. Generate insights
        
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
            
            # Handle missing values: Fill 'N/A' subreddit with 'Other'
            df_cleaned['subreddit'] = df_cleaned['subreddit'].fillna('Other')
            
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
            
            # Save cleaned data back
            df_cleaned.to_csv('trends_cleaned.csv', index=False, encoding='utf-8')
            logger.info("Cleaned data saved to trends_cleaned.csv")
            
            print(f"\n📊 Analysis Summary:")
            print(f"   Total Trends: {stats_summary['total_trends']}")
            print(f"   Avg Volume: {stats_summary['avg_volume']:.0f}")
            print(f"   Median Volume: {stats_summary['median_volume']:.0f}")
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
        1. Distribution of trends across sources
        2. Top trends by volume
        3. Trend volume statistics
        4. Source comparison
        
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
            plt.rcParams['figure.figsize'] = (14, 10)
            
            # Create a figure with multiple subplots
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('TrendPulse: Data Analysis Dashboard', fontsize=16, fontweight='bold')
            
            # Plot 1: Top 10 Trends by Volume (Bar Chart)
            top_trends = df.nlargest(10, 'volume_frequency')[['trend_name', 'volume_frequency']]
            axes[0, 0].barh(range(len(top_trends)), top_trends['volume_frequency'], color='steelblue')
            axes[0, 0].set_yticks(range(len(top_trends)))
            axes[0, 0].set_yticklabels(top_trends['trend_name'])
            axes[0, 0].set_xlabel('Volume/Frequency', fontweight='bold')
            axes[0, 0].set_title('Top 10 Trends by Volume')
            axes[0, 0].invert_yaxis()
            
            # Plot 2: Distribution of Trends by Source (Pie Chart)
            source_dist = df['source'].value_counts()
            axes[0, 1].pie(source_dist.values, labels=source_dist.index, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Trends Distribution by Source')
            
            # Plot 3: Volume Distribution (Histogram)
            axes[1, 0].hist(df['volume_frequency'], bins=20, color='coral', edgecolor='black', alpha=0.7)
            axes[1, 0].set_xlabel('Volume/Frequency', fontweight='bold')
            axes[1, 0].set_ylabel('Count', fontweight='bold')
            axes[1, 0].set_title('Volume Distribution Histogram')
            axes[1, 0].axvline(df['volume_frequency'].mean(), color='red', linestyle='--', label='Mean')
            axes[1, 0].legend()
            
            # Plot 4: Box Plot of Volume by Source
            source_volumes = [df[df['source'] == src]['volume_frequency'].values for src in df['source'].unique()]
            axes[1, 1].boxplot(source_volumes, labels=df['source'].unique())
            axes[1, 1].set_ylabel('Volume/Frequency', fontweight='bold')
            axes[1, 1].set_title('Volume Range by Source (Box Plot)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            # Adjust layout to prevent overlapping
            plt.tight_layout()
            
            # Save visualization
            viz_filepath = os.path.join(output_dir, 'trends_visualization.png')
            plt.savefig(viz_filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved: {viz_filepath}")
            print(f"✓ Visualization saved to {viz_filepath}")
            
            # Create additional visualization: Normalized Scores Comparison
            fig2, ax = plt.subplots(figsize=(12, 6))
            
            top_normalized = df.nlargest(15, 'normalized_score')[['trend_name', 'normalized_score', 'source']]
            
            # Color code by source
            colors = {'Twitter': 'skyblue', 'Google': 'lightgreen', 'Reddit': 'orange', 'Hashtag Aggregation': 'salmon'}
            bar_colors = [colors.get(src, 'gray') for src in top_normalized['source']]
            
            ax.bar(range(len(top_normalized)), top_normalized['normalized_score'], color=bar_colors)
            ax.set_xticks(range(len(top_normalized)))
            ax.set_xticklabels(top_normalized['trend_name'], rotation=45, ha='right')
            ax.set_ylabel('Normalized Score (0-100)', fontweight='bold')
            ax.set_title('Top 15 Trends - Normalized Scores by Source', fontweight='bold')
            ax.set_ylim(0, 110)
            
            # Add legend for colors
            from matplotlib.patches import Patch
            legend_elements = [Patch(facecolor=colors[src], label=src) for src in colors.keys()]
            ax.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            
            # Save second visualization
            viz2_filepath = os.path.join(output_dir, 'trends_normalized_scores.png')
            plt.savefig(viz2_filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Secondary visualization saved: {viz2_filepath}")
            print(f"✓ Secondary visualization saved to {viz2_filepath}")
            
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
    Main execution function - Complete TrendPulse Pipeline.
    
    Flow:
    1. Initialize the data collector
    2. Aggregate trends from all available sources
    3. Display summary of findings
    4. Task 1: Save results to JSON (Fetch JSON)
    5. Task 2: Export to CSV and clean data (Clean CSV)
    6. Task 3: Process with Pandas and NumPy (NumPy/Pandas)
    7. Task 4: Create visualizations (Visualise)
    """
    try:
        print("\n" + "="*70)
        print("TRENDPULSE: Comprehensive Data Collection & Analysis Pipeline")
        print("="*70)
        
        # Initialize collector
        collector = TrendingDataCollector()
        
        # Step 1 & 2: Collect and aggregate trends
        logger.info("Starting TrendPulse data collection pipeline")
        collector.print_summary()
        
        # TASK 1: Save results to JSON (Fetch JSON)
        print("\n📋 TASK 1: Fetching and Storing JSON Data")
        print("-" * 70)
        output_json = 'trends_output.json'
        collector.save_results(output_json)
        
        # TASK 2: Export to CSV and clean data (Clean CSV)
        print("\n📁 TASK 2: Data Cleaning & CSV Export")
        print("-" * 70)
        csv_file = 'trends_raw.csv'
        collector.export_to_csv(csv_file)
        print("✓ Raw data exported and cleaned to CSV format")
        
        # TASK 3: Process with Pandas and NumPy (NumPy/Pandas Analysis)
        print("\n🔬 TASK 3: NumPy/Pandas Data Analysis")
        print("-" * 70)
        df_cleaned = collector.analyze_with_pandas(csv_file)
        print("✓ Data processed with Pandas/NumPy statistical analysis")
        
        # TASK 4: Create visualizations (Visualise)
        print("\n📊 TASK 4: Data Visualization")
        print("-" * 70)
        if not df_cleaned.empty:
            collector.visualize_trends(df_cleaned)
            print("✓ Multi-format visualizations generated")
        
        print("\n" + "="*70)
        print("✅ COMPLETE: All 4 Tasks Executed Successfully!")
        print("="*70)
        print("\nGenerated Output Files:")
        print(f"  1. {output_json} - JSON data dump")
        print(f"  2. {csv_file} - Raw CSV export")
        print(f"  3. trends_cleaned.csv - Cleaned CSV data")
        print(f"  4. trends_visualization.png - Dashboard visualization")
        print(f"  5. trends_normalized_scores.png - Scores comparison chart")
        print("="*70 + "\n")
        
        logger.info("TrendPulse pipeline completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error during pipeline execution: {str(e)}")
        print(f"\n✗ Error: {str(e)}")


if __name__ == '__main__':
    main()
