import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import DBSCAN
import random
from datetime import datetime, timedelta

class AdvancedThreatDetector:
    def __init__(self):
        # Multiple specialized models
        self.tide_detector = IsolationForest(contamination=0.1, random_state=42)
        self.weather_detector = IsolationForest(contamination=0.12, random_state=42)
        self.multi_threat_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.anomaly_clusterer = DBSCAN(eps=0.5, min_samples=3)
        
        self.scalers = {
            'tide': StandardScaler(),
            'weather': StandardScaler(),
            'water_quality': MinMaxScaler()
        }
        
        self.threat_history = []
        self.is_trained = False
        
    def quick_train(self, historical_data):
        print("🧠 Training advanced AI models...")
        
        # Generate comprehensive training data
        tide_data, weather_data, quality_data, threat_labels = self._generate_training_data()
        
        # Train individual detectors
        tide_scaled = self.scalers['tide'].fit_transform(tide_data)
        weather_scaled = self.scalers['weather'].fit_transform(weather_data)
        quality_scaled = self.scalers['water_quality'].fit_transform(quality_data)
        
        self.tide_detector.fit(tide_scaled)
        self.weather_detector.fit(weather_scaled)
        
        # Train multi-threat classifier
        combined_features = np.hstack([tide_scaled, weather_scaled, quality_scaled])
        self.multi_threat_classifier.fit(combined_features, threat_labels)
        
        self.is_trained = True
        print("✅ Advanced AI models trained!")
        
    def _generate_training_data(self, n_samples=500):
        """Generate realistic training scenarios"""
        tide_data = []
        weather_data = []
        quality_data = []
        threat_labels = []
        
        for _ in range(n_samples):
            # Normal conditions (80%)
            if random.random() < 0.8:
                tide = [random.uniform(0.5, 3.2), random.uniform(5, 30), random.uniform(0, 2)]
                weather = [random.uniform(15, 35), random.uniform(1005, 1020), random.uniform(60, 85)]
                quality = [random.uniform(7.5, 8.5), random.uniform(6, 9), random.uniform(0, 0.2)]
                label = 0  # No threat
            else:
                # Threat scenarios (20%)
                scenario = random.choice(['storm', 'pollution', 'extreme_tide', 'combined'])
                
                if scenario == 'storm':
                    tide = [random.uniform(3.5, 6), random.uniform(40, 80), random.uniform(2, 4)]
                    weather = [random.uniform(20, 40), random.uniform(980, 1000), random.uniform(70, 95)]
                    quality = [random.uniform(7.8, 8.3), random.uniform(5, 8), random.uniform(0.1, 0.3)]
                    label = 1
                elif scenario == 'pollution':
                    tide = [random.uniform(1, 4), random.uniform(5, 25), random.uniform(0, 1)]
                    weather = [random.uniform(25, 35), random.uniform(1008, 1018), random.uniform(65, 80)]
                    quality = [random.uniform(6.5, 7.5), random.uniform(3, 6), random.uniform(0.4, 0.8)]
                    label = 2
                elif scenario == 'extreme_tide':
                    tide = [random.uniform(4, 8), random.uniform(20, 50), random.uniform(3, 6)]
                    weather = [random.uniform(20, 35), random.uniform(995, 1015), random.uniform(70, 90)]
                    quality = [random.uniform(7.5, 8.2), random.uniform(6, 8), random.uniform(0.1, 0.3)]
                    label = 3
                else:  # combined
                    tide = [random.uniform(4, 7), random.uniform(45, 75), random.uniform(2.5, 5)]
                    weather = [random.uniform(18, 42), random.uniform(975, 1005), random.uniform(75, 95)]
                    quality = [random.uniform(6.8, 7.8), random.uniform(4, 7), random.uniform(0.3, 0.6)]
                    label = 4
            
            tide_data.append(tide)
            weather_data.append(weather)
            quality_data.append(quality)
            threat_labels.append(label)
        
        return np.array(tide_data), np.array(weather_data), np.array(quality_data), np.array(threat_labels)
    
    def comprehensive_threat_analysis(self, data_point):
        """Advanced multi-factor threat analysis"""
        if not self.is_trained:
            return self.fallback_analysis(data_point)
        
        # Extract features
        tide_features = [
            data_point['tide']['tide_level'],
            data_point['weather']['wind_speed'],
            data_point['tide']['tidal_range']
        ]
        
        weather_features = [
            data_point['weather']['temperature'],
            data_point['weather']['pressure'],
            data_point['weather']['humidity']
        ]
        
        quality_features = [
            data_point['water_quality']['ph_level'],
            data_point['water_quality']['dissolved_oxygen'],
            data_point['water_quality']['pollution_index']
        ]
        
        # Scale features
        tide_scaled = self.scalers['tide'].transform([tide_features])
        weather_scaled = self.scalers['weather'].transform([weather_features])
        quality_scaled = self.scalers['water_quality'].transform([quality_features])
        
        # Individual anomaly scores
        tide_anomaly = self.tide_detector.decision_function(tide_scaled)[0]
        weather_anomaly = self.weather_detector.decision_function(weather_scaled)[0]
        
        # Combined threat classification
        combined_features = np.hstack([tide_scaled, weather_scaled, quality_scaled])
        threat_prob = self.multi_threat_classifier.predict_proba(combined_features)[0]
        predicted_threat = self.multi_threat_classifier.predict(combined_features)[0]
        
        # Threat severity calculation
        severity = self._calculate_severity(tide_features, weather_features, quality_features)
        
        # Multiple threat detection
        threats_detected = self._detect_multiple_threats(data_point)
        
        return {
            'primary_threat': self._interpret_threat_class(predicted_threat),
            'threat_probability': np.max(threat_prob),
            'severity_score': severity,
            'individual_anomalies': {
                'tide_anomaly': tide_anomaly < -0.1,
                'weather_anomaly': weather_anomaly < -0.1
            },
            'multiple_threats': threats_detected,
            'confidence': np.max(threat_prob),
            'risk_factors': self._identify_risk_factors(data_point),
            'recommendations': self._generate_recommendations(predicted_threat, severity)
        }
    
    def _calculate_severity(self, tide_features, weather_features, quality_features):
        """Calculate threat severity score (0-1)"""
        tide_level, wind_speed, tidal_range = tide_features
        temperature, pressure, humidity = weather_features
        ph, oxygen, pollution = quality_features
        
        severity = 0
        
        # Tide severity
        if tide_level > 4: severity += 0.3
        elif tide_level > 3.5: severity += 0.2
        
        # Weather severity
        if wind_speed > 50: severity += 0.25
        elif wind_speed > 35: severity += 0.15
        
        if pressure < 990: severity += 0.2
        elif pressure < 1000: severity += 0.1
        
        # Water quality severity
        if pollution > 0.4: severity += 0.2
        elif pollution > 0.2: severity += 0.1
        
        if oxygen < 5: severity += 0.15
        
        return min(severity, 1.0)
    
    def _detect_multiple_threats(self, data_point):
        """Detect multiple simultaneous threats"""
        threats = []
        
        # Satellite-based threats
        for threat in data_point['satellite']['threats_detected']:
            threats.append({
                'type': threat['type'],
                'severity': threat['severity'],
                'source': 'satellite',
                'confidence': threat['confidence']
            })
        
        # Sensor-based threat detection
        tide_level = data_point['tide']['tide_level']
        wind_speed = data_point['weather']['wind_speed']
        pressure = data_point['weather']['pressure']
        pollution = data_point['water_quality']['pollution_index']
        
        if tide_level > 3.8 and wind_speed > 40:
            threats.append({
                'type': 'storm_surge',
                'severity': 0.8,
                'source': 'sensor_fusion',
                'confidence': 0.9
            })
        
        if pollution > 0.3:
            threats.append({
                'type': 'water_contamination',
                'severity': pollution,
                'source': 'water_quality',
                'confidence': 0.85
            })
        
        return threats
    
    def _identify_risk_factors(self, data_point):
        """Identify specific risk factors"""
        risk_factors = []
        
        if data_point['tide']['battery_level'] < 0.3:
            risk_factors.append("Low sensor battery - monitoring may be interrupted")
        
        if data_point['satellite']['cloud_cover'] > 0.7:
            risk_factors.append("High cloud cover - satellite monitoring limited")
        
        if data_point['weather']['visibility'] < 5:
            risk_factors.append("Poor visibility - navigation hazardous")
        
        return risk_factors
    
    def _generate_recommendations(self, threat_class, severity):
        """Generate specific recommendations"""
        recommendations = []
        
        if threat_class == 1:  # Storm
            recommendations.extend([
                "Issue storm surge warning",
                "Advise evacuation of low-lying areas",
                "Deploy emergency response teams"
            ])
        elif threat_class == 2:  # Pollution
            recommendations.extend([
                "Investigate pollution source",
                "Issue water quality advisory",
                "Monitor marine life impact"
            ])
        elif threat_class == 3:  # Extreme tide
            recommendations.extend([
                "Issue high tide warning",
                "Check coastal infrastructure",
                "Monitor for flooding"
            ])
        
        if severity > 0.7:
            recommendations.append("IMMEDIATE ACTION REQUIRED")
        elif severity > 0.4:
            recommendations.append("Monitor closely - prepare response")
        
        return recommendations
    
    def _interpret_threat_class(self, threat_class):
        """Convert numeric class to threat name"""
        threat_names = {
            0: 'normal',
            1: 'storm_system',
            2: 'pollution_event',
            3: 'extreme_tide',
            4: 'multiple_threats'
        }
        return threat_names.get(threat_class, 'unknown')
    
    def fallback_analysis(self, data_point):
        """Simple rule-based analysis when AI not trained"""
        tide_level = data_point['tide']['tide_level']
        wind_speed = data_point['weather']['wind_speed']
        pressure = data_point['weather']['pressure']
        
        if tide_level > 4 and wind_speed > 45:
            return {
                'primary_threat': 'severe_storm_surge',
                'threat_probability': 0.9,
                'severity_score': 0.9,
                'confidence': 0.8,
                'method': 'rule_based'
            }
        elif tide_level > 3.5:
            return {
                'primary_threat': 'high_tide_warning',
                'threat_probability': 0.7,
                'severity_score': 0.6,
                'confidence': 0.75,
                'method': 'rule_based'
            }
        
        return {
            'primary_threat': 'normal',
            'threat_probability': 0.1,
            'severity_score': 0.2,
            'confidence': 0.6,
            'method': 'rule_based'
        }

    def predict_future_threats(self, historical_data, hours_ahead=6):
        """Predict threats in the next few hours"""
        if len(historical_data) < 10:
            return {"prediction": "insufficient_data"}
        
        # Analyze trends
        recent_tides = [d['tide']['tide_level'] for d in historical_data[-10:]]
        recent_pressure = [d['weather']['pressure'] for d in historical_data[-10:]]
        
        tide_trend = np.polyfit(range(len(recent_tides)), recent_tides, 1)[0]
        pressure_trend = np.polyfit(range(len(recent_pressure)), recent_pressure, 1)[0]
        
        prediction = {
            "time_horizon": f"{hours_ahead} hours",
            "tide_trend": "rising" if tide_trend > 0.1 else "falling" if tide_trend < -0.1 else "stable",
            "pressure_trend": "falling" if pressure_trend < -0.5 else "rising" if pressure_trend > 0.5 else "stable",
            "threat_likelihood": "high" if (tide_trend > 0.2 and pressure_trend < -1) else "moderate" if abs(tide_trend) > 0.1 else "low"
        }
        
        return prediction

if __name__ == "__main__":
    detector = AdvancedThreatDetector()
    detector.quick_train([])
    print("🧪 Advanced threat detector ready for testing!")