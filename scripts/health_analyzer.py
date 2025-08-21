#!/usr/bin/env python3
"""
Apple Health Data Summary - From May 1, 2025
Efficiently parses large XML files using streaming to avoid memory issues
"""

import xml.etree.ElementTree as ET
from datetime import datetime, date
from collections import defaultdict, Counter
import json
import sys
from typing import Dict, List, Any

class HealthDataParser:
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.start_date = datetime(2025, 5, 1)
        self.stats = defaultdict(int)
        self.workouts = []
        self.heart_rate_data = []
        self.step_data = []
        self.energy_data = []
        
    def parse_xml_streaming(self):
        """Parse XML file using streaming to avoid loading entire file into memory"""
        print(f"Parsing {self.xml_file} from {self.start_date.strftime('%Y-%m-%d')}...")
        
        context = ET.iterparse(self.xml_file, events=('start', 'end'))
        
        current_element = None
        record_count = 0
        workout_count = 0
        
        for event, elem in context:
            if event == 'start':
                current_element = elem
                
            elif event == 'end':
                if elem.tag == 'Record':
                    record_count += 1
                    self._process_record(elem)
                    
                elif elem.tag == 'Workout':
                    workout_count += 1
                    self._process_workout(elem)
                
                # Clear element to free memory
                elem.clear()
                
                # Progress indicator
                if record_count % 10000 == 0:
                    print(f"Processed {record_count} records, {workout_count} workouts...")
        
        print(f"Completed! Processed {record_count} records and {workout_count} workouts.")
    
    def _process_record(self, elem):
        """Process individual record element"""
        start_date_str = elem.get('startDate')
        if not start_date_str:
            return
            
        try:
            # Parse date (format: "2025-05-01 16:32:36 +0200")
            record_date = datetime.strptime(start_date_str.split(' ')[0], '%Y-%m-%d')
            
            if record_date >= self.start_date:
                record_type = elem.get('type', 'Unknown')
                self.stats[record_type] += 1
                
                # Collect specific data types
                if record_type == 'HKQuantityTypeIdentifierHeartRate':
                    value = elem.get('value')
                    if value:
                        self.heart_rate_data.append({
                            'date': start_date_str,
                            'value': float(value)
                        })
                        
                elif record_type == 'HKQuantityTypeIdentifierStepCount':
                    value = elem.get('value')
                    if value:
                        self.step_data.append({
                            'date': start_date_str,
                            'value': int(value)
                        })
                        
                elif record_type in ['HKQuantityTypeIdentifierActiveEnergyBurned', 'HKQuantityTypeIdentifierBasalEnergyBurned']:
                    value = elem.get('value')
                    if value:
                        self.energy_data.append({
                            'date': start_date_str,
                            'type': record_type,
                            'value': float(value)
                        })
                        
        except (ValueError, TypeError) as e:
            pass  # Skip invalid dates
    
    def _process_workout(self, elem):
        """Process workout element"""
        start_date_str = elem.get('startDate')
        if not start_date_str:
            return
            
        try:
            workout_date = datetime.strptime(start_date_str.split(' ')[0], '%Y-%m-%d')
            
            if workout_date >= self.start_date:
                workout_info = {
                    'type': elem.get('workoutActivityType', 'Unknown'),
                    'start_date': start_date_str,
                    'end_date': elem.get('endDate'),
                    'duration': elem.get('duration'),
                    'duration_unit': elem.get('durationUnit'),
                    'source': elem.get('sourceName')
                }
                
                # Extract workout statistics
                stats = {}
                for stat_elem in elem.findall('.//WorkoutStatistics'):
                    stat_type = stat_elem.get('type')
                    if stat_type:
                        stats[stat_type] = {
                            'average': stat_elem.get('average'),
                            'minimum': stat_elem.get('minimum'),
                            'maximum': stat_elem.get('maximum'),
                            'sum': stat_elem.get('sum'),
                            'unit': stat_elem.get('unit')
                        }
                
                workout_info['statistics'] = stats
                self.workouts.append(workout_info)
                
        except (ValueError, TypeError) as e:
            pass
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary of health data"""
        summary = {
            'period': f"From {self.start_date.strftime('%Y-%m-%d')} to present",
            'total_records': sum(self.stats.values()),
            'total_workouts': len(self.workouts),
            'record_types': dict(self.stats),
            'workouts': self.workouts,
            'heart_rate_summary': self._analyze_heart_rate(),
            'step_summary': self._analyze_steps(),
            'energy_summary': self._analyze_energy(),
            'workout_summary': self._analyze_workouts()
        }
        
        return summary
    
    def _analyze_heart_rate(self) -> Dict[str, Any]:
        """Analyze heart rate data"""
        if not self.heart_rate_data:
            return {'message': 'No heart rate data found'}
        
        values = [hr['value'] for hr in self.heart_rate_data]
        return {
            'total_readings': len(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'recent_readings': self.heart_rate_data[-10:]  # Last 10 readings
        }
    
    def _analyze_steps(self) -> Dict[str, Any]:
        """Analyze step count data"""
        if not self.step_data:
            return {'message': 'No step data found'}
        
        # Group by date
        daily_steps = defaultdict(int)
        for step in self.step_data:
            date_key = step['date'].split(' ')[0]
            daily_steps[date_key] += step['value']
        
        values = list(daily_steps.values())
        return {
            'total_days': len(daily_steps),
            'total_steps': sum(values),
            'average_daily': sum(values) / len(values),
            'max_daily': max(values),
            'min_daily': min(values),
            'daily_breakdown': dict(daily_steps)
        }
    
    def _analyze_energy(self) -> Dict[str, Any]:
        """Analyze energy data"""
        if not self.energy_data:
            return {'message': 'No energy data found'}
        
        active_energy = [e for e in self.energy_data if 'ActiveEnergy' in e['type']]
        basal_energy = [e for e in self.energy_data if 'BasalEnergy' in e['type']]
        
        result = {}
        
        if active_energy:
            active_values = [e['value'] for e in active_energy]
            result['active_energy'] = {
                'total': sum(active_values),
                'average': sum(active_values) / len(active_values),
                'max': max(active_values)
            }
        
        if basal_energy:
            basal_values = [e['value'] for e in basal_energy]
            result['basal_energy'] = {
                'total': sum(basal_values),
                'average': sum(basal_values) / len(basal_values),
                'max': max(basal_values)
            }
        
        return result
    
    def _analyze_workouts(self) -> Dict[str, Any]:
        """Analyze workout data"""
        if not self.workouts:
            return {'message': 'No workouts found'}
        
        workout_types = Counter(w['type'] for w in self.workouts)
        total_duration = 0
        
        for workout in self.workouts:
            if workout['duration']:
                try:
                    total_duration += float(workout['duration'])
                except (ValueError, TypeError):
                    pass
        
        return {
            'total_workouts': len(self.workouts),
            'workout_types': dict(workout_types),
            'total_duration_minutes': total_duration,
            'average_duration': total_duration / len(self.workouts) if self.workouts else 0,
            'recent_workouts': self.workouts[-5:]  # Last 5 workouts
        }

def main():
    parser = HealthDataParser('export.xml')
    
    try:
        parser.parse_xml_streaming()
        summary = parser.generate_summary()
        
        # Save summary to JSON file
        with open('health_summary_may2025.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print key statistics
        print("\n" + "="*50)
        print("HEALTH DATA SUMMARY (May 1, 2025 onwards)")
        print("="*50)
        print(f"Total records: {summary['total_records']:,}")
        print(f"Total workouts: {summary['total_workouts']}")
        
        print("\nTop 10 Record Types:")
        sorted_types = sorted(summary['record_types'].items(), key=lambda x: x[1], reverse=True)
        for record_type, count in sorted_types[:10]:
            print(f"  {record_type}: {count:,}")
        
        if 'workout_summary' in summary and 'message' not in summary['workout_summary']:
            print(f"\nWorkout Summary:")
            print(f"  Total workouts: {summary['workout_summary']['total_workouts']}")
            print(f"  Total duration: {summary['workout_summary']['total_duration_minutes']:.1f} minutes")
            print(f"  Average duration: {summary['workout_summary']['average_duration']:.1f} minutes")
            
            print(f"\nWorkout Types:")
            for workout_type, count in summary['workout_summary']['workout_types'].items():
                print(f"  {workout_type}: {count}")
        
        if 'heart_rate_summary' in summary and 'message' not in summary['heart_rate_summary']:
            hr = summary['heart_rate_summary']
            print(f"\nHeart Rate Summary:")
            print(f"  Total readings: {hr['total_readings']:,}")
            print(f"  Average: {hr['average']:.1f} bpm")
            print(f"  Range: {hr['min']:.0f} - {hr['max']:.0f} bpm")
        
        if 'step_summary' in summary and 'message' not in summary['step_summary']:
            steps = summary['step_summary']
            print(f"\nStep Summary:")
            print(f"  Total days: {steps['total_days']}")
            print(f"  Total steps: {steps['total_steps']:,}")
            print(f"  Average daily: {steps['average_daily']:.0f} steps")
            print(f"  Max daily: {steps['max_daily']:,} steps")
        
        print(f"\nDetailed summary saved to: health_summary_may2025.json")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

