#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for Nigeria IBF System
Production-ready testing with unit, integration, and system tests
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from config import Config, create_config
from advanced_multi_hazard import (
    MLEnhancedVulnerability, AdaptiveImpactFunction,
    MultiHazardInteraction, HazardContext, CompoundingFactors
)
from production_forecast_engine import (
    ProductionForecastEngine, QualityController, AlertManager
)

# ============================================================================
# Unit Tests
# ============================================================================

class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.config = create_config('development')
    
    def test_config_creation(self):
        """Test configuration object creation"""
        self.assertIsInstance(self.config, Config)
        self.assertEqual(self.config.environment, 'development')
    
    def test_config_validation(self):
        """Test configuration validation"""
        self.assertTrue(self.config.validate())
    
    def test_environment_specific_settings(self):
        """Test environment-specific configurations"""
        dev_config = create_config('development')
        prod_config = create_config('production')
        
        # Development should have fewer samples
        self.assertLess(
            dev_config.uncertainty.n_samples,
            prod_config.uncertainty.n_samples
        )
    
    def test_config_serialization(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / 'test_config.yaml'
            self.config.save_to_file(str(config_file))
            self.assertTrue(config_file.exists())


class TestVulnerabilityModels(unittest.TestCase):
    """Test vulnerability assessment"""
    
    def setUp(self):
        self.config = create_config('development')
        self.ml_vuln = MLEnhancedVulnerability(self.config)
        self.context = HazardContext(
            state='Benue',
            region='North_Central',
            month=9,
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
    
    def test_vulnerability_prediction(self):
        """Test vulnerability parameter prediction"""
        flood_vuln = self.ml_vuln.predict_vulnerability(self.context, 'flood')
        conflict_vuln = self.ml_vuln.predict_vulnerability(self.context, 'conflict')
        
        # Check reasonable ranges
        self.assertGreater(flood_vuln, 0.05)
        self.assertLess(flood_vuln, 2.0)
        self.assertGreater(conflict_vuln, 5)
        self.assertLess(conflict_vuln, 100)
    
    def test_regional_defaults(self):
        """Test regional default parameters"""
        for region in ['North_West', 'North_East', 'North_Central',
                      'South_West', 'South_East', 'South_South']:
            context = HazardContext(
                state='Test',
                region=region,
                month=1,
                population_density=100,
                poverty_rate=0.4,
                previous_events_30d=0,
                previous_events_90d=0,
                distance_to_water_km=5,
                elevation_m=100,
                urban_rural='rural',
                infrastructure_quality=0.5,
                early_warning_coverage=0.5
            )
            
            flood_vuln = self.ml_vuln.predict_vulnerability(context, 'flood')
            self.assertIsNotNone(flood_vuln)


class TestImpactFunctions(unittest.TestCase):
    """Test impact function creation and behavior"""
    
    def setUp(self):
        self.config = create_config('development')
        self.context = HazardContext(
            state='Lagos',
            region='South_West',
            month=7,
            population_density=500,
            poverty_rate=0.3,
            previous_events_30d=0,
            previous_events_90d=1,
            distance_to_water_km=1.0,
            elevation_m=50,
            urban_rural='urban',
            infrastructure_quality=0.65,
            early_warning_coverage=0.75
        )
        self.compounding = CompoundingFactors(
            is_rainy_season=True,
            has_recent_flood=False
        )
    
    def test_flood_impact_function(self):
        """Test flood impact function creation"""
        adaptive_impf = AdaptiveImpactFunction(self.config, 'flood')
        impf_set = adaptive_impf.create_contextual_impact_function(
            self.context, self.compounding, intensity_half=1.5
        )
        
        self.assertEqual(len(impf_set.get_func()), 1)
        impf = impf_set.get_func()[0]
        
        # Check function properties
        self.assertEqual(impf.haz_type, 'FL')
        self.assertEqual(impf.intensity_unit, 'm')
        self.assertGreater(len(impf.intensity), 0)
        
        # Check impact curve behavior
        # At threshold, impact should be near zero
        idx_thresh = np.argmin(np.abs(impf.intensity - 0.3))
        self.assertLess(impf.mdd[idx_thresh], 0.1)
        
        # At high intensity, impact should be high
        idx_high = np.argmin(np.abs(impf.intensity - 3.0))
        self.assertGreater(impf.mdd[idx_high], 0.5)
    
    def test_conflict_impact_function(self):
        """Test conflict impact function creation"""
        adaptive_impf = AdaptiveImpactFunction(self.config, 'conflict')
        impf_set = adaptive_impf.create_contextual_impact_function(
            self.context, self.compounding, intensity_half=40
        )
        
        impf = impf_set.get_func()[0]
        self.assertEqual(impf.haz_type, 'CF')


class TestMultiHazardInteraction(unittest.TestCase):
    """Test multi-hazard combination logic"""
    
    def setUp(self):
        self.config = create_config('development')
        self.multi_hazard = MultiHazardInteraction(self.config)
        self.context = HazardContext(
            state='Borno',
            region='North_East',
            month=8,
            population_density=200,
            poverty_rate=0.55,
            previous_events_30d=3,
            previous_events_90d=8,
            distance_to_water_km=10,
            elevation_m=300,
            urban_rural='rural',
            infrastructure_quality=0.25,
            early_warning_coverage=0.35
        )
    
    def test_simple_combination(self):
        """Test simple maximum combination"""
        flood_int = np.array([0.5, 1.0, 1.5, 2.0])
        conflict_int = np.array([10, 20, 30, 40])
        flood_impact = np.array([0.1, 0.3, 0.5, 0.7])
        conflict_impact = np.array([0.2, 0.4, 0.6, 0.8])
        
        combined, metrics = self.multi_hazard.combine_hazards(
            flood_int, conflict_int, flood_impact, conflict_impact,
            self.context, method='simple_max'
        )
        
        # Should take maximum
        expected = np.maximum(flood_impact, conflict_impact)
        np.testing.assert_array_equal(combined, expected)
    
    def test_sophisticated_combination(self):
        """Test sophisticated combination with interactions"""
        flood_int = np.ones(100) * 1.5
        conflict_int = np.ones(100) * 30
        flood_impact = np.ones(100) * 0.4
        conflict_impact = np.ones(100) * 0.5
        
        combined, metrics = self.multi_hazard.combine_hazards(
            flood_int, conflict_int, flood_impact, conflict_impact,
            self.context, method='sophisticated'
        )
        
        # With compounding, should be higher than simple max
        self.assertGreater(combined.mean(), max(flood_impact.mean(), conflict_impact.mean()))
        
        # Check metrics
        self.assertIn('compounding_factor', metrics)
        self.assertGreater(metrics['compounding_factor'], 1.0)


# ============================================================================
# Integration Tests
# ============================================================================

class TestQualityControl(unittest.TestCase):
    """Test quality control system"""
    
    def setUp(self):
        self.config = create_config('development')
        self.qc = QualityController(self.config)
    
    def test_output_validation_valid(self):
        """Test output validation with valid data"""
        results = pd.DataFrame({
            'forecasted_displacement': np.random.lognormal(10, 0.3, 1000) * 1000
        })
        
        is_valid, warnings = self.qc.validate_outputs(results)
        self.assertTrue(is_valid)
    
    def test_output_validation_invalid(self):
        """Test output validation with invalid data"""
        # Test with NaN values
        results = pd.DataFrame({
            'forecasted_displacement': [1000, 2000, np.nan, 4000]
        })
        
        is_valid, warnings = self.qc.validate_outputs(results)
        self.assertFalse(is_valid)
        self.assertIn('NaN', str(warnings))
    
    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        score = self.qc.calculate_quality_score(
            hazard_quality=0.8,
            model_confidence=0.75,
            data_completeness=0.9,
            n_warnings=2
        )
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        
        # More warnings should decrease score
        score_many_warnings = self.qc.calculate_quality_score(
            hazard_quality=0.8,
            model_confidence=0.75,
            data_completeness=0.9,
            n_warnings=5
        )
        
        self.assertLess(score_many_warnings, score)


class TestAlertManager(unittest.TestCase):
    """Test alert generation and distribution"""
    
    def setUp(self):
        self.config = create_config('development')
        self.alert_mgr = AlertManager(self.config)
    
    def test_alert_level_determination(self):
        """Test alert level determination"""
        # Watch level
        level = self.alert_mgr._determine_alert_level(6000, 8000)
        self.assertEqual(level, 'watch')
        
        # Advisory level
        level = self.alert_mgr._determine_alert_level(12000, 15000)
        self.assertEqual(level, 'advisory')
        
        # Warning level
        level = self.alert_mgr._determine_alert_level(30000, 35000)
        self.assertEqual(level, 'warning')
        
        # Emergency level
        level = self.alert_mgr._determine_alert_level(60000, 75000)
        self.assertEqual(level, 'emergency')
    
    def test_alert_message_generation(self):
        """Test alert message generation"""
        message = self.alert_mgr._generate_alert_message(
            alert_level='warning',
            mean_disp=35000,
            p90_disp=45000,
            states=['Benue', 'Kogi'],
            actions=['Action 1', 'Action 2']
        )
        
        self.assertIn('WARNING', message)
        self.assertIn('35,000', message)
        self.assertIn('Benue', message)
        self.assertIn('Action 1', message)


# ============================================================================
# System Tests
# ============================================================================

class TestProductionEngine(unittest.TestCase):
    """Test complete forecasting engine"""
    
    def setUp(self):
        self.config = create_config('development')
        # Use smaller sample size for faster testing
        self.config.uncertainty.n_samples = 100
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        # This will fail if centroids file doesn't exist
        # In production tests, you'd have test data
        try:
            engine = ProductionForecastEngine(self.config)
            self.assertIsNotNone(engine)
        except FileNotFoundError:
            self.skipTest("Test data not available")
    
    def test_forecast_workflow(self):
        """Test complete forecast workflow (integration test)"""
        # This requires full test data setup
        # Would be run in CI/CD environment with test data
        self.skipTest("Requires full test data infrastructure")


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Test system performance and scalability"""
    
    def test_vulnerability_prediction_speed(self):
        """Test speed of vulnerability predictions"""
        config = create_config('development')
        ml_vuln = MLEnhancedVulnerability(config)
        
        context = HazardContext(
            state='Test', region='North_Central', month=1,
            population_density=100, poverty_rate=0.4,
            previous_events_30d=0, previous_events_90d=0,
            distance_to_water_km=5, elevation_m=100,
            urban_rural='rural', infrastructure_quality=0.5,
            early_warning_coverage=0.5
        )
        
        import time
        start = time.time()
        
        for _ in range(1000):
            ml_vuln.predict_vulnerability(context, 'flood')
        
        elapsed = time.time() - start
        
        # Should complete 1000 predictions in under 1 second
        self.assertLess(elapsed, 1.0)
        print(f"1000 vulnerability predictions: {elapsed:.3f}s")
    
    def test_impact_function_creation_speed(self):
        """Test speed of impact function creation"""
        config = create_config('development')
        
        context = HazardContext(
            state='Test', region='North_Central', month=1,
            population_density=100, poverty_rate=0.4,
            previous_events_30d=0, previous_events_90d=0,
            distance_to_water_km=5, elevation_m=100,
            urban_rural='rural', infrastructure_quality=0.5,
            early_warning_coverage=0.5
        )
        
        compounding = CompoundingFactors()
        
        adaptive_impf = AdaptiveImpactFunction(config, 'flood')
        
        import time
        start = time.time()
        
        for _ in range(100):
            adaptive_impf.create_contextual_impact_function(
                context, compounding, intensity_half=1.5
            )
        
        elapsed = time.time() - start
        
        # Should be fast
        self.assertLess(elapsed, 5.0)
        print(f"100 impact function creations: {elapsed:.3f}s")


# ============================================================================
# Test Runner
# ============================================================================

def run_tests(test_suite='all', verbosity=2):
    """
    Run test suite
    
    Args:
        test_suite: 'all', 'unit', 'integration', 'system', 'performance'
        verbosity: Test output verbosity (0-2)
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if test_suite in ['all', 'unit']:
        suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
        suite.addTests(loader.loadTestsFromTestCase(TestVulnerabilityModels))
        suite.addTests(loader.loadTestsFromTestCase(TestImpactFunctions))
        suite.addTests(loader.loadTestsFromTestCase(TestMultiHazardInteraction))
    
    if test_suite in ['all', 'integration']:
        suite.addTests(loader.loadTestsFromTestCase(TestQualityControl))
        suite.addTests(loader.loadTestsFromTestCase(TestAlertManager))
    
    if test_suite in ['all', 'system']:
        suite.addTests(loader.loadTestsFromTestCase(TestProductionEngine))
    
    if test_suite in ['all', 'performance']:
        suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Nigeria IBF Tests')
    parser.add_argument('--suite', default='all',
                       choices=['all', 'unit', 'integration', 'system', 'performance'],
                       help='Test suite to run')
    parser.add_argument('--verbosity', type=int, default=2, choices=[0, 1, 2],
                       help='Test output verbosity')
    
    args = parser.parse_args()
    
    success = run_tests(args.suite, args.verbosity)
    
    exit(0 if success else 1)
