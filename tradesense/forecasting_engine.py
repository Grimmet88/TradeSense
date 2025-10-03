"""
Forecasting engine for generating buy/sell/hold recommendations
"""

from typing import Dict, Optional, Tuple
import pandas as pd
from .data_aggregator import DataAggregator


class ForecastingEngine:
    """Generate trading recommendations based on multiple data sources and indicators"""
    
    def __init__(self):
        self.aggregator = DataAggregator()
        self.recommendation_weights = {
            'technical': 0.30,
            'fundamental': 0.30,
            'sentiment': 0.20,
            'analyst': 0.20
        }
    
    def analyze_stock(self, symbol: str, period: str = "1mo") -> Dict:
        """
        Complete stock analysis with recommendation
        
        Args:
            symbol: Stock ticker symbol
            period: Time period for analysis
            
        Returns:
            Dictionary with analysis results and recommendation
        """
        # Collect all data
        data = self.aggregator.collect_all_data(symbol, period)
        
        # Calculate metrics
        price_metrics = self.aggregator.get_price_metrics(data['historical_data'])
        fundamental_metrics = self.aggregator.get_fundamental_metrics(data['stock_info'])
        
        # Generate signals
        technical_signal = self._technical_analysis(price_metrics)
        fundamental_signal = self._fundamental_analysis(fundamental_metrics)
        sentiment_signal = self._sentiment_analysis(data['news_sentiment'], data['news'])
        analyst_signal = self._analyst_analysis(data['analyst_recommendations'], 
                                               fundamental_metrics)
        
        # Combine signals for final recommendation
        final_recommendation = self._combine_signals({
            'technical': technical_signal,
            'fundamental': fundamental_signal,
            'sentiment': sentiment_signal,
            'analyst': analyst_signal
        })
        
        # Compile results
        analysis = {
            'symbol': symbol.upper(),
            'timestamp': data['timestamp'],
            'recommendation': final_recommendation['action'],
            'confidence': final_recommendation['confidence'],
            'signals': {
                'technical': technical_signal,
                'fundamental': fundamental_signal,
                'sentiment': sentiment_signal,
                'analyst': analyst_signal
            },
            'metrics': {
                'price': price_metrics,
                'fundamental': fundamental_metrics
            },
            'data': data
        }
        
        return analysis
    
    def _technical_analysis(self, price_metrics: Optional[Dict]) -> Dict:
        """
        Perform technical analysis
        
        Args:
            price_metrics: Dictionary with price metrics
            
        Returns:
            Signal dictionary with action and score
        """
        if not price_metrics:
            return {'action': 'HOLD', 'score': 0, 'signals': ['Insufficient data']}
        
        signals = []
        score = 0
        
        # RSI Analysis (Relative Strength Index)
        if 'rsi' in price_metrics:
            rsi = price_metrics['rsi']
            if rsi < 30:
                signals.append(f"RSI oversold ({rsi:.1f})")
                score += 2
            elif rsi > 70:
                signals.append(f"RSI overbought ({rsi:.1f})")
                score -= 2
            else:
                signals.append(f"RSI neutral ({rsi:.1f})")
        
        # Moving Average Analysis
        current_price = price_metrics.get('current_price', 0)
        if 'sma_50' in price_metrics and current_price:
            sma_50 = price_metrics['sma_50']
            if current_price > sma_50:
                signals.append("Price above 50-day MA")
                score += 1
            else:
                signals.append("Price below 50-day MA")
                score -= 1
        
        if 'sma_200' in price_metrics and current_price:
            sma_200 = price_metrics['sma_200']
            if current_price > sma_200:
                signals.append("Price above 200-day MA")
                score += 1
            else:
                signals.append("Price below 200-day MA")
                score -= 1
        
        # Price momentum
        price_change_percent = price_metrics.get('price_change_percent', 0)
        if price_change_percent > 10:
            signals.append(f"Strong upward momentum (+{price_change_percent:.1f}%)")
            score += 1
        elif price_change_percent < -10:
            signals.append(f"Strong downward momentum ({price_change_percent:.1f}%)")
            score -= 1
        
        # Determine action
        if score >= 2:
            action = 'BUY'
        elif score <= -2:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'score': score,
            'signals': signals
        }
    
    def _fundamental_analysis(self, fundamental_metrics: Optional[Dict]) -> Dict:
        """
        Perform fundamental analysis
        
        Args:
            fundamental_metrics: Dictionary with fundamental metrics
            
        Returns:
            Signal dictionary with action and score
        """
        if not fundamental_metrics:
            return {'action': 'HOLD', 'score': 0, 'signals': ['Insufficient data']}
        
        signals = []
        score = 0
        
        # P/E Ratio Analysis
        pe_ratio = fundamental_metrics.get('pe_ratio')
        if pe_ratio:
            if pe_ratio < 15:
                signals.append(f"Low P/E ratio ({pe_ratio:.1f}) - potentially undervalued")
                score += 1
            elif pe_ratio > 30:
                signals.append(f"High P/E ratio ({pe_ratio:.1f}) - potentially overvalued")
                score -= 1
            else:
                signals.append(f"Moderate P/E ratio ({pe_ratio:.1f})")
        
        # PEG Ratio Analysis
        peg_ratio = fundamental_metrics.get('peg_ratio')
        if peg_ratio:
            if peg_ratio < 1:
                signals.append(f"Good PEG ratio ({peg_ratio:.2f})")
                score += 1
            elif peg_ratio > 2:
                signals.append(f"High PEG ratio ({peg_ratio:.2f})")
                score -= 1
        
        # Profit Margin
        profit_margin = fundamental_metrics.get('profit_margin')
        if profit_margin:
            if profit_margin > 0.20:
                signals.append(f"Strong profit margin ({profit_margin*100:.1f}%)")
                score += 1
            elif profit_margin < 0:
                signals.append(f"Negative profit margin ({profit_margin*100:.1f}%)")
                score -= 1
        
        # Revenue Growth
        revenue_growth = fundamental_metrics.get('revenue_growth')
        if revenue_growth:
            if revenue_growth > 0.15:
                signals.append(f"Strong revenue growth ({revenue_growth*100:.1f}%)")
                score += 1
            elif revenue_growth < 0:
                signals.append(f"Negative revenue growth ({revenue_growth*100:.1f}%)")
                score -= 1
        
        # Beta (Volatility)
        beta = fundamental_metrics.get('beta')
        if beta:
            if beta > 1.5:
                signals.append(f"High volatility (β={beta:.2f})")
            elif beta < 0.5:
                signals.append(f"Low volatility (β={beta:.2f})")
        
        # Determine action
        if score >= 2:
            action = 'BUY'
        elif score <= -2:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'score': score,
            'signals': signals
        }
    
    def _sentiment_analysis(self, sentiment: str, news: list) -> Dict:
        """
        Analyze news sentiment
        
        Args:
            sentiment: Overall sentiment ('positive', 'negative', 'neutral')
            news: List of news items
            
        Returns:
            Signal dictionary with action and score
        """
        signals = []
        score = 0
        
        if sentiment == 'positive':
            signals.append(f"Positive news sentiment ({len(news)} articles analyzed)")
            score = 2
            action = 'BUY'
        elif sentiment == 'negative':
            signals.append(f"Negative news sentiment ({len(news)} articles analyzed)")
            score = -2
            action = 'SELL'
        else:
            signals.append(f"Neutral news sentiment ({len(news)} articles analyzed)")
            score = 0
            action = 'HOLD'
        
        # Add recent news headlines
        if news:
            signals.append(f"Recent headlines: {len(news)} articles available")
        
        return {
            'action': action,
            'score': score,
            'signals': signals
        }
    
    def _analyst_analysis(self, recommendations: Optional[pd.DataFrame], 
                         fundamental_metrics: Optional[Dict]) -> Dict:
        """
        Analyze analyst recommendations
        
        Args:
            recommendations: DataFrame with analyst recommendations
            fundamental_metrics: Dictionary with fundamental metrics
            
        Returns:
            Signal dictionary with action and score
        """
        signals = []
        score = 0
        
        # Check analyst recommendation from stock info
        if fundamental_metrics and fundamental_metrics.get('recommendation'):
            rec = fundamental_metrics['recommendation']
            if rec in ['buy', 'strong_buy']:
                signals.append(f"Analyst consensus: {rec.upper()}")
                score = 2
                action = 'BUY'
            elif rec in ['sell', 'strong_sell']:
                signals.append(f"Analyst consensus: {rec.upper()}")
                score = -2
                action = 'SELL'
            else:
                signals.append(f"Analyst consensus: {rec.upper()}")
                score = 0
                action = 'HOLD'
        else:
            # Analyze recommendations DataFrame if available
            if recommendations is not None and not recommendations.empty:
                latest_recs = recommendations.tail(10)
                buy_count = latest_recs[latest_recs['To Grade'].str.contains('Buy', case=False, na=False)].shape[0]
                sell_count = latest_recs[latest_recs['To Grade'].str.contains('Sell', case=False, na=False)].shape[0]
                
                if buy_count > sell_count:
                    signals.append(f"Recent analyst upgrades ({buy_count} buy vs {sell_count} sell)")
                    score = 1
                    action = 'BUY'
                elif sell_count > buy_count:
                    signals.append(f"Recent analyst downgrades ({sell_count} sell vs {buy_count} buy)")
                    score = -1
                    action = 'SELL'
                else:
                    signals.append("Mixed analyst opinions")
                    score = 0
                    action = 'HOLD'
            else:
                signals.append("No analyst recommendations available")
                score = 0
                action = 'HOLD'
        
        return {
            'action': action,
            'score': score,
            'signals': signals
        }
    
    def _combine_signals(self, signals: Dict) -> Dict:
        """
        Combine all signals into final recommendation
        
        Args:
            signals: Dictionary with all signal types
            
        Returns:
            Dictionary with final action and confidence
        """
        # Calculate weighted score
        total_score = 0
        for signal_type, weight in self.recommendation_weights.items():
            signal = signals.get(signal_type, {})
            score = signal.get('score', 0)
            total_score += score * weight
        
        # Determine final action
        if total_score >= 1.0:
            action = 'BUY'
        elif total_score <= -1.0:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        # Calculate confidence (0-100%)
        confidence = min(abs(total_score) / 2.0 * 100, 100)
        
        return {
            'action': action,
            'confidence': confidence,
            'weighted_score': total_score
        }
