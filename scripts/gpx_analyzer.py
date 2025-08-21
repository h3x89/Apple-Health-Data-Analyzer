#!/usr/bin/env python3
"""
GPX Workout Route Analyzer - From May 1, 2025
Analyzes GPX files for workout routes and provides statistics
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import json
import math
from typing import Dict, List, Any

class GPXAnalyzer:
    def __init__(self, gpx_dir: str = "workout-routes"):
        self.gpx_dir = gpx_dir
        self.start_date = datetime(2025, 5, 1)
        self.routes = []
        
    def analyze_gpx_files(self):
        """Analyze all GPX files from May 1, 2025 onwards"""
        print(f"Analyzing GPX files from {self.start_date.strftime('%Y-%m-%d')}...")
        
        if not os.path.exists(self.gpx_dir):
            print(f"Directory {self.gpx_dir} not found!")
            return
        
        gpx_files = [f for f in os.listdir(self.gpx_dir) if f.endswith('.gpx')]
        gpx_files.sort()
        
        processed_count = 0
        total_count = 0
        
        for gpx_file in gpx_files:
            total_count += 1
            file_path = os.path.join(self.gpx_dir, gpx_file)
            
            # Extract date from filename (format: route_2025-05-10_5.09pm.gpx)
            try:
                date_part = gpx_file.split('_')[1]  # 2025-05-10
                route_date = datetime.strptime(date_part, '%Y-%m-%d')
                
                if route_date >= self.start_date:
                    route_info = self._analyze_single_gpx(file_path, gpx_file, route_date)
                    if route_info:
                        self.routes.append(route_info)
                        processed_count += 1
                        
            except (ValueError, IndexError) as e:
                print(f"Could not parse date from {gpx_file}: {e}")
                continue
        
        print(f"Processed {processed_count} GPX files from {total_count} total files.")
    
    def _analyze_single_gpx(self, file_path: str, filename: str, route_date: datetime) -> Dict[str, Any]:
        """Analyze a single GPX file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Define namespace
            ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
            
            # Extract track points
            track_points = []
            for trkpt in root.findall('.//gpx:trkpt', ns):
                lat = float(trkpt.get('lat', 0))
                lon = float(trkpt.get('lon', 0))
                
                # Get elevation and time if available
                ele = trkpt.find('gpx:ele', ns)
                time = trkpt.find('gpx:time', ns)
                
                point = {
                    'lat': lat,
                    'lon': lon,
                    'ele': float(ele.text) if ele is not None else None,
                    'time': time.text if time is not None else None
                }
                track_points.append(point)
            
            if not track_points:
                return None
            
            # Calculate route statistics
            distance = self._calculate_distance(track_points)
            elevation_gain = self._calculate_elevation_gain(track_points)
            duration = self._calculate_duration(track_points)
            
            route_info = {
                'filename': filename,
                'date': route_date.strftime('%Y-%m-%d'),
                'datetime': route_date.isoformat(),
                'track_points': len(track_points),
                'distance_km': distance,
                'elevation_gain_m': elevation_gain,
                'duration_minutes': duration,
                'start_point': {
                    'lat': track_points[0]['lat'],
                    'lon': track_points[0]['lon']
                },
                'end_point': {
                    'lat': track_points[-1]['lat'],
                    'lon': track_points[-1]['lon']
                }
            }
            
            return route_info
            
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            return None
    
    def _calculate_distance(self, points: List[Dict]) -> float:
        """Calculate total distance in kilometers using Haversine formula"""
        if len(points) < 2:
            return 0.0
        
        total_distance = 0.0
        
        for i in range(len(points) - 1):
            lat1, lon1 = points[i]['lat'], points[i]['lon']
            lat2, lon2 = points[i + 1]['lat'], points[i + 1]['lon']
            
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_lat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * 
                 math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            
            total_distance += distance
        
        return total_distance
    
    def _calculate_elevation_gain(self, points: List[Dict]) -> float:
        """Calculate total elevation gain in meters"""
        if len(points) < 2:
            return 0.0
        
        elevation_gain = 0.0
        
        for i in range(len(points) - 1):
            ele1 = points[i]['ele']
            ele2 = points[i + 1]['ele']
            
            if ele1 is not None and ele2 is not None:
                elevation_diff = ele2 - ele1
                if elevation_diff > 0:  # Only count gains, not losses
                    elevation_gain += elevation_diff
        
        return elevation_gain
    
    def _calculate_duration(self, points: List[Dict]) -> float:
        """Calculate duration in minutes"""
        if len(points) < 2:
            return 0.0
        
        # Find first and last points with time data
        start_time = None
        end_time = None
        
        for point in points:
            if point['time']:
                if start_time is None:
                    start_time = point['time']
                end_time = point['time']
        
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = (end_dt - start_dt).total_seconds() / 60.0
                return duration
            except ValueError:
                pass
        
        return 0.0
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary of GPX routes"""
        if not self.routes:
            return {'message': 'No routes found for the specified period'}
        
        # Calculate statistics
        total_distance = sum(r['distance_km'] for r in self.routes)
        total_elevation = sum(r['elevation_gain_m'] for r in self.routes)
        total_duration = sum(r['duration_minutes'] for r in self.routes)
        total_points = sum(r['track_points'] for r in self.routes)
        
        # Group by month
        monthly_stats = defaultdict(lambda: {
            'routes': 0,
            'distance': 0.0,
            'elevation': 0.0,
            'duration': 0.0
        })
        
        for route in self.routes:
            month_key = route['date'][:7]  # YYYY-MM
            monthly_stats[month_key]['routes'] += 1
            monthly_stats[month_key]['distance'] += route['distance_km']
            monthly_stats[month_key]['elevation'] += route['elevation_gain_m']
            monthly_stats[month_key]['duration'] += route['duration_minutes']
        
        summary = {
            'period': f"From {self.start_date.strftime('%Y-%m-%d')} to present",
            'total_routes': len(self.routes),
            'total_distance_km': total_distance,
            'total_elevation_gain_m': total_elevation,
            'total_duration_minutes': total_duration,
            'total_track_points': total_points,
            'average_distance_per_route': total_distance / len(self.routes),
            'average_elevation_per_route': total_elevation / len(self.routes),
            'average_duration_per_route': total_duration / len(self.routes),
            'monthly_breakdown': dict(monthly_stats),
            'routes': self.routes
        }
        
        return summary

def main():
    analyzer = GPXAnalyzer()
    
    try:
        analyzer.analyze_gpx_files()
        summary = analyzer.generate_summary()
        
        # Save summary to JSON file
        with open('gpx_summary_may2025.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print key statistics
        print("\n" + "="*50)
        print("GPX ROUTES SUMMARY (May 1, 2025 onwards)")
        print("="*50)
        
        if 'message' in summary:
            print(summary['message'])
        else:
            print(f"Total routes: {summary['total_routes']}")
            print(f"Total distance: {summary['total_distance_km']:.1f} km")
            print(f"Total elevation gain: {summary['total_elevation_gain_m']:.0f} m")
            print(f"Total duration: {summary['total_duration_minutes']:.1f} minutes")
            print(f"Total track points: {summary['total_track_points']:,}")
            
            print(f"\nAverages per route:")
            print(f"  Distance: {summary['average_distance_per_route']:.1f} km")
            print(f"  Elevation gain: {summary['average_elevation_per_route']:.0f} m")
            print(f"  Duration: {summary['average_duration_per_route']:.1f} minutes")
            
            print(f"\nMonthly breakdown:")
            for month, stats in sorted(summary['monthly_breakdown'].items()):
                print(f"  {month}: {stats['routes']} routes, {stats['distance']:.1f} km, {stats['elevation']:.0f} m")
            
            print(f"\nRecent routes:")
            for route in summary['routes'][-5:]:  # Last 5 routes
                print(f"  {route['date']}: {route['distance_km']:.1f} km, {route['elevation_gain_m']:.0f} m")
        
        print(f"\nDetailed summary saved to: gpx_summary_may2025.json")
        
    except Exception as e:
        print(f"Error analyzing GPX files: {e}")

if __name__ == "__main__":
    main()

