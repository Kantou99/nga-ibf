#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Multi-Hazard Impact Modeling for Nigeria IBF
Production-ready system with ML-enhanced vulnerability and sophisticated compounding effects

Features:
- Machine learning-enhanced vulnerability assessment
- Dynamic vulnerability based on context
- Sophisticated multi-hazard interaction modeling
- Real-time model updating
- Cascading effects modeling
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from scipy.stats import beta, gamma
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging

from climada.entity import ImpactFunc, ImpactFuncSet
from config import Config

logger = logging.getLogger('NigeriaIBF.MultiHazard')

# ============================================================================
# Data Classes for Context
# ============================================================================

@dataclass
class HazardContext:
    """Context information for hazard event"""
    state: str
    region: str
    month: int
    population_density: float
    poverty_rate: float
    previous_events_30d: int
    previous_events_90d: int
    distance_to_water_km: float
    elevation_m: float
    urban_rural: str  # 'urban', 'rural', 'peri-urban'
    infrastructure_quality: float  # 0-1 scale
    early_warning_coverage: float  # 0-1 scale
    

@dataclass
class CompoundingFactors:
    """Factors that modify displacement due to compounding effects"""
    has_recent_flood: bool = False
    has_recent_conflict: bool = False
    has_displacement_camp: bool = False
    is_rainy_season: bool = False
    is_harvest_season: bool = False
    market_access_disrupted: bool = False
    healthcare_access_limited: bool = False


# ============================================================================
# Advanced Vulnerability Models
# ============================================================================

class MLEnhancedVulnerability:
    """
    Machine learning-enhanced vulnerability assessment
    Uses trained models to predict context-specific vulnerability
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.flood_model = None
        self.conflict_model = None
        self.scaler = StandardScaler()
        self.trained = False
        
        # Load pre-trained models if available
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained vulnerability models"""
        try:
            flood_model_path = self.config.paths.models_dir / self.config.paths.flood_vulnerability_model
            conflict_model_path = self.config.paths.models_dir / self.config.paths.conflict_vulnerability_model
            
            if flood_model_path.exists():
                self.flood_model = joblib.load(flood_model_path)
                logger.info("Loaded pre-trained flood vulnerability model")
            
            if conflict_model_path.exists():
                self.conflict_model = joblib.load(conflict_model_path)
                logger.info("Loaded pre-trained conflict vulnerability model")
            
            self.trained = True
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
            self.trained = False
    
    def train(self, historical_data: pd.DataFrame, hazard_type: str):
        """
        Train vulnerability model on historical data
        
        Args:
            historical_data: DataFrame with columns: features + 'displacement_rate' target
            hazard_type: 'flood' or 'conflict'
        """
        logger.info(f"Training {hazard_type} vulnerability model...")
        
        # Prepare features
        feature_cols = [
            'population_density', 'poverty_rate', 'previous_events_30d',
            'distance_to_water_km', 'elevation_m', 'infrastructure_quality',
            'early_warning_coverage', 'month', 'urban_rural_code'
        ]
        
        X = historical_data[feature_cols].values
        y = historical_data['displacement_rate'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train ensemble model
        model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        
        model.fit(X_scaled, y)
        
        # Store model
        if hazard_type == 'flood':
            self.flood_model = model
        else:
            self.conflict_model = model
        
        # Calculate feature importance
        importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"Model trained. Top features:\n{importance.head()}")
        
        self.trained = True
        
        # Save model
        self._save_model(hazard_type)
    
    def _save_model(self, hazard_type: str):
        """Save trained model"""
        if hazard_type == 'flood':
            model_path = self.config.paths.models_dir / self.config.paths.flood_vulnerability_model
            joblib.dump(self.flood_model, model_path)
        else:
            model_path = self.config.paths.models_dir / self.config.paths.conflict_vulnerability_model
            joblib.dump(self.conflict_model, model_path)
        
        logger.info(f"Model saved to {model_path}")
    
    def predict_vulnerability(self, context: HazardContext, hazard_type: str) -> float:
        """
        Predict vulnerability parameter based on context
        
        Args:
            context: HazardContext with relevant information
            hazard_type: 'flood' or 'conflict'
        
        Returns:
            Predicted intensity_half parameter
        """
        if not self.trained:
            logger.warning("Models not trained, using regional defaults")
            return self._get_regional_default(context.region, hazard_type)
        
        # Prepare features
        urban_rural_map = {'urban': 0, 'peri-urban': 1, 'rural': 2}
        features = np.array([[
            context.population_density,
            context.poverty_rate,
            context.previous_events_30d,
            context.distance_to_water_km,
            context.elevation_m,
            context.infrastructure_quality,
            context.early_warning_coverage,
            context.month,
            urban_rural_map.get(context.urban_rural, 1)
        ]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        model = self.flood_model if hazard_type == 'flood' else self.conflict_model
        vulnerability = model.predict(features_scaled)[0]
        
        # Clip to reasonable range
        if hazard_type == 'flood':
            vulnerability = np.clip(vulnerability, 0.05, 2.0)
        else:
            vulnerability = np.clip(vulnerability, 5, 100)
        
        return vulnerability
    
    def _get_regional_default(self, region: str, hazard_type: str) -> float:
        """Get regional default vulnerability parameter"""
        if hazard_type == 'flood':
            params = self.config.vulnerability.flood_params.get(
                region, self.config.vulnerability.flood_params['North_Central']
            )
        else:
            params = self.config.vulnerability.conflict_params.get(
                region, self.config.vulnerability.conflict_params['North_Central']
            )
        
        return params['p50']  # Use median as default


# ============================================================================
# Advanced Impact Functions
# ============================================================================

class AdaptiveImpactFunction:
    """
    Adaptive impact function that adjusts based on context
    Incorporates multiple factors beyond simple intensity
    """
    
    def __init__(self, config: Config, hazard_type: str):
        self.config = config
        self.hazard_type = hazard_type
        self.base_functions = {}
        
    def create_contextual_impact_function(
        self,
        context: HazardContext,
        compounding: CompoundingFactors,
        intensity_half: float
    ) -> ImpactFuncSet:
        """
        Create impact function adjusted for context and compounding effects
        
        Args:
            context: Hazard context information
            compounding: Compounding factors
            intensity_half: Base vulnerability parameter
        
        Returns:
            Adjusted ImpactFuncSet
        """
        # Base impact function
        impf = ImpactFunc()
        impf.haz_type = 'FL' if self.hazard_type == 'flood' else 'CF'
        impf.id = 1
        
        # Adjust intensity_half based on context
        adjusted_half = self._adjust_for_context(intensity_half, context)
        adjusted_half = self._adjust_for_compounding(adjusted_half, compounding)
        
        # Define intensity range
        if self.hazard_type == 'flood':
            intensity = np.arange(0, 6, 0.05)  # 0-6m flood depth
            intensity_thresh = self.config.forecast.flood_depth_threshold_m
            impf.intensity_unit = 'm'
        else:
            intensity = np.arange(0, 250, 2)  # 0-250 fatalities
            intensity_thresh = self.config.forecast.conflict_fatality_threshold
            impf.intensity_unit = 'events'
        
        # Create more sophisticated impact curve
        mdd = self._create_impact_curve(
            intensity, intensity_thresh, adjusted_half, context
        )
        
        # Population affected area (varies by context)
        paa = self._create_paa_curve(intensity, context)
        
        impf.intensity = intensity
        impf.mdd = mdd
        impf.paa = paa
        impf.name = f'{self.hazard_type}_adaptive_{context.state}'
        
        impf_set = ImpactFuncSet()
        impf_set.append(impf)
        
        return impf_set
    
    def _adjust_for_context(self, intensity_half: float, context: HazardContext) -> float:
        """Adjust vulnerability based on contextual factors"""
        adjustment = 1.0
        
        # Infrastructure quality effect
        if context.infrastructure_quality < 0.3:
            adjustment *= 0.85  # Lower threshold (more vulnerable)
        elif context.infrastructure_quality > 0.7:
            adjustment *= 1.15  # Higher threshold (less vulnerable)
        
        # Early warning effect
        if context.early_warning_coverage > 0.7:
            adjustment *= 1.25  # Better prepared
        elif context.early_warning_coverage < 0.3:
            adjustment *= 0.9  # Less prepared
        
        # Urban/rural effect
        if context.urban_rural == 'urban':
            adjustment *= 1.1  # Urban areas slightly more resilient (better escape routes)
        elif context.urban_rural == 'rural':
            adjustment *= 0.95  # Rural areas more vulnerable (isolation)
        
        # Poverty effect
        if context.poverty_rate > 0.5:
            adjustment *= 0.85  # High poverty = more vulnerable
        
        return intensity_half * adjustment
    
    def _adjust_for_compounding(
        self, intensity_half: float, compounding: CompoundingFactors
    ) -> float:
        """Adjust for compounding/cascading effects"""
        adjustment = 1.0
        
        # Recent events reduce coping capacity
        if compounding.has_recent_flood:
            adjustment *= 0.8
        if compounding.has_recent_conflict:
            adjustment *= 0.75
        
        # Displacement camps indicate already vulnerable population
        if compounding.has_displacement_camp:
            adjustment *= 0.7
        
        # Seasonal effects
        if compounding.is_rainy_season and self.hazard_type == 'flood':
            adjustment *= 0.85
        if compounding.is_harvest_season:
            adjustment *= 1.1  # People less likely to leave during harvest
        
        # Service disruptions
        if compounding.market_access_disrupted:
            adjustment *= 0.9
        if compounding.healthcare_access_limited:
            adjustment *= 0.85
        
        return intensity_half * adjustment
    
    def _create_impact_curve(
        self,
        intensity: np.ndarray,
        threshold: float,
        intensity_half: float,
        context: HazardContext
    ) -> np.ndarray:
        """
        Create sophisticated impact curve with multiple regimes
        
        Different curve shapes based on hazard intensity and context
        """
        # Base sigmoid
        steepness = 5 if self.hazard_type == 'flood' else 3
        mdd = 1 / (1 + np.exp(-steepness * (intensity - intensity_half) / intensity_half))
        
        # Apply threshold
        mdd[intensity < threshold] = 0
        
        # Low intensity regime: gradual onset
        low_intensity_mask = (intensity >= threshold) & (intensity < intensity_half * 0.5)
        if np.any(low_intensity_mask):
            # Slower increase at low intensities
            low_vals = intensity[low_intensity_mask]
            mdd[low_intensity_mask] *= 0.5 + 0.5 * ((low_vals - threshold) / 
                                                     (intensity_half * 0.5 - threshold))
        
        # High intensity regime: saturation
        high_intensity_mask = intensity > intensity_half * 2
        if np.any(high_intensity_mask):
            # Asymptotic approach to 1.0 (never quite 100% displacement)
            mdd[high_intensity_mask] = 0.85 + 0.14 * (1 - np.exp(-(intensity[high_intensity_mask] - 
                                                                     intensity_half * 2) / intensity_half))
        
        # Context adjustments to curve shape
        if context.early_warning_coverage > 0.7:
            # Better warning = lower initial impact but similar eventual impact
            mdd = mdd * (0.85 + 0.15 * (intensity / intensity.max()))
        
        return np.clip(mdd, 0, 0.95)  # Max 95% displacement
    
    def _create_paa_curve(self, intensity: np.ndarray, context: HazardContext) -> np.ndarray:
        """
        Create percentage of affected area curve
        
        Not all areas equally affected - depends on spatial distribution
        """
        # Default: assume wide-area impact
        paa = np.ones_like(intensity)
        
        if self.hazard_type == 'flood':
            # Floods have more localized impacts at low intensity
            paa = 0.3 + 0.7 * (1 - np.exp(-intensity / 0.5))
        else:
            # Conflict can have very localized or wide-area impacts
            if context.population_density > 500:  # Urban
                paa = 0.5 + 0.5 * (1 - np.exp(-intensity / 20))
            else:  # Rural - more dispersed impact
                paa = 0.7 + 0.3 * (1 - np.exp(-intensity / 30))
        
        return np.clip(paa, 0.1, 1.0)


# ============================================================================
# Multi-Hazard Interaction Modeling
# ============================================================================

class MultiHazardInteraction:
    """
    Sophisticated modeling of flood-conflict interactions
    Handles cascading, compounding, and triggering effects
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.interaction_matrix = self._build_interaction_matrix()
    
    def _build_interaction_matrix(self) -> np.ndarray:
        """
        Build interaction matrix for hazard combinations
        
        Returns:
            2x2 matrix: [flood, conflict] x [flood, conflict]
            Values represent multiplicative interaction effects
        """
        # [flood-flood, flood-conflict]
        # [conflict-flood, conflict-conflict]
        return np.array([
            [1.0, 1.3],  # Flood worsened by conflict displacement
            [1.2, 1.0]   # Conflict worsened by flood resource scarcity
        ])
    
    def combine_hazards(
        self,
        flood_intensity: np.ndarray,
        conflict_intensity: np.ndarray,
        flood_impact: np.ndarray,
        conflict_impact: np.ndarray,
        context: HazardContext,
        method: str = 'sophisticated'
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Combine multiple hazards with interaction effects
        
        Args:
            flood_intensity: Flood hazard intensity
            conflict_intensity: Conflict hazard intensity
            flood_impact: Flood displacement impact
            conflict_impact: Conflict displacement impact
            context: Hazard context
            method: 'simple_max', 'weighted_sum', 'sophisticated'
        
        Returns:
            Combined impact and interaction metrics
        """
        if method == 'simple_max':
            combined = np.maximum(flood_impact, conflict_impact)
            metrics = {'method': 'max', 'interaction': 0}
            
        elif method == 'weighted_sum':
            # Weight by intensity
            flood_weight = flood_intensity / (flood_intensity + conflict_intensity + 1e-10)
            conflict_weight = 1 - flood_weight
            combined = flood_weight * flood_impact + conflict_weight * conflict_impact
            metrics = {'method': 'weighted', 'interaction': 0.1}
            
        else:  # sophisticated
            combined, metrics = self._sophisticated_combination(
                flood_intensity, conflict_intensity,
                flood_impact, conflict_impact,
                context
            )
        
        return combined, metrics
    
    def _sophisticated_combination(
        self,
        flood_intensity: np.ndarray,
        conflict_intensity: np.ndarray,
        flood_impact: np.ndarray,
        conflict_impact: np.ndarray,
        context: HazardContext
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Sophisticated combination accounting for:
        - Cascading effects (one hazard triggers another)
        - Compounding effects (simultaneous hazards worsen each other)
        - Temporal dynamics (sequence matters)
        """
        # Normalize intensities
        flood_norm = flood_intensity / (np.max(flood_intensity) + 1e-10)
        conflict_norm = conflict_intensity / (np.max(conflict_intensity) + 1e-10)
        
        # Base combination (weighted by intensity)
        base_combined = np.maximum(flood_impact, conflict_impact)
        
        # Compounding multiplier (when both hazards present)
        both_present = (flood_norm > 0.1) & (conflict_norm > 0.1)
        compounding_factor = 1.0
        
        if np.any(both_present):
            # Interaction strength depends on context
            interaction_base = self.config.vulnerability.flood_conflict_interaction
            
            # Adjust based on context
            if context.infrastructure_quality < 0.3:
                interaction_base *= 1.2  # Weaker infrastructure = stronger interaction
            if context.poverty_rate > 0.5:
                interaction_base *= 1.15  # Poverty amplifies compounding
            
            compounding_factor = 1 + (interaction_base - 1) * flood_norm * conflict_norm
        
        # Apply compounding
        combined = base_combined * compounding_factor
        
        # Cascading effects (flood can trigger conflict over resources)
        cascading_flood_to_conflict = 0
        if np.mean(flood_norm) > 0.5:  # Significant flood
            # Probability of conflict escalation
            cascade_prob = 0.15 * np.mean(flood_norm) * (1 - context.infrastructure_quality)
            cascading_flood_to_conflict = cascade_prob
            combined += cascade_prob * conflict_impact * 0.3
        
        # Cascading effects (conflict can damage flood infrastructure)
        cascading_conflict_to_flood = 0
        if np.mean(conflict_norm) > 0.5:  # Significant conflict
            # Increased flood vulnerability due to damaged infrastructure
            cascade_prob = 0.10 * np.mean(conflict_norm)
            cascading_conflict_to_flood = cascade_prob
            combined += cascade_prob * flood_impact * 0.2
        
        # Cap at realistic maximum (can't displace >95% of population)
        combined = np.clip(combined, 0, 0.95)
        
        # Calculate metrics
        metrics = {
            'method': 'sophisticated',
            'base_interaction': self.config.vulnerability.flood_conflict_interaction,
            'compounding_factor': float(np.mean(compounding_factor)),
            'cascade_flood_to_conflict': cascading_flood_to_conflict,
            'cascade_conflict_to_flood': cascading_conflict_to_flood,
            'max_displacement_rate': float(np.max(combined))
        }
        
        return combined, metrics


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    from config import create_config
    
    # Create config
    config = create_config('development')
    
    # Create ML-enhanced vulnerability model
    ml_vuln = MLEnhancedVulnerability(config)
    
    # Create context
    context = HazardContext(
        state='Benue',
        region='North_Central',
        month=9,  # September
        population_density=150,
        poverty_rate=0.45,
        previous_events_30d=2,
        previous_events_90d=5,
        distance_to_water_km=2.5,
        elevation_m=120,
        urban_rural='rural',
        infrastructure_quality=0.35,
        early_warning_coverage=0.55
    )
    
    # Predict vulnerability
    flood_vuln = ml_vuln.predict_vulnerability(context, 'flood')
    print(f"Predicted flood vulnerability: {flood_vuln:.2f}m")
    
    # Create adaptive impact function
    compounding = CompoundingFactors(
        is_rainy_season=True,
        has_recent_flood=True
    )
    
    adaptive_impf = AdaptiveImpactFunction(config, 'flood')
    impf_set = adaptive_impf.create_contextual_impact_function(
        context, compounding, flood_vuln
    )
    
    print(f"Created adaptive impact function for {context.state}")
