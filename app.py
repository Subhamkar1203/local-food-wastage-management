import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

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

def run_query(query, params=None):
    if conn:
        try:
            if params:
                return pd.read_sql(query, conn, params=params)
            else:
                return pd.read_sql(query, conn)
        except pd.io.sql.DatabaseError as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

menu = ["Dashboard", "Analytics Dashboard", "Claims", "Food Listings", "CRUD Operations"]
choice = st.sidebar.selectbox("Menu", menu)

st.title("Local Food Wastage Management System")
st.markdown("---")

if choice == "Dashboard":
    st.subheader("System Overview")
    
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
        fig = px.bar(
            city_data, 
            x='Location', 
            y='Total_Quantity',
            title='Total Food Quantity by City',
            labels={'Total_Quantity': 'Quantity (Units)', 'Location': 'City'},
            text='Total_Quantity'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No food data available to display.")

elif choice == "Analytics Dashboard":
    st.subheader("In-depth Analytics")
    
    st.markdown("---")
    
    # --- 1. Providers and Receivers by City (Grouped Bar Chart) ---
    st.write("#### 1. Providers and Receivers by City")
    providers_receivers_by_city = run_query("""
        SELECT City, COUNT(DISTINCT Provider_ID) AS Providers,
               (SELECT COUNT(DISTINCT Receiver_ID) FROM Receivers WHERE City = p.City) AS Receivers
        FROM Providers p
        GROUP BY City;
    """)
    if not providers_receivers_by_city.empty:
        fig = px.bar(
            providers_receivers_by_city.melt(id_vars='City', value_vars=['Providers', 'Receivers']),
            x='City', y='value', color='variable',
            barmode='group',
            labels={'value': 'Count', 'variable': 'Type'},
            title='Providers vs Receivers by City'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for providers and receivers by city.")
    
    st.markdown("---")

    # --- 2. Top Provider Type (Donut Chart) ---
    st.write("#### 2. Top Provider Type")
    top_provider_type = run_query("SELECT Type, COUNT(*) AS Count FROM Providers GROUP BY Type ORDER BY Count DESC;")
    if not top_provider_type.empty:
        fig = px.pie(
            top_provider_type, names='Type', values='Count',
            title="Distribution of Provider Types", hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for provider types.")
    
    st.markdown("---")

    # --- 3. Provider Contact by City (DataFrame) ---
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

    # --- 4. Top Receivers by Claims (Bar Chart) ---
    st.write("#### 4. Top Receivers by Claims")
    top_receivers_by_claims = run_query("""
        SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Name
        ORDER BY Total_Claims DESC;
    """)
    if not top_receivers_by_claims.empty:
        fig = px.bar(
            top_receivers_by_claims, x='Name', y='Total_Claims',
            title='Top Receivers by Total Claims', text='Total_Claims'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No claims data available to show top receivers.")
    
    st.markdown("---")
    
    # --- 5. Total Food Quantity (Metric) ---
    st.write("#### 5. Total Food Quantity")
    total_food_quantity = run_query("SELECT SUM(Quantity) AS Total_Quantity FROM Food_Listings;")
    if not total_food_quantity.empty:
        st.metric("Total Quantity of Food Listed", f" {total_food_quantity.iloc[0]['Total_Quantity']}")
    else:
        st.info("No food listings available.")
        
    st.markdown("---")

    # --- 6. City with Most Food Listings (Metric) ---
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

    # --- 7. Most Common Food Types (Bar Chart) ---
    st.write("#### 7. Most Common Food Types")
    most_common_food_types = run_query("""
        SELECT Food_Type, COUNT(*) AS Count
        FROM Food_Listings
        GROUP BY Food_Type
        ORDER BY Count DESC;
    """)
    if not most_common_food_types.empty:
        fig = px.bar(
            most_common_food_types, x='Food_Type', y='Count', color='Food_Type',
            title='Most Common Food Types', text='Count'
        )
        # Update layout to increase font size for x-axis labels
        fig.update_layout(xaxis_title_font=dict(size=18), xaxis_tickfont=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for food types.")
    
    st.markdown("---")
    
    # --- 8. Claims per Food Item (Bar Chart) ---
    st.write("#### 8. Claims per Food Item")
    claims_per_food_item = run_query("""
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims
        FROM Claims c
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_Name;
    """)
    if not claims_per_food_item.empty:
        fig = px.bar(
            claims_per_food_item, x='Food_Name', y='Claims', color='Claims',
            title='Claims per Food Item', text='Claims'
        )
        # Update layout for larger font sizes
        fig.update_layout(xaxis_title_font=dict(size=18), xaxis_tickfont=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No claims data available.")
        
    st.markdown("---")

    # --- 9. Provider with Most Successful Claims (Metric) ---
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

    # --- 10. Claims Status Percentages (Donut Chart) ---
    st.write("#### 10. Claims Status Percentages")
    claims_status_percentages = run_query("""
        SELECT Status, 
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) AS Percentage
        FROM Claims
        GROUP BY Status;
    """)
    if not claims_status_percentages.empty:
        fig = px.pie(
            claims_status_percentages, names='Status', values='Percentage',
            title='Claims Status Distribution', hole=0.3
        )
        # Update font size for the pie chart's text labels
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig.update_layout(uniformtext_minsize=14, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No claims status data available.")
        
    st.markdown("---")

    # --- 11. Average Quantity Per Receiver (Bar Chart) ---
    st.write("#### 11. Average Quantity Per Receiver")
    avg_quantity_per_receiver = run_query("""
        SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings f ON c.Food_ID = f.Food_ID
        GROUP BY r.Name;
    """)
    if not avg_quantity_per_receiver.empty:
        fig = px.bar(
            avg_quantity_per_receiver, x='Name', y='Avg_Quantity',
            title='Average Quantity per Receiver', text='Avg_Quantity'
        )
        # Update font size for x-axis labels
        fig.update_layout(xaxis_title_font=dict(size=18), xaxis_tickfont=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available.")
        
    st.markdown("---")

    # --- 12. Most Claimed Meal Type (Metric) ---
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

    # --- 13. Total Donated by Provider (Bar Chart) ---
    st.write("#### 13. Total Donated by Provider")
    total_donated_by_provider = run_query("""
        SELECT p.Name, SUM(f.Quantity) AS Total_Donated
        FROM Food_Listings f
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Name;
    """)
    if not total_donated_by_provider.empty:
        fig = px.bar(
            total_donated_by_provider, x='Name', y='Total_Donated',
            title='Total Donated by Provider', text='Total_Donated'
        )
        # Update font size for x-axis labels
        fig.update_layout(xaxis_title_font=dict(size=18), xaxis_tickfont=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available.")
        
    st.markdown("---")

    # --- 14. Top City by Completed Claims (Metric) ---
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

    # --- 15. Expired Food Items (DataFrame) ---
    st.write("#### 15. Expired Food Items")
    expired_food_items = run_query("""
        SELECT Food_Name, Expiry_Date
        FROM Food_Listings
        WHERE DATE(Expiry_Date) < DATE('now');
    """)
    if not expired_food_items.empty:
        st.dataframe(expired_food_items, use_container_width=True)
    else:
        st.success("No food items have expired! Great job!")

elif choice == "Claims":
    st.subheader("Food Claims Overview")
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
    st.subheader("Available Food Listings")
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
    st.subheader("Manage Food Listings")
    
    # --- Add New Food Listing Form ---
    st.write("### Add New Food Listing")
    with st.form("Add Food"):
        food_id = st.number_input("Food ID", min_value=1, format="%d", help="The unique ID for the new food item.")
        food_name = st.text_input("Food Name", help="The name of the food item.")
        qty = st.number_input("Quantity", min_value=1, help="The quantity of the food item.")
        expiry = st.date_input("Expiry Date", help="The expiration date of the food item.")
        provider_id = st.number_input("Provider ID", min_value=1, help="The ID of the provider.")
        location = st.text_input("Location", help="The city where the food is located.")
        food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"], help="The dietary type of the food.")
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"], help="The meal the food is intended for.")
        submitted = st.form_submit_button("Add Listing")
        
        if submitted:
            if food_id and food_name and qty and expiry and provider_id and location and food_type and meal_type:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Food_Listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (food_id, food_name, qty, str(expiry), provider_id, location, food_type, meal_type))
                    conn.commit()
                    st.success(f"Food listing with ID {food_id} added successfully!")
                    st.experimental_rerun()
                except sqlite3.Error as e:
                    st.error(f"An error occurred while adding the listing: {e}")
            else:
                st.warning("Please fill in all the fields.")

    st.markdown("---")

    # --- Delete Food Listing Form ---
    st.write("### Delete a Food Listing")
    with st.form("Delete Food"):
        food_id = st.number_input("Food ID to Delete", min_value=1, format="%d", help="Enter the ID of the food item to delete.")
        delete_button = st.form_submit_button("Delete Listing")

        if delete_button:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM Food_Listings WHERE Food_ID = ?", (food_id,))
                    exists = cursor.fetchone()[0] > 0
                    
                    if exists:
                        conn.execute("DELETE FROM Food_Listings WHERE Food_ID = ?", (food_id,))
                        conn.commit()
                        st.success(f"Food listing with ID {food_id} has been successfully deleted.")
                        st.experimental_rerun()
                    else:
                        st.warning(f"No food listing found with ID {food_id}.")
                except sqlite3.Error as e:
                    st.error(f"An error occurred while deleting the listing: {e}")