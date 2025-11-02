"""
Custom BAY States Visualizations - Starter Template
====================================================
Use this template to create your own visualizations!

Instructions:
1. Copy this file to your project directory
2. Modify the custom_plot functions below
3. Run: python custom_bay_visualizations.py
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import pandas as pd
from matplotlib.gridspec import GridSpec
import sys

# Import the main analyzer
# Make sure bay_states_visualizations.py is in the same directory
from bay_states_visualizations import BAYStatesAnalyzer

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class CustomBAYVisualizer:
    """
    Extended visualizer for custom BAY states plots
    Add your own visualization methods here!
    """
    
    def __init__(self, analyzer):
        """
        Initialize with an existing BAYStatesAnalyzer
        
        Args:
            analyzer: BAYStatesAnalyzer instance with generated data
        """
        self.analyzer = analyzer
        self.data = analyzer.data
        self.bay_states = analyzer.bay_states
        self.time = analyzer.time
        
    # ==========================================
    # TEMPLATE 1: Simple Bar Chart
    # ==========================================
    
    def plot_custom_bar_chart(self):
        """
        Template: Create a custom bar chart
        Modify this to create your own bar visualizations!
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Example: Average energy consumption by state
        energy_means = self.data.groupby('State')['Energy'].mean()
        energy_stds = self.data.groupby('State')['Energy'].std()
        
        states = ['B', 'A', 'Y']
        colors = [self.bay_states[s]['color'] for s in states]
        
        bars = ax.bar(states, energy_means, yerr=energy_stds, 
                     color=colors, alpha=0.7, capsize=10,
                     edgecolor='black', linewidth=2)
        
        ax.set_xlabel('State', fontweight='bold', fontsize=12)
        ax.set_ylabel('Mean Energy Consumption', fontweight='bold', fontsize=12)
        ax.set_title('Custom Bar Chart: Energy by State', 
                    fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, val in zip(bars, energy_means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/custom_01_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom bar chart created!")
    
    # ==========================================
    # TEMPLATE 2: Scatter Plot
    # ==========================================
    
    def plot_custom_scatter(self):
        """
        Template: Create a custom scatter plot
        Great for showing relationships between two variables
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Example: Activation vs Response Time
        for state in ['B', 'A', 'Y']:
            data_state = self.data[self.data['State'] == state]
            ax.scatter(data_state['Activation'], 
                      data_state['Response_Time'],
                      c=self.bay_states[state]['color'],
                      marker=self.bay_states[state]['marker'],
                      s=100, alpha=0.6, edgecolors='black', linewidth=0.5,
                      label=f"{state} - {self.bay_states[state]['name']}")
        
        ax.set_xlabel('Activation Level', fontweight='bold', fontsize=12)
        ax.set_ylabel('Response Time', fontweight='bold', fontsize=12)
        ax.set_title('Custom Scatter: Activation vs Response Time', 
                    fontweight='bold', fontsize=14)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/custom_02_scatter.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom scatter plot created!")
    
    # ==========================================
    # TEMPLATE 3: Heatmap
    # ==========================================
    
    def plot_custom_heatmap(self):
        """
        Template: Create a custom heatmap
        Useful for showing patterns in 2D data
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Example: Create a correlation-like matrix
        # You can replace this with your own data
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        # Calculate mean values for each state
        state_means = self.data.groupby('State')[features].mean()
        
        # Create heatmap
        sns.heatmap(state_means.T, annot=True, fmt='.2f', 
                   cmap='coolwarm', center=1.5,
                   xticklabels=['B', 'A', 'Y'],
                   yticklabels=[f.replace('_', ' ') for f in features],
                   ax=ax, cbar_kws={'label': 'Mean Value'})
        
        ax.set_title('Custom Heatmap: Feature Means by State', 
                    fontweight='bold', fontsize=14, pad=20)
        
        plt.tight_layout()
        plt.savefig('outputs/custom_03_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom heatmap created!")
    
    # ==========================================
    # TEMPLATE 4: Line Plot with Multiple Series
    # ==========================================
    
    def plot_custom_line_series(self):
        """
        Template: Create a line plot with multiple series
        Good for time series or sequential data
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Example: Plot cumulative sums of a feature
        for state in ['B', 'A', 'Y']:
            data_state = self.data[self.data['State'] == state]
            # Sort by some criterion (here by index)
            values = data_state['Activation'].sort_values().reset_index(drop=True)
            cumsum = values.cumsum()
            
            ax.plot(cumsum, label=f"{state} - {self.bay_states[state]['name']}", 
                   color=self.bay_states[state]['color'], linewidth=2.5)
        
        ax.set_xlabel('Sample Index', fontweight='bold', fontsize=12)
        ax.set_ylabel('Cumulative Activation', fontweight='bold', fontsize=12)
        ax.set_title('Custom Line Plot: Cumulative Activation', 
                    fontweight='bold', fontsize=14)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/custom_04_line_series.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom line series plot created!")
    
    # ==========================================
    # TEMPLATE 5: Multi-Panel Dashboard
    # ==========================================
    
    def plot_custom_dashboard(self):
        """
        Template: Create a custom multi-panel dashboard
        Combine multiple visualizations in one figure
        """
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Panel 1: Histogram
        ax1 = fig.add_subplot(gs[0, 0])
        for state in ['B', 'A', 'Y']:
            data_state = self.data[self.data['State'] == state]['Activation']
            ax1.hist(data_state, bins=30, alpha=0.5, 
                    color=self.bay_states[state]['color'], 
                    label=state)
        ax1.set_xlabel('Activation', fontweight='bold')
        ax1.set_ylabel('Frequency', fontweight='bold')
        ax1.set_title('Activation Distribution', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Box plot
        ax2 = fig.add_subplot(gs[0, 1])
        data_for_box = [self.data[self.data['State'] == s]['Response_Time'] 
                        for s in ['B', 'A', 'Y']]
        colors = [self.bay_states[s]['color'] for s in ['B', 'A', 'Y']]
        bp = ax2.boxplot(data_for_box, labels=['B', 'A', 'Y'], 
                        patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax2.set_ylabel('Response Time', fontweight='bold')
        ax2.set_title('Response Time by State', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Panel 3: Scatter
        ax3 = fig.add_subplot(gs[1, 0])
        for state in ['B', 'A', 'Y']:
            data_state = self.data[self.data['State'] == state]
            ax3.scatter(data_state['Energy'], data_state['Coherence'],
                       c=self.bay_states[state]['color'], 
                       alpha=0.5, s=50, label=state)
        ax3.set_xlabel('Energy', fontweight='bold')
        ax3.set_ylabel('Coherence', fontweight='bold')
        ax3.set_title('Energy vs Coherence', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Statistics table
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('tight')
        ax4.axis('off')
        
        stats_data = []
        for state in ['B', 'A', 'Y']:
            state_data = self.data[self.data['State'] == state]
            stats_data.append([
                state,
                f"{state_data['Activation'].mean():.2f}",
                f"{state_data['Response_Time'].mean():.2f}",
                f"{state_data['Energy'].mean():.2f}",
                len(state_data)
            ])
        
        table = ax4.table(cellText=stats_data,
                         colLabels=['State', 'Act.', 'Resp.', 'Enrg.', 'n'],
                         cellLoc='center', loc='center',
                         colWidths=[0.15, 0.2, 0.2, 0.2, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 3)
        ax4.set_title('Summary Statistics', fontweight='bold', pad=20)
        
        plt.suptitle('Custom Multi-Panel Dashboard', 
                    fontsize=16, fontweight='bold')
        
        plt.savefig('outputs/custom_05_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom dashboard created!")
    
    # ==========================================
    # TEMPLATE 6: Advanced Statistical Plot
    # ==========================================
    
    def plot_custom_advanced_stats(self):
        """
        Template: Create an advanced statistical visualization
        Example: Confidence intervals and hypothesis testing
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Panel 1: Confidence intervals
        ax1 = axes[0]
        feature = 'Activation'
        
        means = []
        cis = []
        states = ['B', 'A', 'Y']
        
        for state in states:
            data = self.data[self.data['State'] == state][feature]
            mean = data.mean()
            # 95% confidence interval
            ci = stats.t.interval(0.95, len(data)-1, 
                                 loc=mean, 
                                 scale=stats.sem(data))
            means.append(mean)
            cis.append((mean - ci[0], ci[1] - mean))
        
        colors = [self.bay_states[s]['color'] for s in states]
        ax1.errorbar(states, means, 
                    yerr=np.array(cis).T, 
                    fmt='o', markersize=10,
                    capsize=10, capthick=2, 
                    color='black', ecolor=colors,
                    linewidth=2)
        
        # Color the markers
        for i, (state, mean) in enumerate(zip(states, means)):
            ax1.scatter(i, mean, s=200, c=colors[i], 
                       edgecolor='black', linewidth=2, zorder=5)
        
        ax1.set_ylabel(f'{feature} (Mean ± 95% CI)', fontweight='bold')
        ax1.set_title('Confidence Intervals', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Panel 2: Effect sizes between groups
        ax2 = axes[1]
        
        # Calculate Cohen's d for all pairs
        pairs = [('B', 'A'), ('B', 'Y'), ('A', 'Y')]
        effect_sizes = []
        pair_labels = []
        
        for s1, s2 in pairs:
            d1 = self.data[self.data['State'] == s1][feature]
            d2 = self.data[self.data['State'] == s2][feature]
            
            # Cohen's d
            pooled_std = np.sqrt(((len(d1)-1)*d1.std()**2 + 
                                 (len(d2)-1)*d2.std()**2) / 
                                (len(d1) + len(d2) - 2))
            cohens_d = (d1.mean() - d2.mean()) / pooled_std
            
            effect_sizes.append(cohens_d)
            pair_labels.append(f'{s1} vs {s2}')
        
        bars = ax2.barh(pair_labels, effect_sizes, 
                       color=['steelblue', 'coral', 'forestgreen'],
                       alpha=0.7, edgecolor='black', linewidth=2)
        
        # Add reference lines
        ax2.axvline(0, color='black', linewidth=1)
        ax2.axvline(0.2, color='gray', linestyle='--', alpha=0.5, label='Small')
        ax2.axvline(0.5, color='gray', linestyle='--', alpha=0.7, label='Medium')
        ax2.axvline(0.8, color='gray', linestyle='--', alpha=0.9, label='Large')
        
        ax2.set_xlabel("Cohen's d (Effect Size)", fontweight='bold')
        ax2.set_title('Effect Sizes Between States', fontweight='bold')
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle(f'Advanced Statistics: {feature}', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        plt.savefig('outputs/custom_06_advanced_stats.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Custom advanced statistics plot created!")
    
    # ==========================================
    # YOUR CUSTOM PLOT HERE!
    # ==========================================
    
    def plot_your_custom_visualization(self):
        """
        ADD YOUR OWN VISUALIZATION HERE!
        
        Steps:
        1. Create figure and axes
        2. Access data via self.data or self.analyzer
        3. Create your plot
        4. Add labels, title, legend
        5. Save to outputs/custom_##_yourname.png
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # TODO: Add your visualization code here!
        # Example ideas:
        # - Pie chart of state proportions
        # - Radar chart of features
        # - Animated plot
        # - 3D surface plot
        # - Network graph
        # - Sankey diagram
        # - Ridge plot
        # - Violin plot variations
        
        ax.text(0.5, 0.5, 'Add Your Visualization Here!', 
               ha='center', va='center', fontsize=20, 
               transform=ax.transAxes)
        
        plt.tight_layout()
        plt.savefig('outputs/custom_99_your_plot.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Your custom plot created!")
    
    # ==========================================
    # Generate All Custom Plots
    # ==========================================
    
    def generate_all_custom_plots(self):
        """Generate all custom visualizations"""
        print("\n🎨 Generating Custom BAY States Visualizations")
        print("=" * 60)
        
        plots = [
            ("Bar Chart", self.plot_custom_bar_chart),
            ("Scatter Plot", self.plot_custom_scatter),
            ("Heatmap", self.plot_custom_heatmap),
            ("Line Series", self.plot_custom_line_series),
            ("Dashboard", self.plot_custom_dashboard),
            ("Advanced Stats", self.plot_custom_advanced_stats),
            ("Your Custom Plot", self.plot_your_custom_visualization),
        ]
        
        for i, (name, func) in enumerate(plots, 1):
            print(f"[{i}/{len(plots)}] Generating {name}...", end=" ")
            try:
                func()
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✨ Custom visualizations complete!")
        print("📁 Check the outputs/ folder for your new plots!")


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Custom BAY States Visualization System")
    print("="*60)
    
    # Step 1: Create the base analyzer
    print("\n📊 Step 1: Generating BAY states data...")
    analyzer = BAYStatesAnalyzer(n_samples=1000, random_state=42)
    print("✅ Data generated!")
    
    # Step 2: Create custom visualizer
    print("\n🎨 Step 2: Creating custom visualizer...")
    custom_viz = CustomBAYVisualizer(analyzer)
    print("✅ Visualizer ready!")
    
    # Step 3: Generate all custom plots
    print("\n📈 Step 3: Generating custom visualizations...")
    custom_viz.generate_all_custom_plots()
    
    print("\n" + "="*60)
    print("🎉 All done! Check the outputs/ folder!")
    print("="*60 + "\n")
