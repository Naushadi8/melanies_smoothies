import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Use Streamlit Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Customer name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from Snowflake
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col('SEARCH_ON')
))
#st.dataframe(data=my_dataframe, use_container_width = True)
#st.stop()

# Convert the Snowpark DataFrame to a pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()
fruit_options = fruit_df["FRUIT_NAME"].tolist()

# Fruit multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/watermelon"
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write("Selected ingredients:", ingredients_string)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        safe_ingredients = ingredients_string.replace("'", "''")
        safe_name = name_on_order.replace("'", "''")

        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
