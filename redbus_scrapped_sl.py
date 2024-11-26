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


# Fetch unique route names based on a starting letter
def fetch_route_names(engine, starting_letter):
    query = text("""
    SELECT DISTINCT Route_Name 
    FROM bus_routes 
    WHERE Route_Name LIKE :letter
    """)
    with engine.connect() as connection:
        result = connection.execution_options(stream_results=True).execute(
            query, {"letter": f"{starting_letter}%"}
        )
        route_names = [row[0] for row in result]
    return route_names


# Fetch unique bus types for filtering
def fetch_bus_types(engine):
    query = text("SELECT DISTINCT Bus_Type FROM bus_routes")
    with engine.connect() as connection:
        result = connection.execute(query)
        bus_types = [row[0] for row in result]
    return bus_types


# Fetch bus data with multiple filters
def fetch_data(engine, route_name, price_range, star_rating, bus_type, availability, price_sort_order):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = f"""
        SELECT * 
        FROM bus_routes 
        WHERE Route_Name = :route_name
          AND Price BETWEEN :price_min AND :price_max
          AND Star_Rating >= :star_rating
          AND (:bus_type IS NULL OR Bus_Type = :bus_type)
          AND (:availability IS NULL OR Seat_Availability > 0)
        ORDER BY Star_Rating DESC, Price {price_sort_order_sql}
    """
    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {
                "route_name": route_name,
                "price_min": price_range[0],
                "price_max": price_range[1],
                "star_rating": star_rating,
                "bus_type": bus_type if bus_type != "All" else None,
                "availability": availability if availability else None,
            },
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


# Streamlit App Main Function
def main():
    st.title("Bus Booking Data")
    
    # Connect to the database
    engine = get_engine()
    
    # User input for route filter
    starting_letter = st.text_input("Enter the starting letter of the route:", "").strip()
    
    if starting_letter:
        try:
            route_names = fetch_route_names(engine, starting_letter.upper())
            if route_names:
                route_name = st.selectbox("Select a route:", route_names)
                
                # Additional filters
                price_range = st.slider("Select Price Range:", 0, 5000, (500, 2000))
                star_rating = st.slider("Minimum Star Rating:", 0.0, 5.0, 3.0, step=0.5)
                bus_types = ["All"] + fetch_bus_types(engine)
                bus_type = st.selectbox("Select Bus Type:", bus_types)
                availability = st.checkbox("Only show available buses")
                price_sort_order = st.radio("Sort by Price:", ["Low to High", "High to Low"])
                
                if st.button("Show Data"):
                    bus_data = fetch_data(
                        engine, route_name, price_range, star_rating, bus_type, availability, price_sort_order
                    )
                    if not bus_data.empty:
                        st.write("Available Buses:")
                        st.dataframe(bus_data)
                    else:
                        st.warning("No buses found for the selected criteria.")
            else:
                st.warning("No routes found with the given starting letter.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Please enter a starting letter to search routes.")


if __name__ == "__main__":
    main()
