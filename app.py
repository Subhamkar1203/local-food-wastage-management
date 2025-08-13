import streamlit as st
import pandas as pd
import sqlite3

# Set page configuration for a better look
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="",
    layout="wide",
)

@st.cache_resource
def get_connection():
    try:
        return sqlite3.connect("food_waste.db", check_same_thread=False)
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

conn = get_connection()

def run_query(query):
    if conn:
        try:
            return pd.read_sql(query, conn)
        except pd.io.sql.DatabaseError as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

menu = ["Dashboard", "Analytics Dashboard", "Claims", "Food Listings", "CRUD Operations"]
choice = st.sidebar.selectbox("Menu", menu)

st.title(" Local Food Wastage Management System")
st.markdown("---")

if choice == "Dashboard":
    st.subheader(" System Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_providers = run_query("SELECT COUNT(*) as Total FROM Providers")["Total"][0]
        st.metric(label="Total Providers", value=f" {total_providers}")
    
    with col2:
        total_receivers = run_query("SELECT COUNT(*) as Total FROM Receivers")["Total"][0]
        st.metric(label="Total Receivers", value=f" {total_receivers}")
        
    with col3:
        total_food = run_query("SELECT SUM(Quantity) as Total FROM Food_Listings")["Total"][0]
        st.metric(label="Total Food Quantity Listed", value=f" {total_food}")

    st.markdown("---")
    
    st.write("### Food Quantity by City")
    city_data = run_query("""
        SELECT Location, SUM(Quantity) as Total_Quantity
        FROM Food_Listings
        GROUP BY Location
    """)
    if not city_data.empty:
        st.bar_chart(city_data.set_index("Location"))
    else:
        st.info("No food data available to display.")

elif choice == "Analytics Dashboard":
    st.subheader("In-depth Analytics")
    
    st.markdown("---")
    
    st.write("#### 1. Providers and Receivers by City")
    providers_receivers_by_city = run_query("""
        SELECT City, COUNT(DISTINCT Provider_ID) AS Providers,
                (SELECT COUNT(DISTINCT Receiver_ID) FROM Receivers WHERE City = p.City) AS Receivers
        FROM Providers p
        GROUP BY City;
    """)
    if not providers_receivers_by_city.empty:
        providers_receivers_by_city = providers_receivers_by_city.set_index("City")
        st.bar_chart(providers_receivers_by_city)
    else:
        st.info("No data available for providers and receivers by city.")
    
    st.markdown("---")

    st.write("#### 2. Top Provider Type")
    top_provider_type = run_query("SELECT Type, COUNT(*) AS Count FROM Providers GROUP BY Type ORDER BY Count DESC LIMIT 1;")
    if not top_provider_type.empty:
        st.metric("Most Common Provider Type", f" {top_provider_type.iloc[0]['Type']}")
    else:
        st.info("No data available for provider types.")
    
    st.markdown("---")

    st.write("#### 3. Provider Contact by City")
    providers_in_db = run_query("SELECT DISTINCT City FROM Providers")
    if not providers_in_db.empty:
        selected_city = st.selectbox("Select a City to view Provider Contacts:", providers_in_db["City"])
        provider_contact_by_city = run_query(f"SELECT Name, Contact FROM Providers WHERE City = '{selected_city}';")
        if not provider_contact_by_city.empty:
            st.dataframe(provider_contact_by_city, use_container_width=True)
        else:
            st.info("No providers found for the selected city.")
    else:
        st.info("No cities available to select.")
    
    st.markdown("---")

    st.write("#### 4. Top Receivers by Claims")
    top_receivers_by_claims = run_query("""
        SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Name
        ORDER BY Total_Claims DESC;
    """)
    if not top_receivers_by_claims.empty:
        st.bar_chart(top_receivers_by_claims.set_index("Name"))
    else:
        st.info("No claims data available to show top receivers.")
    
    st.markdown("---")
    
    st.write("#### 5. Total Food Quantity")
    total_food_quantity = run_query("SELECT SUM(Quantity) AS Total_Quantity FROM Food_Listings;")
    if not total_food_quantity.empty:
        st.metric("Total Quantity of Food Listed", f" {total_food_quantity.iloc[0]['Total_Quantity']}")
    else:
        st.info("No food listings available.")
        
    st.markdown("---")

    st.write("#### 6. City with Most Food Listings")
    city_with_most_food_listings = run_query("""
        SELECT Location, COUNT(*) AS Listings
        FROM Food_Listings
        GROUP BY Location
        ORDER BY Listings DESC
        LIMIT 1;
    """)
    if not city_with_most_food_listings.empty:
        st.metric("City with Most Listings", f" {city_with_most_food_listings.iloc[0]['Location']}")
    else:
        st.info("No data available.")

    st.markdown("---")

    st.write("#### 7. Most Common Food Types")
    most_common_food_types = run_query("""
        SELECT Food_Type, COUNT(*) AS Count
        FROM Food_Listings
        GROUP BY Food_Type
        ORDER BY Count DESC;
    """)
    if not most_common_food_types.empty:
        st.bar_chart(most_common_food_types.set_index("Food_Type"))
    else:
        st.info("No data available for food types.")
    
    st.markdown("---")
    
    st.write("#### 8. Claims per Food Item")
    claims_per_food_item = run_query("""
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_Name;
    """)
    if not claims_per_food_item.empty:
        st.bar_chart(claims_per_food_item.set_index("Food_Name"))
    else:
        st.info("No claims data available.")
        
    st.markdown("---")

    st.write("#### 9. Provider with Most Successful Claims")
    provider_with_most_successful_claims = run_query("""
        SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY Successful_Claims DESC
        LIMIT 1;
    """)
    if not provider_with_most_successful_claims.empty:
        st.metric("Top Provider by Successful Claims", f" {provider_with_most_successful_claims.iloc[0]['Name']}")
    else:
        st.info("No data available.")

    st.markdown("---")

    st.write("#### 10. Claims Status Percentages")
    claims_status_percentages = run_query("""
        SELECT Status, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) AS Percentage
        FROM Claims
        GROUP BY Status;
    """)
    if not claims_status_percentages.empty:
        st.dataframe(claims_status_percentages, use_container_width=True)
    else:
        st.info("No claims status data available.")
        
    st.markdown("---")

    st.write("#### 11. Average Quantity Per Receiver")
    avg_quantity_per_receiver = run_query("""
        SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY r.Name;
    """)
    if not avg_quantity_per_receiver.empty:
        st.bar_chart(avg_quantity_per_receiver.set_index("Name"))
    else:
        st.info("No data available.")
        
    st.markdown("---")

    st.write("#### 12. Most Claimed Meal Type")
    most_claimed_meal_type = run_query("""
        SELECT Meal_Type, COUNT(*) AS Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY Meal_Type
        ORDER BY Claims DESC
        LIMIT 1;
    """)
    if not most_claimed_meal_type.empty:
        st.metric("Most Claimed Meal Type", f" {most_claimed_meal_type.iloc[0]['Meal_Type']}")
    else:
        st.info("No data available.")
        
    st.markdown("---")

    st.write("#### 13. Total Donated by Provider")
    total_donated_by_provider = run_query("""
        SELECT p.Name, SUM(f.Quantity) AS Total_Donated
        FROM Food_Listings f
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Name;
    """)
    if not total_donated_by_provider.empty:
        st.bar_chart(total_donated_by_provider.set_index("Name"))
    else:
        st.info("No data available.")
        
    st.markdown("---")

    st.write("#### 14. Top City by Completed Claims")
    top_city_by_completed_claims = run_query("""
        SELECT f.Location, COUNT(*) AS Completed_Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY f.Location
        ORDER BY Completed_Claims DESC
        LIMIT 1;
    """)
    if not top_city_by_completed_claims.empty:
        st.metric("City with the Most Completed Claims", f" {top_city_by_completed_claims.iloc[0]['Location']}")
    else:
        st.info("No data available.")
        
    st.markdown("---")

    st.write("#### 15. Expired Food Items")
    expired_food_items = run_query("""
        SELECT Food_Name, Expiry_Date
        FROM Food_Listings
        WHERE DATE(Expiry_Date) < DATE('now');
    """)
    if not expired_food_items.empty:
        st.dataframe(expired_food_items, use_container_width=True)
    else:
        st.success(" No food items have expired! Great job!")

elif choice == "Claims":
    st.subheader(" Food Claims Overview")
    claims_data = run_query("""
        SELECT c.Claim_ID, f.Food_Name, r.Name as Receiver, c.Status, c.Timestamp
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    """)
    if not claims_data.empty:
        st.dataframe(claims_data, use_container_width=True)
    else:
        st.info("No claims data available.")

elif choice == "Food Listings":
    st.subheader(" Available Food Listings")
    listings = run_query("SELECT * FROM Food_Listings")
    if not listings.empty:
        city = st.selectbox("Filter by City", ["All"] + list(listings["Location"].unique()))
        if city != "All":
            filtered_listings = listings[listings["Location"] == city]
            st.dataframe(filtered_listings, use_container_width=True)
        else:
            st.dataframe(listings, use_container_width=True)
    else:
        st.info("No food listings available.")

elif choice == "CRUD Operations":
    st.subheader(" Manage Food Listings")
    st.write("Use the form below to add a new food listing.")
    
    with st.form("Add Food"):
        st.write("### Add New Food Listing")
        food_name = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=1)
        expiry = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        location = st.text_input("Location")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        submitted = st.form_submit_button("Add Listing")
        
        if submitted:
            if food_name and qty and expiry and provider_id and location and food_type and meal_type:
                try:
                    conn.execute("""
                        INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (food_name, qty, str(expiry), provider_id, location, food_type, meal_type))
                    conn.commit()
                    st.success(" Food listing added successfully!")
                except sqlite3.Error as e:
                    st.error(f"An error occurred while adding the listing: {e}")
            else:
                st.warning("Please fill in all the fields.")
