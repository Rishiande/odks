import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString
import folium
from streamlit_folium import folium_static
import math
from datetime import datetime, timedelta
from scipy import stats
import itertools
from folium.plugins import HeatMap, MarkerCluster, MeasureControl
import branca.colormap as cm
import plotly.express as px
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from dotenv import load_dotenv
import os
from dateutil.parser import parse

# Set page config as the first Streamlit command
st.set_page_config(layout="wide", page_title="Survey Analysis Dashboard")

# Load environment variables from .env file
load_dotenv()

# Configuration
ODK_USERNAME = "rushi@tnodk01.ii.com"
ODK_PASSWORD = "rushi2025&"
AZURE_MAPS_API_KEY = "944BjlSA5zZyX94AAvM2mM4gIRV005pWgXAOpFbvVNEWSGmFMEm7JQQJ99BDACYeBjFgSQNNAAAgAZMP3Cok"
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")  # Fallback to localhost if not set

# MongoDB setup with error handling
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test the connection
    db = client["survey_analysis"]
    collection = db["submissions"]
    mongo_connected = True
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    mongo_connected = False
    client = None
    db = None
    collection = None

# Updated forms dictionary
forms = {
    "Server 1": {
        "TN Master": {
            "Master Landscape Survey 04-2025 ODK XLSForm": {
                "project_id": 3,
                "form_id": "Master Landscape Survey 04-2025 ODK XLSForm"
            }
        },
        "BK TN AC Landscape": {
            "201-Cumbum": {"project_id": 4, "form_id": "201-Cumbum Landscape Survey 04-2025"},
            "39-Sholingur": {"project_id": 4, "form_id": "39-Sholingur Landscape Survey 04-2025"},
            "155-Cuddalore": {"project_id": 4, "form_id": "155-Cuddalore Landscape Survey 04-2025"},
            "66-Polur": {"project_id": 4, "form_id": "66-Polur Landscape Survey 04-2025"},
            "144-Manachanallur": {"project_id": 4, "form_id": "144-Manachanallur Landscape Survey 04-2025"},
            "145-Musiri": {"project_id": 4, "form_id": "145-Musiri Landscape Survey 04-2025"},
            "56-Thalli": {"project_id": 4, "form_id": "56-Thalli Landscape Survey 04-2025"},
            "3-Thirutthani": {"project_id": 4, "form_id": "3-Thirutthani Landscape Survey 04-2025"},
            "146-Thuraiyur": {"project_id": 4, "form_id": "146. Thuraiyur (SC) Landscape Survey 04-2025"},
            "182-Alangudi": {"project_id": 4, "form_id": "182-Alangudi Landscape Survey 04-2025"},
            "137-Kulithalai": {"project_id": 4, "form_id": "137-Kulithalai Landscape Survey 04-2025"},
            "12-Perambur": {"project_id": 4, "form_id": "12-Perambur Landscape Survey 04-2025"},
            "171-Kumbakonam": {"project_id": 4, "form_id": "171-Kumbakonam Landscape Survey 04-2025"},
            "150-Jayankondam": {"project_id": 4, "form_id": "150-Jayankondam Landscape Survey 04-2025"},
            "132-Dindigul": {"project_id": 4, "form_id": "132 Dindigul Landscape Survey 04-2025"},
            "20-Thousand Lights": {"project_id": 4, "form_id": "20-Thousand Lights Landscape Survey 04-2025"},
            "37-Kancheepuram": {"project_id": 4, "form_id": "37-Kancheepuram Landscape Survey 04-2025"},
            "136-Krishnarayapuram": {"project_id": 4, "form_id": "136-Krishnarayapuram (SC) Landscape Survey 04-2025"},
            "38-Arakkonam": {"project_id": 4, "form_id": "38-Arakkonam (SC) Landscape Survey 04-2025"},
            "200-Bodinayakanur": {"project_id": 4, "form_id": "200-Bodinayakanur Landscape Survey 04-2025"},
            "118-Coimbatore North": {"project_id": 4, "form_id": "118-Coimbatore North Landscape Survey 04-2025"},
            "189-Madurai East": {"project_id": 4, "form_id": "189-Madurai East Landscape Survey 04-2025"},
            "103-Perundurai": {"project_id": 4, "form_id": "103-Perundurai Landscape Survey 04-2025"},
            "199-Periyakulam": {"project_id": 4, "form_id": "199. Periyakulam (SC) Landscape Survey 04-2025"},
            "149-Ariyalur": {"project_id": 4, "form_id": "149-Ariyalur Landscape Survey 04-2025"},
            "135-Karur": {"project_id": 4, "form_id": "135-Karur Landscape Survey 04-2025"},
            "138-Manapparai": {"project_id": 4, "form_id": "138-Manapparai Landscape Survey 04-2025"},
            "152-Vriddhachalam": {"project_id": 4, "form_id": "152-Vriddhachalam Landscape Survey 04-2025"},
            "153-Neyveli": {"project_id": 4, "form_id": "153-Neyveli Landscape Survey 04-2025"},
            "156-Kurinjipadi": {"project_id": 4, "form_id": "156-Kurinjipadi Landscape Survey 04-2025"},
            "161-Mayiladuthurai": {"project_id": 4, "form_id": "161-Mayiladuthurai Landscape Survey 04-2025"},
            "166-Thiruthuraipoondi": {"project_id": 4, "form_id": "166-Thiruthuraipoondi (SC) Landscape Survey 04-2025"},
            "178-Gandharvakottai": {"project_id": 4, "form_id": "178-Gandharvakottai (SC) Landscape Survey 04-2025 copy 3"},
            "198-Andipatti": {"project_id": 4, "form_id": "198-Andipatti Landscape Survey 04-2025"},
            "51-Uthangarai": {"project_id": 4, "form_id": "51-Uthangarai (SC) Landscape Survey 04-2025"},
            "60-Pappireddippatti": {"project_id": 4, "form_id": "60-Pappireddippatti Landscape Survey 04-2025"},
            "61-Harur": {"project_id": 4, "form_id": "61-Harur (SC) Landscape Survey 04-2025"},
            "180-Pudukkottai": {"project_id": 4, "form_id": "180-Pudukkottai Landscape Survey 04-2025"},
            "158-Chidambaram": {"project_id": 4, "form_id": "158-Chidambaram Landscape Survey 04-2025"},
            "216-Srivaikuntam Landscape Survey 04-2025": {"project_id": 4, "form_id": "216-Srivaikuntam Landscape Survey 04-2025"},
            "133-Vedasandur Landscape Survey 04-2025": {"project_id": 4, "form_id": "133-Vedasandur Landscape Survey 04-2025"},
            "110-Coonoor Landscape Survey 04-2025": {"project_id": 4, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "109-Gudalur (SC) Landscape Survey 04-2025": {"project_id": 4, "form_id": "109-Gudalur (SC) Landscape Survey 04-2025"}
        },
        "03 TN AC Landscape": {
            "110-Coonoor": {"project_id": 5, "form_id": "110-Coonoor Landscape Survey 04-2025"},
            "222-Tenkasi": {"project_id": 5, "form_id": "222-Tenkasi Landscape Survey 04-2025"},
            "223-Alangulam": {"project_id": 5, "form_id": "223-Alangulam Landscape Survey 04-2025"},
            "48-Ambur": {"project_id": 5, "form_id": "48-AmburLandscape Survey 04-2025"},
            "49-Jolarpet": {"project_id": 5, "form_id": "49-Jolarpet Landscape Survey 04-2025"},
            "63-Tiruvannamalai": {"project_id": 5, "form_id": "63-Tiruvannamalai Landscape Survey 04-2025"},
            "64-Kilpennathur": {"project_id": 5, "form_id": "64-KilpennathurLandscape Survey 04-2025"},
            "65-Kalasapakkam": {"project_id": 5, "form_id": "65-Kalasapakkam Landscape Survey 04-2025"},
            "67-Arani": {"project_id": 5, "form_id": "67-Arani Landscape Survey 04-2025"},
            "68-Cheyyar": {"project_id": 5, "form_id": "68-Cheyyar Landscape Survey 04-2025"}
        },
        "04 TN AC Landscape": {
            "183-Aranthangi": {"project_id": 6, "form_id": "183-Aranthangi Landscape Survey 04-2025"},
            "181-Thirumayam": {"project_id": 6, "form_id": "181-Thirumayam Landscape Survey 04-2025"}
        }
    }
}

# Helper function to validate coordinates
def validate_coordinates(lat, lon):
    """Validate latitude and longitude values."""
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90):
            return False, f"Latitude {lat} is out of range [-90, 90]"
        if not (-180 <= lon <= 180):
            return False, f"Longitude {lon} is out of range [-180, 180]"
        return True, None
    except (ValueError, TypeError):
        return False, f"Invalid coordinate values: lat={lat}, lon={lon}"

# Helper functions
def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on earth in kilometers."""
    # Validate coordinates
    valid1, error1 = validate_coordinates(lat1, lon1)
    valid2, error2 = validate_coordinates(lat2, lon2)
    if not valid1:
        raise ValueError(error1)
    if not valid2:
        raise ValueError(error2)

    R = 6371  # Earth radius in km

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def calculate_interpoint_distances(df):
    """Calculate distances between all pairs of points in the dataframe."""
    valid_df = df.dropna(subset=['latitude', 'longitude'])

    if len(valid_df) <= 1:
        return pd.DataFrame(columns=['point1_id', 'point2_id', 'distance_km'])

    # Validate all coordinates
    invalid_coords = []
    for idx, row in valid_df.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Found {len(invalid_coords)} invalid coordinates. Skipping these points.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        valid_df = valid_df[~valid_df['submission_id'].isin([x[0] for x in invalid_coords])]

    if len(valid_df) <= 1:
        return pd.DataFrame(columns=['point1_id', 'point2_id', 'distance_km'])

    distances = []

    for i, row1 in valid_df.iterrows():
        for j, row2 in valid_df.iterrows():
            if i < j:
                try:
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
                except ValueError as e:
                    st.warning(f"Error calculating distance between {row1['submission_id']} and {row2['submission_id']}: {str(e)}")

    return pd.DataFrame(distances)

def fetch_submissions(project_id, form_id):
    """Fetch all submissions from ODK Central for specific project and form."""
    try:
        form_api_url = f"https://tnodk01.indiaintentions.com/v1/projects/{project_id}/forms/{form_id.replace(' ', '%20')}.svc/Submissions"
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
    """Parse a single submission into a structured format."""
    try:
        group_six = submission.get("group_six", {})

        submission_date = None
        instance_id = submission.get("meta", {}).get("instanceID", "")
        if instance_id:
            try:
                parts = instance_id.split(':')
                if len(parts) > 1:
                    date_parts = parts[1].split('-')
                    if len(date_parts) >= 3:
                        submission_date = f"{date_parts[0][:4]}-{date_parts[0][4:6]}-{date_parts[0][6:8]}"
            except:
                submission_date = instance_id

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
            "timestamp": submission.get("__system", {}).get("submissionDate", ""),
            "fetch_timestamp": datetime.utcnow().isoformat()
        }

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

def clean_name(name):
    """Clean surveyor names by removing unwanted characters, converting to lowercase, and stripping spaces."""
    if pd.isna(name):
        return ""
    name = str(name).lower().strip()
    return ''.join(char for char in name if char.isalnum() or char in [' ', '.', '-'])

def load_data_from_mongodb(project_id, form_id):
    """Load data from MongoDB if it's recent, otherwise return None."""
    if not mongo_connected:
        return None

    try:
        cache_key = f"project_{project_id}_form_{form_id}"
        cached_data = collection.find_one({"cache_key": cache_key})

        if cached_data:
            fetch_time = parse(cached_data["fetch_timestamp"])
            if datetime.utcnow() - fetch_time < timedelta(hours=1):
                return pd.DataFrame(cached_data["data"])
            else:
                collection.delete_one({"cache_key": cache_key})
                return None
        return None
    except Exception as e:
        st.warning(f"Error loading data from MongoDB: {str(e)}. Falling back to ODK.")
        return None

def save_data_to_mongodb(project_id, form_id, df):
    """Save data to MongoDB with a fetch timestamp."""
    if not mongo_connected:
        return

    try:
        cache_key = f"project_{project_id}_form_{form_id}"
        collection.delete_one({"cache_key": cache_key})
        collection.insert_one({
            "cache_key": cache_key,
            "fetch_timestamp": datetime.utcnow().isoformat(),
            "data": df.to_dict("records")
        })
    except Exception as e:
        st.warning(f"Error saving data to MongoDB: {str(e)}")

def analyze_surveyor_patterns(df):
    """Analyze surveyor patterns and identify if they're collecting from same/different locations."""
    results = []

    for surveyor in df['submitted_by'].unique():
        surveyor_data = df[df['submitted_by'] == surveyor]
        num_submissions = len(surveyor_data)
        villages = surveyor_data['village'].nunique()
        blocks = surveyor_data['block'].nunique()
        missing_coords = surveyor_data['missing_coordinates'].sum()

        location_diversity = "Low"
        avg_distance = 0
        submission_rate = None

        if num_submissions > 1:
            distances = []
            coords_df = surveyor_data[['latitude', 'longitude']].dropna()

            # Validate coordinates
            invalid_coords = []
            for idx, row in coords_df.iterrows():
                valid, error = validate_coordinates(row['latitude'], row['longitude'])
                if not valid:
                    invalid_coords.append((idx, error))

            if invalid_coords:
                st.warning(f"Surveyor {surveyor}: Found {len(invalid_coords)} invalid coordinates.")
                for idx, error in invalid_coords:
                    st.warning(f"Index {idx}: {error}")
                coords_df = coords_df.drop([x[0] for x in invalid_coords])

            coords = coords_df.values

            for i in range(len(coords)):
                for j in range(i+1, len(coords)):
                    lat1, lon1 = coords[i]
                    lat2, lon2 = coords[j]
                    try:
                        distance = haversine_distance(lat1, lon1, lat2, lon2)
                        distances.append(distance)
                    except ValueError as e:
                        st.warning(f"Surveyor {surveyor}: Error calculating distance: {str(e)}")

            if distances:
                avg_distance = sum(distances) / len(distances)
                if avg_distance > 3.0:
                    location_diversity = "High"
                elif avg_distance > 1.0:
                    location_diversity = "Medium"
                else:
                    location_diversity = "Low"

            try:
                if 'timestamp' in surveyor_data.columns and not surveyor_data['timestamp'].isna().all():
                    timestamps = pd.to_datetime(surveyor_data['timestamp'], utc=True)
                    if not timestamps.empty:
                        date_range = (timestamps.max() - timestamps.min()).days + 1
                        if date_range > 0:
                            submission_rate = num_submissions / date_range
                            submission_rate = round(submission_rate, 2)
            except Exception as e:
                st.warning(f"Surveyor {surveyor}: Error calculating submission rate: {str(e)}")

        outlier_status = "Normal"
        if avg_distance > 10:
            outlier_status = "Potential outlier: Large area coverage"
        elif num_submissions > 20 and villages == 1:
            outlier_status = "Potential outlier: High submissions in single village"
        elif submission_rate and submission_rate > 15:
            outlier_status = "Potential outlier: High submission rate"
        elif missing_coords > 0:
            outlier_status = f"Potential outlier: {missing_coords} submissions with missing coordinates"

        results.append({
            "Surveyor": surveyor,
            "Submissions": num_submissions,
            "Villages Covered": villages,
            "Blocks Covered": blocks,
            "Location Diversity": location_diversity,
            "Avg Distance (km)": round(avg_distance, 2),
            "Submissions/Day": submission_rate,
            "Missing Coordinates": missing_coords,
            "Status": outlier_status,
            "Primary Village": surveyor_data['village'].mode()[0] if not surveyor_data['village'].empty else "",
            "Primary Block": surveyor_data['block'].mode()[0] if not surveyor_data['block'].empty else ""
        })

    return pd.DataFrame(results)

def detect_location_outliers(df):
    """Detect outliers in survey locations using statistical methods."""
    geo_df = df.dropna(subset=['latitude', 'longitude']).copy()

    if len(geo_df) <= 5:
        return pd.DataFrame(), [], []

    # Validate coordinates
    invalid_coords = []
    for idx, row in geo_df.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Found {len(invalid_coords)} invalid coordinates in outlier detection.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        geo_df = geo_df[~geo_df['submission_id'].isin([x[0] for x in invalid_coords])]

    if len(geo_df) <= 5:
        return pd.DataFrame(), [], []

    geo_df['lat_zscore'] = stats.zscore(geo_df['latitude'])
    geo_df['lon_zscore'] = stats.zscore(geo_df['longitude'])

    mean_lat = geo_df['latitude'].mean()
    mean_lon = geo_df['longitude'].mean()

    geo_df['distance_from_mean'] = geo_df.apply(
        lambda row: haversine_distance(row['latitude'], row['longitude'], mean_lat, mean_lon),
        axis=1
    )

    geo_df['distance_zscore'] = stats.zscore(geo_df['distance_from_mean'])

    outliers = geo_df[(abs(geo_df['lat_zscore']) > 2.5) |
                      (abs(geo_df['lon_zscore']) > 2.5) |
                      (abs(geo_df['distance_zscore']) > 2.5)]

    extreme_outliers = geo_df[(abs(geo_df['lat_zscore']) > 3.5) |
                              (abs(geo_df['lon_zscore']) > 3.5) |
                              (abs(geo_df['distance_zscore']) > 3.5)]

    return geo_df, outliers, extreme_outliers

def detect_time_outliers(df):
    """Detect outliers in submission timing patterns."""
    if 'timestamp' not in df.columns or df['timestamp'].isna().all():
        return pd.DataFrame()

    time_df = df.copy()

    if pd.api.types.is_string_dtype(time_df['timestamp']):
        time_df['timestamp'] = pd.to_datetime(time_df['timestamp'], utc=True)

    time_df['date'] = time_df['timestamp'].dt.date
    daily_counts = time_df.groupby(['submitted_by', 'date']).size().reset_index(name='submissions_per_day')

    surveyor_stats = daily_counts.groupby('submitted_by').agg(
        avg_submissions=('submissions_per_day', 'mean'),
        max_submissions=('submissions_per_day', 'max'),
        std_submissions=('submissions_per_day', 'std'),
        total_days=('date', 'count'),
        total_submissions=('submissions_per_day', 'sum')
    ).reset_index()

    surveyor_stats['std_submissions'] = surveyor_stats['std_submissions'].fillna(0)

    overall_mean = daily_counts['submissions_per_day'].mean()
    overall_std = daily_counts['submissions_per_day'].std()

    high_threshold = overall_mean + 2 * overall_std

    surveyor_stats['time_outlier_status'] = 'Normal'
    surveyor_stats.loc[surveyor_stats['max_submissions'] > high_threshold, 'time_outlier_status'] = 'Potential time outlier'

    return surveyor_stats

def plot_surveyor_locations(df, surveyor, plot_distances=False):
    """Plot a surveyor's data collection locations on a map."""
    surveyor_data = df[df['submitted_by'] == surveyor].dropna(subset=['latitude', 'longitude'])

    # Validate coordinates
    invalid_coords = []
    for idx, row in surveyor_data.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Surveyor {surveyor}: Found {len(invalid_coords)} invalid coordinates in map plotting.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        surveyor_data = surveyor_data[~surveyor_data['submission_id'].isin([x[0] for x in invalid_coords])]

    if surveyor_data.empty:
        st.warning(f"No valid location data available for {surveyor}")
        return None

    avg_lat = surveyor_data['latitude'].mean()
    avg_lon = surveyor_data['longitude'].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    MeasureControl(position='topright', primary_length_unit='kilometers').add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

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

    if plot_distances and len(surveyor_data) > 1:
        points = surveyor_data[['submission_id', 'latitude', 'longitude']].values

        min_distance = 0
        max_distance = 10
        colormap = cm.LinearColormap(
            colors=['green', 'yellow', 'orange', 'red'],
            vmin=min_distance,
            vmax=max_distance
        )

        for i in range(len(points)):
            for j in range(i+1, len(points)):
                point1 = points[i]
                point2 = points[j]

                id1, lat1, lon1 = point1
                id2, lat2, lon2 = point2

                try:
                    distance = haversine_distance(lat1, lon1, lat2, lon2)
                    if distance < 20:
                        color = colormap(min(distance, max_distance))

                        folium.PolyLine(
                            locations=[(lat1, lon1), (lat2, lon2)],
                            color=color,
                            weight=2,
                            opacity=0.7,
                            tooltip=f"Distance: {distance:.2f} km"
                        ).add_to(m)
                except ValueError as e:
                    st.warning(f"Error plotting distance between {id1} and {id2}: {str(e)}")

        colormap.caption = 'Distance (km)'
        colormap.add_to(m)

    heat_data = [[row['latitude'], row['longitude']] for _, row in surveyor_data.iterrows()]
    HeatMap(heat_data).add_to(m)

    return m

def plot_all_locations(df, highlight_outliers=True):
    """Plot all survey locations on a map, highlighting outliers."""
    geo_df = df.dropna(subset=['latitude', 'longitude']).copy()

    # Validate coordinates
    invalid_coords = []
    for idx, row in geo_df.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Found {len(invalid_coords)} invalid coordinates in map plotting.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        geo_df = geo_df[~geo_df['submission_id'].isin([x[0] for x in invalid_coords])]

    if geo_df.empty:
        st.warning("No valid location data available")
        return None, pd.DataFrame(), pd.DataFrame()

    if highlight_outliers:
        processed_df, outliers, extreme_outliers = detect_location_outliers(geo_df)
    else:
        processed_df, outliers, extreme_outliers = geo_df, pd.DataFrame(), pd.DataFrame()

    avg_lat = geo_df['latitude'].mean()
    avg_lon = geo_df['longitude'].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    MeasureControl(position='topright', primary_length_unit='kilometers').add_to(m)

    normal_cluster = MarkerCluster(name="Normal Points").add_to(m)
    outlier_cluster = MarkerCluster(name="Potential Outliers").add_to(m)

    for idx, row in geo_df.iterrows():
        popup_text = (
            f"<b>Village:</b> {row['village']}<br>"
            f"<b>Surveyor:</b> {row['submitted_by']}<br>"
            f"<b>Respondent:</b> {row['respondent_name']}<br>"
            f"<b>Submission ID:</b> {row['submission_id']}"
        )

        is_outlier = False
        is_extreme = False

        if highlight_outliers and not outliers.empty:
            is_outlier = row['submission_id'] in outliers['submission_id'].values
            is_extreme = row['submission_id'] in extreme_outliers['submission_id'].values

        if is_extreme:
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text + "<br><b>Status:</b> Extreme Outlier", max_width=300),
                tooltip=f"{row['village']} (Extreme Outlier)",
                icon=folium.Icon(color='red', icon='warning-sign')
            ).add_to(outlier_cluster)
        elif is_outlier:
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text + "<br><b>Status:</b> Potential Outlier", max_width=300),
                tooltip=f"{row['village']} (Outlier)",
                icon=folium.Icon(color='orange', icon='info-sign')
            ).add_to(outlier_cluster)
        else:
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['village']}",
                icon=folium.Icon(color='blue')
            ).add_to(normal_cluster)

    folium.LayerControl().add_to(m)

    return m, outliers, extreme_outliers

def analyze_village_distance_distribution(df):
    """Analyze the distribution of distances within villages."""
    if 'village' not in df.columns or df['village'].isna().all():
        return pd.DataFrame()

    geo_df = df.dropna(subset=['latitude', 'longitude']).copy()

    if len(geo_df) <= 1:
        return pd.DataFrame()

    # Validate coordinates
    invalid_coords = []
    for idx, row in geo_df.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Found {len(invalid_coords)} invalid coordinates in village analysis.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        geo_df = geo_df[~geo_df['submission_id'].isin([x[0] for x in invalid_coords])]

    if len(geo_df) <= 1:
        return pd.DataFrame()

    results = []

    for village in geo_df['village'].unique():
        village_data = geo_df[geo_df['village'] == village]

        if len(village_data) <= 1:
            continue

        distances = []
        for i, row1 in village_data.iterrows():
            for j, row2 in village_data.iterrows():
                if i < j:
                    try:
                        dist = haversine_distance(
                            row1['latitude'], row1['longitude'],
                            row2['latitude'], row2['longitude']
                        )
                        distances.append(dist)
                    except ValueError as e:
                        st.warning(f"Village {village}: Error calculating distance: {str(e)}")

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
    """Calculate an approximate area covered by the points in square kilometers."""
    if len(points_df) <= 2:
        return 0

    # Validate coordinates
    invalid_coords = []
    for idx, row in points_df.iterrows():
        valid, error = validate_coordinates(row['latitude'], row['longitude'])
        if not valid:
            invalid_coords.append((row['submission_id'], error))

    if invalid_coords:
        st.warning(f"Found {len(invalid_coords)} invalid coordinates in area calculation.")
        for submission_id, error in invalid_coords:
            st.warning(f"Submission {submission_id}: {error}")
        points_df = points_df[~points_df['submission_id'].isin([x[0] for x in invalid_coords])]

    if len(points_df) <= 2:
        return 0

    lat_range = points_df['latitude'].max() - points_df['latitude'].min()
    lon_range = points_df['longitude'].max() - points_df['longitude'].min()

    lat_km = lat_range * 111
    lon_km = lon_range * 111 * math.cos(math.radians(points_df['latitude'].mean()))

    rectangular_area = lat_km * lon_km

    correction_factor = 0.8 if len(points_df) > 5 else 0.6

    return round(rectangular_area * correction_factor, 2)

# Main Streamlit app
def main():
    if mongo_connected:
        st.success("Successfully connected to MongoDB!")
    else:
        st.error("Failed to connect to MongoDB. Falling back to direct ODK fetching.")

    st.title("Landscape Survey Analysis Dashboard")

    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()
    if 'original_df' not in st.session_state:
        st.session_state.original_df = pd.DataFrame()
    if 'last_fetch_time' not in st.session_state:
        st.session_state.last_fetch_time = None

    with st.sidebar:
        st.header("Filters")

        selected_server = st.selectbox(
            "Select Server",
            list(forms.keys()),
            index=0
        )

        available_projects = list(forms[selected_server].keys())
        selected_project = st.selectbox(
            "Select Project",
            available_projects,
            index=0
        )

        available_forms = list(forms[selected_server][selected_project].keys())
        selected_form = st.selectbox(
            "Select Form",
            available_forms,
            index=0
        )

        project_id = forms[selected_server][selected_project][selected_form]["project_id"]
        form_id = forms[selected_server][selected_project][selected_form]["form_id"]

        if st.button("Refresh ODK Server Data"):
            with st.spinner("Fetching latest data from ODK server..."):
                submissions = fetch_submissions(project_id, form_id)
                if submissions:
                    parsed_data = [parse_submission(sub) for sub in submissions.get("value", [])]
                    df = pd.DataFrame([d for d in parsed_data if d is not None])

                    if 'submitted_by' in df.columns:
                        df['submitted_by'] = df['submitted_by'].apply(clean_name)
                        df = df[df['submitted_by'] != '']

                    df['missing_coordinates'] = df[['latitude', 'longitude']].isna().any(axis=1)

                    st.session_state.df = df.copy()
                    st.session_state.original_df = df.copy()
                    st.session_state.last_fetch_time = datetime.now()

                    save_data_to_mongodb(project_id, form_id, df)

                    st.success("Data refreshed successfully!")
                else:
                    st.error("Failed to fetch data from ODK server.")

        if st.session_state.df.empty:
            with st.spinner("Loading data..."):
                df = load_data_from_mongodb(project_id, form_id)

                if df is None:
                    submissions = fetch_submissions(project_id, form_id)
                    if submissions:
                        parsed_data = [parse_submission(sub) for sub in submissions.get("value", [])]
                        df = pd.DataFrame([d for d in parsed_data if d is not None])

                        if 'submitted_by' in df.columns:
                            df['submitted_by'] = df['submitted_by'].apply(clean_name)
                            df = df[df['submitted_by'] != '']

                        df['missing_coordinates'] = df[['latitude', 'longitude']].isna().any(axis=1)

                        save_data_to_mongodb(project_id, form_id, df)

                        st.session_state.last_fetch_time = datetime.now()
                    else:
                        df = pd.DataFrame()
                st.session_state.df = df.copy()
                st.session_state.original_df = df.copy()

        if st.session_state.last_fetch_time:
            st.write(f"Last fetched: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")

        st.metric("Overall Total Submissions", len(st.session_state.original_df) if not st.session_state.original_df.empty else 0)

    if st.session_state.df.empty:
        st.warning("No data available for the selected filters")
        return

    df = st.session_state.df.copy()

    if df.empty:
        st.warning("No data available for the selected filters")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Surveyor Analysis",
        "Location Analysis",
        "Distance Analysis",
        "Outlier Detection"
    ])

    with tab1:
        st.header("Survey Overview")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Submissions", len(df))

        with col2:
            st.metric("Unique Surveyors", df['submitted_by'].nunique())

        with col3:
            st.metric("Villages Covered", df['village'].nunique())

        with col4:
            st.metric("Blocks Covered", df['block'].nunique())

        with col5:
            missing_coords_count = df['missing_coordinates'].sum()
            st.metric("Submissions with Missing Coordinates", missing_coords_count)

        if missing_coords_count > 0:
            st.subheader("Missing Coordinates Distribution by Surveyor")
            missing_by_surveyor = df[df['missing_coordinates']].groupby('submitted_by').size().reset_index(name='count')
            fig = px.bar(
                missing_by_surveyor,
                x='submitted_by',
                y='count',
                title='Submissions with Missing Coordinates by Surveyor',
                labels={'submitted_by': 'Surveyor', 'count': 'Number of Submissions'},
                text='count',
                color_discrete_sequence=['#FF4D4D']
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title="Surveyor",
                yaxis_title="Number of Submissions",
                xaxis_tickangle=-45,
                height=400,
                width=1000
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("All Survey Locations")

        if 'latitude' in df.columns and 'longitude' in df.columns:
            map_obj, outliers, extreme_outliers = plot_all_locations(df)
            if map_obj:
                folium_static(map_obj, width=1000, height=500)

                if not outliers.empty:
                    st.info(f"Detected {len(outliers)} potential location outliers, including {len(extreme_outliers)} extreme outliers.")
            else:
                st.warning("Unable to display map: No valid location data available")

        st.subheader("Village Coverage")
        village_stats = df.groupby('village').agg({
            'submitted_by': 'nunique',
            'submission_id': 'count',
            'missing_coordinates': 'sum'
        }).rename(columns={
            'submitted_by': 'Surveyors',
            'submission_id': 'Submissions',
            'missing_coordinates': 'Missing Coordinates'
        }).sort_values('Submissions', ascending=False)

        st.dataframe(village_stats)

        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            st.subheader("Submission Timeline")

            if pd.api.types.is_string_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

            df['date'] = df['timestamp'].dt.date
            daily_counts = df.groupby('date').size().reset_index(name='submissions')

            fig = px.bar(
                daily_counts,
                x='date',
                y='submissions',
                title='Daily Submission Counts',
                labels={'date': 'Date', 'submissions': 'Number of Submissions'},
                text='submissions'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Submissions",
                xaxis_tickangle=-45,
                height=400,
                width=1000
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Surveyor Performance Analysis")

        analysis_df = analyze_surveyor_patterns(df)

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

        st.dataframe(analysis_df.sort_values("Submissions", ascending=False))

        st.subheader("Surveyor Performance Visualizations")

        col1, col2 = st.columns(2)

        with col1:
            if not analysis_df.empty:
                plot_data = analysis_df.sort_values('Submissions', ascending=False).head(10)
                colors = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
                plot_data['Color'] = plot_data['Location Diversity'].map(colors).fillna('blue')

                fig = px.bar(
                    plot_data,
                    x='Surveyor',
                    y='Submissions',
                    title='Top 10 Surveyors by Submission Count',
                    labels={'Surveyor': 'Surveyor', 'Submissions': 'Number of Submissions'},
                    color='Color',
                    color_discrete_map={'green': 'green', 'orange': 'orange', 'red': 'red', 'blue': 'blue'},
                    text='Submissions'
                )
                fig.update_traces(textposition='outside', showlegend=False)
                fig.update_layout(
                    xaxis_title="Surveyor",
                    yaxis_title="Number of Submissions",
                    xaxis_tickangle=-45,
                    height=500,
                    width=600,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("""
                **Location Diversity Color Code:**
                - 🟢 High: Wide area coverage (>3km average distance)
                - 🟠 Medium: Moderate area coverage (1-3km average distance)
                - 🔴 Low: Concentrated area (<1km average distance)
                """)

        with col2:
            if not analysis_df.empty:
                plot_data = analysis_df.sort_values('Villages Covered', ascending=False).head(10)

                fig = px.bar(
                    plot_data,
                    x='Surveyor',
                    y='Villages Covered',
                    title='Top 10 Surveyors by Village Coverage',
                    labels={'Surveyor': 'Surveyor', 'Villages Covered': 'Number of Villages'},
                    color_discrete_sequence=['#1f77b4'],
                    text='Villages Covered'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Surveyor",
                    yaxis_title="Number of Villages",
                    xaxis_tickangle=-45,
                    height=500,
                    width=600,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Individual Surveyor Analysis")

        surveyor_names = sorted(set(df['submitted_by'].dropna()))

        if surveyor_names:
            selected_surveyor = st.selectbox(
                "Select a surveyor to view details:",
                surveyor_names
            )

            surveyor_data = df[df['submitted_by'] == selected_surveyor]

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader(f"Data Collection Map for {selected_surveyor}")
                st.checkbox("Show distance lines between points", key="show_distances")
                map_obj = plot_surveyor_locations(df, selected_surveyor, st.session_state.show_distances)
                if map_obj:
                    folium_static(map_obj, width=700, height=500)
                else:
                    st.warning(f"Unable to display map for {selected_surveyor}: No valid location data available")

            with col2:
                surveyor_info = analysis_df[analysis_df['Surveyor'] == selected_surveyor]

                if not surveyor_info.empty:
                    st.subheader("Surveyor Metrics")
                    metrics = {
                        "Submissions": surveyor_info['Submissions'].values[0],
                        "Villages": surveyor_info['Villages Covered'].values[0],
                        "Blocks": surveyor_info['Blocks Covered'].values[0],
                        "Location Diversity": surveyor_info['Location Diversity'].values[0],
                        "Avg Distance (km)": surveyor_info['Avg Distance (km)'].values[0],
                        "Missing Coordinates": surveyor_info['Missing Coordinates'].values[0]
                    }

                    if 'avg_submissions' in surveyor_info.columns:
                        metrics["Avg Submissions/Day"] = surveyor_info['avg_submissions'].values[0]
                    if 'max_submissions' in surveyor_info.columns:
                        metrics["Max Submissions/Day"] = surveyor_info['max_submissions'].values[0]

                    status = surveyor_info['Status'].values[0]
                    if status != "Normal":
                        st.warning(f"⚠️ {status}")

                    for key, value in metrics.items():
                        st.metric(key, value)

                st.subheader("Village Breakdown")
                village_counts = surveyor_data['village'].value_counts().reset_index()
                village_counts.columns = ['Village', 'Count']
                st.dataframe(village_counts)

            with st.expander("View All Submissions by this Surveyor"):
                st.dataframe(surveyor_data)
        else:
            st.warning("No surveyors available to select.")

    with tab3:
        st.header("Location Analysis")

        st.subheader("Location Clustering and Outlier Detection")

        col1, col2 = st.columns([3, 1])

        with col1:
            map_obj, outliers, extreme_outliers = plot_all_locations(df)
            if map_obj:
                folium_static(map_obj, width=800, height=500)
            else:
                st.warning("Unable to display map: No valid location data available")

        with col2:
            st.metric("Total Locations", len(df.dropna(subset=['latitude', 'longitude'])))
            st.metric("Potential Outliers", len(outliers))
            st.metric("Extreme Outliers", len(extreme_outliers))
            st.metric("Missing Coordinates", df['missing_coordinates'].sum())

            st.markdown("""
            **Outlier Detection Method:**
            - Statistical analysis using z-scores for latitude and longitude
            - Distance calculation from the mean center point
            - Potential outliers: z-score > 2.5
            - Extreme outliers: z-score > 3.5
            """)

        if not outliers.empty:
            st.subheader("Outlier Details")

            display_cols = ['submission_id', 'submitted_by', 'village', 'latitude', 'longitude', 'distance_from_mean']
            outlier_display = outliers[display_cols].copy()
            outlier_display['distance_from_mean'] = outlier_display['distance_from_mean'].round(2)
            outlier_display.columns = ['Submission ID', 'Surveyor', 'Village', 'Latitude', 'Longitude', 'Distance from Mean (km)']

            st.dataframe(outlier_display)

        st.subheader("Village Location Analysis")

        village_location_stats = analyze_village_distance_distribution(df)

        if not village_location_stats.empty:
            display_df = village_location_stats.copy()
            for col in ['Min Distance (km)', 'Max Distance (km)', 'Avg Distance (km)', 'Distance Range (km)']:
                display_df[col] = display_df[col].round(2)

            st.dataframe(display_df.sort_values('Points', ascending=False))

            if len(display_df) > 1:
                plot_data = display_df.sort_values('Total Area Covered (km²)', ascending=False).head(10)

                fig = px.bar(
                    plot_data,
                    x='Village',
                    y='Total Area Covered (km²)',
                    title='Area Coverage by Village (Top 10)',
                    labels={'Village': 'Village', 'Total Area Covered (km²)': 'Approximate Area Covered (km²)'},
                    text='Total Area Covered (km²)',
                    color_discrete_sequence=['#1f77b4']
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title="Village",
                    yaxis_title="Approximate Area Covered (km²)",
                    xaxis_tickangle=-45,
                    height=600,
                    width=1000
                )
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("Distance Analysis")

        with st.spinner("Calculating distances between points..."):
            distances_df = calculate_interpoint_distances(df)

        if not distances_df.empty:
            st.subheader("Point-to-Point Distance Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Number of Point Pairs", len(distances_df))

            with col2:
                st.metric("Average Distance (km)", round(distances_df['distance_km'].mean(), 2))

            with col3:
                st.metric("Maximum Distance (km)", round(distances_df['distance_km'].max(), 2))

            with col4:
                st.metric("Minimum Distance (km)", round(distances_df['distance_km'].min(), 2))

            st.subheader("Distance Distribution")

            plot_data = distances_df[distances_df['distance_km'] <= 20]

            fig = px.histogram(
                plot_data,
                x='distance_km',
                nbins=30,
                title='Distribution of Distances Between Survey Points (≤20km)',
                labels={'distance_km': 'Distance (km)', 'count': 'Frequency'},
                marginal='rug',
                opacity=0.7
            )
            fig.update_layout(
                xaxis_title="Distance (km)",
                yaxis_title="Frequency",
                height=600,
                width=1000
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Within-Village vs Between-Village Distances")

            same_village = distances_df[distances_df['same_village']].copy()
            diff_village = distances_df[~distances_df['same_village']].copy()

            same_village['Category'] = 'Within Same Village'
            diff_village['Category'] = 'Between Villages'
            combined_data = pd.concat([same_village, diff_village])
            combined_data = combined_data[combined_data['distance_km'] <= 20]

            col1, col2 = st.columns(2)

            with col1:
                if not same_village.empty:
                    st.metric("Avg Within-Village Distance (km)", round(same_village['distance_km'].mean(), 2))
                    st.metric("Max Within-Village Distance (km)", round(same_village['distance_km'].max(), 2))
                else:
                    st.warning("No within-village distance data available")

            with col2:
                if not diff_village.empty:
                    st.metric("Avg Between-Village Distance (km)", round(diff_village['distance_km'].mean(), 2))
                    st.metric("Max Between-Village Distance (km)", round(diff_village['distance_km'].max(), 2))
                else:
                    st.warning("No between-village distance data available")

            if not combined_data.empty:
                fig = px.histogram(
                    combined_data,
                    x='distance_km',
                    color='Category',
                    nbins=20,
                    opacity=0.5,
                    title='Comparison of Within-Village and Between-Village Distances',
                    labels={'distance_km': 'Distance (km)', 'count': 'Frequency'},
                    barmode='overlay'
                )
                fig.update_layout(
                    xaxis_title="Distance (km)",
                    yaxis_title="Frequency",
                    height=600,
                    width=1000
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Point-to-Point Distance Table")

            col1, col2, col3 = st.columns(3)
            with col1:
                min_dist = st.number_input("Minimum Distance (km)", 0.0, 100.0, 0.0, 0.1)
            with col2:
                max_dist = st.number_input("Maximum Distance (km)", 0.0, 100.0, 10.0, 0.1)
            with col3:
                same_village_only = st.checkbox("Same Village Only")

            filtered_distances = distances_df[
                (distances_df['distance_km'] >= min_dist) &
                (distances_df['distance_km'] <= max_dist)
            ]

            if same_village_only:
                filtered_distances = filtered_distances[filtered_distances['same_village']]

            filtered_distances = filtered_distances.sort_values('distance_km')

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

        outlier_tabs = st.tabs(["Location Outliers", "Surveyor Pattern Outliers", "Time Pattern Outliers", "Missing Coordinates"])

        with outlier_tabs[0]:
            st.subheader("Location Outliers")

            geo_df, outliers, extreme_outliers = detect_location_outliers(df)

            if not geo_df.empty:
                st.write("The map below highlights potential outlier locations:")
                map_obj, _, _ = plot_all_locations(df, highlight_outliers=True)
                if map_obj:
                    folium_static(map_obj, width=1000, height=500)
                else:
                    st.warning("Unable to display map: No valid location data available")

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

            analysis_df = analyze_surveyor_patterns(df)

            if not analysis_df.empty:
                pattern_outliers = analysis_df[analysis_df['Status'] != "Normal"]

                if not pattern_outliers.empty:
                    st.subheader(f"Detected Pattern Outliers ({len(pattern_outliers)} surveyors)")
                    st.dataframe(pattern_outliers)

                    st.subheader("Outlier Pattern Visualization")

                    fig = px.scatter(
                        analysis_df,
                        x='Submissions',
                        y='Avg Distance (km)',
                        color='Status',
                        size='Villages Covered',
                        title='Surveyor Pattern Analysis: Submissions vs Distance',
                        labels={'Submissions': 'Number of Submissions', 'Avg Distance (km)': 'Average Distance Between Points (km)'},
                        opacity=0.7
                    )
                    fig.update_layout(
                        xaxis_title="Number of Submissions",
                        yaxis_title="Average Distance Between Points (km)",
                        height=600,
                        width=1000
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("""
                    **Surveyor Pattern Outliers might indicate:**
                    1. **Large area coverage**: Unusually large distances between points could indicate transportation by vehicle instead of walking surveys, or data entry errors
                    2. **High submissions in single village**: Excessive submissions in a single location may need verification
                    3. **High submission rate**: Unusually high number of surveys per day might indicate quality concerns
                    4. **Missing coordinates**: Submissions without location data may indicate device issues or incomplete surveys
                    """)
                else:
                    st.success("No surveyor pattern outliers detected in the data.")
            else:
                st.warning("Insufficient data for surveyor pattern analysis.")

        with outlier_tabs[2]:
            st.subheader("Time Pattern Outliers")

            if 'timestamp' in df.columns and not df['timestamp'].isna().all():
                time_analysis = detect_time_outliers(df)

                if not time_analysis.empty:
                    time_outliers = time_analysis[time_analysis['time_outlier_status'] != 'Normal']

                    if not time_outliers.empty:
                        st.subheader(f"Detected Time Pattern Outliers ({len(time_outliers)} surveyors)")

                        display_cols = [
                            'submitted_by', 'avg_submissions', 'max_submissions',
                            'std_submissions', 'total_days', 'total_submissions'
                        ]

                        display_df = time_outliers[display_cols].copy()

                        for col in ['avg_submissions', 'std_submissions']:
                            display_df[col] = display_df[col].round(2)

                        display_df.columns = [
                            'Surveyor', 'Avg Submissions/Day', 'Max Submissions/Day',
                            'Std Dev', 'Active Days', 'Total Submissions'
                        ]

                        st.dataframe(display_df.sort_values('Max Submissions/Day', ascending=False))

                        st.subheader("Daily Submission Patterns")

                        time_df = df.copy()
                        if pd.api.types.is_string_dtype(time_df['timestamp']):
                            time_df['timestamp'] = pd.to_datetime(time_df['timestamp'], utc=True)

                        time_df['date'] = time_df['timestamp'].dt.date

                        daily_counts = time_df.groupby(['submitted_by', 'date']).size().reset_index(name='submissions')

                        outlier_surveyors = time_outliers['submitted_by'].tolist()
                        plot_data = daily_counts[daily_counts['submitted_by'].isin(outlier_surveyors)]

                        if not plot_data.empty:
                            fig = px.line(
                                plot_data,
                                x='date',
                                y='submissions',
                                color='submitted_by',
                                title='Daily Submission Patterns for Outlier Surveyors',
                                labels={'date': 'Date', 'submissions': 'Submissions'},
                                markers=True
                            )
                            fig.update_layout(
                                xaxis_title="Date",
                                yaxis_title="Submissions",
                                xaxis_tickangle=-45,
                                height=600,
                                width=1000
                            )
                            st.plotly_chart(fig, use_container_width=True)

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

        with outlier_tabs[3]:
            st.subheader("Submissions with Missing Coordinates")

            missing_coords_df = df[df['missing_coordinates']]

            if not missing_coords_df.empty:
                st.subheader(f"Submissions Missing Coordinates ({len(missing_coords_df)} submissions)")

                display_cols = ['submission_id', 'submitted_by', 'village', 'respondent_name', 'submission_date']
                display_df = missing_coords_df[display_cols].copy()
                display_df.columns = ['Submission ID', 'Surveyor', 'Village', 'Respondent Name', 'Submission Date']

                st.dataframe(display_df)

                st.markdown("""
                **Missing Coordinates might indicate:**
                1. **Device Issues**: GPS might not have been enabled or functioning during data collection
                2. **Surveyor Error**: The surveyor may have skipped capturing location data
                3. **Form Configuration**: The form might not be correctly set up to capture geopoint data
                """)
            else:
                st.success("No submissions with missing coordinates detected in the data.")

    st.header("Download Reports")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Download Surveyor Analysis"):
            analysis_df = analyze_surveyor_patterns(df)
            csv = analysis_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="surveyor_analysis.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("Download Village Analysis"):
            village_location_stats = analyze_village_distance_distribution(df)
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

    with col4:
        if st.button("Download Missing Coordinates Report"):
            missing_coords_df = df[df['missing_coordinates']]
            if not missing_coords_df.empty:
                csv = missing_coords_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="missing_coordinates_report.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No submissions with missing coordinates to download")

if __name__ == "__main__":
    main()