#!/usr/bin/env python3
"""
Step Correction Script
Removes steps that were counted during cycling and skating workouts to avoid double counting
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import json
from typing import Dict, Any, List, Tuple

def extract_workout_times():
    """Extract all workout start and end times"""
    print("Extracting workout times...")
    
    workout_times = []
    start_date = datetime(2025, 5, 1)  # Example date - change as needed
    
    context = ET.iterparse('export.xml', events=('start', 'end'))
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'Workout':
            start_date_str = elem.get('startDate')
            end_date_str = elem.get('endDate')
            workout_type = elem.get('workoutActivityType', '')
            
            if start_date_str and end_date_str:
                try:
                    workout_start = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S %z')
                    workout_end = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S %z')
                    
                    # Convert to naive datetime for comparison
                    workout_start_naive = workout_start.replace(tzinfo=None)
                    
                    if workout_start_naive >= start_date:
                        workout_times.append({
                            'start': workout_start,
                            'end': workout_end,
                            'type': workout_type
                        })
                except (ValueError, TypeError):
                    pass
            
            elem.clear()
    
    print(f"Found {len(workout_times)} workouts from specified date")
    return workout_times

def extract_steps_with_times():
    """Extract all step records with their timestamps"""
    print("Extracting step records...")
    
    step_records = []
    start_date = datetime(2025, 5, 1)  # Example date - change as needed
    
    context = ET.iterparse('export.xml', events=('start', 'end'))
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'Record':
            record_type = elem.get('type')
            if record_type == 'HKQuantityTypeIdentifierStepCount':
                start_date_str = elem.get('startDate')
                end_date_str = elem.get('endDate')
                value = elem.get('value')
                
                if start_date_str and end_date_str and value:
                    try:
                        step_start = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S %z')
                        step_end = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S %z')
                        
                        # Convert to naive datetime for comparison
                        step_start_naive = step_start.replace(tzinfo=None)
                        
                        if step_start_naive >= start_date:
                            step_records.append({
                                'start': step_start,
                                'end': step_end,
                                'value': int(value),
                                'source': elem.get('sourceName', 'Unknown')
                            })
                    except (ValueError, TypeError):
                        pass
            
            elem.clear()
    
    print(f"Found {len(step_records)} step records from specified date")
    return step_records

def is_step_during_workout(step_record, workout_times):
    """Check if a step record overlaps with any workout time"""
    for workout in workout_times:
        # Check if step time overlaps with workout time
        if (step_record['start'] <= workout['end'] and 
            step_record['end'] >= workout['start']):
            return True
    return False

def calculate_corrected_steps():
    """Calculate steps with workout steps removed"""
    print("Calculating corrected step count...")
    
    # Get workout times
    workout_times = extract_workout_times()
    
    # Get step records
    step_records = extract_steps_with_times()
    
    # Separate cycling workouts
    cycling_workouts = [w for w in workout_times if 'Cycling' in w['type']]
    skating_workouts = [w for w in workout_times if 'Skating' in w['type']]
    walking_workouts = [w for w in workout_times if 'Walking' in w['type']]
    
    print(f"Cycling workouts: {len(cycling_workouts)}")
    print(f"Skating workouts: {len(skating_workouts)}")
    print(f"Walking workouts: {len(walking_workouts)}")
    
    # Calculate total steps
    total_steps = sum(step['value'] for step in step_records)
    
    # Find steps during cycling workouts
    steps_during_cycling = []
    steps_during_skating = []
    steps_during_walking = []
    
    for step in step_records:
        if is_step_during_workout(step, cycling_workouts):
            steps_during_cycling.append(step)
        elif is_step_during_workout(step, skating_workouts):
            steps_during_skating.append(step)
        elif is_step_during_workout(step, walking_workouts):
            steps_during_walking.append(step)
    
    cycling_steps = sum(step['value'] for step in steps_during_cycling)
    skating_steps = sum(step['value'] for step in steps_during_skating)
    walking_steps = sum(step['value'] for step in steps_during_walking)
    
    # Calculate corrected steps
    corrected_steps = total_steps - cycling_steps - skating_steps
    
    print(f"\n📊 STEP CORRECTION RESULTS:")
    print("-" * 40)
    print(f"• Total steps: {total_steps:,}")
    print(f"• Steps during cycling workouts: {cycling_steps:,}")
    print(f"• Steps during skating workouts: {skating_steps:,}")
    print(f"• Steps during walking (keeping): {walking_steps:,}")
    print(f"• CORRECTED STEPS: {corrected_steps:,}")
    print()
    
    return {
        'total_steps': total_steps,
        'cycling_steps': cycling_steps,
        'skating_steps': skating_steps,
        'walking_steps': walking_steps,
        'corrected_steps': corrected_steps,
        'step_records': step_records,
        'workout_times': workout_times
    }

def generate_corrected_summary():
    """Generate summary with corrected step count"""
    
    # Get corrected step data
    step_data = calculate_corrected_steps()
    
    # Load other data
    health_data = load_json_data('health_summary_sample.json')
    gpx_data = load_json_data('gpx_summary_sample.json')
    
    if not health_data or not gpx_data:
        print("❌ No data available for analysis!")
        return
    
    # Extract workout distances
    workout_distances = extract_workout_distances_from_xml()
    
    # Extract key metrics
    total_workouts = health_data.get('total_workouts', 0)
    corrected_steps = step_data['corrected_steps']
    
    # GPX data
    gpx_distance = gpx_data.get('total_distance_km', 0)
    gpx_elevation = gpx_data.get('total_elevation_gain_m', 0)
    
    # Energy data
    active_energy = health_data.get('energy_summary', {}).get('active_energy', {}).get('total', 0)
    
    print("🎯 CORRECTED FITNESS SUMMARY 🎯")
    print("=" * 50)
    print()
    print(f"📅 Analysis Period: Custom date range")
    print(f"💪 Total Workouts: {total_workouts}")
    print(f"🚶 Corrected Steps: {corrected_steps:,}")
    print(f"🚴 Cycling Distance: {workout_distances['cycling']:.1f} km")
    print(f"⛸️ Skating Distance: {workout_distances['skating']:.1f} km")
    print(f"🚶‍♂️ Walking Distance: {workout_distances['walking']:.1f} km")
    print(f"🔥 Active Calories: {int(active_energy):,} kcal")
    print(f"⛰️ Elevation Gain: {gpx_elevation:.0f} m")
    print()
    print("✨ Data ready for social media posting! ✨")

def extract_workout_distances_from_xml():
    """Extract actual workout distances from XML file"""
    distances = {
        'cycling': 0.0,
        'skating': 0.0,
        'walking': 0.0,
        'running': 0.0
    }
    
    start_date = datetime(2025, 5, 1)  # Example date - change as needed
    
    context = ET.iterparse('export.xml', events=('start', 'end'))
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'Workout':
            start_date_str = elem.get('startDate')
            if start_date_str:
                try:
                    workout_date = datetime.strptime(start_date_str.split(' ')[0], '%Y-%m-%d')
                    if workout_date >= start_date:
                        workout_type = elem.get('workoutActivityType', '')
                        
                        for stat_elem in elem.findall('.//WorkoutStatistics'):
                            stat_type = stat_elem.get('type')
                            if stat_type == 'HKQuantityTypeIdentifierDistanceCycling':
                                distance = float(stat_elem.get('sum', 0))
                                distances['cycling'] += distance
                            elif stat_type == 'HKQuantityTypeIdentifierDistanceSkatingSports':
                                distance = float(stat_elem.get('sum', 0))
                                distances['skating'] += distance
                            elif stat_type == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                                distance = float(stat_elem.get('sum', 0))
                                if 'Running' in workout_type:
                                    distances['running'] += distance
                                else:
                                    distances['walking'] += distance
                except (ValueError, TypeError):
                    pass
            
            elem.clear()
    
    return distances

def load_json_data(filename: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found. Please ensure data files are available.")
        return {}
    except json.JSONDecodeError:
        print(f"Error reading {filename}. Please check file format.")
        return {}

if __name__ == "__main__":
    generate_corrected_summary()