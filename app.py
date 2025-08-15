# Core Libraries
import sqlite3
import pandas as pd
import streamlit as st
import datetime
import plotly.express as px


st.set_page_config(layout="wide")
st.title("Local Food Wastage Management System")

Table_Name = ['Food_Claims']
Table_Info = ['Claim_ID','Receiver_Name','Receiver_Type','Receiver_City','Receiver_Contact',
              'Provider_Name','Provider_Type','Provider_Address','Provider_City','Provider_Contact',
              'Food_Name','Food_Quantity','Food_Type','Meal_Type','Expiry_Date','Claim_Status','Claim_Datetime','Expiry_Status']

# Function to make Execution
def sql_exe(raw_code):
   conn = sqlite3.connect('database.db')
   cursor = conn.cursor()
   cursor.execute(raw_code)
   data = cursor.fetchall()
   columns = [desc[0] for desc in cursor.description] # for column names
   return data,columns

# For CRUD Operation
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# For Data Referencing in CRUD Operation Selectboxes
data_extract,column_extract = sql_exe('SELECT * FROM Food_Claims')
dataframe = pd.DataFrame(data_extract,columns=column_extract)

# Defining Tabs for App Functionality
tab1,tab2,tab3,tab4 = st.tabs(['SQL PlayGround','CRUD Operation','Analysis','Contact Information'])

# SQL Playground UI and Logic
with tab1:
    st.subheader('Sql PlayGround')
    col1,col2 = st.columns(2)
    with col1:
        with st.form(key = 'query form'):
            raw_code = st.text_area('Enter SQL Code')
            submit_code = st.form_submit_button('Execute')

        # Table of Information
        with st.expander('Database Information'):
            t_info = {'Table Name':Table_Name,'Table Columns':Table_Info}
            st.json(t_info)
    # Result Layouts
    with col2:
        if submit_code:
            st.info('Query Submitted')
            st.code(raw_code)

            #results
            try:
                data,columns = sql_exe(raw_code)
                with st.expander('Result Table'):
                    query_df = pd.DataFrame(data, columns=columns)
                    st.dataframe(query_df,hide_index=True)
            except Exception as e:
                st.error('Query Error')

# CRUD Operation UI and Logic
with tab2:
    st.subheader('Administration')
    # Display Options for CRUD Operations
    Operation = ['Create','Read','Update','Delete']
    option = st.selectbox('Select Option',Operation)
    # Perform Selected CRUD Operations
    if option == 'Create':
        st.markdown('#### Create a Record')
        col1,col2 = st.columns(2)
        with col1:
            Claim_ID = st.number_input('Enter Claim_ID',min_value=1001,step=1)
            Receiver_Name = st.text_input('Enter Receiver Name')
            Receiver_Type = st.selectbox('Select Receiver Type',options = dataframe['Receiver_Type'].unique())
            Receiver_City = st.selectbox('Enter Receiver_City',options = dataframe['Receiver_City'].unique())
            Receiver_Contact = st.text_input('Enter Receiver Contact')
            Provider_Name = st.text_input('Enter Provider Name')
            Provider_Type = st.selectbox('Enter Provider Type',options = dataframe['Provider_Type'].unique())
            Provider_Address = st.text_input('Enter Provider Address')
            Provider_City = st.selectbox('Enter Provider City', options=dataframe['Provider_City'].unique())
        with col2:
            Provider_Contact = st.text_input('Enter Provider Contact')
            Food_Name = st.selectbox('Enter Food Name',options = dataframe['Food_Name'].unique())
            Food_Quantity = st.number_input('Enter Food Quantity',min_value = 1,step = 1)
            Food_Type = st.selectbox('Enter Food Type',options = dataframe['Food_Type'].unique())
            Meal_Type = st.selectbox('Enter Meal Type',options = dataframe['Meal_Type'].unique())
            Expiry_Date = st.date_input('Enter Expiry Date')
            Claim_Status = st.selectbox('Enter Claim Status',options = dataframe['Claim_Status'].unique())
            date_value = st.date_input("Select Claim date")
            time_value = st.time_input("Select Claim time")
            Claim_Datetime = datetime.datetime.combine(date_value, time_value)
            Claim_Datetime_disp = datetime.datetime.combine(date_value, time_value).strftime('%Y-%m-%d %H:%M:%S')
            Expiry_Status = "Expired" if Claim_Datetime.date() > Expiry_Date else "Not Expired"
        if st.button('Write to Database'):
            if Claim_ID in dataframe['Claim_ID'].values:
                st.error('Claim ID already exists')
            else:
                try:
                    cursor.execute("""INSERT INTO Food_Claims(Claim_ID,Receiver_Name,Receiver_Type,Receiver_City,Receiver_Contact,
                    Provider_Name,Provider_Type,Provider_Address,Provider_City,Provider_Contact,Food_Name,Food_Quantity,Food_Type,
                    Meal_Type,Expiry_Date,Claim_Status,Claim_Datetime,Expiry_Status)
                                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(Claim_ID,Receiver_Name,Receiver_Type,Receiver_City,Receiver_Contact,
                    Provider_Name,Provider_Type,Provider_Address,Provider_City,Provider_Contact,Food_Name,Food_Quantity,Food_Type,
                    Meal_Type,Expiry_Date,Claim_Status,Claim_Datetime_disp,Expiry_Status))
                    conn.commit()
                    st.success('Data Written Successfully')
                except Exception as e:
                    st.error(f"Error: {e}")

    elif option == 'Read':
        st.markdown('#### Read a Record')
        Claim_ID = st.number_input('Enter Claim_ID',min_value=1,step=1)
        if st.button('Read From Database'):
            if Claim_ID not in dataframe['Claim_ID'].values:
                st.error('Claim ID does not exist')
            else:
                df_1,col_1 = sql_exe(f"SELECT * FROM Food_Claims WHERE Claim_ID = {Claim_ID}")
                df_2 = pd.DataFrame(df_1,columns=col_1)
                st.dataframe(df_2)
    elif option == 'Update':
        st.markdown('#### Update a Record')
        Claim_ID = st.number_input('Enter Claim_ID',min_value=1,step=1)
        record = None
        if Claim_ID in dataframe['Claim_ID'].values:
            record = dataframe.loc[dataframe['Claim_ID'] == Claim_ID].iloc[0]
        col3, col4 = st.columns(2)
        with col3:
            Receiver_Name = st.text_input('Enter Receiver New Name',value=record['Receiver_Name'] if record is not None else "")
            Receiver_Type = st.selectbox('Select Receiver New Type', options=dataframe['Receiver_Type'].unique(),
                                         index = list(dataframe['Receiver_Type'].unique()).index(record['Receiver_Type'] if record is not None else 0))
            Receiver_City = st.selectbox('Enter Receiver New City', options=dataframe['Receiver_City'].unique(),
                                         index = list(dataframe['Receiver_City'].unique()).index(record['Receiver_City'] if record is not None else 0))
            Receiver_Contact = st.text_input('Enter Receiver New Contact',value=record['Receiver_Contact'] if record is not None else "")
            Provider_Name = st.text_input('Enter Provider New Name',value=record['Provider_Name'] if record is not None else "")
            Provider_Type = st.selectbox('Enter Provider New Type', options=dataframe['Provider_Type'].unique(),
                                         index = list(dataframe['Provider_Type'].unique()).index(record['Provider_Type'] if record is not None else 0))
            Provider_Address = st.text_input('Enter Provider New Address',value=record['Provider_Name'] if record is not None else "")
            Provider_City = st.selectbox('Enter Provider New City', options=dataframe['Provider_City'].unique(),
                                         index = list(dataframe['Provider_City'].unique()).index(record['Provider_City'] if record is not None else 0))
            Provider_Contact = st.text_input('Enter Provider New Contact',value=record['Provider_Contact'] if record is not None else "")
        with col4:
            Food_Name = st.selectbox('Enter New Food Name', options=dataframe['Food_Name'].unique(),
                                     index = list(dataframe['Food_Name'].unique()).index(record['Food_Name'] if record is not None else 0))
            Food_Quantity = st.number_input('Enter New Food Quantity', min_value=1, step=1,value=int(record['Food_Quantity']) if record is not None else 0)
            Food_Type = st.selectbox('Enter New Food Type', options=dataframe['Food_Type'].unique(),
                                     index = list(dataframe['Food_Type'].unique()).index(record['Food_Type'] if record is not None else 0))
            Meal_Type = st.selectbox('Enter New Meal Type', options=dataframe['Meal_Type'].unique(),
                                     index = list(dataframe['Meal_Type'].unique()).index(record['Meal_Type'] if record is not None else 0))
            Expiry_Date = st.date_input('Enter New Expiry_Date',value=pd.to_datetime(record['Expiry_Date']) if record is not None else None)
            Claim_Status = st.selectbox('Enter New Claim Status', options=dataframe['Claim_Status'].unique(),
                                        index = list(dataframe['Claim_Status'].unique()).index(record['Claim_Status'] if record is not None else 0))
            date_value = st.date_input("Select New Claim date", value=pd.to_datetime(record['Claim_Datetime']).date() if record is not None else datetime.date.today())
            time_value = st.time_input("Select New Claim time", value=pd.to_datetime(record['Claim_Datetime']).time() if record is not None else datetime.time.now())
            Claim_Datetime = datetime.datetime.combine(date_value, time_value)
            Claim_Datetime_disp = datetime.datetime.combine(date_value, time_value).strftime("%Y-%m-%d %H:%M:%S")
            Expiry_Status = "Expired" if Claim_Datetime.date() > Expiry_Date else "Not Expired"
        if st.button('Update Record'):
            if Claim_ID not in dataframe['Claim_ID'].values:
                st.error('Claim ID does not exist')
            else:
                try:
                    cursor.execute("""
                    UPDATE Food_Claims
                    SET Receiver_Name = ?,
                        Receiver_Type = ?,
                        Receiver_City = ?,
                        Receiver_Contact = ?,
                        Provider_Name = ?,
                        Provider_Type = ?,
                        Provider_Address = ?,
                        Provider_City = ?,
                        Provider_Contact = ?,
                        Food_Name = ?,
                        Food_Quantity = ?,
                        Food_Type = ?,
                        Meal_Type = ?,
                        Expiry_Date = ?,
                        Claim_Status = ?,
                        Claim_Datetime = ?,
                        Expiry_Status = ?
                    WHERE Claim_ID = ?""", (Receiver_Name, Receiver_Type, Receiver_City, Receiver_Contact,Provider_Name, Provider_Type, Provider_Address,
                                            Provider_City, Provider_Contact,Food_Name, Food_Quantity, Food_Type, Meal_Type,
                                            Expiry_Date,Claim_Status, Claim_Datetime_disp, Expiry_Status, Claim_ID)
                                   )
                    conn.commit()
                    st.success('Data Written Successfully')
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown('#### Delete a Record')
        st.caption('Use with Caution')
        Claim_ID = st.number_input('Enter Claim ID to DELETE Record',min_value=1, step=1)
        if st.button('Delete Record'):
            if Claim_ID not in dataframe['Claim_ID'].values:
                st.error('Claim ID does not exist')
            else:
                try:
                    cursor.execute("""
                    DELETE FROM Food_Claims WHERE Claim_ID = ?
                    """, (Claim_ID,))
                    conn.commit()
                    st.success('Data Deleted Successfully')
                except Exception as e:
                    st.error(f"Error: {e}")
# Analysis Operation UI and Logic
with tab3:
    st.subheader('Analysis')
    Questions = {'Q1':'1. View whole table',
                 'Q2':'2. Number of Food Providers in each City',
                 'Q3':'3. Number of Food Receivers in each City',
                 'Q4':'4. Type of Food Provider contributing the most food',
                 'Q5':'5. Contact information of food providers in a specific city',
                 'Q6':'6. Receiver Type claiming the most food',
                 'Q7':'7. Total Quantity of Food Available from all Providers',
                 'Q8':'8. Top 5 City having highest food listings',
                 'Q9':'9. Commonly Available Food Types',
                 'Q10':'10. Claim Status % Distribution',
                 'Q11':'11. Food Claims made for each Food Item',
                 'Q12':'12. Provider having highest successful food claims',
                 'Q13':'13. Average Quantity of Food Claimed Per Receiver',
                 'Q14':'14. Receivers who Received Expired Food',
                 'Q15':'15. Most Claimed Meal Type',
                 'Q16':'16. Total Quantity of Food Donated by each provider',
                 'Q17':'17. Total Quantity of Food Received by each receiver',
                 'Q18':'18. Providers who shipped Expired food but yet not delivered'}
    col1,col2 = st.columns(2)
    with col1:
        selected_query = st.selectbox('Select Your Query', list(Questions.values()))
        submit_query = st.button('Submit',key = 'form1_submit')
        if submit_query:
            if selected_query == Questions['Q1']:
                query = """SELECT * FROM Food_Claims;"""
            elif selected_query == Questions['Q2']:
                query = ("""SELECT 
    Provider_City, 
    COUNT(DISTINCT Provider_Contact) AS Number_of_Food_Providers
FROM Food_Claims
GROUP BY Provider_City;""")
            elif selected_query == Questions['Q3']:
                query = ("""SELECT 
    Receiver_City,
    COUNT(DISTINCT Receiver_Contact) AS Number_of_Food_Receivers
FROM Food_Claims
GROUP BY Receiver_City;""")
            elif selected_query == Questions['Q4']:
                query = ("""SELECT 
    Provider_Type,
    SUM(Food_Quantity) AS Food_Quantity
FROM Food_Claims
GROUP BY Provider_Type;""")
            elif selected_query == Questions['Q5']:
                query = ("""SELECT 
    Provider_City,
    Provider_Address,
    Provider_Contact
FROM Food_Claims
GROUP BY Provider_City;""")
            elif selected_query == Questions['Q6']:
                query = ("""SELECT 
    Receiver_Type,
    SUM(Food_Quantity) AS Food_Quantity
FROM Food_Claims
GROUP BY Receiver_Type;""")
            elif selected_query == Questions['Q7']:
                query = ("""SELECT 
    SUM(Food_Quantity) AS Total_Food_Quantity
FROM Food_Claims;""")
            elif selected_query == Questions['Q8']:
                query = ("""SELECT 
    Provider_City,
    COUNT(Claim_ID) AS Number_of_Listings
FROM Food_Claims
GROUP BY Provider_City
ORDER BY COUNT(Claim_ID) DESC
LIMIT 5;""")
            elif selected_query == Questions['Q9']:
                query = ("""SELECT 
    Food_Name,
    SUM(Food_Quantity) AS Food_Qty
FROM Food_Claims
GROUP BY Food_Name
ORDER BY SUM(Food_Quantity) DESC;""")
            elif selected_query == Questions['Q10']:
                query = ("""SELECT 
    Claim_Status,
    COUNT(*) AS Total_Claims,
    ROUND((COUNT(*)*100.0/(SELECT COUNT(*) FROM Food_Claims)),2) AS Percentage
FROM Food_Claims
GROUP BY Claim_Status;""")
            elif selected_query == Questions['Q11']:
                query = ("""SELECT 
    Food_Name,
    COUNT(Claim_ID) AS Claims
FROM Food_Claims
GROUP BY Food_Name;""")
            elif selected_query == Questions['Q12']:
                query = ("""SELECT
    Provider_Name,
    Provider_City,
    Provider_Contact,
    Provider_Type,
    COUNT(Claim_ID) AS Successful_Claims
FROM Food_Claims 
WHERE Claim_Status = 'Completed'
GROUP BY Provider_Name,Provider_City,Provider_Contact,Provider_Type
ORDER BY Successful_Claims DESC;""")
            elif selected_query == Questions['Q13']:
                query = ("""SELECT 
    ROUND(AVG(Food_Quantity)) AS Avg_Food_Quantity_Per_Receiver
FROM Food_Claims;""")
            elif selected_query == Questions['Q14']:
                query = ("""SELECT 
    Receiver_Name,
    Receiver_Type,
    Receiver_Contact,
    Food_Name,
    Food_Type,
    Meal_Type,
    Provider_Name,
    Provider_Contact
FROM Food_Claims WHERE Expiry_Status = 'Expired' AND Claim_Status = 'Completed';""")
            elif selected_query == Questions['Q15']:
                query = ("""SELECT 
    Meal_Type,
    COUNT(*) AS Total_Claims,
    ROUND((COUNT(*)*100.0/(SELECT COUNT(*) FROM Food_Claims)),2) AS Percentage
FROM Food_Claims
GROUP BY Meal_Type;""")
            elif selected_query == Questions['Q16']:
                query = ("""SELECT 
    Provider_Name,
    Provider_Contact,
    SUM(Food_Quantity) AS Food_Quantity
FROM Food_Claims WHERE Claim_Status = 'Completed'
GROUP BY Provider_Name,Provider_Contact
ORDER BY SUM(Food_Quantity) DESC;""")
            elif selected_query == Questions['Q17']:
                query = ("""SELECT 
    Receiver_Name,
    Receiver_Contact,
    SUM(Food_Quantity) AS Food_Quantity
FROM Food_Claims WHERE Claim_Status = 'Completed'
GROUP BY Receiver_Name,Receiver_Contact
ORDER BY SUM(Food_Quantity) DESC;""")
            else:
                query = ("""SELECT 
    Provider_Name,
    Provider_Type,
    Provider_Contact,
    Food_Quantity
FROM Food_Claims WHERE Expiry_Status = 'Expired' AND Claim_Status = 'Pending'
ORDER BY Food_Quantity DESC;""")
            st.caption('SQL Code:')
            st.code(query)
            data_viz,col_viz = sql_exe(query)
            query_df_viz = pd.DataFrame(data_viz,columns=col_viz)
            num_cols = query_df_viz.select_dtypes(include='number').columns
            cat_cols = query_df_viz.select_dtypes(exclude='number').columns
    with col2:
        if submit_query:
            st.info('Query Submitted')
            data,columns = sql_exe(query)
            with st.expander('Results'):
                query_df = pd.DataFrame(data, columns=columns)
                st.dataframe(query_df,hide_index=True)
            if len(num_cols) > 0 and len(cat_cols) > 0 and query != 'SELECT * FROM Food_Claims;':
                df_plot = px.bar(
                    query_df_viz,
                    x=cat_cols[0],  # first categorical column
                    y=num_cols[0],  # first numeric column
                    color_discrete_sequence=['red']
                )
                df_plot.update_xaxes(showgrid = False)
                df_plot.update_yaxes(showgrid = False)
                st.plotly_chart(df_plot)
            else:
                st.warning("Data format not suitable for bar chart")
# Contact Information UI and Logic
with tab4:
    st.subheader('Contact Information')
    col1,col2 = st.columns(2)
    with col1:
        st.write('##### Providers')
        selected_provider_city = st.selectbox('Select City', options=dataframe['Provider_City'].unique())
        provider_info = cursor.execute("""SELECT Provider_Name,Provider_Contact,Provider_Type 
                                          FROM Food_Claims 
                                          WHERE Provider_City = ?""",(selected_provider_city,)).fetchall()
        df_provider_info = pd.DataFrame(provider_info, columns=['Provider_Name','Provider_Contact','Provider_Type']).drop_duplicates()
        st.dataframe(df_provider_info,hide_index=True)
    with col2:
        st.write('##### Receivers')
        selected_receiver_city = st.selectbox('Select City', options=dataframe['Receiver_City'].unique())
        receiver_info = cursor.execute("""SELECT Receiver_Name, Receiver_Contact, Receiver_Type
                                          FROM Food_Claims
                                          WHERE Receiver_City = ?""", (selected_receiver_city,)).fetchall()
        df_receiver_info = pd.DataFrame(receiver_info, columns=['Receiver_Name', 'Receiver_Contact',
                                                                'Receiver_Type']).drop_duplicates()
        st.dataframe(df_receiver_info, hide_index=True)