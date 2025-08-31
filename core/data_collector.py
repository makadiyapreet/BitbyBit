import requests
import pandas as pd
import time
import random
import math
import json
from datetime import datetime, timedelta

class CoastalDataCollector:
    def __init__(self):
        self.collected_data = []
        self.api_sources = {
            'tide_api': 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter',
            'weather_api': 'http://api.openweathermap.org/data/2.5/weather'
        }
        
    def get_real_tide_data(self, station_id="8461490"):  # New London, CT
        """Get real NOAA tide data"""
        try:
            params = {
                'begin_date': datetime.now().strftime('%Y%m%d %H:%M'),
                'range': '1',
                'station': station_id,
                'product': 'water_level',
                'datum': 'MLLW',
                'format': 'json',
                'units': 'metric'
            }
            response = requests.get(self.api_sources['tide_api'], params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    return float(data['data'][0]['v'])
        except:
            pass
        return None

    def get_weather_data(self, city="Mumbai"):
        try:
            # Simulate realistic weather with patterns
            base_temp = 28 + 5 * math.sin(datetime.now().hour * math.pi / 12)
            weather_data = {
                'temperature': round(base_temp + random.gauss(0, 2), 1),
                'humidity': round(random.uniform(65, 85), 1),
                'pressure': round(1013 + random.gauss(0, 8), 1),
                'wind_speed': round(random.expovariate(1/15), 1),
                'wind_direction': round(random.uniform(0, 360), 1),
                'visibility': round(random.uniform(8, 15), 1),
                'timestamp': datetime.now().isoformat(),
                'location': city
            }
            return weather_data
        except Exception as e:
            print(f"❌ Error getting weather data: {e}")
            return None
    
    def simulate_tide_sensor(self, location_name):
        # Try real data first
        real_tide = self.get_real_tide_data()
        if real_tide:
            tide_level = real_tide
        else:
            # Enhanced simulation with tidal harmonics
            hour = datetime.now().hour
            minute = datetime.now().minute
            time_decimal = hour + minute/60
            
            # Multiple tidal components (M2, S2, K1, O1)
            m2_tide = 1.2 * math.cos(time_decimal * math.pi / 6.21)  # Principal lunar semi-diurnal
            s2_tide = 0.3 * math.cos(time_decimal * math.pi / 6)     # Principal solar semi-diurnal
            k1_tide = 0.4 * math.cos(time_decimal * math.pi / 12.43) # Lunar diurnal
            
            base_tide = 2.0 + m2_tide + s2_tide + k1_tide
            variation = random.gauss(0, 0.15)
            
            # Enhanced anomaly detection - multiple threat types
            anomaly_prob = 0.08  # 8% chance
            if random.random() < anomaly_prob:
                anomaly_type = random.choices(
                    ['storm_surge', 'king_tide', 'tsunami_signal'],
                    weights=[0.7, 0.25, 0.05]
                )[0]
                
                if anomaly_type == 'storm_surge':
                    anomaly = random.uniform(1.5, 3.5)
                elif anomaly_type == 'king_tide':
                    anomaly = random.uniform(0.8, 1.5)
                else:  # tsunami
                    anomaly = random.uniform(4, 8)
                
                tide_level = base_tide + variation + anomaly
                print(f"🚨 {anomaly_type.upper()} DETECTED: {location_name}: {tide_level:.2f}m")
            else:
                tide_level = max(0, base_tide + variation)

        return {
            'location': location_name,
            'tide_level': tide_level,
            'tidal_range': abs(tide_level - 2.0),
            'sensor_id': f"TIDE_{location_name.replace(' ', '_')}",
            'timestamp': datetime.now().isoformat(),
            'quality': random.uniform(0.85, 1.0),
            'battery_level': random.uniform(0.7, 1.0)
        }
    
    def simulate_water_quality(self, location_name):
        """Simulate water quality sensors"""
        return {
            'ph_level': random.uniform(7.8, 8.3),
            'dissolved_oxygen': random.uniform(6, 9),
            'turbidity': random.expovariate(1/2),
            'salinity': random.uniform(33, 37),
            'temperature': random.uniform(22, 30),
            'pollution_index': random.uniform(0, 0.3)
        }
    
    def simulate_satellite_data(self, location_name):
        """Enhanced satellite analysis"""
        threats = {
            'algal_bloom': {'prob': 0.04, 'severity': [0.3, 0.8]},
            'oil_spill': {'prob': 0.01, 'severity': [0.7, 0.95]},
            'illegal_dumping': {'prob': 0.02, 'severity': [0.5, 0.8]},
            'coastal_erosion': {'prob': 0.06, 'severity': [0.4, 0.7]},
            'plastic_accumulation': {'prob': 0.08, 'severity': [0.3, 0.6]},
            'sedimentation': {'prob': 0.05, 'severity': [0.4, 0.6]}
        }
        
        detected_threats = []
        for threat_type, params in threats.items():
            if random.random() < params['prob']:
                severity = random.uniform(*params['severity'])
                detected_threats.append({
                    'type': threat_type,
                    'severity': severity,
                    'coordinates': [
                        random.uniform(18, 20), 
                        random.uniform(72, 74)
                    ],
                    'area_affected': random.uniform(0.1, 5.0),  # km²
                    'confidence': random.uniform(0.7, 0.95)
                })
        
        return {
            'location': location_name,
            'threats_detected': detected_threats,
            'image_quality': random.uniform(0.8, 1.0),
            'cloud_cover': random.uniform(0, 0.4),
            'timestamp': datetime.now().isoformat()
        }

    
    def collect_all_regions_data(self):
        locations = [
            {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
            {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
            {"name": "Kochi", "lat": 9.9312, "lon": 76.2673}
        ]
        
        for location in locations:
            weather = self.get_weather_data(location['name'])
            tide = self.simulate_tide_sensor(location['name'])
            water_quality = self.simulate_water_quality(location['name'])
            satellite = self.simulate_satellite_data(location['name'])
            
            combined_data = {
                'location': location,
                'timestamp': datetime.now().isoformat(),
                'weather': weather,
                'tide': tide,
                'water_quality': water_quality,
                'satellite': satellite
            }
            
            self.collected_data.append(combined_data)
            print(f"📊 Complete data collected for {location['name']}")
        
        return self.collected_data

    def export_data(self, format='json'):
        """Export collected data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            with open(f'coastal_data_{timestamp}.json', 'w') as f:
                json.dump(self.collected_data, f, indent=2)
        elif format == 'csv':
            df = pd.json_normalize(self.collected_data)
            df.to_csv(f'coastal_data_{timestamp}.csv', index=False)
        
        print(f"📁 Data exported as {format.upper()}")

if __name__ == "__main__":
    collector = CoastalDataCollector()
    for i in range(10):
        collector.collect_all_data()
        time.sleep(3)
    collector.export_data('json')
    collector.export_data('csv')