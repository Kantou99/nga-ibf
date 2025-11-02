"""
BAY States Comprehensive Visualization System
==============================================
Advanced technical analysis with 13 publication-quality visualizations
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, signal
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

class BAYStatesAnalyzer:
    """Comprehensive BAY states analysis and visualization system"""
    
    def __init__(self, n_samples=1000, random_state=42):
        self.n_samples = n_samples
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Define BAY states with enhanced characteristics
        self.bay_states = {
            'B': {'name': 'Baseline', 'color': '#2E86AB', 'marker': 'o'},
            'A': {'name': 'Activated', 'color': '#A23B72', 'marker': '^'},
            'Y': {'name': 'Yielding', 'color': '#F18F01', 'marker': 's'}
        }
        
        self.generate_bay_data()
    
    def generate_bay_data(self):
        """Generate realistic BAY states data with multiple features"""
        n_per_state = self.n_samples // 3
        
        # Feature 1: Primary activation level
        B_f1 = np.random.normal(0, 0.5, n_per_state)
        A_f1 = np.random.normal(3, 0.6, n_per_state)
        Y_f1 = np.random.normal(1.5, 0.7, n_per_state)
        
        # Feature 2: Response time
        B_f2 = np.random.normal(1, 0.3, n_per_state)
        A_f2 = np.random.normal(0.3, 0.2, n_per_state)
        Y_f2 = np.random.normal(2, 0.4, n_per_state)
        
        # Feature 3: Stability metric
        B_f3 = np.random.normal(2, 0.4, n_per_state)
        A_f3 = np.random.normal(0.5, 0.5, n_per_state)
        Y_f3 = np.random.normal(1.8, 0.3, n_per_state)
        
        # Feature 4: Energy consumption
        B_f4 = np.random.exponential(0.5, n_per_state)
        A_f4 = np.random.exponential(2.0, n_per_state)
        Y_f4 = np.random.exponential(1.2, n_per_state)
        
        # Feature 5: Temporal coherence
        B_f5 = np.random.beta(5, 2, n_per_state)
        A_f5 = np.random.beta(2, 5, n_per_state)
        Y_f5 = np.random.beta(3, 3, n_per_state)
        
        # Combine features
        self.data = pd.DataFrame({
            'State': ['B']*n_per_state + ['A']*n_per_state + ['Y']*n_per_state,
            'Activation': np.concatenate([B_f1, A_f1, Y_f1]),
            'Response_Time': np.concatenate([B_f2, A_f2, Y_f2]),
            'Stability': np.concatenate([B_f3, A_f3, Y_f3]),
            'Energy': np.concatenate([B_f4, A_f4, Y_f4]),
            'Coherence': np.concatenate([B_f5, A_f5, Y_f5])
        })
        
        # Generate time series data
        self.generate_time_series()
        
    def generate_time_series(self):
        """Generate temporal dynamics for each BAY state"""
        t = np.linspace(0, 10, 500)
        
        # Baseline: stable with low-frequency oscillations
        self.B_timeseries = 0.5 * np.sin(2*np.pi*0.5*t) + np.random.normal(0, 0.1, len(t))
        
        # Activated: high amplitude, high frequency
        self.A_timeseries = 2 * np.sin(2*np.pi*2*t) + np.random.normal(0, 0.3, len(t))
        
        # Yielding: decaying oscillations
        self.Y_timeseries = 1.5 * np.exp(-0.3*t) * np.sin(2*np.pi*1*t) + np.random.normal(0, 0.2, len(t))
        
        self.time = t
    
    def plot_1_state_space_3d(self):
        """1. 3D State Space Visualization"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        for state in ['B', 'A', 'Y']:
            data_state = self.data[self.data['State'] == state]
            ax.scatter(data_state['Activation'], 
                      data_state['Response_Time'], 
                      data_state['Stability'],
                      c=self.bay_states[state]['color'],
                      marker=self.bay_states[state]['marker'],
                      label=f"{state} - {self.bay_states[state]['name']}",
                      s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        ax.set_xlabel('Activation Level', fontweight='bold')
        ax.set_ylabel('Response Time', fontweight='bold')
        ax.set_zlabel('Stability Metric', fontweight='bold')
        ax.set_title('BAY States: 3D Feature Space', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/01_bay_3d_state_space.png', bbox_inches='tight')
        plt.close()
    
    def plot_2_temporal_dynamics(self):
        """2. Temporal Dynamics with Spectral Analysis"""
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(3, 2, figure=fig)
        
        # Time series plots
        ax1 = plt.subplot(gs[0, :])
        ax1.plot(self.time, self.B_timeseries, label='B - Baseline', 
                color=self.bay_states['B']['color'], linewidth=2)
        ax1.plot(self.time, self.A_timeseries, label='A - Activated', 
                color=self.bay_states['A']['color'], linewidth=2)
        ax1.plot(self.time, self.Y_timeseries, label='Y - Yielding', 
                color=self.bay_states['Y']['color'], linewidth=2)
        ax1.set_xlabel('Time (s)', fontweight='bold')
        ax1.set_ylabel('Signal Amplitude', fontweight='bold')
        ax1.set_title('BAY States: Temporal Dynamics', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Spectral analysis
        states_ts = [
            ('B', self.B_timeseries, self.bay_states['B']['color']),
            ('A', self.A_timeseries, self.bay_states['A']['color']),
            ('Y', self.Y_timeseries, self.bay_states['Y']['color'])
        ]
        
        for idx, (state, ts, color) in enumerate(states_ts):
            ax = plt.subplot(gs[1 + idx//2, idx%2])
            
            # Compute power spectral density
            freqs, psd = signal.welch(ts, fs=len(ts)/10, nperseg=128)
            ax.semilogy(freqs, psd, color=color, linewidth=2)
            ax.fill_between(freqs, psd, alpha=0.3, color=color)
            ax.set_xlabel('Frequency (Hz)', fontweight='bold')
            ax.set_ylabel('Power Spectral Density', fontweight='bold')
            ax.set_title(f'{state} - Spectral Analysis', fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Add dominant frequency annotation
            dom_freq = freqs[np.argmax(psd)]
            ax.axvline(dom_freq, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
            ax.text(dom_freq, max(psd)*0.7, f'Peak: {dom_freq:.2f} Hz', 
                   rotation=90, va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/02_bay_temporal_dynamics.png', bbox_inches='tight')
        plt.close()
    
    def plot_3_statistical_distributions(self):
        """3. Statistical Distributions with KDE"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        for idx, feature in enumerate(features):
            ax = axes[idx//3, idx%3]
            
            for state in ['B', 'A', 'Y']:
                data_state = self.data[self.data['State'] == state][feature]
                
                # Histogram
                ax.hist(data_state, bins=30, alpha=0.4, 
                       color=self.bay_states[state]['color'],
                       label=f'{state}', density=True)
                
                # KDE
                kde = stats.gaussian_kde(data_state)
                x_range = np.linspace(data_state.min(), data_state.max(), 100)
                ax.plot(x_range, kde(x_range), 
                       color=self.bay_states[state]['color'],
                       linewidth=2.5)
            
            ax.set_xlabel(feature.replace('_', ' '), fontweight='bold')
            ax.set_ylabel('Density', fontweight='bold')
            ax.set_title(f'{feature.replace("_", " ")} Distribution', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Remove extra subplot
        axes[1, 2].remove()
        
        plt.suptitle('BAY States: Statistical Distributions', 
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/03_bay_statistical_distributions.png', bbox_inches='tight')
        plt.close()
    
    def plot_4_correlation_heatmap(self):
        """4. Feature Correlation Analysis"""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        for idx, state in enumerate(['B', 'A', 'Y']):
            data_state = self.data[self.data['State'] == state][features]
            corr = data_state.corr()
            
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, vmin=-1, vmax=1,
                       square=True, ax=axes[idx], cbar_kws={'shrink': 0.8})
            axes[idx].set_title(f'{state} - {self.bay_states[state]["name"]}', 
                              fontweight='bold', fontsize=12)
        
        plt.suptitle('BAY States: Feature Correlation Matrices', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/04_bay_correlation_heatmap.png', bbox_inches='tight')
        plt.close()
    
    def plot_5_pca_analysis(self):
        """5. PCA Dimensionality Reduction"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Prepare data
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        X = self.data[features].values
        X_scaled = StandardScaler().fit_transform(X)
        
        # PCA
        pca = PCA()
        X_pca = pca.fit_transform(X_scaled)
        
        # Plot 1: PC1 vs PC2
        for state in ['B', 'A', 'Y']:
            mask = self.data['State'] == state
            axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1],
                          c=self.bay_states[state]['color'],
                          marker=self.bay_states[state]['marker'],
                          label=f'{state} - {self.bay_states[state]["name"]}',
                          s=60, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', 
                          fontweight='bold')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', 
                          fontweight='bold')
        axes[0].set_title('PCA: First Two Principal Components', fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Variance explained
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        axes[1].bar(range(1, len(cumsum)+1), pca.explained_variance_ratio_*100,
                   alpha=0.7, color='steelblue', edgecolor='black')
        axes[1].plot(range(1, len(cumsum)+1), cumsum*100, 'ro-', linewidth=2, 
                    markersize=8, label='Cumulative')
        axes[1].set_xlabel('Principal Component', fontweight='bold')
        axes[1].set_ylabel('Variance Explained (%)', fontweight='bold')
        axes[1].set_title('PCA: Explained Variance', fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(1, len(cumsum)+1))
        
        plt.suptitle('BAY States: Principal Component Analysis', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/05_bay_pca_analysis.png', bbox_inches='tight')
        plt.close()
    
    def plot_6_box_violin_plots(self):
        """6. Box and Violin Plots for Feature Comparison"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        for idx, feature in enumerate(features):
            ax = axes[idx//3, idx%3]
            
            # Violin plot
            parts = ax.violinplot([self.data[self.data['State'] == state][feature] 
                                   for state in ['B', 'A', 'Y']],
                                  positions=[1, 2, 3],
                                  showmeans=True, showextrema=True, showmedians=True)
            
            # Color violin plots
            for i, state in enumerate(['B', 'A', 'Y']):
                parts['bodies'][i].set_facecolor(self.bay_states[state]['color'])
                parts['bodies'][i].set_alpha(0.6)
            
            # Overlay box plot
            bp = ax.boxplot([self.data[self.data['State'] == state][feature] 
                            for state in ['B', 'A', 'Y']],
                           positions=[1, 2, 3],
                           widths=0.15, showfliers=False,
                           patch_artist=True,
                           boxprops=dict(facecolor='white', alpha=0.7))
            
            ax.set_xticks([1, 2, 3])
            ax.set_xticklabels(['B', 'A', 'Y'])
            ax.set_ylabel(feature.replace('_', ' '), fontweight='bold')
            ax.set_title(f'{feature.replace("_", " ")} by State', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        
        # Remove extra subplot
        axes[1, 2].remove()
        
        plt.suptitle('BAY States: Box and Violin Plots', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/06_bay_box_violin_plots.png', bbox_inches='tight')
        plt.close()
    
    def plot_7_transition_probabilities(self):
        """7. State Transition Probability Matrix"""
        # Simulate state transitions
        n_transitions = 500
        states = ['B', 'A', 'Y']
        transition_matrix = np.array([
            [0.7, 0.2, 0.1],  # From B
            [0.3, 0.5, 0.2],  # From A
            [0.4, 0.1, 0.5]   # From Y
        ])
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Transition matrix heatmap
        sns.heatmap(transition_matrix, annot=True, fmt='.2f', 
                   cmap='YlOrRd', vmin=0, vmax=1,
                   xticklabels=states, yticklabels=states,
                   ax=axes[0], cbar_kws={'label': 'Probability'})
        axes[0].set_xlabel('To State', fontweight='bold')
        axes[0].set_ylabel('From State', fontweight='bold')
        axes[0].set_title('State Transition Probability Matrix', fontweight='bold')
        
        # Plot 2: Transition diagram
        # Simulate a sequence
        current_state = 0  # Start at B
        sequence = [states[current_state]]
        for _ in range(n_transitions):
            current_state = np.random.choice(3, p=transition_matrix[current_state])
            sequence.append(states[current_state])
        
        # Count transitions
        from collections import Counter
        sequence_pairs = [f"{sequence[i]}→{sequence[i+1]}" 
                         for i in range(len(sequence)-1)]
        transition_counts = Counter(sequence_pairs)
        
        # Bar plot
        labels = list(transition_counts.keys())
        values = list(transition_counts.values())
        colors_map = {
            'B': self.bay_states['B']['color'],
            'A': self.bay_states['A']['color'],
            'Y': self.bay_states['Y']['color']
        }
        bar_colors = [colors_map[label[0]] for label in labels]
        
        axes[1].bar(range(len(labels)), values, color=bar_colors, 
                   alpha=0.7, edgecolor='black')
        axes[1].set_xticks(range(len(labels)))
        axes[1].set_xticklabels(labels, rotation=45, ha='right')
        axes[1].set_ylabel('Transition Count', fontweight='bold')
        axes[1].set_title(f'Observed Transitions (n={n_transitions})', fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('BAY States: Transition Analysis', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/07_bay_transition_probabilities.png', 
                   bbox_inches='tight')
        plt.close()
    
    def plot_8_distance_matrix(self):
        """8. State Distance/Similarity Analysis"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        # Calculate mean features for each state
        state_means = self.data.groupby('State')[features].mean()
        
        # Calculate pairwise distances
        distances = squareform(pdist(state_means.values, metric='euclidean'))
        
        # Plot 1: Distance matrix
        im = axes[0].imshow(distances, cmap='viridis', aspect='auto')
        axes[0].set_xticks([0, 1, 2])
        axes[0].set_yticks([0, 1, 2])
        axes[0].set_xticklabels(['B', 'A', 'Y'])
        axes[0].set_yticklabels(['B', 'A', 'Y'])
        
        # Annotate distances
        for i in range(3):
            for j in range(3):
                text = axes[0].text(j, i, f'{distances[i, j]:.2f}',
                                  ha="center", va="center", color="white", 
                                  fontweight='bold')
        
        axes[0].set_title('Euclidean Distance Matrix', fontweight='bold')
        plt.colorbar(im, ax=axes[0], label='Distance')
        
        # Plot 2: Similarity dendrogram
        from scipy.cluster.hierarchy import dendrogram, linkage
        
        Z = linkage(state_means.values, method='ward')
        dendrogram(Z, labels=['B', 'A', 'Y'], ax=axes[1],
                  color_threshold=0, above_threshold_color='black')
        axes[1].set_ylabel('Distance', fontweight='bold')
        axes[1].set_title('Hierarchical Clustering', fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('BAY States: Distance and Similarity Analysis', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/08_bay_distance_matrix.png', bbox_inches='tight')
        plt.close()
    
    def plot_9_anova_statistical_tests(self):
        """9. Statistical Validation: ANOVA and Post-hoc Tests"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        results = []
        
        for idx, feature in enumerate(features):
            ax = axes[idx//3, idx%3]
            
            # Get data for each state
            B_data = self.data[self.data['State'] == 'B'][feature]
            A_data = self.data[self.data['State'] == 'A'][feature]
            Y_data = self.data[self.data['State'] == 'Y'][feature]
            
            # One-way ANOVA
            f_stat, p_value = stats.f_oneway(B_data, A_data, Y_data)
            
            # Plot means with error bars
            means = [B_data.mean(), A_data.mean(), Y_data.mean()]
            sems = [B_data.sem(), A_data.sem(), Y_data.sem()]
            colors = [self.bay_states[s]['color'] for s in ['B', 'A', 'Y']]
            
            bars = ax.bar(['B', 'A', 'Y'], means, yerr=sems, 
                         color=colors, alpha=0.7, capsize=10,
                         edgecolor='black', linewidth=1.5)
            
            # Add individual points
            for i, state in enumerate(['B', 'A', 'Y']):
                data = self.data[self.data['State'] == state][feature]
                x = np.random.normal(i, 0.04, size=len(data))
                ax.scatter(x, data, alpha=0.3, s=10, color='black')
            
            # Add significance markers
            if p_value < 0.001:
                sig_text = '***'
            elif p_value < 0.01:
                sig_text = '**'
            elif p_value < 0.05:
                sig_text = '*'
            else:
                sig_text = 'ns'
            
            ax.text(0.5, 0.95, f'F={f_stat:.2f}, p={p_value:.4f} {sig_text}',
                   transform=ax.transAxes, ha='center', va='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=8)
            
            ax.set_ylabel(feature.replace('_', ' '), fontweight='bold')
            ax.set_title(f'{feature.replace("_", " ")}', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            results.append({
                'Feature': feature,
                'F-statistic': f_stat,
                'p-value': p_value
            })
        
        # Remove extra subplot and add results table
        axes[1, 2].axis('tight')
        axes[1, 2].axis('off')
        
        results_df = pd.DataFrame(results)
        table = axes[1, 2].table(cellText=results_df.values,
                              colLabels=results_df.columns,
                              cellLoc='center',
                              loc='center',
                              colWidths=[0.4, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        plt.suptitle('BAY States: One-Way ANOVA Results\n*** p<0.001, ** p<0.01, * p<0.05', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/09_bay_anova_tests.png', bbox_inches='tight')
        plt.close()
    
    def plot_10_phase_space_trajectory(self):
        """10. Phase Space Trajectories"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Generate phase space data (velocity vs position)
        dt = self.time[1] - self.time[0]
        
        states_data = [
            ('B', self.B_timeseries, self.bay_states['B']['color']),
            ('A', self.A_timeseries, self.bay_states['A']['color']),
            ('Y', self.Y_timeseries, self.bay_states['Y']['color'])
        ]
        
        for idx, (state, ts, color) in enumerate(states_data):
            position = ts
            velocity = np.gradient(ts, dt)
            
            # Phase portrait
            axes[idx].plot(position, velocity, color=color, linewidth=1.5, alpha=0.7)
            axes[idx].scatter(position[0], velocity[0], s=100, color='green', 
                            marker='o', edgecolor='black', linewidth=2, 
                            label='Start', zorder=5)
            axes[idx].scatter(position[-1], velocity[-1], s=100, color='red', 
                            marker='s', edgecolor='black', linewidth=2, 
                            label='End', zorder=5)
            
            axes[idx].set_xlabel('Position', fontweight='bold')
            axes[idx].set_ylabel('Velocity', fontweight='bold')
            axes[idx].set_title(f'{state} - Phase Portrait', fontweight='bold')
            axes[idx].legend(loc='best')
            axes[idx].grid(True, alpha=0.3)
            
            # Add arrows to show direction
            n_arrows = 10
            arrow_indices = np.linspace(0, len(position)-10, n_arrows, dtype=int)
            for i in arrow_indices:
                axes[idx].annotate('', xy=(position[i+5], velocity[i+5]),
                                 xytext=(position[i], velocity[i]),
                                 arrowprops=dict(arrowstyle='->', color=color, 
                                               lw=1.5, alpha=0.6))
        
        plt.suptitle('BAY States: Phase Space Trajectories', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/10_bay_phase_space.png', bbox_inches='tight')
        plt.close()
    
    def plot_11_effect_size_analysis(self):
        """11. Effect Size Analysis (Cohen's d)"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        comparisons = [('B', 'A'), ('B', 'Y'), ('A', 'Y')]
        
        # Calculate Cohen's d for all comparisons
        effect_sizes = []
        
        for feature in features:
            for comp in comparisons:
                state1, state2 = comp
                data1 = self.data[self.data['State'] == state1][feature]
                data2 = self.data[self.data['State'] == state2][feature]
                
                # Cohen's d
                pooled_std = np.sqrt(((len(data1)-1)*data1.std()**2 + 
                                     (len(data2)-1)*data2.std()**2) / 
                                    (len(data1) + len(data2) - 2))
                cohens_d = (data1.mean() - data2.mean()) / pooled_std
                
                effect_sizes.append({
                    'Feature': feature,
                    'Comparison': f'{state1} vs {state2}',
                    'Effect Size': cohens_d
                })
        
        # Create dataframe and pivot for heatmap
        df = pd.DataFrame(effect_sizes)
        pivot_df = df.pivot(index='Feature', columns='Comparison', values='Effect Size')
        
        # Plot heatmap
        sns.heatmap(pivot_df, annot=True, fmt='.2f', cmap='RdBu_r', 
                   center=0, vmin=-3, vmax=3, ax=ax, 
                   cbar_kws={'label': "Cohen's d"})
        
        ax.set_title("BAY States: Effect Size Analysis (Cohen's d)\n" +
                    "Small: 0.2 | Medium: 0.5 | Large: 0.8",
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('State Comparison', fontweight='bold')
        ax.set_ylabel('Feature', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/11_bay_effect_size.png', bbox_inches='tight')
        plt.close()
    
    def plot_12_cumulative_distributions(self):
        """12. Empirical Cumulative Distribution Functions"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        for idx, feature in enumerate(features):
            ax = axes[idx//3, idx%3]
            
            for state in ['B', 'A', 'Y']:
                data_state = self.data[self.data['State'] == state][feature]
                sorted_data = np.sort(data_state)
                y = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
                
                ax.plot(sorted_data, y, linewidth=2.5,
                       color=self.bay_states[state]['color'],
                       label=f'{state} - {self.bay_states[state]["name"]}')
                
                # Add median line
                median = np.median(data_state)
                ax.axvline(median, color=self.bay_states[state]['color'], 
                          linestyle='--', alpha=0.5, linewidth=1.5)
            
            # Perform Kolmogorov-Smirnov tests
            B_data = self.data[self.data['State'] == 'B'][feature]
            A_data = self.data[self.data['State'] == 'A'][feature]
            Y_data = self.data[self.data['State'] == 'Y'][feature]
            
            ks_BA = stats.ks_2samp(B_data, A_data)
            ks_BY = stats.ks_2samp(B_data, Y_data)
            ks_AY = stats.ks_2samp(A_data, Y_data)
            
            ax.set_xlabel(feature.replace('_', ' '), fontweight='bold')
            ax.set_ylabel('Cumulative Probability', fontweight='bold')
            ax.set_title(f'{feature.replace("_", " ")} - ECDF', fontweight='bold')
            ax.legend(loc='best', fontsize=8)
            ax.grid(True, alpha=0.3)
            
            # Add KS test results
            ks_text = f'KS: B-A p={ks_BA.pvalue:.3f}\n' + \
                     f'B-Y p={ks_BY.pvalue:.3f}\n' + \
                     f'A-Y p={ks_AY.pvalue:.3f}'
            ax.text(0.02, 0.98, ks_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=7,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Remove extra subplot
        axes[1, 2].remove()
        
        plt.suptitle('BAY States: Empirical Cumulative Distribution Functions', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('/mnt/user-data/outputs/12_bay_cumulative_distributions.png', 
                   bbox_inches='tight')
        plt.close()
    
    def plot_13_summary_dashboard(self):
        """13. Executive Summary Dashboard"""
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. State counts
        ax1 = fig.add_subplot(gs[0, 0])
        state_counts = self.data['State'].value_counts()
        colors = [self.bay_states[s]['color'] for s in state_counts.index]
        ax1.pie(state_counts, labels=state_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=90, textprops={'fontweight': 'bold'})
        ax1.set_title('State Distribution', fontweight='bold')
        
        # 2. Mean comparison radar chart
        ax2 = fig.add_subplot(gs[0, 1], projection='polar')
        features = ['Activation', 'Response_Time', 'Stability', 'Energy', 'Coherence']
        
        # Normalize data for radar
        feature_data = self.data.groupby('State')[features].mean()
        normalized = (feature_data - feature_data.min()) / (feature_data.max() - feature_data.min())
        
        angles = np.linspace(0, 2*np.pi, len(features), endpoint=False).tolist()
        angles += angles[:1]
        
        for state in ['B', 'A', 'Y']:
            values = normalized.loc[state].tolist()
            values += values[:1]
            ax2.plot(angles, values, 'o-', linewidth=2, 
                    color=self.bay_states[state]['color'], 
                    label=state)
            ax2.fill(angles, values, alpha=0.15, 
                    color=self.bay_states[state]['color'])
        
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels([f.replace('_', '\n') for f in features], fontsize=8)
        ax2.set_ylim(0, 1)
        ax2.set_title('Feature Profile', fontweight='bold', pad=20)
        ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax2.grid(True)
        
        # 3. Key statistics table
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.axis('tight')
        ax3.axis('off')
        
        stats_data = []
        for state in ['B', 'A', 'Y']:
            state_data = self.data[self.data['State'] == state]
            stats_data.append([
                state,
                f"{state_data['Activation'].mean():.2f}",
                f"{state_data['Response_Time'].mean():.2f}",
                f"{state_data['Stability'].mean():.2f}"
            ])
        
        table = ax3.table(cellText=stats_data,
                         colLabels=['State', 'Act.', 'Resp.', 'Stab.'],
                         cellLoc='center', loc='center',
                         colWidths=[0.2, 0.27, 0.27, 0.27])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        ax3.set_title('Mean Values', fontweight='bold', pad=10)
        
        # 4. PCA scatter
        ax4 = fig.add_subplot(gs[1, :2])
        X = self.data[features].values
        X_scaled = StandardScaler().fit_transform(X)
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        for state in ['B', 'A', 'Y']:
            mask = self.data['State'] == state
            ax4.scatter(X_pca[mask, 0], X_pca[mask, 1],
                       c=self.bay_states[state]['color'],
                       marker=self.bay_states[state]['marker'],
                       label=state, s=40, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        ax4.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', 
                      fontweight='bold')
        ax4.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', 
                      fontweight='bold')
        ax4.set_title('Principal Component Analysis', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Time series comparison
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.plot(self.time[:100], self.B_timeseries[:100], 
                color=self.bay_states['B']['color'], label='B', linewidth=2)
        ax5.plot(self.time[:100], self.A_timeseries[:100], 
                color=self.bay_states['A']['color'], label='A', linewidth=2)
        ax5.plot(self.time[:100], self.Y_timeseries[:100], 
                color=self.bay_states['Y']['color'], label='Y', linewidth=2)
        ax5.set_xlabel('Time (s)', fontweight='bold')
        ax5.set_ylabel('Signal', fontweight='bold')
        ax5.set_title('Temporal Dynamics', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6-8. Feature distributions
        feature_subset = ['Activation', 'Response_Time', 'Stability']
        for i, feature in enumerate(feature_subset):
            ax = fig.add_subplot(gs[2, i])
            
            for state in ['B', 'A', 'Y']:
                data_state = self.data[self.data['State'] == state][feature]
                ax.hist(data_state, bins=20, alpha=0.5, 
                       color=self.bay_states[state]['color'], label=state)
            
            ax.set_xlabel(feature.replace('_', ' '), fontweight='bold', fontsize=9)
            ax.set_ylabel('Count', fontweight='bold', fontsize=9)
            ax.set_title(feature.replace('_', ' '), fontweight='bold', fontsize=10)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('BAY States: Executive Summary Dashboard', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.savefig('/mnt/user-data/outputs/13_bay_summary_dashboard.png', 
                   bbox_inches='tight')
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("🎨 BAY States Visualization System")
        print("=" * 60)
        
        plots = [
            ("3D State Space", self.plot_1_state_space_3d),
            ("Temporal Dynamics", self.plot_2_temporal_dynamics),
            ("Statistical Distributions", self.plot_3_statistical_distributions),
            ("Correlation Heatmap", self.plot_4_correlation_heatmap),
            ("PCA Analysis", self.plot_5_pca_analysis),
            ("Box & Violin Plots", self.plot_6_box_violin_plots),
            ("Transition Probabilities", self.plot_7_transition_probabilities),
            ("Distance Matrix", self.plot_8_distance_matrix),
            ("ANOVA Tests", self.plot_9_anova_statistical_tests),
            ("Phase Space", self.plot_10_phase_space_trajectory),
            ("Effect Size", self.plot_11_effect_size_analysis),
            ("Cumulative Distributions", self.plot_12_cumulative_distributions),
            ("Summary Dashboard", self.plot_13_summary_dashboard)
        ]
        
        for i, (name, func) in enumerate(plots, 1):
            print(f"[{i:2d}/13] Generating {name}...", end=" ")
            func()
            print("✅")
        
        print("\n" + "=" * 60)
        print("✨ All 13 visualizations generated successfully!")
        print(f"📊 Total samples analyzed: {self.n_samples}")
        print(f"🎯 BAY states: B (Baseline), A (Activated), Y (Yielding)")
        print("=" * 60)


if __name__ == "__main__":
    analyzer = BAYStatesAnalyzer(n_samples=1000, random_state=42)
    analyzer.generate_all_visualizations()
