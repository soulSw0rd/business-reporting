# -*- coding: utf-8 -*-
"""
Moteur de Prédictions Crypto
Analyse les données de traders scrapées pour générer des signaux prédictifs
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import os

class MarketSignal(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class PredictionSignal:
    """Signal de prédiction généré"""
    signal: MarketSignal
    confidence: float
    time_horizon: str
    reasoning: List[str]
    supporting_traders: int
    consensus_strength: float
    risk_level: str

@dataclass
class TraderAnalysis:
    """Analyse détaillée d'un trader"""
    address: str
    performance_score: float
    reliability_score: float
    influence_weight: float
    trader_type: str
    predicted_action: str
    action_confidence: float

class CryptoPredictionEngine:
    """Moteur principal de prédictions"""
    
    def __init__(self):
        self.min_confidence_threshold = 0.6
        self.min_traders_consensus = 3
        
    def analyze_traders_data(self, traders_data: List[Dict]) -> Dict:
        """Analyse complète des données de traders pour générer des prédictions"""
        print("🧠 Début de l'analyse prédictive...")
        trader_analyses = self._analyze_individual_traders(traders_data)
        top_traders = self._rank_traders_by_influence(trader_analyses)
        market_consensus = self._generate_market_consensus(top_traders)
        prediction_signals = self._generate_prediction_signals(market_consensus, top_traders)
        copy_opportunities = self._identify_copy_opportunities(top_traders)
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'trader_analyses': [t.__dict__ for t in trader_analyses],
            'top_performers': [t.__dict__ for t in top_traders[:10]],
            'market_consensus': market_consensus,
            'prediction_signals': [s.__dict__ for s in prediction_signals],
            'copy_opportunities': copy_opportunities,
            'summary': self._generate_summary(trader_analyses, prediction_signals)
        }
        print(f"✅ Analyse terminée: {len(prediction_signals)} signaux générés")
        return analysis_result
    
    def _analyze_individual_traders(self, traders_data: List[Dict]) -> List[TraderAnalysis]:
        analyses = []
        for trader in traders_data:
            if trader.get('confidence_score', 0) < 0.3:
                continue
            analysis = TraderAnalysis(
                address=trader['address'],
                performance_score=self._calculate_performance_score(trader),
                reliability_score=self._calculate_reliability_score(trader),
                influence_weight=self._calculate_influence_weight(trader),
                trader_type=self._classify_trader_type(trader),
                predicted_action=self._predict_trader_action(trader),
                action_confidence=self._calculate_action_confidence(trader)
            )
            analyses.append(analysis)
        return analyses
    
    def _calculate_performance_score(self, trader: Dict) -> float:
        score = 50
        win_rate = trader.get('win_rate', 0.5)
        score += (win_rate - 0.5) * 80
        pnl = trader.get('pnl_7d', 0) or 0
        if pnl > 0:
            score += min(30, pnl / 1000)
        else:
            score += max(-30, pnl / 1000)
        volume = trader.get('total_volume', 0) or 0
        if volume > 10000:
            score += min(20, volume / 100000 * 20)
        trades = trader.get('total_trades', 0) or 0
        if trades > 10:
            score += min(10, trades / 100 * 10)
        return max(0, min(100, score))
    
    def _calculate_reliability_score(self, trader: Dict) -> float:
        score = 50
        confidence = trader.get('confidence_score', 0) or 0
        score += confidence * 30
        followers = trader.get('followers', 0) or 0
        if followers > 0:
            score += min(20, followers / 100 * 20)
        return max(0, min(100, score))
    
    def _calculate_influence_weight(self, trader: Dict) -> float:
        performance = self._calculate_performance_score(trader)
        reliability = self._calculate_reliability_score(trader)
        base_weight = (performance + reliability) / 200
        volume = trader.get('total_volume', 0) or 0
        if volume > 500000:
            base_weight *= 1.5
        return min(1.0, base_weight)
    
    def _classify_trader_type(self, trader: Dict) -> str:
        volume = trader.get('total_volume', 0) or 0
        win_rate = trader.get('win_rate', 0.5) or 0.5
        trades = trader.get('total_trades', 0) or 0
        if volume > 1000000:
            return "Whale"
        elif win_rate > 0.75 and trades > 50:
            return "Expert"
        elif win_rate > 0.65 and volume > 100000:
            return "Skilled"
        elif trades > 100:
            return "Active"
        else:
            return "Newcomer"
    
    def _predict_trader_action(self, trader: Dict) -> str:
        pnl = trader.get('pnl_7d', 0) or 0
        win_rate = trader.get('win_rate', 0.5) or 0.5
        if pnl > 5000 and win_rate > 0.7:
            return "BUY"
        elif pnl < -2000:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_action_confidence(self, trader: Dict) -> float:
        confidence = trader.get('confidence_score', 0) or 0
        performance = self._calculate_performance_score(trader) / 100
        return (confidence + performance) / 2
    
    def _rank_traders_by_influence(self, analyses: List[TraderAnalysis]) -> List[TraderAnalysis]:
        return sorted(analyses, key=lambda x: x.influence_weight, reverse=True)
    
    def _generate_market_consensus(self, top_traders: List[TraderAnalysis]) -> Dict:
        if len(top_traders) < self.min_traders_consensus:
            return {"error": "Pas assez de traders fiables pour consensus"}
        action_weights = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_weight = 0
        for trader in top_traders[:15]:
            weight = trader.influence_weight * trader.action_confidence
            action_weights[trader.predicted_action] += weight
            total_weight += weight
        if total_weight > 0:
            for action in action_weights:
                action_weights[action] /= total_weight
        dominant_action = max(action_weights, key=action_weights.get)
        dominance_strength = action_weights[dominant_action]
        consensus = {
            'dominant_action': dominant_action,
            'strength': dominance_strength,
            'distribution': action_weights,
            'supporting_traders': len([t for t in top_traders if t.predicted_action == dominant_action]),
            'consensus_quality': self._assess_consensus_quality(action_weights, top_traders)
        }
        return consensus
    
    def _assess_consensus_quality(self, action_weights: Dict, traders: List[TraderAnalysis]) -> str:
        max_weight = max(action_weights.values())
        avg_performance = np.mean([t.performance_score for t in traders[:10]])
        if max_weight > 0.7 and avg_performance > 70:
            return "HIGH"
        elif max_weight > 0.6 and avg_performance > 60:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_prediction_signals(self, consensus: Dict, top_traders: List[TraderAnalysis]) -> List[PredictionSignal]:
        signals = []
        if consensus.get('error'):
            return signals
        action = consensus['dominant_action']
        strength = consensus['strength']
        quality = consensus['consensus_quality']
        if strength > 0.7 and quality == "HIGH":
            signal_type = MarketSignal.STRONG_BUY if action == "BUY" else MarketSignal.STRONG_SELL if action == "SELL" else MarketSignal.HOLD
            time_horizon = "6h-24h" if action != "HOLD" else "1-3d"
        elif strength > 0.6:
            signal_type = MarketSignal.BUY if action == "BUY" else MarketSignal.SELL if action == "SELL" else MarketSignal.HOLD
            time_horizon = "1-3d" if action != "HOLD" else "3-7d"
        else:
            signal_type = MarketSignal.HOLD
            time_horizon = "1-7d"
        reasoning = self._generate_reasoning(consensus, top_traders)
        main_signal = PredictionSignal(signal=signal_type, confidence=min(0.95, strength * (1.2 if quality == "HIGH" else 1.0)), time_horizon=time_horizon, reasoning=reasoning, supporting_traders=consensus['supporting_traders'], consensus_strength=strength, risk_level=self._assess_risk_level(consensus, top_traders))
        signals.append(main_signal)
        signals.extend(self._generate_whale_signals(top_traders))
        return signals
    
    def _generate_reasoning(self, consensus: Dict, traders: List[TraderAnalysis]) -> List[str]:
        reasons = [f"{consensus['supporting_traders']} traders experts prédisent {consensus['dominant_action']}", f"Consensus à {consensus['strength']:.1%} de force"]
        whale_support = len([t for t in traders[:10] if t.trader_type == "Whale" and t.predicted_action == consensus['dominant_action']])
        if whale_support > 0:
            reasons.append(f"{whale_support} whales supportent {consensus['dominant_action']}")
        avg_perf_scores = [t.performance_score for t in traders[:10] if t.predicted_action == consensus['dominant_action']]
        if avg_perf_scores and np.mean(avg_perf_scores) > 75:
            reasons.append("Traders très performants en consensus")
        return reasons
    
    def _assess_risk_level(self, consensus: Dict, traders: List[TraderAnalysis]) -> str:
        strength = consensus['strength']
        quality = consensus['consensus_quality']
        if strength > 0.8 and quality == "HIGH":
            return "LOW"
        elif strength > 0.6 and quality in ["HIGH", "MEDIUM"]:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _generate_whale_signals(self, traders: List[TraderAnalysis]) -> List[PredictionSignal]:
        whale_traders = [t for t in traders if t.trader_type == "Whale"]
        if len(whale_traders) < 2:
            return []
        whale_buy_ratio = whale_traders.count("BUY") / len(whale_traders)
        if whale_buy_ratio > 0.7:
            return [PredictionSignal(signal=MarketSignal.BUY, confidence=0.8, time_horizon="1h-6h", reasoning=[f"{len(whale_traders)} whales prédisent des achats"], supporting_traders=len(whale_traders), consensus_strength=whale_buy_ratio, risk_level="MEDIUM")]
        return []
    
    def _identify_copy_opportunities(self, traders: List[TraderAnalysis]) -> List[Dict]:
        candidates = [t for t in traders if t.performance_score > 75 and t.reliability_score > 70 and t.action_confidence > 0.7]
        opportunities = [{'address': t.address, 'trader_type': t.trader_type, 'performance_score': t.performance_score, 'reliability_score': t.reliability_score, 'predicted_action': t.predicted_action, 'copy_confidence': (t.performance_score + t.reliability_score) / 200, 'estimated_roi_7d': self._estimate_roi(t), 'risk_assessment': self._assess_copy_risk(t)} for t in candidates[:5]]
        return sorted(opportunities, key=lambda x: x['copy_confidence'], reverse=True)
    
    def _estimate_roi(self, trader: TraderAnalysis) -> float:
        base_roi = (trader.performance_score - 50) / 100
        type_multipliers = {"Whale": 1.2, "Expert": 1.5, "Skilled": 1.1, "Active": 1.0, "Newcomer": 0.8}
        return base_roi * type_multipliers.get(trader.trader_type, 1.0)
    
    def _assess_copy_risk(self, trader: TraderAnalysis) -> str:
        if trader.reliability_score > 80 and trader.performance_score > 80:
            return "LOW"
        elif trader.reliability_score > 60 and trader.performance_score > 70:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _generate_summary(self, analyses: List[TraderAnalysis], signals: List[PredictionSignal]) -> Dict:
        return {'total_traders_analyzed': len(analyses), 'high_confidence_signals': len([s for s in signals if s.confidence > 0.8]), 'dominant_signal': signals[0].signal.value if signals else "HOLD", 'market_sentiment': self._determine_market_sentiment(analyses), 'recommendation': self._generate_final_recommendation(signals)}
    
    def _determine_market_sentiment(self, analyses: List[TraderAnalysis]) -> str:
        if not analyses:
            return "NEUTRAL"
        avg_performance = np.mean([a.performance_score for a in analyses])
        buy_ratio = len([a for a in analyses if a.predicted_action == "BUY"]) / len(analyses)
        if avg_performance > 70 and buy_ratio > 0.6:
            return "BULLISH"
        elif avg_performance < 40 or buy_ratio < 0.3:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _generate_final_recommendation(self, signals: List[PredictionSignal]) -> str:
        if not signals:
            return "WAIT - Données insuffisantes"
        main_signal = signals[0]
        if main_signal.confidence > 0.8:
            return f"{main_signal.signal.value} avec forte confiance"
        elif main_signal.confidence > 0.6:
            return f"{main_signal.signal.value} avec confiance modérée"
        else:
            return "WAIT - Signal incertain"

def analyze_scraped_data(json_filepath: str) -> Dict:
    """Analyse les données scrapées et génère des prédictions"""
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        traders_data = data.get('traders', [])
        if not traders_data:
            return {"error": "Aucune donnée de trader trouvée"}
        engine = CryptoPredictionEngine()
        analysis = engine.analyze_traders_data(traders_data)
        return analysis
    except Exception as e:
        return {"error": f"Erreur analyse: {e}"}

if __name__ == "__main__":
    test_data = [{'address': '0x123...', 'win_rate': 0.75, 'pnl_7d': 15000, 'total_volume': 250000, 'total_trades': 45, 'confidence_score': 0.9}]
    engine = CryptoPredictionEngine()
    result = engine.analyze_traders_data(test_data)
    print(json.dumps(result, indent=2)) 