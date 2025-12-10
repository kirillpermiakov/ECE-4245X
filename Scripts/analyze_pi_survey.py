#!/usr/bin/env python3
"""
Analyze Raspberry Pi WiFi Survey Data
Generates comprehensive analysis matching Acrylic methodology

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import pandas as pd
import numpy as np
from pathlib import Path

class PiSurveyAnalyzer:
    
    def __init__(self, parsed_csv):
        self.data = pd.read_csv(parsed_csv)
        self.floor_name = Path(parsed_csv).stem.replace('_floor_parsed', '')
        
    def analyze_slu_network(self):
        slu = self.data[self.data['essid'].str.contains('SLU', na=False, case=False)]
        slu_users = slu[slu['essid'].str.contains('users', na=False, case=False)]
        
        print(f"\n🔬 SLU-USERS NETWORK ANALYSIS ({self.floor_name.upper()} FLOOR)")
        print("="*60)
        
        print(f"\nNetwork Detection:")
        print(f"  Total SLU networks: {len(slu)}")
        print(f"  SLU-users APs: {len(slu_users)}")
        print(f"  Unique SLU-users BSSIDs: {slu_users['bssid'].nunique()}")
        
        if len(slu_users) > 0:
            print(f"\nSignal Strength:")
            print(f"  Average: {slu_users['signal_dbm'].mean():.1f} dBm")
            print(f"  Median: {slu_users['signal_dbm'].median():.1f} dBm")
            print(f"  Best: {slu_users['signal_dbm'].max():.0f} dBm")
            print(f"  Worst: {slu_users['signal_dbm'].min():.0f} dBm")
            print(f"  Std Dev: {slu_users['signal_dbm'].std():.1f} dBm")
            
            excellent = len(slu_users[slu_users['signal_dbm'] > -50])
            good = len(slu_users[(slu_users['signal_dbm'] <= -50) & 
                                  (slu_users['signal_dbm'] > -65)])
            fair = len(slu_users[(slu_users['signal_dbm'] <= -65) & 
                                 (slu_users['signal_dbm'] > -80)])
            poor = len(slu_users[slu_users['signal_dbm'] <= -80])
            
            total = len(slu_users)
            
            print(f"\nCoverage Quality:")
            print(f"  Excellent (>-50 dBm): {excellent} ({excellent/total*100:.1f}%)")
            print(f"  Good (-50 to -65 dBm): {good} ({good/total*100:.1f}%)")
            print(f"  Fair (-65 to -80 dBm): {fair} ({fair/total*100:.1f}%)")
            print(f"  Poor (<-80 dBm): {poor} ({poor/total*100:.1f}%)")
            
            if 'band' in slu_users.columns:
                band_2_4 = len(slu_users[slu_users['band'] == '2.4 GHz'])
                band_5 = len(slu_users[slu_users['band'] == '5 GHz'])
                
                print(f"\nBand Distribution:")
                print(f"  2.4 GHz: {band_2_4} ({band_2_4/total*100:.1f}%)")
                print(f"  5 GHz: {band_5} ({band_5/total*100:.1f}%)")
        
        print("="*60)
        
        return slu_users
    
    def analyze_all_networks(self):
        print(f"\n📡 ALL NETWORKS ANALYSIS ({self.floor_name.upper()} FLOOR)")
        print("="*60)
        
        print(f"\nNetwork Summary:")
        print(f"  Total APs detected: {len(self.data)}")
        print(f"  Unique BSSIDs: {self.data['bssid'].nunique()}")
        print(f"  Unique network names: {self.data['essid'].nunique()}")
        
        print(f"\nTop 10 Networks (by AP count):")
        network_counts = self.data['essid'].value_counts().head(10)
        for network, count in network_counts.items():
            if pd.notna(network) and network:
                print(f"  {network[:30]:30s} {count:4d} APs")
        
        if 'signal_dbm' in self.data.columns:
            print(f"\nOverall Signal Distribution:")
            print(f"  Average: {self.data['signal_dbm'].mean():.1f} dBm")
            print(f"  Median: {self.data['signal_dbm'].median():.1f} dBm")
            print(f"  Range: {self.data['signal_dbm'].min():.0f} to "
                  f"{self.data['signal_dbm'].max():.0f} dBm")
        
        if 'channel' in self.data.columns:
            print(f"\nChannel Usage (top 10):")
            channel_counts = self.data['channel'].value_counts().head(10)
            for channel, count in channel_counts.items():
                if pd.notna(channel):
                    print(f"  Channel {int(channel):3d}: {count:4d} APs")
        
        print("="*60)
    
    def compare_with_acrylic_numbers(self, acrylic_aps, acrylic_networks, acrylic_bssids):
        pi_bssids = self.data['bssid'].nunique()
        pi_networks = self.data['essid'].nunique()
        pi_aps = len(self.data)
        
        print(f"\n🔬 RASPBERRY PI vs ACRYLIC COMPARISON ({self.floor_name.upper()})")
        print("="*60)
        
        print(f"\n{'Metric':<20} {'Acrylic':>10} {'Pi':>10} {'Match':>10}")
        print("-"*60)
        print(f"{'Physical APs':<20} {acrylic_aps:>10} {pi_aps:>10} "
              f"{'✅' if abs(pi_aps - acrylic_aps) < 10 else '⚠️':>10}")
        print(f"{'Total BSSIDs':<20} {acrylic_bssids:>10} {pi_bssids:>10} "
              f"{'✅' if abs(pi_bssids - acrylic_bssids) < 50 else '⚠️':>10}")
        print(f"{'Networks':<20} {acrylic_networks:>10} {pi_networks:>10} "
              f"{'✅' if abs(pi_networks - acrylic_networks) < 5 else '⚠️':>10}")
        
        print("="*60)
        
        bssid_match = min(pi_bssids, acrylic_bssids) / max(pi_bssids, acrylic_bssids) * 100
        network_match = min(pi_networks, acrylic_networks) / max(pi_networks, acrylic_networks) * 100
        
        print(f"\nValidation Results:")
        print(f"  BSSID detection: {bssid_match:.1f}% match")
        print(f"  Network detection: {network_match:.1f}% match")
        
        if bssid_match > 90 and network_match > 90:
            print(f"\n✅ EXCELLENT VALIDATION - Pi survey confirms Acrylic results!")
        elif bssid_match > 80 and network_match > 80:
            print(f"\n✅ GOOD VALIDATION - Pi survey largely confirms Acrylic results")
        else:
            print(f"\n⚠️  PARTIAL VALIDATION - Some differences detected")
        
        print("="*60)

def analyze_all_floors(survey_dir):
    survey_path = Path(survey_dir)
    
    acrylic_data = {
        'ground': {'aps': 86, 'bssids': 422, 'networks': 30},
        'top': {'aps': 103, 'bssids': 446, 'networks': 45},
        'basement': {'aps': 54, 'bssids': 243, 'networks': 17}
    }
    
    print("\n" + "="*60)
    print("🔬 COMPLETE RASPBERRY PI SURVEY ANALYSIS")
    print("="*60)
    
    results = {}
    
    for floor in ['ground', 'top', 'basement']:
        parsed_file = survey_path / f'{floor}_floor_parsed.csv'
        
        if not parsed_file.exists():
            print(f"\n⚠️  No data for {floor} floor")
            continue
        
        analyzer = PiSurveyAnalyzer(parsed_file)
        
        analyzer.analyze_all_networks()
        slu_data = analyzer.analyze_slu_network()
        
        if floor in acrylic_data:
            analyzer.compare_with_acrylic_numbers(
                acrylic_data[floor]['aps'],
                acrylic_data[floor]['networks'],
                acrylic_data[floor]['bssids']
            )
        
        results[floor] = {
            'analyzer': analyzer,
            'slu_data': slu_data
        }
    
    return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_pi_survey.py <survey_directory>")
        print("Example: python analyze_pi_survey.py ~/wifi-survey/")
        sys.exit(1)
    
    survey_dir = sys.argv[1]
    results = analyze_all_floors(survey_dir)
    
    print("\n✅ Analysis complete!")

if __name__ == '__main__':
    main()
