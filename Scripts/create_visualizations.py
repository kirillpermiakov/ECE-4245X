#!/usr/bin/env python3
"""
Generate WiFi Survey Visualizations
Creates comprehensive charts and heatmaps for WiFi coverage analysis

Author: Hamza Abu Khalaf Al Takrouri & Kirill Permiakov
Team: Roametrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_floor_data(data_dir):
    data_path = Path(data_dir)
    floors = {}
    
    for floor_dir in data_path.iterdir():
        if floor_dir.is_dir():
            measurements_file = floor_dir / 'all_measurements.csv'
            if measurements_file.exists():
                df = pd.read_csv(measurements_file)
                floors[floor_dir.name] = df
    
    return floors

def create_signal_distribution(floors_data, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Signal Strength Distribution by Floor (SLU-users Network)', fontsize=16, fontweight='bold')
    
    floor_names = ['ground_floor', 'top_floor', 'basement']
    titles = ['Ground Floor', 'Top Floor', 'Basement']
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    for idx, (floor_key, title, color) in enumerate(zip(floor_names, titles, colors)):
        if floor_key in floors_data:
            df = floors_data[floor_key]
            slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
            
            if len(slu) > 0:
                axes[idx].hist(slu['signal_strength'], bins=30, color=color, alpha=0.7, edgecolor='black')
                axes[idx].axvline(slu['signal_strength'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {slu['signal_strength'].mean():.1f} dBm')
                axes[idx].set_xlabel('Signal Strength (dBm)', fontweight='bold')
                axes[idx].set_ylabel('Frequency', fontweight='bold')
                axes[idx].set_title(title, fontweight='bold')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / '1_signal_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 1_signal_distribution.png")
    plt.close()

def create_network_infrastructure(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Network Infrastructure Analysis', fontsize=16, fontweight='bold')
    
    floor_stats = []
    for floor_name, df in floors_data.items():
        floor_stats.append({
            'Floor': floor_name.replace('_', ' ').title(),
            'BSSIDs': df['bssid'].nunique(),
            'Networks': df['ssid'].nunique(),
            'Measurements': len(df)
        })
    
    stats_df = pd.DataFrame(floor_stats)
    
    ax = axes[0, 0]
    bars = ax.bar(stats_df['Floor'], stats_df['BSSIDs'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Unique BSSIDs by Floor', fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax = axes[0, 1]
    bars = ax.bar(stats_df['Floor'], stats_df['Networks'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Unique Networks by Floor', fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax = axes[1, 0]
    bars = ax.bar(stats_df['Floor'], stats_df['Measurements'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Total Measurements by Floor', fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    axes[1, 1].axis('off')
    summary_text = f"""
    BUILDING-WIDE SUMMARY
    =====================
    
    Total BSSIDs: {stats_df['BSSIDs'].sum()}
    Total Networks: {stats_df['Networks'].sum()}
    Total Measurements: {stats_df['Measurements'].sum():,}
    
    Floors Surveyed: {len(stats_df)}
    """
    axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, fontfamily='monospace', verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig(output_path / '2_network_infrastructure.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 2_network_infrastructure.png")
    plt.close()

def create_coverage_quality(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Coverage Quality Distribution (SLU-users Network)', fontsize=16, fontweight='bold')
    
    floor_names = ['ground_floor', 'top_floor', 'basement']
    titles = ['Ground Floor', 'Top Floor', 'Basement']
    
    for idx, (floor_key, title) in enumerate(zip(floor_names, titles)):
        if floor_key in floors_data:
            df = floors_data[floor_key]
            slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
            
            if len(slu) > 0:
                excellent = len(slu[slu['signal_strength'] > -50])
                good = len(slu[(slu['signal_strength'] <= -50) & (slu['signal_strength'] > -65)])
                fair = len(slu[(slu['signal_strength'] <= -65) & (slu['signal_strength'] > -80)])
                poor = len(slu[slu['signal_strength'] <= -80])
                
                categories = ['Excellent\n(>-50 dBm)', 'Good\n(-50 to -65)', 'Fair\n(-65 to -80)', 'Poor\n(<-80 dBm)']
                values = [excellent, good, fair, poor]
                colors_list = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
                
                bars = axes[idx].bar(categories, values, color=colors_list, alpha=0.7, edgecolor='black')
                axes[idx].set_ylabel('Number of Measurements', fontweight='bold')
                axes[idx].set_title(title, fontweight='bold')
                axes[idx].grid(True, axis='y', alpha=0.3)
                
                for bar, val in zip(bars, values):
                    height = bar.get_height()
                    pct = (val / len(slu) * 100) if len(slu) > 0 else 0
                    axes[idx].text(bar.get_x() + bar.get_width()/2., height, f'{int(val)}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path / '3_coverage_quality.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 3_coverage_quality.png")
    plt.close()

def create_survey_statistics(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('Survey Statistics Dashboard', fontsize=18, fontweight='bold')
    
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    total_measurements = sum(len(df) for df in floors_data.values())
    total_bssids = sum(df['bssid'].nunique() for df in floors_data.values())
    total_networks = sum(df['ssid'].nunique() for df in floors_data.values())
    
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    summary_text = f"""
    COMPREHENSIVE SURVEY SUMMARY
    ============================
    
    Total Measurements Collected: {total_measurements:,}
    Unique BSSIDs Detected: {total_bssids}
    Unique Networks Found: {total_networks}
    Floors Surveyed: {len(floors_data)}
    """
    ax1.text(0.5, 0.5, summary_text, fontsize=14, fontfamily='monospace', ha='center', va='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    floor_data = []
    for floor_name, df in floors_data.items():
        slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
        if len(slu) > 0:
            floor_data.append({
                'Floor': floor_name.replace('_', ' ').title(),
                'Avg Signal': slu['signal_strength'].mean(),
                'Measurements': len(slu)
            })
    
    floor_df = pd.DataFrame(floor_data)
    
    ax2 = fig.add_subplot(gs[1, 0])
    bars = ax2.barh(floor_df['Floor'], floor_df['Avg Signal'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Average Signal Strength (dBm)', fontweight='bold')
    ax2.set_title('Average Signal by Floor', fontweight='bold')
    ax2.grid(True, axis='x', alpha=0.3)
    for bar, val in zip(bars, floor_df['Avg Signal']):
        ax2.text(val, bar.get_y() + bar.get_height()/2., f'{val:.1f} dBm', va='center', fontweight='bold')
    
    ax3 = fig.add_subplot(gs[1, 1])
    bars = ax3.bar(floor_df['Floor'], floor_df['Measurements'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Count', fontweight='bold')
    ax3.set_title('SLU-users Measurements by Floor', fontweight='bold')
    ax3.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax4 = fig.add_subplot(gs[2, :])
    all_slu = []
    for df in floors_data.values():
        slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
        if len(slu) > 0:
            all_slu.append(slu['signal_strength'])
    
    if all_slu:
        combined_slu = pd.concat(all_slu)
        ax4.hist(combined_slu, bins=50, color='#3498db', alpha=0.7, edgecolor='black')
        ax4.axvline(combined_slu.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {combined_slu.mean():.1f} dBm')
        ax4.set_xlabel('Signal Strength (dBm)', fontweight='bold')
        ax4.set_ylabel('Frequency', fontweight='bold')
        ax4.set_title('Building-Wide Signal Distribution (SLU-users)', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.savefig(output_path / '4_survey_statistics.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 4_survey_statistics.png")
    plt.close()

def create_handover_scatter(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Handover Zone Identification (2+ APs > -70 dBm)', fontsize=16, fontweight='bold')
    
    floor_names = ['ground_floor', 'top_floor', 'basement']
    titles = ['Ground Floor', 'Top Floor', 'Basement']
    
    for idx, (floor_key, title) in enumerate(zip(floor_names, titles)):
        if floor_key in floors_data:
            df = floors_data[floor_key]
            slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
            
            if len(slu) > 0:
                locations = slu.groupby(['x_position', 'y_position'])
                
                handover_zones = []
                non_handover = []
                
                for (x, y), group in locations:
                    strong_aps = group[group['signal_strength'] > -70]
                    num_aps = len(strong_aps['bssid'].unique())
                    avg_signal = group['signal_strength'].mean()
                    
                    if num_aps >= 2:
                        handover_zones.append({'x': x, 'y': y, 'signal': avg_signal, 'aps': num_aps})
                    else:
                        non_handover.append({'x': x, 'y': y, 'signal': avg_signal})
                
                if non_handover:
                    nh_df = pd.DataFrame(non_handover)
                    axes[idx].scatter(nh_df['x'], nh_df['y'], c='red', s=20, alpha=0.3, label='Non-handover')
                
                if handover_zones:
                    hz_df = pd.DataFrame(handover_zones)
                    axes[idx].scatter(hz_df['x'], hz_df['y'], c='green', s=50, alpha=0.6, label='Handover zone')
                
                axes[idx].set_xlabel('X Position', fontweight='bold')
                axes[idx].set_ylabel('Y Position', fontweight='bold')
                axes[idx].set_title(title, fontweight='bold')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / '5_handover_scatter.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 5_handover_scatter.png")
    plt.close()

def create_summary_dashboard(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('WiFi Survey Comprehensive Dashboard', fontsize=20, fontweight='bold')
    
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    total_measurements = sum(len(df) for df in floors_data.values())
    total_bssids = sum(df['bssid'].nunique() for df in floors_data.values())
    
    all_slu = []
    for df in floors_data.values():
        slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
        if len(slu) > 0:
            all_slu.append(slu)
    
    combined_slu = pd.concat(all_slu) if all_slu else pd.DataFrame()
    
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    if len(combined_slu) > 0:
        avg_signal = combined_slu['signal_strength'].mean()
        min_signal = combined_slu['signal_strength'].min()
        max_signal = combined_slu['signal_strength'].max()
        
        summary = f"""
        BUILDING-WIDE METRICS (SLU-users Network)
        ==========================================
        
        Total Measurements: {total_measurements:,}  |  Unique BSSIDs: {total_bssids}  |  Floors: {len(floors_data)}
        Average Signal: {avg_signal:.1f} dBm  |  Range: {min_signal:.0f} to {max_signal:.0f} dBm
        """
        ax1.text(0.5, 0.5, summary, fontsize=12, fontfamily='monospace', ha='center', va='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    ax2 = fig.add_subplot(gs[1, 0])
    if len(combined_slu) > 0:
        excellent = len(combined_slu[combined_slu['signal_strength'] > -50])
        good = len(combined_slu[(combined_slu['signal_strength'] <= -50) & (combined_slu['signal_strength'] > -65)])
        fair = len(combined_slu[(combined_slu['signal_strength'] <= -65) & (combined_slu['signal_strength'] > -80)])
        poor = len(combined_slu[combined_slu['signal_strength'] <= -80])
        
        sizes = [excellent, good, fair, poor]
        labels = [f'Excellent\n{excellent}\n({excellent/len(combined_slu)*100:.1f}%)',
                 f'Good\n{good}\n({good/len(combined_slu)*100:.1f}%)',
                 f'Fair\n{fair}\n({fair/len(combined_slu)*100:.1f}%)',
                 f'Poor\n{poor}\n({poor/len(combined_slu)*100:.1f}%)']
        colors_pie = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        
        ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='', startangle=90)
        ax2.set_title('Coverage Quality', fontweight='bold')
    
    ax3 = fig.add_subplot(gs[1, 1])
    floor_data = []
    for floor_name, df in floors_data.items():
        slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
        if len(slu) > 0:
            floor_data.append({
                'Floor': floor_name.replace('_', ' ').title(),
                'BSSIDs': slu['bssid'].nunique()
            })
    
    if floor_data:
        floor_df = pd.DataFrame(floor_data)
        bars = ax3.bar(floor_df['Floor'], floor_df['BSSIDs'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
        ax3.set_ylabel('Count', fontweight='bold')
        ax3.set_title('SLU-users BSSIDs by Floor', fontweight='bold')
        ax3.grid(True, axis='y', alpha=0.3)
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax4 = fig.add_subplot(gs[1, 2])
    if floor_data:
        floor_signal_data = []
        for floor_name, df in floors_data.items():
            slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
            if len(slu) > 0:
                floor_signal_data.append({
                    'Floor': floor_name.replace('_', ' ').title(),
                    'Avg Signal': slu['signal_strength'].mean()
                })
        
        if floor_signal_data:
            signal_df = pd.DataFrame(floor_signal_data)
            bars = ax4.barh(signal_df['Floor'], signal_df['Avg Signal'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
            ax4.set_xlabel('Average Signal (dBm)', fontweight='bold')
            ax4.set_title('Signal Strength by Floor', fontweight='bold')
            ax4.grid(True, axis='x', alpha=0.3)
            for bar, val in zip(bars, signal_df['Avg Signal']):
                ax4.text(val, bar.get_y() + bar.get_height()/2., f'{val:.1f}', va='center', fontweight='bold')
    
    ax5 = fig.add_subplot(gs[2, :])
    if len(combined_slu) > 0:
        ax5.hist(combined_slu['signal_strength'], bins=50, color='#3498db', alpha=0.7, edgecolor='black')
        ax5.axvline(combined_slu['signal_strength'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {combined_slu['signal_strength'].mean():.1f} dBm')
        ax5.axvline(-50, color='green', linestyle=':', linewidth=2, label='Excellent threshold')
        ax5.axvline(-65, color='orange', linestyle=':', linewidth=2, label='Good threshold')
        ax5.axvline(-80, color='red', linestyle=':', linewidth=2, label='Fair threshold')
        ax5.set_xlabel('Signal Strength (dBm)', fontweight='bold')
        ax5.set_ylabel('Frequency', fontweight='bold')
        ax5.set_title('Building-Wide Signal Distribution', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
    
    plt.savefig(output_path / '6_summary_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 6_summary_dashboard.png")
    plt.close()

def create_building_comparison(floors_data, output_dir):
    output_path = Path(output_dir)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Building-Wide Floor Comparison', fontsize=16, fontweight='bold')
    
    floor_analysis = []
    for floor_name, df in floors_data.items():
        slu = df[df['ssid'].str.contains('SLU-users', na=False, case=False)]
        if len(slu) > 0:
            locations = slu.groupby(['x_position', 'y_position'])
            
            handover_count = 0
            for (x, y), group in locations:
                strong_aps = group[group['signal_strength'] > -70]
                if len(strong_aps['bssid'].unique()) >= 2:
                    handover_count += 1
            
            handover_coverage = (handover_count / locations.ngroups * 100) if locations.ngroups > 0 else 0
            
            floor_analysis.append({
                'Floor': floor_name.replace('_', ' ').title(),
                'Avg Signal': slu['signal_strength'].mean(),
                'Locations': locations.ngroups,
                'Handover Coverage': handover_coverage,
                'BSSIDs': slu['bssid'].nunique()
            })
    
    analysis_df = pd.DataFrame(floor_analysis)
    
    ax = axes[0, 0]
    bars = ax.barh(analysis_df['Floor'], analysis_df['Avg Signal'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_xlabel('Average Signal (dBm)', fontweight='bold')
    ax.set_title('Average Signal Strength', fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    for bar, val in zip(bars, analysis_df['Avg Signal']):
        ax.text(val, bar.get_y() + bar.get_height()/2., f'{val:.1f}', va='center', fontweight='bold')
    
    ax = axes[0, 1]
    bars = ax.bar(analysis_df['Floor'], analysis_df['Locations'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Surveyed Locations', fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax = axes[1, 0]
    bars = ax.barh(analysis_df['Floor'], analysis_df['Handover Coverage'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_xlabel('Coverage (%)', fontweight='bold')
    ax.set_title('Handover Zone Coverage', fontweight='bold')
    ax.set_xlim([0, 105])
    ax.grid(True, axis='x', alpha=0.3)
    for bar, val in zip(bars, analysis_df['Handover Coverage']):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2., f'{val:.1f}%', va='center', fontweight='bold')
    
    ax = axes[1, 1]
    bars = ax.bar(analysis_df['Floor'], analysis_df['BSSIDs'], color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('Unique BSSIDs (SLU-users)', fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path / '7_building_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Created: 7_building_comparison.png")
    plt.close()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python create_visualizations.py <data_directory> [output_directory]")
        print("Example: python create_visualizations.py ./acrylic_data/ ./visualizations/")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './visualizations'
    
    print(f"\n{'='*60}")
    print("CREATING VISUALIZATIONS")
    print(f"{'='*60}\n")
    
    floors_data = load_floor_data(data_dir)
    
    if not floors_data:
        print("Error: No floor data found")
        sys.exit(1)
    
    print(f"Loaded data for {len(floors_data)} floors\n")
    
    create_signal_distribution(floors_data, output_dir)
    create_network_infrastructure(floors_data, output_dir)
    create_coverage_quality(floors_data, output_dir)
    create_survey_statistics(floors_data, output_dir)
    create_handover_scatter(floors_data, output_dir)
    create_summary_dashboard(floors_data, output_dir)
    create_building_comparison(floors_data, output_dir)
    
    print(f"\n{'='*60}")
    print(f"All visualizations saved to: {output_dir}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
