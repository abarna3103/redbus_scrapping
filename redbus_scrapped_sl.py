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
        # Use tuple unpacking or access via indexes if results are tuples
        route_names = [row[0] for row in result]  # Access the first column of the tuple
    return route_names




# Fetch bus data for a specific route
def fetch_data(engine, route_name, price_sort_order):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = f"""
        SELECT * 
        FROM bus_routes 
        WHERE Route_Name = :route_name 
        ORDER BY Star_Rating DESC, Price {price_sort_order_sql}
    """
    with engine.connect() as connection:
        result = connection.execute(text(query), {"route_name": route_name})
        # Convert to DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())  # Use .keys() for column names
    return df


# Streamlit App Main Function
def main():
    st.title("Online Bus Booking Data Viewer")
    
    # Connect to the database
    engine = get_engine()
    
    # User inputs
    starting_letter = st.text_input("Enter the starting letter of the route:", "").strip()
    
    if starting_letter:
        try:
            route_names = fetch_route_names(engine, starting_letter.upper())
            if route_names:
                route_name = st.selectbox("Select a route:", route_names)
                price_sort_order = st.radio("Sort by Price:", ["Low to High", "High to Low"])
                
                if st.button("Show Data"):
                    bus_data = fetch_data(engine, route_name, price_sort_order)
                    if not bus_data.empty:
                        st.write("Available Buses:")
                        st.dataframe(bus_data)
                    else:
                        st.warning("No buses found for the selected route.")
            else:
                st.warning("No routes found with the given starting letter.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Please enter a starting letter to search routes.")

if __name__ == "__main__":
    main()
