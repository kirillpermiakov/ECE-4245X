#!/usr/bin/env python3
"""
Parse Raspberry Pi WiFi Survey Data
Converts airodump-ng CSV format to analyzable format

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import pandas as pd
import numpy as np
from pathlib import Path

class AirodumpParser:
    
    def __init__(self, csv_file):
        self.csv_file = Path(csv_file)
        self.raw_data = None
        self.access_points = None
        self.clients = None
        
    def parse(self):
        print(f"📄 Parsing: {self.csv_file.name}")
        
        with open(self.csv_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        ap_start = 0
        client_start = 0
        
        for i, line in enumerate(lines):
            if line.startswith('BSSID'):
                ap_start = i
            elif line.startswith('Station MAC'):
                client_start = i
                break
        
        if ap_start > 0 and client_start > ap_start:
            ap_lines = lines[ap_start:client_start]
            self.access_points = self._parse_access_points(ap_lines)
        
        if client_start > 0:
            client_lines = lines[client_start:]
            self.clients = self._parse_clients(client_lines)
        
        print(f"✅ Parsed {len(self.access_points)} access points")
        
        return {
            'access_points': self.access_points,
            'clients': self.clients
        }
    
    def _parse_access_points(self, lines):
        header = lines[0].strip().split(',')
        header = [h.strip() for h in header]
        
        data = []
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = self._csv_split(line)
            
            if len(parts) >= len(header):
                data.append(parts[:len(header)])
        
        df = pd.DataFrame(data, columns=header)
        df = self._clean_ap_dataframe(df)
        
        return df
    
    def _parse_clients(self, lines):
        if len(lines) < 2:
            return pd.DataFrame()
        
        header = lines[0].strip().split(',')
        header = [h.strip() for h in header]
        
        data = []
        for line in lines[1:]:
            if not line.strip():
                continue
            
            parts = self._csv_split(line)
            
            if len(parts) >= len(header):
                data.append(parts[:len(header)])
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data, columns=header)
        
        return df
    
    def _csv_split(self, line):
        parts = line.strip().split(',')
        return [p.strip() for p in parts]
    
    def _clean_ap_dataframe(self, df):
        column_map = {
            'BSSID': 'bssid',
            'First time seen': 'first_seen',
            'Last time seen': 'last_seen',
            'channel': 'channel',
            'Speed': 'speed',
            'Privacy': 'privacy',
            'Cipher': 'cipher',
            'Authentication': 'authentication',
            'Power': 'power',
            '# beacons': 'beacons',
            '# IV': 'iv',
            'LAN IP': 'lan_ip',
            'ID-length': 'id_length',
            'ESSID': 'essid',
            'Key': 'key'
        }
        
        rename_dict = {k: v for k, v in column_map.items() if k in df.columns}
        df = df.rename(columns=rename_dict)
        
        if 'power' in df.columns:
            df['power'] = pd.to_numeric(df['power'], errors='coerce')
            df = df.rename(columns={'power': 'signal_dbm'})
        
        if 'channel' in df.columns:
            df['channel'] = df['channel'].astype(str).str.strip()
            df['channel'] = pd.to_numeric(df['channel'], errors='coerce')
        
        if 'beacons' in df.columns:
            df['beacons'] = pd.to_numeric(df['beacons'], errors='coerce')
        
        if 'essid' in df.columns:
            df['essid'] = df['essid'].str.strip()
            df['essid'] = df['essid'].str.replace('"', '')
        
        if 'bssid' in df.columns:
            df['bssid'] = df['bssid'].str.strip()
            df['bssid'] = df['bssid'].str.upper()
        
        if 'first_seen' in df.columns:
            df['first_seen'] = pd.to_datetime(df['first_seen'], 
                                             format='%Y-%m-%d %H:%M:%S', 
                                             errors='coerce')
        
        if 'last_seen' in df.columns:
            df['last_seen'] = pd.to_datetime(df['last_seen'], 
                                            format='%Y-%m-%d %H:%M:%S', 
                                            errors='coerce')
        
        if 'channel' in df.columns:
            df['frequency'] = df['channel'].apply(self._channel_to_frequency)
        
        if 'frequency' in df.columns:
            df['band'] = df['frequency'].apply(
                lambda f: '2.4 GHz' if f and f < 3000 else '5 GHz' if f else None
            )
        
        return df
    
    def _channel_to_frequency(self, channel):
        if pd.isna(channel):
            return None
        
        channel = int(channel)
        
        if 1 <= channel <= 14:
            return 2407 + (channel * 5)
        elif 36 <= channel <= 165:
            return 5000 + (channel * 5)
        else:
            return None
    
    def export_to_csv(self, output_file):
        if self.access_points is not None:
            self.access_points.to_csv(output_file, index=False)
            print(f"✅ Exported to: {output_file}")
    
    def get_summary_stats(self):
        if self.access_points is None:
            return None
        
        df = self.access_points
        
        stats = {
            'total_aps': len(df),
            'unique_bssids': df['bssid'].nunique(),
            'unique_essids': df['essid'].nunique() if 'essid' in df.columns else 0,
            'avg_signal': df['signal_dbm'].mean() if 'signal_dbm' in df.columns else None,
            'min_signal': df['signal_dbm'].min() if 'signal_dbm' in df.columns else None,
            'max_signal': df['signal_dbm'].max() if 'signal_dbm' in df.columns else None,
            'channels_used': df['channel'].nunique() if 'channel' in df.columns else 0,
            'band_2_4ghz': len(df[df['band'] == '2.4 GHz']) if 'band' in df.columns else 0,
            'band_5ghz': len(df[df['band'] == '5 GHz']) if 'band' in df.columns else 0,
        }
        
        return stats

def parse_all_surveys(survey_dir):
    survey_path = Path(survey_dir)
    results = {}
    csv_files = list(survey_path.glob('survey_*-01.csv'))
    
    print(f"\n{'='*60}")
    print(f"📡 PARSING RASPBERRY PI SURVEY DATA")
    print(f"{'='*60}\n")
    
    for csv_file in csv_files:
        filename = csv_file.stem
        parts = filename.split('_')
        
        if len(parts) >= 2:
            floor = parts[1]
        else:
            floor = 'unknown'
        
        print(f"\n--- {floor.upper()} FLOOR ---")
        
        parser = AirodumpParser(csv_file)
        data = parser.parse()
        stats = parser.get_summary_stats()
        
        if stats:
            print(f"\n📊 Statistics:")
            print(f"   Total APs detected: {stats['total_aps']}")
            print(f"   Unique BSSIDs: {stats['unique_bssids']}")
            print(f"   Unique Networks: {stats['unique_essids']}")
            print(f"   Average signal: {stats['avg_signal']:.1f} dBm")
            print(f"   Signal range: {stats['min_signal']:.0f} to {stats['max_signal']:.0f} dBm")
            print(f"   2.4 GHz APs: {stats['band_2_4ghz']}")
            print(f"   5 GHz APs: {stats['band_5ghz']}")
        
        output_file = survey_path / f'{floor}_floor_parsed.csv'
        parser.export_to_csv(output_file)
        
        results[floor] = {
            'data': data['access_points'],
            'stats': stats,
            'csv_file': csv_file,
            'output_file': output_file
        }
    
    print(f"\n{'='*60}\n")
    
    return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_pi_data.py <survey_directory>")
        print("Example: python parse_pi_data.py ~/wifi-survey/")
        sys.exit(1)
    
    survey_dir = sys.argv[1]
    results = parse_all_surveys(survey_dir)
    
    print("\n📊 OVERALL SUMMARY:")
    print("="*60)
    
    total_aps = sum(r['stats']['total_aps'] for r in results.values())
    total_networks = sum(r['stats']['unique_essids'] for r in results.values())
    
    print(f"Total APs across all floors: {total_aps}")
    print(f"Total unique networks: {total_networks}")
    print(f"Floors surveyed: {len(results)}")
    print("="*60)

if __name__ == '__main__':
    main()
