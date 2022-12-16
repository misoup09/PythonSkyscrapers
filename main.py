import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import time
import pydeck as pdk

APP_NAME = "Skyscrapers 😎"

st.title(APP_NAME)
st.set_option('deprecation.showPyplotGlobalUse', False)

def load_data():
    """
    This program reads the file and converts meters, feet, and floors into an integer to be displayed
    """
    # Read data
    data = pd.read_csv("Skyscrapers_2021.csv")
    # Convert all columns to lower case
    data.columns = map(str.lower, data.columns)
    # Remove units of measurement and convert values to floats
    data["meters"] = data["meters"].str.replace(" m", "").str.replace(",", "").astype(float)
    data["feet"] = data["feet"].str.replace(" ft", "").str.replace(",", "").astype(float)
    # Convert NA to NaN
    data["floors"] = pd.to_numeric(data["floors"], errors="coerce").fillna(0).astype(float)
    # Round the values in the "Meters" and "Feet" columns to the nearest integer and convert them to int
    data["meters"], data["feet"], data["floors"] = \
        round(data["meters"]).astype(int), round(data["feet"]).astype(int), round(data["floors"]).astype(int)
    return data

def group_city(data, metric="meters"):
    """
    Group duplicate city and sum the meters
    """
    df_by_city = pd.DataFrame(data, columns=["city", "meters"]).groupby('city', as_index=False).mean()
    df_by_city['meters'] = df_by_city['meters'].astype(int)
    # Group the data by the "CITY" column and sum the "Meters" column
    if metric == "meters":
        df_by_city = pd.DataFrame(data, columns=["city", "meters"]).groupby('city', as_index=False).mean()
        df_by_city['meters'] = df_by_city['meters'].astype(int)
    # Group data by City and Feet
    elif metric == "feet":
        df_by_city = pd.DataFrame(data, columns=["city", "feet"]).groupby('city', as_index=False).mean()
        df_by_city['feet'] = df_by_city['feet'].astype(int)
    # Group data by City and Floors
    elif metric == "floors":
        df_by_city = pd.DataFrame(data, columns=["city", "floors"]).groupby('city', as_index=False).mean()
        df_by_city['floors'] = df_by_city['floors'].astype(int)
    df_by_city.index = range(1, len(df_by_city) + 1)
    print(df_by_city)
    return df_by_city

df = load_data()

def show_building_height_by_name_or_city():
    """
    Displays the building's name and city through the minimum and maximum values using the unit
    """
    y_min, y_max = 0, 1000
    selected_names = None
    plt.figure(figsize=(10, 5))
    unit = st.sidebar.radio("Unit", ["Meters", "Feet", "Floors"])
    x_axis = st.sidebar.radio("Select name or city", ["Name", "City"])  # Add an option to select the x-axis
    city_df = group_city(df)
    if x_axis == "Name":
        selected_names = st.sidebar.multiselect("Select buildings by name", df["name"],
                                                default=df["name"].head(3))
    elif x_axis == "City":
        selected_names = st.sidebar.multiselect("Select buildings by city", city_df["city"],
                                                default=city_df["city"].head(3))
    selected_names = sorted(selected_names)
    # Check if the length of the selected_names list is less than 1 and display an error message if it is
    if len(selected_names) < 1:
        st.error("Please select at least 1 building name or city")
        return

    # Unit in Meters
    if unit == "Meters":
        if x_axis == "Name":
            plt.bar(selected_names, df[df["name"].isin(selected_names)]["meters"])
            y_min, y_max = get_y_axis_range(df, "meters")
            plt.title("Building Height by Meters", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            # Plot a bar chart using the selected cities and meters values
            plt.bar(selected_names, city_df[city_df["city"].isin(selected_names)]["meters"])
            y_min, y_max = get_y_axis_range(city_df, "meters")
            plt.title("City Average Building Height by Meters", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Meters")
        plt.ylim(y_min, y_max)
    # Unit in Feet
    elif unit == "Feet":
        city_df = group_city(df, "feet")
        if x_axis == "Name":
            plt.bar(selected_names, df[df["name"].isin(selected_names)]["feet"])
            print(selected_names)
            y_min, y_max = get_y_axis_range(df, "feet")
            plt.title("Building Height by Feet", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            # Plot a bar chart using the selected cities and meters values
            plt.bar(selected_names, city_df[city_df["city"].isin(selected_names)]["feet"])
            y_min, y_max = get_y_axis_range(city_df, "feet")
            plt.title("City Average Building Height by Feet", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Feet")
        plt.ylim(y_min, y_max)
    # Unit in Floors
    elif unit == "Floors":
        city_df = group_city(df, "floors")
        if x_axis == "Name":
            plt.bar(selected_names, df[df["name"].isin(selected_names)]["floors"])
            y_min, y_max = get_y_axis_range(df, "floors")
            plt.title("Building Height by Floors", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            # Plot a bar chart using the selected cities and meters values
            plt.bar(selected_names, city_df[city_df["city"].isin(selected_names)]["floors"])
            y_min, y_max = get_y_axis_range(city_df, "floors")
            plt.title("City Average Building Height by Floors", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Floors")
        plt.ylim(y_min, y_max)
    plt.xticks(rotation=90)
    st.pyplot()
    # Show data grid of the data
    if x_axis == "Name":
        show_data_frame(df[df["name"].isin(selected_names)], "name")
    elif x_axis == "City":
        show_data_frame(city_df[city_df["city"].isin(selected_names)], "city")

def show_building_height_by_slider():
    """
    The building is displayed on a sliding scale based on its height
    """
    y_min, y_max = 0, 1000
    plt.figure(figsize=(10, 5))
    unit = st.sidebar.radio("Unit", ["Meters", "Feet", "Floors"])
    x_axis = st.sidebar.radio("Select name or city", ["Name", "City"])  # Add an option to select the x-axis
    city_df = group_city(df, "")

    # Unit in Meters
    if unit == "Meters":
        if x_axis == "Name":
            y_max = df["meters"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[500, y_max], step=10)
            df_filtered = df[(df['meters'] >= y_range[0]) & (df['meters'] <= y_range[1])]
            plt.bar(df_filtered["name"], df_filtered["meters"])
            plt.title("Building Height by Meters", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            y_max = city_df["meters"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[0, y_max], step=10)
            df_filtered = city_df[(city_df['meters'] >= y_range[0]) & (city_df['meters'] <= y_range[1])]
            plt.bar(df_filtered["city"], df_filtered["meters"])
            plt.title("City Average Building Height by Meters", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Meters")
        plt.ylim(y_min, y_max)
    # Unit in Feet
    elif unit == "Feet":
        city_df = group_city(df, "feet")
        if x_axis == "Name":
            y_max = df["feet"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[1200, y_max], step=10)
            df_filtered = df[(df['feet'] >= y_range[0]) & (df['feet'] <= y_range[1])]
            plt.bar(df_filtered["name"], df_filtered["feet"])
            plt.title("Building Height by Feet", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            y_max = city_df["feet"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[0, y_max], step=10)
            df_filtered = city_df[(city_df['feet'] >= y_range[0]) & (city_df['feet'] <= y_range[1])]
            plt.bar(df_filtered["city"], df_filtered["feet"])
            plt.title("City Average Building Height by Feet", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Feet")
        plt.ylim(y_min, y_max)
    # Unit in Floors
    elif unit == "Floors":
        city_df = group_city(df, "floors")
        if x_axis == "Name":
            y_max = df["floors"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[90, y_max], step=10)
            df_filtered = df[(df['floors'] >= y_range[0]) & (df['floors'] <= y_range[1])]
            plt.bar(df_filtered["name"], df_filtered["floors"])
            plt.title("Building Height by Floors", fontsize=18)
            plt.xlabel("Building Name")
        elif x_axis == "City":
            y_max = city_df["floors"].max() + 50
            y_range = st.sidebar.slider("Range for y-axis", min_value=0, max_value=y_max, value=[0, y_max], step=10)
            df_filtered = city_df[(city_df['floors'] >= y_range[0]) & (city_df['floors'] <= y_range[1])]
            plt.bar(df_filtered["city"], df_filtered["floors"])
            plt.title("City Average Building Height by Floors", fontsize=18)
            plt.xlabel("City")
        plt.ylabel("Floors")
        plt.ylim(y_min, y_max)
    plt.xticks(rotation=90)
    st.pyplot()


def show_city_building_count():
    """
    It counts the amount of buildings in each city
    """
    city_counts = {}
    for city, count in df['city'].value_counts().iteritems():
        city_counts[city] = count
    print(city_counts)
    city_df = pd.DataFrame.from_dict(city_counts, orient='index', columns=['Buildings'])
    print(city_df)
    city_df.plot.bar(y='Buildings')
    plt.title('Buildings Per City')
    plt.xlabel('Cities')
    plt.ylabel('Buildings')
    st.pyplot()

def show_city_building_count_pie():
    """
    The purpose of this code is to count the buildings in each city and display it as a pie chart
    """
    city_counts = {}
    for city, count in df['city'].value_counts().iteritems():
        city_counts[city] = count
    print(city_counts)

    # Add a sidebar with a multiselect dropdown for the data dictionary keys
    selected_keys = st.sidebar.multiselect("Select keys:", list(city_counts.keys()),
                                           default=[list(city_counts.keys())[0], list(city_counts.keys())[1]])

    if not selected_keys:
        # Create an empty pie chart if no keys are selected
        fig, ax = plt.subplots()
        ax.pie([])
        ax.legend().remove()
    else:
        # Filter the data dictionary based on the selected keys
        filtered_data = {key: value for key, value in city_counts.items() if key in selected_keys}

        # Create the pie chart and legend
        labels = list(filtered_data.keys())
        sizes = list(filtered_data.values())
        colors = plt.cm.rainbow(np.linspace(0, 1, len(filtered_data)))

        fig1, ax1 = plt.subplots()
        patches, texts = ax1.pie(sizes, colors=colors, labels=labels, startangle=90)

        # Create legend with percentage next to label
        legend_labels = []
        total_size = sum(sizes)
        for patch, label in zip(patches, labels):
            value = float(filtered_data[label])  # retrieve value from data dictionary
            percentage = round(value / total_size * 100, 1)  # calculate percentage
            legend_labels.append(f'{label} {percentage}%')
        ax1.legend(patches, legend_labels, bbox_to_anchor=(1, 1))

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        pie_df = pd.DataFrame(list(filtered_data.items()), columns=['City', 'Number of Buildings'])
    st.pyplot()
    show_data_frame(pie_df, "pie")

def show_data_frame(data, type):
    """
    This shows the number of skyscrapers for each city and allows the user to pick a city to see the average
    height of each city's skyscrapers
    """
    if data is None:
        return
    if type == "pie":
        st.header("Skyscrapers by height or city")
        st.markdown("Find which city is dominating the world with the most sky scrapers!")
        st.subheader("Pick a city")
        st.dataframe(data)
    elif type == "name":
        st.header("Number of Skyscrapers Per City")
        st.markdown("Learn more about the skyscrapers near you!")
        st.subheader("Pick a city")
        st.dataframe(data)
    elif type == "city":
        st.header("Average Height of Skyscrapers in Each City")
        st.markdown("Find which city is dominating in building the most sky scrapers!")
        st.subheader("Pick a city")
        data = data.rename(columns={"city": "City"})
        st.dataframe(data)

def show_skyscraper_completion_line_chart():
# Select the relevant columns from the data frame
    d = df[['completion', 'name']]

    # Group the data frame by 'COMPLETION' and count the number of buildings for each completion year
    d = d.groupby('completion').count()
    d = d.rename(columns={'name': 'Skyscrapers Built Per Year'})
    st.line_chart(d)

def show_city_map():
    # Create a dropdown with the 'name' options
    name = st.selectbox("Select a skyscraper:", df["name"])

    # Select the row corresponding to the selected name
    city_df = df[df["name"] == name]

    # Create a map centered on the selected city
    view_state = pdk.ViewState(latitude=city_df["latitude"].iloc[0],
                               longitude=city_df["longitude"].iloc[0],
                               zoom=10)

    # Add a marker at the location of the selected city
    marker = pdk.Layer(
        "ScatterplotLayer",
        data=city_df,
        get_position=["longitude", "latitude"],
        get_text=["name"],
        get_color=[255, 0, 0],  # Set marker color to red
        pickable=True,
        radius_scale=100,
        radius_min_pixels=5,
        radius_max_pixels=100,
    )

    # Display the map
    r = pdk.Deck(layers=[marker], initial_view_state=view_state)
    st.pydeck_chart(r)

def get_y_axis_range(data, metric):
    """
    The y-axis is calculated in meters, feet, and floors
    """
    range = None
    if metric == "meters":
        range = st.sidebar.slider("Height in Meters", 0, data["meters"].max(),
                                  (0, int(data["meters"].max() + data["meters"].max() * .1)))
    elif metric == "feet":
        range = st.sidebar.slider("Height in Feet", 0, data["feet"].max(),
                                  (0, int(data["feet"].max() + data["feet"].max() * .1)))
    elif metric == "floors":
        range = st.sidebar.slider("Height in Floors", 0, data["floors"].max(),
                                  (0, int(data["floors"].max() + data["floors"].max() * .1)))
    return range


def show_main_page():
    """
    This introduces the project (it's the heading)
    """
    st.markdown("# CS 230 | Introduction to Programing with Python")


def menu():
    """
    Allows the user to select which part of the page they would like to open up
    """
    chart_type = st.sidebar.selectbox("Select chart type",
                                      ["Main Page", "Building Height by Name or City", "Building Height By Range",
                                       "Cities with Most Buildings", "Buildings (Pie Chart)", "Map of Skyscrapers "
                                                                                               "in the World",
                                       "Skyscraper Completion Year Line Chart"])

    # Depending on the selection, display the corresponding chart
    if chart_type == "Main Page":
        show_main_page()
        st.markdown("Take a look to see some interesting statistics about the top 100 tallest buildings around the world")
        # Create a list of image file names
        image_files = ['cuteSky.jpg', 'skyscrapers.jpg', 'tall.jpg']
        # Set the interval at which the images should change, in seconds
        interval = 5
        # Load your images into a list
        images = [Image.open('cuteSky.jpg'), Image.open('skyscrapers.jpg'), Image.open('tall.jpg')]
        # Create a slider using the st.slider widget
        slider = st.slider("Select an image", 0, len(images) - 1)
        # Use the slider value to select an image from the list
        selected_image = images[slider]
        # Display the selected image using the st.image widget
        st.image(selected_image, width=800)
    elif chart_type == "Building Height by Name or City":
        image = Image.open('cuteSky.jpg')
        # Display the image
        st.image(image, use_column_width=True)
        show_building_height_by_name_or_city()
        st.markdown("Skyscrapers' height by name or city based on the input data")
    elif chart_type == "Building Height By Range":
        show_building_height_by_slider()
    elif chart_type == "Cities with Most Buildings":
        show_city_building_count()
    elif chart_type == "Buildings (Pie Chart)":
        show_city_building_count_pie()
    elif chart_type == "Skyscraper Completion Year Line Chart":
        show_skyscraper_completion_line_chart()
        st.markdown("This line chart shows the amount of buildings built per year on a worldwild scale 🏗️")
    elif chart_type == "Map of Skyscrapers in the World":
        show_city_map()
        st.markdown("Please use the drop down menu to select a building you'd like to see!"
                    " The dot on the map shows the location and city of each skyscraper")

menu()

