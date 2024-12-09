import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# Database connection setup
def get_engine():
    username = "root"
    password = "123456789"
    host = "127.0.0.1"
    database = "redbus"
    return create_engine(f"mysql+mysqlconnector://{username}:{password}@{host}/{database}")


# Fetch unique source names for filtering
def fetch_source_names(engine):
    query = text("""
    SELECT DISTINCT Source 
    FROM bus_routes 
    ORDER BY Source
    """)
    with engine.connect() as connection:
        result = connection.execute(query)
        source_names = [row[0] for row in result]
    return source_names


# Fetch filtered bus types for selection
def fetch_bus_types():
    return ["NON A/C Seater", "NON A/C Sleeper", "AC Sleeper", "AC Seater", "NON A/C Semi Sleeper", "AC Semi Sleeper"]


# Fetch bus data with multiple filters
def fetch_data(engine, source, route_name, price_range, star_range, bus_type, availability, price_sort_order, departure_slot):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    
    # Map departure slots to SQL-compatible ranges
    departure_time_slots = {
        "6 AM - 12 PM": ("06:00", "12:00"),
        "12 PM - 6 PM": ("12:00", "18:00"),
        "6 PM - 12 AM": ("18:00", "23:59"),
        "12 AM - 6 AM": ("00:00", "06:00"),
    }
    start_time, end_time = departure_time_slots.get(departure_slot, ("00:00", "23:59"))
    
    # Dynamically construct the query based on bus_type
    bus_type_condition = ""
    if bus_type != "All":
        bus_type_condition = "AND LOWER(Bus_Type) LIKE LOWER(:bus_type)"
    
    query = f"""
        SELECT * 
        FROM bus_routes 
        WHERE Source = :source
          AND Route_Name = :route_name
          AND Price BETWEEN :price_min AND :price_max
          AND Star_Rating BETWEEN :star_min AND :star_max
          {bus_type_condition}
          AND (:availability IS NULL OR Seat_Availability > 0)
          AND (
              (Departing_Time BETWEEN :start_time AND :end_time)
              OR (:start_time = '00:00' AND Departing_Time < :end_time)
          )
        ORDER BY Star_Rating DESC, Price {price_sort_order_sql}
    """
    
    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {
                "source": source,
                "route_name": route_name,
                "price_min": price_range[0],
                "price_max": price_range[1],
                "star_min": star_range[0],
                "star_max": star_range[1],
                "bus_type": bus_type if bus_type != "All" else None,
                "availability": availability if availability else None,
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        result_data = result.fetchall()
        df = pd.DataFrame(result_data, columns=result.keys())
    return df


# Streamlit App Main Function
def main():
    st.title("Bus Booking Data")
    
    # Connect to the database
    engine = get_engine()
    
    try:
        # Fetch available sources
        sources = fetch_source_names(engine)
        
        # User input for source filter
        source = st.selectbox("Select Source:", sources)
        
        if source:
            # Fetch route names for the selected source
            route_query = text("""
            SELECT DISTINCT Route_Name 
            FROM bus_routes 
            WHERE Source = :source
            """)
            with engine.connect() as connection:
                result = connection.execute(route_query, {"source": source})
                route_names = [row[0] for row in result]
            
            if route_names:
                route_name = st.selectbox("Select a route:", route_names)
                
                # Additional filters
                price_range = st.slider("Select Price Range:", 0, 5000, (500, 2000))
                star_range = st.slider("Select Star Rating Range:", 0.0, 5.0, (3.0, 4.5), step=0.5)
                bus_types = ["All"] + fetch_bus_types()
                bus_type = st.selectbox("Select Bus Type:", bus_types)
                availability = st.checkbox("Only show available buses")
                price_sort_order = st.radio("Sort by Price:", ["Low to High", "High to Low"])
                departure_slot = st.selectbox(
                    "Select Departure Time Slot:",
                    ["6 AM - 12 PM", "12 PM - 6 PM", "6 PM - 12 AM", "12 AM - 6 AM"]
                )
                
                if st.button("Show Data"):
                    bus_data = fetch_data(
                        engine, source, route_name, price_range, star_range, bus_type, availability, price_sort_order, departure_slot
                    )
                    if not bus_data.empty:
                        st.write("Available Buses:")
                        st.dataframe(bus_data)
                    else:
                        st.warning("No buses found for the selected criteria.")
            else:
                st.warning("No routes found for the selected source.")
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
