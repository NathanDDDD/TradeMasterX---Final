#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Phase 10 Status Reporter
Generate detailed status reports for the Phase 10 learning loop
"""

import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/phase_10_reporter.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Phase10Reporter")

class Phase10Reporter:
    """Generate comprehensive reports on Phase 10 status and performance"""
    
    def __init__(self):
        self.data_dir = Path("data/performance")
        self.reports_dir = Path("reports")
        self.logs_dir = Path("logs")
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset collections
        self.trade_data = None
        self.bot_metrics = None
        self.system_status = None
        
    def load_data(self):
        """Load all relevant data for reporting"""
        logger.info("🔍 Loading performance data...")
        
        # Load trade data from all available CSV files
        trade_files = list(self.data_dir.glob("trades_*.csv"))
        if trade_files:
            dfs = []
            for file in trade_files:
                try:
                    df = pd.read_csv(file)
                    dfs.append(df)
                except Exception as e:
                    logger.warning(f"⚠️ Error loading {file.name}: {e}")
            
            if dfs:
                self.trade_data = pd.concat(dfs, ignore_index=True)
                logger.info(f"📊 Loaded {len(self.trade_data)} trade records")
        
        # Load bot metrics data
        metrics_file = self.reports_dir / "phase_10_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    self.bot_metrics = json.load(f)
                logger.info(f"📊 Loaded metrics for {len(self.bot_metrics.get('trade_accuracy', {}))} bots")
            except Exception as e:
                logger.warning(f"⚠️ Error loading bot metrics: {e}")
        
        # Load system status
        status_file = self.logs_dir / "phase_10_status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    self.system_status = json.load(f)
                logger.info(f"📊 Loaded system status from {status_file}")
            except Exception as e:
                logger.warning(f"⚠️ Error loading system status: {e}")
                
        return bool(self.trade_data is not None)
    
    def generate_summary_report(self):
        """Generate a comprehensive text-based summary report"""
        if not self.load_data():
            logger.error("❌ No data available for reporting")
            return False
            
        logger.info("📝 Generating summary report...")
        
        report_lines = [
            "=" * 80,
            "TradeMasterX 2.0 - PHASE 10 SUMMARY REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        
        # System status
        report_lines.append("SYSTEM STATUS")
        report_lines.append("-" * 50)
        
        if self.system_status:
            timestamp = self.system_status.get('timestamp', 'Unknown')
            active = self.system_status.get('active', False)
            trades = self.system_status.get('trades_completed', 0)
            
            report_lines.append(f"Last Updated: {timestamp}")
            report_lines.append(f"Learning Loop Active: {'✅ Yes' if active else '❌ No'}")
            report_lines.append(f"Total Trades Completed: {trades}")
            
            # Add learning status details
            learning_status = self.system_status.get('learning_status', {})
            if learning_status:
                session_start = learning_status.get('session_start')
                if session_start:
                    start_time = datetime.fromisoformat(session_start)
                    duration = datetime.now() - start_time
                    report_lines.append(f"Session Duration: {duration.days}d {duration.seconds//3600}h {(duration.seconds//60)%60}m")
                
                next_retrain = learning_status.get('next_retrain_in', 0)
                report_lines.append(f"Next Retraining In: {next_retrain//3600:.1f}h")
                
        else:
            report_lines.append("⚠️ System status data not available")
        
        report_lines.append("")
        
        # Trade statistics
        report_lines.append("TRADE STATISTICS")
        report_lines.append("-" * 50)
        
        if self.trade_data is not None:
            # Calculate basic stats
            total_trades = len(self.trade_data)
            
            # Convert columns if needed
            if 'actual_return' in self.trade_data.columns:
                self.trade_data['actual_return'] = pd.to_numeric(self.trade_data['actual_return'], errors='coerce')
                
                avg_return = self.trade_data['actual_return'].mean()
                positive_trades = (self.trade_data['actual_return'] > 0).sum()
                win_rate = positive_trades / total_trades if total_trades > 0 else 0
                
                report_lines.append(f"Total Trades: {total_trades}")
                report_lines.append(f"Average Return: {avg_return:.4%}")
                report_lines.append(f"Win Rate: {win_rate:.2%}")
                
                # Calculate daily stats if timestamp available
                if 'timestamp' in self.trade_data.columns:
                    try:
                        self.trade_data['date'] = pd.to_datetime(self.trade_data['timestamp']).dt.date
                        daily_stats = self.trade_data.groupby('date')['actual_return'].agg(['count', 'mean', 'sum'])
                        
                        report_lines.append("\nDaily Activity:")
                        for date, row in daily_stats.iterrows():
                            report_lines.append(f"  {date}: {row['count']} trades, Avg: {row['mean']:.4%}, Total: {row['sum']:.4%}")
                    except:
                        pass
            else:
                report_lines.append(f"Total Trades: {total_trades}")
                report_lines.append("⚠️ Return data not available")
        else:
            report_lines.append("⚠️ No trade data available")
        
        report_lines.append("")
        
        # Bot performance
        report_lines.append("BOT PERFORMANCE")
        report_lines.append("-" * 50)
        
        if self.bot_metrics:
            # Get accuracy metrics
            accuracy = self.bot_metrics.get('trade_accuracy', {})
            contribution = self.bot_metrics.get('contribution_score', {})
            
            # Sort bots by contribution score
            if contribution:
                sorted_bots = sorted(contribution.items(), key=lambda x: float(x[1]), reverse=True)
                
                for bot_id, score in sorted_bots:
                    acc = accuracy.get(bot_id, 0)
                    report_lines.append(f"{bot_id}:")
                    report_lines.append(f"  Contribution Score: {float(score):.4f}")
                    report_lines.append(f"  Accuracy: {float(acc):.2%}")
            else:
                report_lines.append("⚠️ No bot contribution data available")
        else:
            report_lines.append("⚠️ No bot metrics available")
        
        # System recommendations based on data
        report_lines.append("\nRECOMMENDATIONS")
        report_lines.append("-" * 50)
        
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report_lines.append(f"• {rec}")
        
        # Write report to file
        report_path = self.reports_dir / f"phase_10_summary_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, 'w') as f:
            f.write("\n".join(report_lines))
            
        logger.info(f"✅ Summary report saved to {report_path}")
        
        return report_path
    
    def generate_performance_charts(self):
        """Generate performance visualization charts"""
        if not self.load_data() or self.trade_data is None:
            logger.error("❌ No trade data available for charting")
            return False
            
        logger.info("📊 Generating performance charts...")
        
        # Ensure output directory exists
        charts_dir = self.reports_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        try:
            # Prepare data
            if 'timestamp' in self.trade_data.columns:
                self.trade_data['datetime'] = pd.to_datetime(self.trade_data['timestamp'])
                self.trade_data['date'] = self.trade_data['datetime'].dt.date
            
            if 'actual_return' in self.trade_data.columns:
                self.trade_data['actual_return'] = pd.to_numeric(self.trade_data['actual_return'], errors='coerce')
                
                # 1. Cumulative Returns Chart
                plt.figure(figsize=(12, 6))
                cumulative_returns = (1 + self.trade_data['actual_return']).cumprod() - 1
                plt.plot(range(len(cumulative_returns)), cumulative_returns * 100)
                plt.title('Cumulative Returns (%)')
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(charts_dir / 'cumulative_returns.png')
                plt.close()
                
                # 2. Daily Returns Chart
                if 'date' in self.trade_data.columns:
                    daily_returns = self.trade_data.groupby('date')['actual_return'].sum()
                    
                    plt.figure(figsize=(12, 6))
                    daily_returns.plot(kind='bar')
                    plt.title('Daily Returns (%)')
                    plt.grid(True)
                    plt.tight_layout()
                    plt.savefig(charts_dir / 'daily_returns.png')
                    plt.close()
                
                # 3. Return Distribution
                plt.figure(figsize=(10, 6))
                plt.hist(self.trade_data['actual_return'] * 100, bins=30)
                plt.title('Return Distribution (%)')
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(charts_dir / 'return_distribution.png')
                plt.close()
            
            # 4. Bot Performance Comparison
            if self.bot_metrics and 'contribution_score' in self.bot_metrics:
                contribution = self.bot_metrics['contribution_score']
                accuracy = self.bot_metrics['trade_accuracy']
                
                # Get top 10 bots by contribution
                top_bots = sorted(contribution.items(), key=lambda x: float(x[1]), reverse=True)[:10]
                
                # Create comparison chart
                fig, ax1 = plt.subplots(figsize=(12, 6))
                
                bot_ids = [bot[0] for bot in top_bots]
                contrib_scores = [float(bot[1]) for bot in top_bots]
                acc_scores = [float(accuracy.get(bot[0], 0)) * 100 for bot in top_bots]
                
                x = np.arange(len(bot_ids))
                width = 0.35
                
                ax1.bar(x, contrib_scores, width, label='Contribution Score')
                ax1.set_ylabel('Contribution Score')
                ax1.set_title('Bot Performance Comparison')
                
                ax2 = ax1.twinx()
                ax2.bar(x + width, acc_scores, width, color='orange', label='Accuracy (%)')
                ax2.set_ylabel('Accuracy (%)')
                
                ax1.set_xticks(x + width / 2)
                ax1.set_xticklabels(bot_ids, rotation=45, ha='right')
                
                # Add legend
                ax1.legend(loc='upper left')
                ax2.legend(loc='upper right')
                
                fig.tight_layout()
                plt.savefig(charts_dir / 'bot_comparison.png')
                plt.close()
            
            logger.info(f"✅ Charts saved to {charts_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating charts: {e}")
            return False
    
    def _generate_recommendations(self):
        """Generate system recommendations based on data analysis"""
        recommendations = []
        
        # Analyze trade performance
        if self.trade_data is not None and 'actual_return' in self.trade_data.columns:
            avg_return = self.trade_data['actual_return'].mean()
            win_rate = (self.trade_data['actual_return'] > 0).mean()
            
            if win_rate < 0.5:
                recommendations.append(
                    "Win rate is below 50%. Consider adjusting confidence thresholds or retraining models."
                )
                
            if avg_return < 0:
                recommendations.append(
                    "Average return is negative. Review risk management settings and bot scoring algorithms."
                )
        
        # Analyze bot performance
        if self.bot_metrics and 'contribution_score' in self.bot_metrics:
            contribution = self.bot_metrics['contribution_score']
            
            # If we have at least 3 bots
            if len(contribution) >= 3:
                # Sort bots
                sorted_bots = sorted(contribution.items(), key=lambda x: float(x[1]), reverse=True)
                
                # Check for problematic bots (negative contribution)
                problem_bots = [bot_id for bot_id, score in contribution.items() if float(score) < 0]
                if problem_bots:
                    recommendations.append(
                        f"Identified {len(problem_bots)} bots with negative contribution scores. "
                        f"Consider removing or retraining: {', '.join(problem_bots[:3])}"
                    )
                
                # Focus on top performers
                top_bots = [bot_id for bot_id, _ in sorted_bots[:3]]
                recommendations.append(
                    f"Your top performing bots are: {', '.join(top_bots)}. "
                    f"Consider prioritizing these strategies for live trading."
                )
        
        # General recommendation based on data volume
        if self.trade_data is not None:
            trades_count = len(self.trade_data)
            
            if trades_count < 100:
                recommendations.append(
                    f"Only {trades_count} trades recorded. Continue collecting more data for more reliable analysis."
                )
            elif trades_count > 1000:
                recommendations.append(
                    f"Sufficient data ({trades_count} trades) collected. Ready for comprehensive analysis and readiness assessment."
                )
        
        # Add general recommendations if we have few specific ones
        if len(recommendations) < 3:
            recommendations.append(
                "Continue running the learning loop for the full 7-day period to collect comprehensive performance data."
            )
            recommendations.append(
                "Monitor bot performance metrics and consider replacing underperforming strategies."
            )
        
        return recommendations

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='TradeMasterX 2.0 - Phase 10 Reporter')
    parser.add_argument('--charts', action='store_true', help='Generate performance charts')
    parser.add_argument('--full', action='store_true', help='Generate full report with charts')
    parser.add_argument('--output', type=str, help='Output directory for reports', default='reports')
    
    args = parser.parse_args()
    
    # Create reporter
    reporter = Phase10Reporter()
    
    # Generate requested reports
    if args.full or not args.charts:
        # Generate text report by default or with --full
        report_path = reporter.generate_summary_report()
        if report_path:
            print(f"✅ Summary report generated: {report_path}")
    
    if args.charts or args.full:
        # Generate charts
        success = reporter.generate_performance_charts()
        if success:
            print(f"📊 Performance charts generated in {args.output}/charts/")
    
    return 0

if __name__ == "__main__":
    print("\n📊 TradeMasterX 2.0 - Phase 10 Reporter\n")
    sys.exit(main())
