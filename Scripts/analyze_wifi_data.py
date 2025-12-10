#!/usr/bin/env python3
"""
Analyze WiFi Survey Data
Calculates signal strength statistics, identifies handover zones, and computes efficiency metrics

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_floor(floor_dir, floor_name):
    print(f"\n{'='*60}")
    print(f"Analyzing: {floor_name.upper()}")
    print(f"{'='*60}\n")
    
    measurements_file = Path(floor_dir) / 'all_measurements.csv'
    
    if not measurements_file.exists():
        print(f"Error: {measurements_file} not found")
        return None
    
    df = pd.read_csv(measurements_file)
    
    print("📊 Overall Statistics:")
    print(f"  Total measurements: {len(df)}")
    print(f"  Unique locations: {df.groupby(['x_position', 'y_position']).ngroups}")
    print(f"  Unique BSSIDs: {df['bssid'].nunique()}")
    print(f"  Unique SSIDs: {df['ssid'].nunique()}")
    
    slu_users = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
    
    if len(slu_users) == 0:
        print("\n⚠ No SLU-users network data found")
        return None
    
    print(f"\n📡 SLU-users Network Analysis:")
    print(f"  Measurements: {len(slu_users)}")
    print(f"  Unique BSSIDs: {slu_users['bssid'].nunique()}")
    
    print(f"\n📶 Signal Strength Distribution:")
    print(f"  Average: {slu_users['signal_strength'].mean():.1f} dBm")
    print(f"  Median: {slu_users['signal_strength'].median():.1f} dBm")
    print(f"  Min: {slu_users['signal_strength'].min():.0f} dBm")
    print(f"  Max: {slu_users['signal_strength'].max():.0f} dBm")
    print(f"  Std Dev: {slu_users['signal_strength'].std():.1f} dBm")
    
    excellent = len(slu_users[slu_users['signal_strength'] > -50])
    good = len(slu_users[(slu_users['signal_strength'] <= -50) & (slu_users['signal_strength'] > -65)])
    fair = len(slu_users[(slu_users['signal_strength'] <= -65) & (slu_users['signal_strength'] > -80)])
    poor = len(slu_users[slu_users['signal_strength'] <= -80])
    total = len(slu_users)
    
    print(f"\n📊 Coverage Quality:")
    print(f"  Excellent (>-50 dBm): {excellent} ({excellent/total*100:.1f}%)")
    print(f"  Good (-50 to -65 dBm): {good} ({good/total*100:.1f}%)")
    print(f"  Fair (-65 to -80 dBm): {fair} ({fair/total*100:.1f}%)")
    print(f"  Poor (<-80 dBm): {poor} ({poor/total*100:.1f}%)")
    
    locations = slu_users.groupby(['x_position', 'y_position'])
    
    handover_threshold = -70
    
    handover_zones = []
    for (x, y), group in locations:
        strong_aps = group[group['signal_strength'] > handover_threshold]
        num_aps = len(strong_aps['bssid'].unique())
        
        if num_aps >= 2:
            handover_zones.append({
                'x': x,
                'y': y,
                'num_aps': num_aps,
                'avg_signal': strong_aps['signal_strength'].mean()
            })
    
    handover_df = pd.DataFrame(handover_zones)
    
    total_locations = locations.ngroups
    handover_locations = len(handover_df)
    handover_coverage = (handover_locations / total_locations * 100) if total_locations > 0 else 0
    
    print(f"\n🔄 Handover Zone Analysis:")
    print(f"  Total surveyed locations: {total_locations}")
    print(f"  Handover zones (2+ APs > -70 dBm): {handover_locations}")
    print(f"  Handover coverage: {handover_coverage:.1f}%")
    
    if len(handover_df) > 0:
        print(f"  Average APs per handover zone: {handover_df['num_aps'].mean():.1f}")
        print(f"  Max APs in single zone: {handover_df['num_aps'].max():.0f}")
        print(f"  Average signal in handover zones: {handover_df['avg_signal'].mean():.1f} dBm")
    
    coverage_score = (excellent + good) / total * 100 if total > 0 else 0
    
    handover_score = handover_coverage
    
    avg_handover_signal = handover_df['avg_signal'].mean() if len(handover_df) > 0 else -100
    signal_quality_score = min(100, max(0, (avg_handover_signal + 100) * 2))
    
    avg_aps_per_zone = handover_df['num_aps'].mean() if len(handover_df) > 0 else 0
    density_score = min(100, (avg_aps_per_zone / 20) * 100)
    
    efficiency_score = (
        handover_score * 0.4 +
        signal_quality_score * 0.3 +
        density_score * 0.3
    )
    
    print(f"\n🎯 Efficiency Metrics:")
    print(f"  Coverage score: {coverage_score:.1f}/100")
    print(f"  Handover score: {handover_score:.1f}/100")
    print(f"  Signal quality score: {signal_quality_score:.1f}/100")
    print(f"  AP density score: {density_score:.1f}/100")
    print(f"  Overall efficiency: {efficiency_score:.1f}/100")
    
    return {
        'floor': floor_name,
        'total_measurements': len(slu_users),
        'locations': total_locations,
        'avg_signal': slu_users['signal_strength'].mean(),
        'handover_coverage': handover_coverage,
        'handover_zones': handover_locations,
        'efficiency_score': efficiency_score
    }

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_wifi_data.py <data_directory>")
        print("Example: python analyze_wifi_data.py ./acrylic_data/")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    
    if not data_dir.exists():
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)
    
    floor_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    
    results = []
    for floor_dir in floor_dirs:
        result = analyze_floor(floor_dir, floor_dir.name)
        if result:
            results.append(result)
    
    if results:
        print(f"\n{'='*60}")
        print("BUILDING-WIDE SUMMARY")
        print(f"{'='*60}\n")
        
        total_measurements = sum(r['total_measurements'] for r in results)
        avg_efficiency = sum(r['efficiency_score'] for r in results) / len(results)
        avg_handover_coverage = sum(r['handover_coverage'] for r in results) / len(results)
        
        print(f"Floors analyzed: {len(results)}")
        print(f"Total measurements: {total_measurements}")
        print(f"Average handover coverage: {avg_handover_coverage:.1f}%")
        print(f"Average efficiency score: {avg_efficiency:.1f}/100")

if __name__ == '__main__':
    main()
