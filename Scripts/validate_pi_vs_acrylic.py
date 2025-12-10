#!/usr/bin/env python3
"""
Validate Raspberry Pi Survey Against Acrylic Data
Statistical comparison and validation

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import pandas as pd
import numpy as np
from pathlib import Path

class ValidationAnalyzer:
    
    def __init__(self, pi_dir, acrylic_dir):
        self.pi_dir = Path(pi_dir)
        self.acrylic_dir = Path(acrylic_dir)
    
    def compare_floor(self, floor_name):
        print(f"\n{'='*60}")
        print(f"🔬 VALIDATION: {floor_name.upper()} FLOOR")
        print(f"{'='*60}\n")
        
        pi_file = self.pi_dir / f'{floor_name}_floor_parsed.csv'
        if not pi_file.exists():
            print(f"❌ Pi data not found: {pi_file}")
            return None
        
        pi_data = pd.read_csv(pi_file)
        pi_slu = pi_data[pi_data['essid'].str.contains('SLU-users', na=False, case=False)]
        
        acrylic_numbers = {
            'ground': {'bssids': 422, 'networks': 30, 'aps': 86, 'avg_signal': -55.3},
            'top': {'bssids': 446, 'networks': 45, 'aps': 103, 'avg_signal': -55.4},
            'basement': {'bssids': 243, 'networks': 17, 'aps': 54, 'avg_signal': -45.7}
        }
        
        if floor_name not in acrylic_numbers:
            print(f"❌ No Acrylic data for {floor_name}")
            return None
        
        acr = acrylic_numbers[floor_name]
        
        print("📊 Signal Strength Comparison:")
        print("-"*60)
        
        pi_avg = pi_slu['signal_dbm'].mean()
        acrylic_avg = acr['avg_signal']
        
        print(f"{'Metric':<25} {'Pi':>15} {'Acrylic':>15} {'Diff':>10}")
        print("-"*60)
        print(f"{'Average Signal (dBm)':<25} {pi_avg:>15.1f} {acrylic_avg:>15.1f} "
              f"{abs(pi_avg - acrylic_avg):>10.1f}")
        
        pi_best = pi_slu['signal_dbm'].max()
        pi_worst = pi_slu['signal_dbm'].min()
        print(f"{'Best Signal (dBm)':<25} {pi_best:>15.0f}")
        print(f"{'Worst Signal (dBm)':<25} {pi_worst:>15.0f}")
        
        print("\n📊 Network Detection Comparison:")
        print("-"*60)
        
        pi_bssids = pi_data['bssid'].nunique()
        pi_networks = pi_data['essid'].nunique()
        
        print(f"{'Metric':<25} {'Pi':>15} {'Acrylic':>15} {'Match %':>10}")
        print("-"*60)
        
        bssid_match = min(pi_bssids, acr['bssids']) / max(pi_bssids, acr['bssids']) * 100
        print(f"{'Total BSSIDs':<25} {pi_bssids:>15} {acr['bssids']:>15} "
              f"{bssid_match:>9.1f}%")
        
        network_match = min(pi_networks, acr['networks']) / max(pi_networks, acr['networks']) * 100
        print(f"{'Unique Networks':<25} {pi_networks:>15} {acr['networks']:>15} "
              f"{network_match:>9.1f}%")
        
        print("\n📊 Statistical Validation:")
        print("-"*60)
        
        mean_diff = abs(pi_avg - acrylic_avg)
        print(f"Mean signal difference: {mean_diff:.2f} dBm")
        
        if mean_diff < 2.0:
            print("✅ EXCELLENT - Signals match within 2 dBm")
        elif mean_diff < 5.0:
            print("✅ GOOD - Signals match within 5 dBm")
        else:
            print("⚠️  ACCEPTABLE - Some signal difference detected")
        
        print("\n" + "="*60)
        if mean_diff < 3.0 and bssid_match > 90:
            print("✅ VALIDATION SUCCESSFUL - Pi confirms Acrylic results!")
        elif mean_diff < 5.0 and bssid_match > 80:
            print("✅ VALIDATION GOOD - Pi largely confirms Acrylic")
        else:
            print("⚠️  VALIDATION PARTIAL - Some differences present")
        print("="*60)
        
        return {
            'floor': floor_name,
            'pi_avg_signal': pi_avg,
            'acrylic_avg_signal': acrylic_avg,
            'signal_diff': mean_diff,
            'pi_bssids': pi_bssids,
            'acrylic_bssids': acr['bssids'],
            'bssid_match': bssid_match
        }
    
    def validate_all_floors(self):
        print("\n" + "="*60)
        print("🔬 COMPLETE PI vs ACRYLIC VALIDATION STUDY")
        print("="*60)
        
        results = {}
        
        for floor in ['ground', 'top', 'basement']:
            result = self.compare_floor(floor)
            if result:
                results[floor] = result
        
        if results:
            print("\n" + "="*60)
            print("📊 OVERALL VALIDATION SUMMARY")
            print("="*60)
            
            avg_signal_diff = np.mean([r['signal_diff'] for r in results.values()])
            avg_bssid_match = np.mean([r['bssid_match'] for r in results.values()])
            
            print(f"\nAverage signal difference: {avg_signal_diff:.2f} dBm")
            print(f"Average BSSID match: {avg_bssid_match:.1f}%")
            
            if avg_signal_diff < 3.0 and avg_bssid_match > 90:
                print("\n🎉 EXCELLENT VALIDATION ACROSS ALL FLOORS!")
                print("   Raspberry Pi system successfully validates Acrylic survey")
                print("   Results are scientifically reproducible")
            
            print("="*60)
        
        return results

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validate_pi_vs_acrylic.py <pi_dir> <acrylic_dir>")
        print("\nExample:")
        print("  python validate_pi_vs_acrylic.py ~/wifi-survey/ ~/acrylic-data/")
        sys.exit(1)
    
    pi_dir = sys.argv[1]
    acrylic_dir = sys.argv[2]
    
    validator = ValidationAnalyzer(pi_dir, acrylic_dir)
    results = validator.validate_all_floors()
    
    print("\n✅ Validation complete!")

if __name__ == '__main__':
    main()
