#!/usr/bin/env python3
"""
Extract WiFi Survey Data from Acrylic WiFi Heatmaps
Extracts raw measurements, signal statistics, and AP information from Acrylic .prj files

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def extract_acrylic_data(prj_file, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(prj_file)
    
    floors_query = "SELECT id, name FROM floors"
    floors_df = pd.read_sql_query(floors_query, conn)
    
    print(f"\n{'='*60}")
    print(f"Extracting data from: {Path(prj_file).name}")
    print(f"{'='*60}\n")
    
    for _, floor in floors_df.iterrows():
        floor_id = floor['id']
        floor_name = floor['name']
        
        print(f"Processing floor: {floor_name}")
        
        floor_dir = output_path / floor_name.replace(' ', '_').lower()
        floor_dir.mkdir(parents=True, exist_ok=True)
        
        measurements_query = f"""
        SELECT 
            m.id,
            m.timestamp,
            m.x_position,
            m.y_position,
            a.bssid,
            a.ssid,
            a.channel,
            a.frequency,
            m.signal_strength
        FROM measurements m
        JOIN access_points a ON m.ap_id = a.id
        WHERE m.floor_id = {floor_id}
        ORDER BY m.timestamp, a.ssid
        """
        
        try:
            measurements_df = pd.read_sql_query(measurements_query, conn)
            
            if len(measurements_df) > 0:
                measurements_file = floor_dir / 'all_measurements.csv'
                measurements_df.to_csv(measurements_file, index=False)
                print(f"  ✓ Exported {len(measurements_df)} measurements")
                
                unique_ssids = measurements_df['ssid'].unique()
                print(f"  ✓ Found {len(unique_ssids)} unique networks")
                
                for ssid in unique_ssids:
                    if pd.notna(ssid) and ssid:
                        ssid_df = measurements_df[measurements_df['ssid'] == ssid]
                        safe_ssid = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in ssid)
                        ssid_file = floor_dir / f'{safe_ssid}_measurements.csv'
                        ssid_df.to_csv(ssid_file, index=False)
                
                signal_stats = measurements_df.groupby(['bssid', 'ssid']).agg({
                    'signal_strength': ['mean', 'min', 'max', 'std', 'count']
                }).reset_index()
                
                signal_stats.columns = ['bssid', 'ssid', 'avg_signal', 'min_signal', 'max_signal', 'std_signal', 'measurement_count']
                
                stats_file = floor_dir / 'signal_statistics.csv'
                signal_stats.to_csv(stats_file, index=False)
                print(f"  ✓ Exported signal statistics for {len(signal_stats)} APs")
                
            else:
                print(f"  ⚠ No measurements found")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Extraction complete! Data saved to: {output_path}")
    print(f"{'='*60}\n")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extract_acrylic_data.py <acrylic_prj_file> [output_directory]")
        print("Example: python extract_acrylic_data.py survey.prj ./extracted_data/")
        sys.exit(1)
    
    prj_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './acrylic_data'
    
    if not os.path.exists(prj_file):
        print(f"Error: File not found: {prj_file}")
        sys.exit(1)
    
    extract_acrylic_data(prj_file, output_dir)

if __name__ == '__main__':
    main()
