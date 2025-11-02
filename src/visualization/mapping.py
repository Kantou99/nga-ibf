"""
Mapping Module
Creates maps and spatial visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MapVisualizer:
    """Create maps and spatial visualizations"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
        
        # Color schemes for different indicators
        self.color_schemes = {
            'risk': ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c'],  # Green to Red
            'impact': ['#3498db', '#9b59b6', '#e74c3c', '#c0392b'],  # Blue to Dark Red
            'alert': {
                'Green': '#2ecc71',
                'Yellow': '#f1c40f',
                'Orange': '#e67e22',
                'Red': '#e74c3c'
            }
        }
    
    def create_risk_map(self, lga_data: pd.DataFrame,
                       risk_column: str = 'flood_risk_score',
                       title: str = 'Multi-Hazard Risk Map',
                       output_file: Optional[str] = None):
        """
        Create choropleth map of risk levels
        
        Args:
            lga_data: GeoDataFrame or DataFrame with LGA data
            risk_column: Column containing risk scores
            title: Map title
            output_file: Path to save figure
        """
        logger.info(f"Creating risk map for {len(lga_data)} LGAs...")
        
        try:
            import geopandas as gpd
            
            if not isinstance(lga_data, gpd.GeoDataFrame):
                logger.warning("Data is not a GeoDataFrame, cannot create map without geometry")
                return self._create_risk_chart(lga_data, risk_column, title, output_file)
            
            fig, ax = plt.subplots(1, 1, figsize=(12, 10))
            
            # Create map
            lga_data.plot(
                column=risk_column,
                ax=ax,
                legend=True,
                cmap='YlOrRd',
                edgecolor='black',
                linewidth=0.5,
                legend_kwds={'label': 'Risk Score', 'orientation': 'vertical'}
            )
            
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # Add north arrow and scale (simplified)
            ax.text(0.05, 0.95, 'N ?', transform=ax.transAxes, fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                logger.info(f"Map saved to {output_file}")
            else:
                plt.show()
            
            self.fig = fig
            self.ax = ax
            
        except ImportError:
            logger.warning("GeoPandas not available, creating alternative visualization")
            return self._create_risk_chart(lga_data, risk_column, title, output_file)
    
    def _create_risk_chart(self, lga_data: pd.DataFrame,
                          risk_column: str,
                          title: str,
                          output_file: Optional[str] = None):
        """Create bar chart alternative to map"""
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by risk score
        data = lga_data.copy()
        
        if risk_column not in data.columns:
            logger.error(f"Column {risk_column} not found")
            return
        
        data = data.sort_values(risk_column, ascending=True).tail(20)  # Top 20
        
        # Create color based on risk level
        colors = []
        for score in data[risk_column]:
            if score >= 0.75:
                colors.append(self.color_schemes['risk'][3])
            elif score >= 0.5:
                colors.append(self.color_schemes['risk'][2])
            elif score >= 0.25:
                colors.append(self.color_schemes['risk'][1])
            else:
                colors.append(self.color_schemes['risk'][0])
        
        lga_col = 'lga' if 'lga' in data.columns else data.columns[0]
        
        ax.barh(data[lga_col], data[risk_column], color=colors)
        ax.set_xlabel('Risk Score', fontsize=12)
        ax.set_ylabel('LGA', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved to {output_file}")
        else:
            plt.show()
    
    def create_impact_dashboard(self, impact_data: pd.DataFrame,
                              output_file: Optional[str] = None):
        """
        Create dashboard with multiple impact visualizations
        
        Args:
            impact_data: DataFrame with impact forecasts
            output_file: Path to save figure
        """
        logger.info("Creating impact dashboard...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Multi-Hazard Impact-Based Forecast Dashboard', fontsize=16, fontweight='bold')
        
        # 1. People at Risk by LGA (top 10)
        if 'people_at_risk' in impact_data.columns:
            top_lgas = impact_data.nlargest(10, 'people_at_risk')
            lga_col = 'lga' if 'lga' in top_lgas.columns else top_lgas.columns[0]
            
            axes[0, 0].barh(top_lgas[lga_col], top_lgas['people_at_risk'], color='#e74c3c')
            axes[0, 0].set_xlabel('People at Risk')
            axes[0, 0].set_title('Top 10 LGAs by People at Risk')
            axes[0, 0].grid(axis='x', alpha=0.3)
        
        # 2. Impact Level Distribution
        if 'impact_level' in impact_data.columns:
            impact_counts = impact_data['impact_level'].value_counts()
            colors = [self.color_schemes['risk'][i] for i in range(len(impact_counts))]
            
            axes[0, 1].pie(impact_counts.values, labels=impact_counts.index,
                          autopct='%1.1f%%', colors=colors, startangle=90)
            axes[0, 1].set_title('Impact Level Distribution')
        
        # 3. Hazard Probability Distribution
        prob_cols = [col for col in impact_data.columns if 'probability' in col.lower()]
        if prob_cols:
            prob_data = impact_data[prob_cols[0]].dropna()
            axes[1, 0].hist(prob_data, bins=20, color='#3498db', edgecolor='black', alpha=0.7)
            axes[1, 0].set_xlabel('Probability')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].set_title('Hazard Probability Distribution')
            axes[1, 0].grid(alpha=0.3)
        
        # 4. Priority Level Summary
        if 'priority_level' in impact_data.columns:
            priority_counts = impact_data['priority_level'].value_counts()
            
            axes[1, 1].bar(range(len(priority_counts)), priority_counts.values,
                          color=self.color_schemes['impact'])
            axes[1, 1].set_xticks(range(len(priority_counts)))
            axes[1, 1].set_xticklabels(priority_counts.index, rotation=45)
            axes[1, 1].set_ylabel('Number of LGAs')
            axes[1, 1].set_title('Priority Level Distribution')
            axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Dashboard saved to {output_file}")
        else:
            plt.show()
    
    def create_time_series_plot(self, time_series_data: pd.DataFrame,
                               date_col: str = 'date',
                               value_col: str = 'individuals_displaced',
                               title: str = 'Displacement Trends Over Time',
                               output_file: Optional[str] = None):
        """
        Create time series visualization
        
        Args:
            time_series_data: DataFrame with time series data
            date_col: Date column name
            value_col: Value column name
            title: Plot title
            output_file: Path to save figure
        """
        logger.info("Creating time series plot...")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        df = time_series_data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        
        ax.plot(df[date_col], df[value_col], linewidth=2, color='#3498db', marker='o', markersize=4)
        ax.fill_between(df[date_col], df[value_col], alpha=0.3, color='#3498db')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(value_col.replace('_', ' ').title(), fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {output_file}")
        else:
            plt.show()
    
    def create_alert_map(self, forecast_data: pd.DataFrame,
                        alert_column: str = 'alert_level',
                        title: str = 'Multi-Hazard Alert Map',
                        output_file: Optional[str] = None):
        """
        Create map with color-coded alerts
        
        Args:
            forecast_data: DataFrame with forecast and alert data
            alert_column: Column with alert levels
            title: Map title
            output_file: Path to save figure
        """
        logger.info("Creating alert map...")
        
        # Create color mapping
        if alert_column not in forecast_data.columns:
            logger.error(f"Column {alert_column} not found")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by alert level
        alert_order = ['Green', 'Yellow', 'Orange', 'Red']
        data = forecast_data.copy()
        
        # Get unique alerts in order
        alerts = [a for a in alert_order if a in data[alert_column].values]
        
        for alert in alerts:
            alert_data = data[data[alert_column] == alert]
            color = self.color_schemes['alert'].get(alert, '#95a5a6')
            
            lga_col = 'lga' if 'lga' in alert_data.columns else alert_data.columns[0]
            ax.barh(alert_data[lga_col], [1] * len(alert_data),
                   color=color, label=alert, alpha=0.8)
        
        ax.set_xlabel('Alert Status')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(title='Alert Level')
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Alert map saved to {output_file}")
        else:
            plt.show()


if __name__ == "__main__":
    # Example usage
    visualizer = MapVisualizer()
    print("Map visualizer ready")
