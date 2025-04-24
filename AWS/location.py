import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from azure.maps.render import MapsRenderClient
from azure.maps.search import MapsSearchClient
from azure.core.exceptions import HttpResponseError
import geopandas as gpd
from shapely.geometry import Point, LineString
import folium
from streamlit_folium import folium_static
import math
from datetime import datetime
from scipy import stats
import itertools
from folium.plugins import HeatMap, MarkerCluster, MeasureControl
import branca.colormap as cm

# Configuration
ODK_USERNAME = "rushi@tnodk01.ii.com"
ODK_PASSWORD = "rushi2025&"
AZURE_MAPS_API_KEY = "944BjlSA5zZyX94AAvM2mM4gIRV005pWgXAOpFbvVNEWSGmFMEm7JQQJ99BDACYeBjFgSQNNAAAgAZMP3Cok"
PROJECT_ID = 4
FORM_ID = "144-Manachanallur Landscape Survey 04-2025"
API_URL = f"https://tnodk01.indiaintentions.com/v1/projects/{PROJECT_ID}/forms/{FORM_ID.replace(' ', '%20')}.svc/Submissions"

# Sample project data
PROJECTS = {
    "BK TN AC Landscape": {
        "forms": ["144-Manachanallur Landscape Survey 04-2025", "145-Another Form"],
        "id": 4
    },
    "Another Project": {
        "forms": ["Form 1", "Form 2"],
        "id": 5
    }
}

# Helper functions
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on earth in kilometers"""
    R = 6371  # Earth radius in km
    
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    
    a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def calculate_interpoint_distances(df):
    """Calculate distances between all pairs of points in the dataframe"""
    # Only consider rows with valid coordinates
    valid_df = df.dropna(subset=['latitude', 'longitude'])
    
    if len(valid_df) <= 1:
        return pd.DataFrame(columns=['point1_id', 'point2_id', 'distance_km'])
    
    # Create list to store distances
    distances = []
    
    # Calculate distance between every pair of points
    for i, row1 in valid_df.iterrows():
        for j, row2 in valid_df.iterrows():
            if i < j:  # To avoid duplicate calculations
                dist = haversine_distance(
                    row1['latitude'], row1['longitude'],
                    row2['latitude'], row2['longitude']
                )
                
                distances.append({
                    'point1_id': row1['submission_id'],
                    'point1_village': row1['village'],
                    'point1_lat': row1['latitude'],
                    'point1_lon': row1['longitude'],
                    'point2_id': row2['submission_id'],
                    'point2_village': row2['village'],
                    'point2_lat': row2['latitude'],
                    'point2_lon': row2['longitude'],
                    'distance_km': dist,
                    'same_village': row1['village'] == row2['village'],
                    'same_surveyor': row1['submitted_by'] == row2['submitted_by']
                })
    
    return pd.DataFrame(distances)

def fetch_submissions(project_id, form_name):
    """Fetch all submissions from ODK Central for specific project and form"""
    try:
        form_api_url = f"https://tnodk01.indiaintentions.com/v1/projects/{project_id}/forms/{form_name.replace(' ', '%20')}.svc/Submissions"
        response = requests.get(
            form_api_url,
            auth=HTTPBasicAuth(ODK_USERNAME, ODK_PASSWORD),
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def parse_submission(submission):
    """Parse a single submission into a structured format"""
    try:
        group_six = submission.get("group_six", {})
        
        # Try to parse date from instanceID
        submission_date = None
        instance_id = submission.get("meta", {}).get("instanceID", "")
        if instance_id:
            # Try to extract date format from instanceID (typically contains a timestamp)
            try:
                # Example format: uuid:226e9d69-ed88-4a38-857a-32d6a35c7cc3
                # Often the timestamp is embedded in this ID
                parts = instance_id.split(':')
                if len(parts) > 1:
                    date_parts = parts[1].split('-')
                    if len(date_parts) >= 3:
                        submission_date = f"{date_parts[0][:4]}-{date_parts[0][4:6]}-{date_parts[0][6:8]}"
            except:
                submission_date = instance_id  # Fallback to the whole ID
        
        data = {
            "submission_id": submission.get("__id", ""),
            "submitted_by": group_six.get("submittedBy", ""),
            "submission_date": submission_date,
            "device_id": submission.get("deviceid", ""),
            "block": group_six.get("D1_Block", ""),
            "village": group_six.get("D2_Village_GP", ""),
            "respondent_name": group_six.get("D7_Name", ""),
            "phone_number": group_six.get("D8_PhoneNumber", ""),
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "timestamp": submission.get("__system", {}).get("submissionDate", "")
        }
        
        # Extract geopoint if available
        geopoint = group_six.get("geopoint_widget", {})
        if geopoint and "coordinates" in geopoint:
            data["longitude"] = geopoint["coordinates"][0]
            data["latitude"] = geopoint["coordinates"][1]
            data["accuracy"] = geopoint["coordinates"][2] if len(geopoint["coordinates"]) > 2 else None
            if "properties" in geopoint and "accuracy" in geopoint["properties"]:
                data["accuracy"] = geopoint["properties"]["accuracy"]
                
        return data
    except Exception as e:
        st.warning(f"Error parsing submission: {str(e)}")
        return None

def analyze_surveyor_patterns(df):
    """Analyze surveyor patterns and identify if they're collecting from same/different locations"""
    results = []
    
    for surveyor in df['submitted_by'].unique():
        surveyor_data = df[df['submitted_by'] == surveyor]
        num_submissions = len(surveyor_data)
        villages = surveyor_data['village'].nunique()
        blocks = surveyor_data['block'].nunique()
        
        # Calculate location diversity
        location_diversity = "Low"
        avg_distance = 0
        submission_rate = None
        
        if num_submissions > 1:
            # Calculate average distance between points
            distances = []
            coords = surveyor_data[['latitude', 'longitude']].dropna().values
            
            for i in range(len(coords)):
                for j in range(i+1, len(coords)):
                    lat1, lon1 = coords[i]
                    lat2, lon2 = coords[j]
                    try:
                        distance = haversine_distance(lat1, lon1, lat2, lon2)
                        distances.append(distance)
                    except:
                        pass
            
            if distances:
                avg_distance = sum(distances) / len(distances)
                if avg_distance > 3.0:  # More than 3 km average distance
                    location_diversity = "High"
                elif avg_distance > 1.0:
                    location_diversity = "Medium"
                else:
                    location_diversity = "Low"
            
            # Calculate submission rate (submissions per day)
            try:
                if 'timestamp' in surveyor_data.columns and not surveyor_data['timestamp'].isna().all():
                    timestamps = pd.to_datetime(surveyor_data['timestamp'])
                    if not timestamps.empty:
                        date_range = (timestamps.max() - timestamps.min()).days + 1
                        if date_range > 0:
                            submission_rate = num_submissions / date_range
                            submission_rate = round(submission_rate, 2)
            except:
                pass
        
        # Check for potential outliers
        outlier_status = "Normal"
        if avg_distance > 10:  # Large distance spread
            outlier_status = "Potential outlier: Large area coverage"
        elif num_submissions > 20 and villages == 1:
            outlier_status = "Potential outlier: High submissions in single village"
        elif submission_rate and submission_rate > 15:
            outlier_status = "Potential outlier: High submission rate"
        
        results.append({
            "Surveyor": surveyor,
            "Submissions": num_submissions,
            "Villages Covered": villages,
            "Blocks Covered": blocks,
            "Location Diversity": location_diversity,
            "Avg Distance (km)": round(avg_distance, 2),
            "Submissions/Day": submission_rate,
            "Status": outlier_status,
            "Primary Village": surveyor_data['village'].mode()[0] if not surveyor_data['village'].empty else "",
            "Primary Block": surveyor_data['block'].mode()[0] if not surveyor_data['block'].empty else ""
        })
    
    return pd.DataFrame(results)

def detect_location_outliers(df):
    """Detect outliers in survey locations using statistical methods"""
    # Requires valid coordinates
    geo_df = df.dropna(subset=['latitude', 'longitude'])
    
    if len(geo_df) <= 5:  # Need enough data for meaningful outlier detection
        return pd.DataFrame(), [], []
    
    # Calculate z-scores for latitude and longitude
    geo_df['lat_zscore'] = stats.zscore(geo_df['latitude'])
    geo_df['lon_zscore'] = stats.zscore(geo_df['longitude'])
    
    # Calculate Euclidean distance from mean point
    mean_lat = geo_df['latitude'].mean()
    mean_lon = geo_df['longitude'].mean()
    
    geo_df['distance_from_mean'] = geo_df.apply(
        lambda row: haversine_distance(row['latitude'], row['longitude'], mean_lat, mean_lon),
        axis=1
    )
    
    # Calculate z-score for this distance
    geo_df['distance_zscore'] = stats.zscore(geo_df['distance_from_mean'])
    
    # Define outliers (points with z-score > 2.5 in either dimension)
    outliers = geo_df[(abs(geo_df['lat_zscore']) > 2.5) | 
                      (abs(geo_df['lon_zscore']) > 2.5) |
                      (abs(geo_df['distance_zscore']) > 2.5)]
    
    # Define extreme outliers (z-score > 3.5)
    extreme_outliers = geo_df[(abs(geo_df['lat_zscore']) > 3.5) | 
                              (abs(geo_df['lon_zscore']) > 3.5) |
                              (abs(geo_df['distance_zscore']) > 3.5)]
    
    return geo_df, outliers, extreme_outliers

def detect_time_outliers(df):
    """Detect outliers in submission timing patterns"""
    # Need timestamp data
    if 'timestamp' not in df.columns or df['timestamp'].isna().all():
        return pd.DataFrame()
    
    time_df = df.copy()
    
    # Convert timestamp to datetime if it's not already
    if pd.api.types.is_string_dtype(time_df['timestamp']):
        time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
    
    # Group by surveyor and date to get submissions per surveyor per day
    time_df['date'] = time_df['timestamp'].dt.date
    daily_counts = time_df.groupby(['submitted_by', 'date']).size().reset_index(name='submissions_per_day')
    
    # Calculate statistics
    surveyor_stats = daily_counts.groupby('submitted_by').agg(
        avg_submissions=('submissions_per_day', 'mean'),
        max_submissions=('submissions_per_day', 'max'),
        std_submissions=('submissions_per_day', 'std'),
        total_days=('date', 'count'),
        total_submissions=('submissions_per_day', 'sum')
    ).reset_index()
    
    # Fill NaN standard deviations with 0
    surveyor_stats['std_submissions'] = surveyor_stats['std_submissions'].fillna(0)
    
    # Define outlier thresholds
    overall_mean = daily_counts['submissions_per_day'].mean()
    overall_std = daily_counts['submissions_per_day'].std()
    
    high_threshold = overall_mean + 2 * overall_std
    
    # Flag outliers
    surveyor_stats['time_outlier_status'] = 'Normal'
    surveyor_stats.loc[surveyor_stats['max_submissions'] > high_threshold, 'time_outlier_status'] = 'Potential time outlier'
    
    return surveyor_stats

def plot_surveyor_locations(df, surveyor, plot_distances=False):
    """Plot a surveyor's data collection locations on a map"""
    surveyor_data = df[df['submitted_by'] == surveyor].dropna(subset=['latitude', 'longitude'])
    
    if surveyor_data.empty:
        st.warning(f"No location data available for {surveyor}")
        return
    
    # Create map centered on the average location
    avg_lat = surveyor_data['latitude'].mean()
    avg_lon = surveyor_data['longitude'].mean()
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)
    
    # Add measure control for manual distance measurements
    MeasureControl(position='topright', primary_length_unit='kilometers').add_to(m)
    
    # Create a marker cluster for better visibility
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add points to the map
    for idx, row in surveyor_data.iterrows():
        popup_text = (
            f"<b>Village:</b> {row['village']}<br>"
            f"<b>Respondent:</b> {row['respondent_name']}<br>"
            f"<b>Submission ID:</b> {row['submission_id']}<br>"
            f"<b>Accuracy:</b> {row['accuracy'] if not pd.isna(row['accuracy']) else 'N/A'} m"
        )
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"Point {idx+1}: {row['village']}",
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)
    
    # Plot distances between points if requested and there are multiple points
    if plot_distances and len(surveyor_data) > 1:
        # Calculate distances between all pairs
        points = surveyor_data[['submission_id', 'latitude', 'longitude']].values
        
        # Use a colormap based on distance
        min_distance = 0
        max_distance = 10  # 10km as max for color scaling
        colormap = cm.LinearColormap(
            colors=['green', 'yellow', 'orange', 'red'],
            vmin=min_distance,
            vmax=max_distance
        )
        
        # Add lines between points
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                point1 = points[i]
                point2 = points[j]
                
                id1, lat1, lon1 = point1
                id2, lat2, lon2 = point2
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                
                # Only show lines for distances less than 20km (to avoid clutter)
                if distance < 20:
                    color = colormap(min(distance, max_distance))
                    
                    folium.PolyLine(
                        locations=[(lat1, lon1), (lat2, lon2)],
                        color=color,
                        weight=2,
                        opacity=0.7,
                        tooltip=f"Distance: {distance:.2f} km"
                    ).add_to(m)
        
        # Add the colormap to the map
        colormap.caption = 'Distance (km)'
        colormap.add_to(m)
    
    # Add a heatmap layer
    heat_data = [[row['latitude'], row['longitude']] for _, row in surveyor_data.iterrows()]
    HeatMap(heat_data).add_to(m)
    
    return m

def plot_all_locations(df, highlight_outliers=True):
    """Plot all survey locations on a map, highlighting outliers"""
    geo_df = df.dropna(subset=['latitude', 'longitude'])
    
    if geo_df.empty:
        st.warning("No location data available")
        return
    
    # Run outlier detection if requested
    if highlight_outliers:
        processed_df, outliers, extreme_outliers = detect_location_outliers(geo_df)
    else:
        processed_df, outliers, extreme_outliers = geo_df, pd.DataFrame(), pd.DataFrame()
    
    # Create map centered on the average location
    avg_lat = geo_df['latitude'].mean()
    avg_lon = geo_df['longitude'].mean()
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
    
    # Add measure control
    MeasureControl(position='topright', primary_length_unit='kilometers').add_to(m)
    
    # Create separate marker clusters for normal and outlier points
    normal_cluster = MarkerCluster(name="Normal Points").add_to(m)
    outlier_cluster = MarkerCluster(name="Potential Outliers").add_to(m)
    
    # Add points to the map
    for idx, row in geo_df.iterrows():
        popup_text = (
            f"<b>Village:</b> {row['village']}<br>"
            f"<b>Surveyor:</b> {row['submitted_by']}<br>"
            f"<b>Respondent:</b> {row['respondent_name']}<br>"
            f"<b>Submission ID:</b> {row['submission_id']}"
        )
        
        # Check if this point is an outlier
        is_outlier = False
        is_extreme = False
        
        if highlight_outliers and not outliers.empty:
            is_outlier = row['submission_id'] in outliers['submission_id'].values
            is_extreme = row['submission_id'] in extreme_outliers['submission_id'].values
        
        if is_extreme:
            # Extreme outliers with red icon
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text + "<br><b>Status:</b> Extreme Outlier", max_width=300),
                tooltip=f"{row['village']} (Extreme Outlier)",
                icon=folium.Icon(color='red', icon='warning-sign')
            ).add_to(outlier_cluster)
        elif is_outlier:
            # Regular outliers with orange icon
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text + "<br><b>Status:</b> Potential Outlier", max_width=300),
                tooltip=f"{row['village']} (Outlier)",
                icon=folium.Icon(color='orange', icon='info-sign')
            ).add_to(outlier_cluster)
        else:
            # Normal points with default blue icon
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['village']}",
                icon=folium.Icon(color='blue')
            ).add_to(normal_cluster)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m, outliers, extreme_outliers

def analyze_village_distance_distribution(df):
    """Analyze the distribution of distances within villages"""
    # Need at least villages and coordinates
    if 'village' not in df.columns or df['village'].isna().all():
        return pd.DataFrame()
    
    geo_df = df.dropna(subset=['latitude', 'longitude'])
    
    if len(geo_df) <= 1:
        return pd.DataFrame()
    
    # Calculate distances between points within the same village
    results = []
    
    for village in geo_df['village'].unique():
        village_data = geo_df[geo_df['village'] == village]
        
        if len(village_data) <= 1:
            continue
        
        # Calculate distances between every pair of points in this village
        distances = []
        for i, row1 in village_data.iterrows():
            for j, row2 in village_data.iterrows():
                if i < j:  # To avoid duplicate calculations
                    dist = haversine_distance(
                        row1['latitude'], row1['longitude'],
                        row2['latitude'], row2['longitude']
                    )
                    distances.append(dist)
        
        if distances:
            results.append({
                'Village': village,
                'Points': len(village_data),
                'Surveyors': village_data['submitted_by'].nunique(),
                'Min Distance (km)': min(distances),
                'Max Distance (km)': max(distances),
                'Avg Distance (km)': sum(distances) / len(distances),
                'Distance Range (km)': max(distances) - min(distances),
                'Total Area Covered (km²)': calculate_approximate_area(village_data)
            })
    
    return pd.DataFrame(results)

def calculate_approximate_area(points_df):
    """Calculate an approximate area covered by the points in square kilometers"""
    if len(points_df) <= 2:
        return 0
    
    # Simple rectangular approximation first
    lat_range = points_df['latitude'].max() - points_df['latitude'].min()
    lon_range = points_df['longitude'].max() - points_df['longitude'].min()
    
    # Convert to km (approximate conversion, will vary by latitude)
    lat_km = lat_range * 111  # 1 degree latitude is approx 111 km
    lon_km = lon_range * 111 * math.cos(math.radians(points_df['latitude'].mean()))  # Adjust for latitude
    
    rectangular_area = lat_km * lon_km
    
    # Apply a correction factor for more realistic area approximation
    # (points rarely form a perfect rectangle, so this gives a more conservative estimate)
    correction_factor = 0.8 if len(points_df) > 5 else 0.6
    
    return round(rectangular_area * correction_factor, 2)

# Main Streamlit app
def main():
    st.set_page_config(layout="wide", page_title="Survey Analysis Dashboard")
    
    st.title("BK TN AC Landscape Survey Analysis")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Project dropdown
        selected_project = st.selectbox(
            "Select Project",
            list(PROJECTS.keys()),
            index=0  # Default to first project
        )
        
        # Form dropdown (based on selected project)
        available_forms = PROJECTS[selected_project]["forms"]
        selected_form = st.selectbox(
            "Select Form",
            available_forms,
            index=0  # Default to first form
        )
        
        # Fetch data based on selections
        with st.spinner("Loading data..."):
            submissions = fetch_submissions(PROJECTS[selected_project]["id"], selected_form)
            
            if submissions:
                parsed_data = [parse_submission(sub) for sub in submissions.get("value", [])]
                df = pd.DataFrame([d for d in parsed_data if d is not None])
                
                # Store the original dataframe for total count
                original_df = df.copy() if not df.empty else pd.DataFrame()
                
                # Display total submission count in sidebar
                st.metric("Overall Total Submissions", len(original_df) if not original_df.empty else 0)
                
                # Ensure submitted_by has valid entries
                if not df.empty and 'submitted_by' in df.columns and not df['submitted_by'].empty:
                    # Remove any empty or null entries and sort
                    all_submitters = ["All"] + sorted(df['submitted_by'].dropna().unique().tolist())
                else:
                    all_submitters = ["All"]
                
                # Submitted By dropdown
                selected_submitter = st.selectbox(
                    "Submitted By",
                    all_submitters,
                    index=0  # Default to "All"
                )
                
                # Filter data based on submitter selection
                if selected_submitter != "All" and not df.empty:
                    df = df[df['submitted_by'] == selected_submitter]
            else:
                df = pd.DataFrame()
                original_df = pd.DataFrame()
                st.error("No data available for selected filters")

    # Main content area
    if df.empty:
        st.warning("No data available for the selected filters")
        return
    
    # Add navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", 
        "Surveyor Analysis", 
        "Location Analysis", 
        "Distance Analysis",
        "Outlier Detection"
    ])
    
    with tab1:
        st.header("Survey Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Submissions", len(df))
        
        with col2:
            st.metric("Unique Surveyors", df['submitted_by'].nunique())
        
        with col3:
            st.metric("Villages Covered", df['village'].nunique())
        
        with col4:
            st.metric("Blocks Covered", df['block'].nunique())
        
        # Summary map
        st.subheader("All Survey Locations")
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            map_obj, outliers, extreme_outliers = plot_all_locations(df)
            folium_static(map_obj, width=1000, height=500)
            
            if not outliers.empty:
                st.info(f"Detected {len(outliers)} potential location outliers, including {len(extreme_outliers)} extreme outliers.")
        
        # Village coverage
        st.subheader("Village Coverage")
        village_stats = df.groupby('village').agg({
            'submitted_by': 'nunique',
            'submission_id': 'count'
        }).rename(columns={
            'submitted_by': 'Surveyors',
            'submission_id': 'Submissions'
        }).sort_values('Submissions', ascending=False)
        
        st.dataframe(village_stats)
        
        # Submission timeline if timestamp data is available
        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            st.subheader("Submission Timeline")
            
            # Convert to datetime if string
            if pd.api.types.is_string_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
            # Group by date
            df['date'] = df['timestamp'].dt.date
            daily_counts = df.groupby('date').size().reset_index(name='submissions')
            
            # Plot
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(daily_counts['date'], daily_counts['submissions'])
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Submissions')
            ax.set_title('Daily Submission Counts')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    with tab2:
        st.header("Surveyor Performance Analysis")
        
        # Analyze surveyor patterns
        analysis_df = analyze_surveyor_patterns(df)
        
        # Add time-based analysis if timestamp is available
        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            time_analysis = detect_time_outliers(df)
            if not time_analysis.empty:
                analysis_df = analysis_df.merge(
                    time_analysis[['submitted_by', 'avg_submissions', 'max_submissions', 'time_outlier_status']],
                    left_on='Surveyor',
                    right_on='submitted_by',
                    how='left'
                )
                analysis_df.drop('submitted_by', axis=1, inplace=True)
        
        # Display the analysis
        st.dataframe(analysis_df.sort_values("Submissions", ascending=False))
        
        # Visualizations of surveyor performance
        st.subheader("Surveyor Performance Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Submissions per surveyor
            if not analysis_df.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                
                # Sort by number of submissions
                plot_data = analysis_df.sort_values('Submissions', ascending=False).head(10)
                
                # Colormap based on location diversity
                colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
                bar_colors = [colors.get(div, 'blue') for div in plot_data['Location Diversity']]
                
                ax.bar(plot_data['Surveyor'], plot_data['Submissions'], color=bar_colors)
                ax.set_xlabel('Surveyor')
                ax.set_ylabel('Number of Submissions')
                ax.set_title('Top 10 Surveyors by Submission Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
                
                # Create a legend for the colors
                st.markdown("""
                **Location Diversity Color Code:**
                - 🟢 High: Wide area coverage (>3km average distance)
                - 🟠 Medium: Moderate area coverage (1-3km average distance)
                - 🔴 Low: Concentrated area (<1km average distance)
                """)
        
        with col2:
            # Villages covered per surveyor
            if not analysis_df.empty:
                fig, ax = plt.subplots(figsize=(8, 5))
                
                # Sort by number of villages
                plot_data = analysis_df.sort_values('Villages Covered', ascending=False).head(10)
                
                ax.bar(plot_data['Surveyor'], plot_data['Villages Covered'])
                ax.set_xlabel('Surveyor')
                ax.set_ylabel('Number of Villages')
                ax.set_title('Top 10 Surveyors by Village Coverage')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
        
        # Surveyor selector for detailed view
        st.subheader("Individual Surveyor Analysis")
        
        if selected_submitter == "All":
            selected_surveyor = st.selectbox(
                "Select a surveyor to view details:",
                df['submitted_by'].unique()
            )
        else:
            selected_surveyor = selected_submitter
        
        # Show selected surveyor's data
        surveyor_data = df[df['submitted_by'] == selected_surveyor]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Data Collection Map for {selected_surveyor}")
            st.checkbox("Show distance lines between points", key="show_distances")
            map_obj = plot_surveyor_locations(df, selected_surveyor, st.session_state.show_distances)
            folium_static(map_obj, width=700, height=500)
        
        with col2:
            # Surveyor metrics
            surveyor_info = analysis_df[analysis_df['Surveyor'] == selected_surveyor]
            
            if not surveyor_info.empty:
                st.subheader("Surveyor Metrics")
                metrics = {
                    "Submissions": surveyor_info['Submissions'].values[0],
                    "Villages": surveyor_info['Villages Covered'].values[0],
                    "Blocks": surveyor_info['Blocks Covered'].values[0],
                    "Location Diversity": surveyor_info['Location Diversity'].values[0],
                    "Avg Distance (km)": surveyor_info['Avg Distance (km)'].values[0]
                }
                
                # Add time metrics if available
                if 'avg_submissions' in surveyor_info.columns:
                    metrics["Avg Submissions/Day"] = surveyor_info['avg_submissions'].values[0]
                if 'max_submissions' in surveyor_info.columns:
                    metrics["Max Submissions/Day"] = surveyor_info['max_submissions'].values[0]
                
                # Alert for outlier status
                status = surveyor_info['Status'].values[0]
                if status != "Normal":
                    st.warning(f"⚠️ {status}")
                
                # Display metrics
                for key, value in metrics.items():
                    st.metric(key, value)
            
            # Village breakdown
            st.subheader("Village Breakdown")
            village_counts = surveyor_data['village'].value_counts().reset_index()
            village_counts.columns = ['Village', 'Count']
            st.dataframe(village_counts)
        
        # Show surveyor's submissions
        with st.expander("View All Submissions by this Surveyor"):
            st.dataframe(surveyor_data)
    
    with tab3:
        st.header("Location Analysis")
        
        # Location clustering and outlier detection
        st.subheader("Location Clustering and Outlier Detection")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Map with outliers highlighted
            map_obj, outliers, extreme_outliers = plot_all_locations(df)
            folium_static(map_obj, width=800, height=500)
        
        with col2:
            # Outlier statistics
            st.metric("Total Locations", len(df.dropna(subset=['latitude', 'longitude'])))
            st.metric("Potential Outliers", len(outliers))
            st.metric("Extreme Outliers", len(extreme_outliers))
            
            # Explanation
            st.markdown("""
            **Outlier Detection Method:**
            - Statistical analysis using z-scores for latitude and longitude
            - Distance calculation from the mean center point
            - Potential outliers: z-score > 2.5
            - Extreme outliers: z-score > 3.5
            """)
        
        # If outliers found, show them in detail
        if not outliers.empty:
            st.subheader("Outlier Details")
            
            # Clean outlier data for display
            display_cols = ['submission_id', 'submitted_by', 'village', 'latitude', 'longitude', 'distance_from_mean']
            outlier_display = outliers[display_cols].copy()
            outlier_display['distance_from_mean'] = outlier_display['distance_from_mean'].round(2)
            outlier_display.columns = ['Submission ID', 'Surveyor', 'Village', 'Latitude', 'Longitude', 'Distance from Mean (km)']
            
            st.dataframe(outlier_display)
        
        # Village location analysis
        st.subheader("Village Location Analysis")
        
        # Calculate village stats
        village_location_stats = analyze_village_distance_distribution(df)
        
        if not village_location_stats.empty:
            # Round values for display
            display_df = village_location_stats.copy()
            for col in ['Min Distance (km)', 'Max Distance (km)', 'Avg Distance (km)', 'Distance Range (km)']:
                display_df[col] = display_df[col].round(2)
            
            st.dataframe(display_df.sort_values('Points', ascending=False))
            
            # Visualization of village area coverage
            if len(display_df) > 1:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Sort by area covered
                plot_data = display_df.sort_values('Total Area Covered (km²)', ascending=False).head(10)
                
                ax.bar(plot_data['Village'], plot_data['Total Area Covered (km²)'])
                ax.set_xlabel('Village')
                ax.set_ylabel('Approximate Area Covered (km²)')
                ax.set_title('Area Coverage by Village (Top 10)')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
    
    with tab4:
        st.header("Distance Analysis")
        
        # Calculate interpoint distances
        with st.spinner("Calculating distances between points..."):
            distances_df = calculate_interpoint_distances(df)
        
        if not distances_df.empty:
            st.subheader("Point-to-Point Distance Statistics")
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Number of Point Pairs", len(distances_df))
            
            with col2:
                st.metric("Average Distance (km)", round(distances_df['distance_km'].mean(), 2))
            
            with col3:
                st.metric("Maximum Distance (km)", round(distances_df['distance_km'].max(), 2))
            
            with col4:
                st.metric("Minimum Distance (km)", round(distances_df['distance_km'].min(), 2))
            
            # Distance distribution visualization
            st.subheader("Distance Distribution")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Filter to distances under 20km for better visualization
            plot_data = distances_df[distances_df['distance_km'] <= 20]
            
            sns.histplot(plot_data['distance_km'], bins=30, kde=True, ax=ax)
            ax.set_xlabel('Distance (km)')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Distances Between Survey Points (≤20km)')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Distance analysis by village
            st.subheader("Within-Village vs Between-Village Distances")
            
            # Calculate stats
            same_village = distances_df[distances_df['same_village']]['distance_km']
            diff_village = distances_df[~distances_df['same_village']]['distance_km']
            
            col1, col2 = st.columns(2)
            
            with col1:
                if not same_village.empty:
                    st.metric("Avg Within-Village Distance (km)", round(same_village.mean(), 2))
                    st.metric("Max Within-Village Distance (km)", round(same_village.max(), 2))
                else:
                    st.warning("No within-village distance data available")
            
            with col2:
                if not diff_village.empty:
                    st.metric("Avg Between-Village Distance (km)", round(diff_village.mean(), 2))
                    st.metric("Max Between-Village Distance (km)", round(diff_village.max(), 2))
                else:
                    st.warning("No between-village distance data available")
            
            # Compare distributions
            if not same_village.empty and not diff_village.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Filter to distances under 20km for better visualization
                same_village_plot = same_village[same_village <= 20]
                diff_village_plot = diff_village[diff_village <= 20]
                
                if not same_village_plot.empty:
                    sns.histplot(same_village_plot, bins=20, alpha=0.5, label='Within Same Village', ax=ax)
                    
                if not diff_village_plot.empty:
                    sns.histplot(diff_village_plot, bins=20, alpha=0.5, label='Between Villages', ax=ax)
                
                ax.set_xlabel('Distance (km)')
                ax.set_ylabel('Frequency')
                ax.set_title('Comparison of Within-Village and Between-Village Distances')
                ax.legend()
                plt.tight_layout()
                st.pyplot(fig)
            
            # Distance table view (with filters)
            st.subheader("Point-to-Point Distance Table")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                min_dist = st.number_input("Minimum Distance (km)", 0.0, 100.0, 0.0, 0.1)
            with col2:
                max_dist = st.number_input("Maximum Distance (km)", 0.0, 100.0, 10.0, 0.1)
            with col3:
                same_village_only = st.checkbox("Same Village Only")
            
            # Apply filters
            filtered_distances = distances_df[
                (distances_df['distance_km'] >= min_dist) & 
                (distances_df['distance_km'] <= max_dist)
            ]
            
            if same_village_only:
                filtered_distances = filtered_distances[filtered_distances['same_village']]
            
            # Sort by distance
            filtered_distances = filtered_distances.sort_values('distance_km')
            
            # Clean for display
            display_cols = [
                'point1_id', 'point1_village', 'point2_id', 'point2_village', 
                'distance_km', 'same_village', 'same_surveyor'
            ]
            display_df = filtered_distances[display_cols].copy()
            display_df['distance_km'] = display_df['distance_km'].round(3)
            display_df.columns = [
                'Point 1 ID', 'Point 1 Village', 'Point 2 ID', 'Point 2 Village',
                'Distance (km)', 'Same Village', 'Same Surveyor'
            ]
            
            st.dataframe(display_df)
        else:
            st.warning("Insufficient location data for distance analysis")
    
    with tab5:
        st.header("Outlier Detection")
        
        # Tabs for different types of outlier detection
        outlier_tabs = st.tabs(["Location Outliers", "Surveyor Pattern Outliers", "Time Pattern Outliers"])
        
        with outlier_tabs[0]:
            st.subheader("Location Outliers")
            
            # Run outlier detection
            geo_df, outliers, extreme_outliers = detect_location_outliers(df)
            
            if not geo_df.empty:
                # Map with outliers
                st.write("The map below highlights potential outlier locations:")
                map_obj, _, _ = plot_all_locations(df, highlight_outliers=True)
                folium_static(map_obj, width=1000, height=500)
                
                # Outlier table
                if not outliers.empty:
                    st.subheader(f"Outlier Details ({len(outliers)} points)")
                    
                    display_cols = [
                        'submission_id', 'submitted_by', 'village', 'latitude', 'longitude', 
                        'distance_from_mean', 'distance_zscore'
                    ]
                    
                    display_df = outliers[display_cols].copy()
                    display_df['distance_from_mean'] = display_df['distance_from_mean'].round(2)
                    display_df['distance_zscore'] = display_df['distance_zscore'].round(2)
                    
                    display_df.columns = [
                        'Submission ID', 'Surveyor', 'Village', 'Latitude', 'Longitude',
                        'Distance from Mean (km)', 'Distance Z-Score'
                    ]
                    
                    st.dataframe(display_df.sort_values('Distance Z-Score', ascending=False))
                    
                    # Explanation
                    st.markdown("""
                    **How to interpret:**
                    - **Distance from Mean**: Physical distance from the average location of all points
                    - **Distance Z-Score**: Number of standard deviations away from the mean distance
                    - Z-scores above 2.5 indicate potential outliers
                    - Z-scores above 3.5 indicate extreme outliers that should be carefully reviewed
                    """)
                else:
                    st.success("No location outliers detected in the data.")
            else:
                st.warning("Insufficient location data for outlier detection.")
        
        with outlier_tabs[1]:
            st.subheader("Surveyor Pattern Outliers")
            
            # Run surveyor pattern analysis
            analysis_df = analyze_surveyor_patterns(df)
            
            if not analysis_df.empty:
                # Filter to only show outliers
                pattern_outliers = analysis_df[analysis_df['Status'] != "Normal"]
                
                if not pattern_outliers.empty:
                    st.subheader(f"Detected Pattern Outliers ({len(pattern_outliers)} surveyors)")
                    st.dataframe(pattern_outliers)
                    
                    # Visualize outlier patterns
                    st.subheader("Outlier Pattern Visualization")
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Create scatter plot of submissions vs distance
                    sns.scatterplot(
                        data=analysis_df,
                        x='Submissions',
                        y='Avg Distance (km)',
                        hue='Status',
                        size='Villages Covered',
                        sizes=(50, 200),
                        alpha=0.7,
                        ax=ax
                    )
                    
                    ax.set_xlabel('Number of Submissions')
                    ax.set_ylabel('Average Distance Between Points (km)')
                    ax.set_title('Surveyor Pattern Analysis: Submissions vs Distance')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Explanation
                    st.markdown("""
                    **Surveyor Pattern Outliers might indicate:**
                    1. **Large area coverage**: Unusually large distances between points could indicate transportation by vehicle instead of walking surveys, or data entry errors
                    2. **High submissions in single village**: Excessive submissions in a single location may need verification
                    3. **High submission rate**: Unusually high number of surveys per day might indicate quality concerns
                    """)
                else:
                    st.success("No surveyor pattern outliers detected in the data.")
            else:
                st.warning("Insufficient data for surveyor pattern analysis.")
        
        with outlier_tabs[2]:
            st.subheader("Time Pattern Outliers")
            
            if 'timestamp' in df.columns and not df['timestamp'].isna().all():
                # Analyze time patterns
                time_analysis = detect_time_outliers(df)
                
                if not time_analysis.empty:
                    # Filter to only time outliers
                    time_outliers = time_analysis[time_analysis['time_outlier_status'] != 'Normal']
                    
                    if not time_outliers.empty:
                        st.subheader(f"Detected Time Pattern Outliers ({len(time_outliers)} surveyors)")
                        
                        display_cols = [
                            'submitted_by', 'avg_submissions', 'max_submissions', 
                            'std_submissions', 'total_days', 'total_submissions'
                        ]
                        
                        display_df = time_outliers[display_cols].copy()
                        
                        # Round values
                        for col in ['avg_submissions', 'std_submissions']:
                            display_df[col] = display_df[col].round(2)
                        
                        display_df.columns = [
                            'Surveyor', 'Avg Submissions/Day', 'Max Submissions/Day',
                            'Std Dev', 'Active Days', 'Total Submissions'
                        ]
                        
                        st.dataframe(display_df.sort_values('Max Submissions/Day', ascending=False))
                        
                        # Visualize daily submission patterns
                        st.subheader("Daily Submission Patterns")
                        
                        # Convert timestamp to datetime if needed
                        time_df = df.copy()
                        if pd.api.types.is_string_dtype(time_df['timestamp']):
                            time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
                        
                        # Create date field
                        time_df['date'] = time_df['timestamp'].dt.date
                        
                        # Create daily counts by surveyor
                        daily_counts = time_df.groupby(['submitted_by', 'date']).size().reset_index(name='submissions')
                        
                        # Filter to just the outliers for plotting
                        outlier_surveyors = time_outliers['submitted_by'].tolist()
                        plot_data = daily_counts[daily_counts['submitted_by'].isin(outlier_surveyors)]
                        
                        if len(plot_data) > 0:
                            fig, ax = plt.subplots(figsize=(10, 6))
                            
                            sns.lineplot(
                                data=plot_data,
                                x='date',
                                y='submissions',
                                hue='submitted_by',
                                markers=True,
                                ax=ax
                            )
                            
                            ax.set_xlabel('Date')
                            ax.set_ylabel('Submissions')
                            ax.set_title('Daily Submission Patterns for Outlier Surveyors')
                            plt.xticks(rotation=45)
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            # Explanation
                            st.markdown("""
                            **Time Pattern Outliers might indicate:**
                            1. **High volume days**: Days with unusually high number of submissions might suggest rushed surveys
                            2. **Irregular patterns**: Highly variable submission counts might indicate inconsistent field work
                            3. **Batch submissions**: Multiple surveys submitted at exactly the same time might indicate offline data collection
                            """)
                    else:
                        st.success("No time pattern outliers detected in the data.")
                else:
                    st.warning("Insufficient data for time pattern analysis.")
            else:
                st.warning("Timestamp data is required for time pattern analysis. No timestamps found in the current dataset.")
    
    # Footer with download options
    st.header("Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Surveyor Analysis"):
            csv = analysis_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="surveyor_analysis.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download Village Analysis"):
            if not village_location_stats.empty:
                csv = village_location_stats.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="village_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No village analysis data available to download")
    
    with col3:
        if st.button("Download Full Dataset"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="full_survey_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()