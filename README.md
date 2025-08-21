# Apple Health Data Analyzer 🏃‍♂️📱

A comprehensive toolkit for analyzing data exported from Apple Health, enabling detailed activity reports generation and social media content creation.

## 🚀 Features

- **Health data analysis**: Processing large XML files from Apple Health Export
- **GPX route analysis**: Calculating distances, elevation gains, and activity duration
- **Step correction**: Intelligent removal of steps counted during cycling or skating workouts
- **Report generation**: Creating detailed activity summaries
- **Instagram content**: Automatic generation of posts with sports metrics

## 📁 Project Structure

```
apple-health-analyzer/
├── scripts/                    # Main analysis scripts
│   ├── health_analyzer.py      # Basic health data analysis
│   ├── gpx_analyzer.py         # GPX route analysis
│   └── step_corrector.py       # Advanced analysis with step correction
├── examples/                   # Usage examples and results
│   ├── sample_results/         # Sample JSON output files
│   └── instagram_post/         # Instagram content examples
├── docs/                       # Documentation
├── requirements.txt            # Dependencies (mainly Python stdlib)
└── README.md                   # This file
```

## 📥 How to Export Data from Apple Health

1. Open the **Health** app on iPhone
2. Tap **profile** (person icon in top right corner)
3. Scroll down and select **Export All Health Data**
4. Wait for export preparation (may take several minutes)
5. Share the ZIP file via AirDrop, email, or cloud
6. Unzip the file - you'll get folders:
   - `export.xml` - main health data (can be very large!)
   - `export_cda.xml` - medical format data
   - `electrocardiograms/` - ECG data
   - `workout-routes/` - GPX routes from workouts

## 🛠️ Installation and Usage

### Requirements

- Python 3.7+
- Data exported from Apple Health

### Basic Usage

1. **Clone repository**

```bash
git clone <repository-url>
cd apple-health-analyzer
```

2. **Place data files**
   - Copy files from Apple Health export to main project folder
   - Files `export.xml`, `export_cda.xml` and folders `electrocardiograms/`, `workout-routes/` are automatically ignored by git

3. **Basic health data analysis**

```bash
python3 scripts/health_analyzer.py
```

4. **GPX route analysis**

```bash
python3 scripts/gpx_analyzer.py
```

5. **Full analysis with step correction** (RECOMMENDED)

```bash
python3 scripts/step_corrector.py
```

## 📊 Types of Analyzed Data

### Health data (export.xml)

- **Steps**: Daily step count with correction for sports activities
- **Calories**: Active and basal energy expenditure
- **Heart Rate**: Average, minimum and maximum values
- **Workouts**: Activity types, duration, statistics

### GPX data (workout-routes/)

- **Distances**: Actual routes calculated with Haversine algorithm
- **Elevation Gain**: Sum of climbs during activities
- **Duration**: Actual activity time
- **Speed**: Average speed on routes

## 🎯 Data Accuracy

### ✅ Very Accurate

- **GPS Distances**: Cycling, running, walking routes with GPS
- **Workout Calories**: Measured during active sessions
- **Elevation Gain**: From Apple Watch barometric data
- **Workout Time**: Precise start/stop time

### ⚠️ Moderately Accurate

- **Steps**: Apple Watch may count steps while driving, working at computer, or other hand movements
- **Basal Calories**: Estimated based on user profile

### 🔧 Applied Corrections

- **Removing workout steps**: Steps counted during cycling and skating workouts are subtracted from daily total
- **Data filtering**: Only data from specified time period
- **Deduplication**: Avoiding double counting of distances

## 📱 Instagram Content Generation

The script automatically generates:

- Formatted post with key metrics
- Detailed description explaining data sources
- Information about measurement accuracy

### Example Generated Post

```
📅 Sample Period 🏆

💪 XX workouts in X months!
🚶 XXX,XXX steps
🚴 XXX km cycling  
⛸️ XXX km skating
🚶‍♂️ XX km hiking
🔥 XX,XXX kcal burned
⛰️ X,XXX m elevation gain
```

## ⚡ Performance

- **Streaming XML parsing**: Handles files >1GB without memory issues
- **Fast processing**: Analyzes months of data in seconds
- **Minimal dependencies**: Uses mainly Python standard library

## 🔒 Privacy

- All health data is processed locally
- Personal data files are automatically ignored by git
- No data sent to external services
- Repository examples contain no real personal data

## 🤝 Contributing

Pull requests are welcome for:

- New analysis types
- Performance improvements
- Additional export formats
- Documentation improvements

## 📄 License

MIT License - see LICENSE file for details

---

**💡 Tip**: Before first use, check the size of `export.xml` file - it can be very large (>1GB). All scripts are optimized for handling large files.
