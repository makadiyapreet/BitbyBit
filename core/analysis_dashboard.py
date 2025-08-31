import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class CoastalAnalyticsDashboard:
    def __init__(self, data_file=None):
        self.data = []
        self.alerts_log = []
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, data_file):
        """Load data from JSON file"""
        try:
            with open(data_file, 'r') as f:
                self.data = json.load(f)
            print(f"📊 Loaded {len(self.data)} data points")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def generate_comprehensive_report(self):
        """Generate detailed analytics report"""
        if not self.data:
            return "No data available for analysis"
        
        df = pd.json_normalize(self.data)
        
        report = {
            'summary': self._generate_summary_stats(df),
            'threat_analysis': self._analyze_threats(),
            'location_comparison': self._compare_locations(),
            'temporal_patterns': self._analyze_temporal_patterns(),
            'risk_assessment': self._assess_overall_risk(),
            'predictions': self._generate_predictions()
        }
        
        return report
    
    def _generate_summary_stats(self, df):
        """Generate summary statistics"""
        try:
            return {
                'total_data_points': len(df),
                'locations_monitored': df['location.name'].nunique(),
                'avg_tide_level': df['tide.tide_level'].mean(),
                'max_tide_level': df['tide.tide_level'].max(),
                'avg_wind_speed': df['weather.wind_speed'].mean(),
                'pressure_range': [df['weather.pressure'].min(), df['weather.pressure'].max()],
                'data_quality_score': df['tide.quality'].mean(),
                'monitoring_duration': self._calculate_duration()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_threats(self):
        """Analyze threat patterns"""
        threat_count = 0
        threat_types = {}
        high_severity_events = 0
        
        for data_point in self.data:
            # Count satellite threats
            sat_threats = data_point.get('satellite', {}).get('threats_detected', [])
            threat_count += len(sat_threats)
            
            for threat in sat_threats:
                threat_type = threat.get('type', 'unknown')
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
                if threat.get('severity', 0) > 0.7:
                    high_severity_events += 1
            
            # Check for high tide/weather threats
            tide_level = data_point.get('tide', {}).get('tide_level', 0)
            wind_speed = data_point.get('weather', {}).get('wind_speed', 0)
            
            if tide_level > 3.5 or wind_speed > 40:
                high_severity_events += 1
        
        return {
            'total_threats_detected': threat_count,
            'threat_types_distribution': threat_types,
            'high_severity_events': high_severity_events,
            'threat_frequency': threat_count / len(self.data) if self.data else 0
        }
    
    def _compare_locations(self):
        """Compare different monitoring locations"""
        location_stats = {}
        
        for data_point in self.data:
            location = data_point.get('location', {}).get('name', 'unknown')
            
            if location not in location_stats:
                location_stats[location] = {
                    'tide_levels': [],
                    'wind_speeds': [],
                    'threats': 0
                }
            
            location_stats[location]['tide_levels'].append(
                data_point.get('tide', {}).get('tide_level', 0)
            )
            location_stats[location]['wind_speeds'].append(
                data_point.get('weather', {}).get('wind_speed', 0)
            )
            location_stats[location]['threats'] += len(
                data_point.get('satellite', {}).get('threats_detected', [])
            )
        
        # Calculate averages
        comparison = {}
        for location, stats in location_stats.items():
            comparison[location] = {
                'avg_tide_level': np.mean(stats['tide_levels']),
                'max_tide_level': np.max(stats['tide_levels']),
                'avg_wind_speed': np.mean(stats['wind_speeds']),
                'total_threats': stats['threats'],
                'risk_score': self._calculate_location_risk(stats)
            }
        
        return comparison
    
    def _calculate_location_risk(self, stats):
        """Calculate risk score for a location"""
        avg_tide = np.mean(stats['tide_levels'])
        max_tide = np.max(stats['tide_levels'])
        avg_wind = np.mean(stats['wind_speeds'])
        threats = stats['threats']
        
        risk_score = 0
        if avg_tide > 3: risk_score += 0.3
        if max_tide > 4: risk_score += 0.3
        if avg_wind > 30: risk_score += 0.2
        if threats > 2: risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _analyze_temporal_patterns(self):
        """Analyze patterns over time"""
        if not self.data:
            return {}
        
        timestamps = []
        tide_levels = []
        
        for data_point in self.data:
            try:
                timestamp = datetime.fromisoformat(data_point['timestamp'].replace('Z', ''))
                timestamps.append(timestamp)
                tide_levels.append(data_point.get('tide', {}).get('tide_level', 0))
            except:
                continue
        
        if not timestamps:
            return {}
        
        df_temp = pd.DataFrame({
            'timestamp': timestamps,
            'tide_level': tide_levels
        })
        df_temp['hour'] = df_temp['timestamp'].dt.hour
        
        return {
            'hourly_tide_pattern': df_temp.groupby('hour')['tide_level'].mean().to_dict(),
            'peak_tide_hours': df_temp.groupby('hour')['tide_level'].max().idxmax(),
            'data_collection_rate': len(self.data) / ((max(timestamps) - min(timestamps)).total_seconds() / 60) if len(timestamps) > 1 else 0
        }
    
    def _assess_overall_risk(self):
        """Assess overall coastal risk"""
        if not self.data:
            return {}
        
        high_tide_count = sum(1 for d in self.data if d.get('tide', {}).get('tide_level', 0) > 3.5)
        severe_weather_count = sum(1 for d in self.data if d.get('weather', {}).get('wind_speed', 0) > 40)
        total_threats = sum(len(d.get('satellite', {}).get('threats_detected', [])) for d in self.data)
        
        risk_level = "LOW"
        if high_tide_count > len(self.data) * 0.2:
            risk_level = "HIGH"
        elif severe_weather_count > len(self.data) * 0.1:
            risk_level = "MEDIUM"
        
        return {
            'overall_risk_level': risk_level,
            'high_tide_events': high_tide_count,
            'severe_weather_events': severe_weather_count,
            'total_satellite_threats': total_threats,
            'system_uptime': self._calculate_uptime(),
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _calculate_uptime(self):
        """Calculate system uptime percentage"""
        if not self.data:
            return 100
        
        expected_readings = len(self.data)
        actual_readings = sum(1 for d in self.data if d.get('tide', {}).get('quality', 0) > 0.5)
        
        return (actual_readings / expected_readings) * 100 if expected_readings > 0 else 100
    
    def _get_risk_recommendation(self, risk_level):
        """Get recommendation based on risk level"""
        recommendations = {
            'LOW': "Continue routine monitoring. System operating normally.",
            'MEDIUM': "Increase monitoring frequency. Prepare response teams.",
            'HIGH': "IMMEDIATE ATTENTION REQUIRED. Deploy emergency protocols."
        }
        return recommendations.get(risk_level, "Monitor conditions closely.")
    
    def _calculate_duration(self):
        """Calculate monitoring duration"""
        if len(self.data) < 2:
            return "< 1 minute"
        
        try:
            start_time = datetime.fromisoformat(self.data[0]['timestamp'].replace('Z', ''))
            end_time = datetime.fromisoformat(self.data[-1]['timestamp'].replace('Z', ''))
            duration = end_time - start_time
            
            if duration.total_seconds() < 3600:
                return f"{duration.total_seconds()/60:.1f} minutes"
            else:
                return f"{duration.total_seconds()/3600:.1f} hours"
        except:
            return "unknown"
    
    def _generate_predictions(self):
        """Generate predictive insights"""
        if len(self.data) < 5:
            return {"status": "insufficient_data"}
        
        # Analyze recent trends
        recent_data = self.data[-10:]
        tide_levels = [d.get('tide', {}).get('tide_level', 0) for d in recent_data]
        pressures = [d.get('weather', {}).get('pressure', 1013) for d in recent_data]
        
        tide_trend = np.polyfit(range(len(tide_levels)), tide_levels, 1)[0]
        pressure_trend = np.polyfit(range(len(pressures)), pressures, 1)[0]
        
        next_6h_risk = "LOW"
        if tide_trend > 0.3 and pressure_trend < -2:
            next_6h_risk = "HIGH"
        elif abs(tide_trend) > 0.2 or abs(pressure_trend) > 1:
            next_6h_risk = "MEDIUM"
        
        return {
            "next_6_hours": next_6h_risk,
            "tide_trend": "rising" if tide_trend > 0.1 else "falling" if tide_trend < -0.1 else "stable",
            "pressure_trend": "falling" if pressure_trend < -0.5 else "rising" if pressure_trend > 0.5 else "stable",
            "confidence": 0.75
        }
    
    def print_detailed_report(self):
        """Print formatted analysis report"""
        report = self.generate_comprehensive_report()
        
        print("\n" + "="*80)
        print("🌊 COASTAL THREAT ANALYSIS REPORT")
        print("="*80)
        
        # Summary
        summary = report['summary']
        print(f"\n📊 MONITORING SUMMARY:")
        print(f"   🕒 Duration: {summary.get('monitoring_duration', 'N/A')}")
        print(f"   📍 Locations: {summary.get('locations_monitored', 'N/A')}")
        print(f"   📈 Data Points: {summary.get('total_data_points', 'N/A')}")
        print(f"   🌊 Avg Tide: {summary.get('avg_tide_level', 0):.2f}m")
        print(f"   💨 Avg Wind: {summary.get('avg_wind_speed', 0):.1f}km/h")
        print(f"   ⚡ System Quality: {summary.get('data_quality_score', 0):.2%}")
        
        # Threat Analysis
        threats = report['threat_analysis']
        print(f"\n🚨 THREAT ANALYSIS:")
        print(f"   ⚠️  Total Threats: {threats.get('total_threats_detected', 0)}")
        print(f"   🔴 High Severity: {threats.get('high_severity_events', 0)}")
        print(f"   📊 Threat Rate: {threats.get('threat_frequency', 0):.2%} per reading")
        
        threat_types = threats.get('threat_types_distribution', {})
        if threat_types:
            print("   📋 Threat Types:")
            for threat_type, count in threat_types.items():
                print(f"      - {threat_type.replace('_', ' ').title()}: {count}")
        
        # Location Comparison
        locations = report['location_comparison']
        print(f"\n📍 LOCATION RISK ASSESSMENT:")
        for location, stats in locations.items():
            risk_emoji = "🔴" if stats['risk_score'] > 0.7 else "🟡" if stats['risk_score'] > 0.4 else "🟢"
            print(f"   {risk_emoji} {location}:")
            print(f"      • Risk Score: {stats['risk_score']:.2f}/1.0")
            print(f"      • Avg Tide: {stats['avg_tide_level']:.2f}m")
            print(f"      • Max Tide: {stats['max_tide_level']:.2f}m")
            print(f"      • Threats: {stats['total_threats']}")
        
        # Overall Risk
        risk = report['risk_assessment']
        risk_emoji = "🔴" if risk['overall_risk_level'] == 'HIGH' else "🟡" if risk['overall_risk_level'] == 'MEDIUM' else "🟢"
        print(f"\n{risk_emoji} OVERALL RISK LEVEL: {risk['overall_risk_level']}")
        print(f"   💡 Recommendation: {risk['recommendation']}")
        print(f"   📶 System Uptime: {risk['system_uptime']:.1f}%")
        
        # Predictions
        predictions = report['predictions']
        if predictions.get('status') != 'insufficient_data':
            pred_emoji = "🔴" if predictions['next_6_hours'] == 'HIGH' else "🟡" if predictions['next_6_hours'] == 'MEDIUM' else "🟢"
            print(f"\n🔮 NEXT 6 HOURS FORECAST:")
            print(f"   {pred_emoji} Risk Level: {predictions['next_6_hours']}")
            print(f"   🌊 Tide Trend: {predictions['tide_trend']}")
            print(f"   🌪️  Pressure Trend: {predictions['pressure_trend']}")
            print(f"   🎯 Confidence: {predictions['confidence']:.0%}")
        
        print("\n" + "="*80)
        
        return report
    
    def generate_actionable_insights(self):
        """Generate specific actionable insights"""
        insights = []
        
        if not self.data:
            return ["No data available for analysis"]
        
        # Analyze recent data
        recent_data = self.data[-5:] if len(self.data) >= 5 else self.data
        
        # Check for immediate concerns
        for data_point in recent_data:
            location = data_point.get('location', {}).get('name', 'Unknown')
            tide = data_point.get('tide', {}).get('tide_level', 0)
            wind = data_point.get('weather', {}).get('wind_speed', 0)
            pressure = data_point.get('weather', {}).get('pressure', 1013)
            
            if tide > 3.8:
                insights.append(f"🚨 URGENT: {location} experiencing dangerous tide levels ({tide:.2f}m)")
            
            if wind > 45 and pressure < 995:
                insights.append(f"⛈️  STORM WARNING: {location} - High winds ({wind:.1f}km/h) with low pressure ({pressure:.1f}hPa)")
            
            pollution = data_point.get('water_quality', {}).get('pollution_index', 0)
            if pollution > 0.4:
                insights.append(f"🏭 POLLUTION ALERT: {location} - High contamination detected ({pollution:.2f})")
        
        # Strategic insights
        df = pd.json_normalize(self.data)
        if len(df) > 10:
            if df['tide.tide_level'].std() > 1.0:
                insights.append("📈 HIGH VARIABILITY: Tide levels showing unusual fluctuations - monitor closely")
            
            if df['weather.pressure'].min() < 990:
                insights.append("🌀 PRESSURE DROP: Significant pressure drops detected - storm system possible")
        
        return insights if insights else ["✅ No immediate threats identified - continue monitoring"]

if __name__ == "__main__":
    # Test the analytics
    dashboard = CoastalAnalyticsDashboard()
    print("📊 Analytics Dashboard ready for data!")
