#!/usr/bin/env python3
"""
Dashboard de Prédictions Multi-Wallets
Identifie les meilleurs traders et génère des prédictions globales
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import logging
from simple_wallet_analyzer import run_complete_analysis, generate_mock_wallet_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionDashboard:
    """Dashboard pour analyser plusieurs wallets et générer des prédictions"""
    
    def __init__(self):
        self.analyzed_wallets = []
        self.market_signals = []
        
    def analyze_wallet_list(self, wallet_addresses):
        """Analyse une liste de wallets"""
        logger.info(f"🔍 Analyse de {len(wallet_addresses)} wallets...")
        
        results = []
        for i, address in enumerate(wallet_addresses):
            logger.info(f"📊 Analyse wallet {i+1}/{len(wallet_addresses)}: {address[:10]}...")
            
            try:
                analysis = run_complete_analysis(address)
                results.append(analysis)
            except Exception as e:
                logger.error(f"❌ Erreur analyse {address}: {e}")
                continue
        
        self.analyzed_wallets = results
        logger.info(f"✅ {len(results)} wallets analysés avec succès")
        return results
    
    def rank_traders(self):
        """Classe les traders par performance"""
        if not self.analyzed_wallets:
            return []
        
        rankings = []
        for analysis in self.analyzed_wallets:
            summary = analysis['summary']
            predictions = analysis['predictions']
            
            # Score composite
            composite_score = (
                summary['trading_score'] * 0.4 +
                summary['win_rate'] * 100 * 0.3 +
                min(100, max(0, 50 + summary['total_pnl'] / 1000)) * 0.3
            )
            
            rankings.append({
                'address': analysis['wallet_address'],
                'composite_score': composite_score,
                'trading_score': summary['trading_score'],
                'win_rate': summary['win_rate'],
                'total_pnl': summary['total_pnl'],
                'total_volume': summary['total_volume_usd'],
                'trader_type': predictions['trader_type'],
                'next_action': predictions['next_action'],
                'confidence': predictions['confidence'],
                'risk_level': predictions['risk_level']
            })
        
        # Trier par score composite
        rankings.sort(key=lambda x: x['composite_score'], reverse=True)
        return rankings
    
    def generate_market_signals(self, top_n=10):
        """Génère des signaux de marché basés sur les top traders"""
        rankings = self.rank_traders()
        top_traders = rankings[:top_n]
        
        if not top_traders:
            return {}
        
        # Analyser les actions prédites
        action_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        weighted_confidence = 0
        total_weight = 0
        
        for trader in top_traders:
            action = trader['next_action']
            confidence = trader['confidence']
            weight = trader['composite_score'] / 100
            
            action_counts[action] += weight
            weighted_confidence += confidence * weight
            total_weight += weight
        
        # Signal majoritaire
        dominant_action = max(action_counts, key=action_counts.get)
        action_strength = action_counts[dominant_action] / total_weight if total_weight > 0 else 0
        
        # Tokens recommandés par les top traders
        recommended_tokens = {}
        for analysis in self.analyzed_wallets[:top_n]:
            tokens = analysis['predictions'].get('recommended_tokens', [])
            for token in tokens:
                recommended_tokens[token] = recommended_tokens.get(token, 0) + 1
        
        top_tokens = sorted(recommended_tokens.items(), key=lambda x: x[1], reverse=True)[:5]
        
        signals = {
            'timestamp': datetime.now().isoformat(),
            'market_signal': {
                'action': dominant_action,
                'strength': action_strength,
                'confidence': weighted_confidence / total_weight if total_weight > 0 else 0,
                'consensus': f"{action_strength:.1%} des top traders"
            },
            'recommended_tokens': [token for token, count in top_tokens],
            'market_sentiment': self._calculate_market_sentiment(top_traders),
            'risk_assessment': self._assess_overall_risk(top_traders)
        }
        
        self.market_signals.append(signals)
        return signals
    
    def _calculate_market_sentiment(self, traders):
        """Calcule le sentiment général du marché"""
        total_pnl = sum(t['total_pnl'] for t in traders)
        avg_win_rate = np.mean([t['win_rate'] for t in traders])
        
        if total_pnl > 50000 and avg_win_rate > 0.6:
            return {"sentiment": "Très Bullish", "score": 0.8}
        elif total_pnl > 0 and avg_win_rate > 0.5:
            return {"sentiment": "Bullish", "score": 0.6}
        elif total_pnl > -20000:
            return {"sentiment": "Neutre", "score": 0.5}
        else:
            return {"sentiment": "Bearish", "score": 0.3}
    
    def _assess_overall_risk(self, traders):
        """Évalue le risque global"""
        high_risk_count = sum(1 for t in traders if t['risk_level'] == 'Élevé')
        risk_ratio = high_risk_count / len(traders)
        
        if risk_ratio > 0.7:
            return {"level": "Élevé", "description": "Majorité de traders à haut risque"}
        elif risk_ratio > 0.3:
            return {"level": "Moyen", "description": "Mix de profils de risque"}
        else:
            return {"level": "Faible", "description": "Traders majoritairement prudents"}
    
    def find_copy_candidates(self, min_score=80):
        """Trouve les traders à copier"""
        rankings = self.rank_traders()
        candidates = [t for t in rankings if t['composite_score'] >= min_score]
        
        copy_candidates = []
        for candidate in candidates:
            copy_info = {
                'address': candidate['address'],
                'reasons_to_copy': [],
                'copy_score': candidate['composite_score'],
                'expected_roi': self._estimate_roi(candidate),
                'risk_level': candidate['risk_level']
            }
            
            # Raisons de copier
            if candidate['win_rate'] > 0.7:
                copy_info['reasons_to_copy'].append("Excellent taux de réussite")
            
            if candidate['total_pnl'] > 10000:
                copy_info['reasons_to_copy'].append("Profits substantiels")
            
            if candidate['trader_type'] in ["Expert Profitable", "Trader Expérimenté"]:
                copy_info['reasons_to_copy'].append("Profil de trader expérimenté")
            
            if candidate['total_volume'] > 100000:
                copy_info['reasons_to_copy'].append("Volume de trading élevé")
            
            copy_candidates.append(copy_info)
        
        return copy_candidates
    
    def _estimate_roi(self, trader_data):
        """Estime le ROI potentiel"""
        base_roi = trader_data['total_pnl'] / max(trader_data['total_volume'], 1) * 100
        
        # Ajuster selon le profil de risque
        risk_multiplier = {'Faible': 0.8, 'Moyen': 1.0, 'Élevé': 1.3}
        adjusted_roi = base_roi * risk_multiplier.get(trader_data['risk_level'], 1.0)
        
        return max(-50, min(200, adjusted_roi))  # Limiter entre -50% et +200%
    
    def generate_dashboard_report(self):
        """Génère le rapport complet du dashboard"""
        if not self.analyzed_wallets:
            return {"error": "Aucun wallet analysé"}
        
        rankings = self.rank_traders()
        signals = self.generate_market_signals()
        copy_candidates = self.find_copy_candidates()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_wallets_analyzed': len(self.analyzed_wallets),
                'top_performers_count': len([r for r in rankings if r['composite_score'] >= 80]),
                'total_volume_analyzed': sum(r['total_volume'] for r in rankings),
                'total_pnl_analyzed': sum(r['total_pnl'] for r in rankings),
                'average_win_rate': np.mean([r['win_rate'] for r in rankings])
            },
            'top_traders': rankings[:10],
            'market_signals': signals,
            'copy_trading_candidates': copy_candidates,
            'performance_distribution': self._get_performance_distribution(rankings),
            'recommendations': self._generate_dashboard_recommendations(rankings, signals)
        }
        
        return report
    
    def _get_performance_distribution(self, rankings):
        """Analyse la distribution des performances"""
        scores = [r['composite_score'] for r in rankings]
        
        return {
            'excellent': len([s for s in scores if s >= 90]),
            'good': len([s for s in scores if 70 <= s < 90]),
            'average': len([s for s in scores if 50 <= s < 70]),
            'poor': len([s for s in scores if s < 50]),
            'avg_score': np.mean(scores),
            'median_score': np.median(scores)
        }
    
    def _generate_dashboard_recommendations(self, rankings, signals):
        """Génère des recommandations globales"""
        recommendations = []
        
        # Basé sur le signal de marché
        market_action = signals['market_signal']['action']
        if market_action == 'BUY' and signals['market_signal']['strength'] > 0.6:
            recommendations.append("Signal d'achat fort - Considérer l'entrée sur le marché")
        elif market_action == 'SELL' and signals['market_signal']['strength'] > 0.6:
            recommendations.append("Signal de vente - Considérer la prise de profits")
        
        # Basé sur les performances
        top_performers = len([r for r in rankings if r['composite_score'] >= 80])
        if top_performers >= 3:
            recommendations.append(f"Opportunité de copy trading avec {top_performers} traders performants")
        
        # Basé sur les tokens
        if signals['recommended_tokens']:
            top_token = signals['recommended_tokens'][0]
            recommendations.append(f"Token le plus recommandé par les experts: {top_token}")
        
        return recommendations
    
    def save_dashboard(self, report, filename=None):
        """Sauvegarde le rapport du dashboard"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prediction_dashboard_{timestamp}.json"
        
        import os
        os.makedirs("data", exist_ok=True)
        filepath = f"data/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"💾 Dashboard sauvegardé: {filepath}")
        return filepath
    
    def print_dashboard(self, report):
        """Affiche le dashboard de manière lisible"""
        print("\n" + "="*80)
        print("🚀 DASHBOARD DE PRÉDICTIONS CRYPTO - ANALYSE MULTI-WALLETS")
        print("="*80)
        
        summary = report['summary']
        print(f"\n📊 RÉSUMÉ GLOBAL")
        print(f"Wallets analysés: {summary['total_wallets_analyzed']}")
        print(f"Top performers: {summary['top_performers_count']}")
        print(f"Volume total analysé: ${summary['total_volume_analyzed']:,.2f}")
        print(f"PnL total: ${summary['total_pnl_analyzed']:,.2f}")
        print(f"Taux de réussite moyen: {summary['average_win_rate']:.1%}")
        
        # Top traders
        print(f"\n🏆 TOP 5 TRADERS")
        print("-" * 50)
        for i, trader in enumerate(report['top_traders'][:5]):
            print(f"{i+1}. {trader['address'][:15]}... - Score: {trader['composite_score']:.1f}")
            print(f"   Win Rate: {trader['win_rate']:.1%} | PnL: ${trader['total_pnl']:,.0f} | Action: {trader['next_action']}")
        
        # Signaux de marché
        signals = report['market_signals']
        print(f"\n📈 SIGNAUX DE MARCHÉ")
        print(f"Action recommandée: {signals['market_signal']['action']}")
        print(f"Force du signal: {signals['market_signal']['strength']:.1%}")
        print(f"Confiance: {signals['market_signal']['confidence']:.1%}")
        print(f"Sentiment: {signals['market_sentiment']['sentiment']}")
        
        if signals['recommended_tokens']:
            print(f"Tokens recommandés: {', '.join(signals['recommended_tokens'][:3])}")
        
        # Candidats au copy trading
        if report['copy_trading_candidates']:
            print(f"\n🎯 CANDIDATS COPY TRADING")
            for candidate in report['copy_trading_candidates'][:3]:
                print(f"• {candidate['address'][:15]}... - ROI estimé: {candidate['expected_roi']:+.1f}%")
                print(f"  Raisons: {', '.join(candidate['reasons_to_copy'][:2])}")
        
        # Recommandations
        if report['recommendations']:
            print(f"\n💡 RECOMMANDATIONS")
            for rec in report['recommendations']:
                print(f"• {rec}")

def main():
    """Test du dashboard avec plusieurs wallets"""
    dashboard = PredictionDashboard()
    
    # Wallets de test (incluant celui fourni)
    test_wallets = [
        "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303",  # Wallet fourni
        "0x1234567890123456789012345678901234567890",  # Wallet test 1
        "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",  # Wallet test 2
        "0x9876543210987654321098765432109876543210",  # Wallet test 3
        "0x5555666677778888999900001111222233334444",  # Wallet test 4
    ]
    
    print("🚀 DASHBOARD DE PRÉDICTIONS MULTI-WALLETS")
    print("Analyse des meilleurs traders crypto pour prédictions et copy trading")
    
    # Analyser tous les wallets
    dashboard.analyze_wallet_list(test_wallets)
    
    # Générer le rapport complet
    report = dashboard.generate_dashboard_report()
    
    # Afficher le dashboard
    dashboard.print_dashboard(report)
    
    # Sauvegarder
    filepath = dashboard.save_dashboard(report)
    print(f"\n📁 Dashboard complet sauvegardé: {filepath}")
    
    return report

if __name__ == "__main__":
    main() 