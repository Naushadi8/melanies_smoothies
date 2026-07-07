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
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake dataframe to pandas/list
fruit_df = my_dataframe.to_pandas()
fruit_options = fruit_df["FRUIT_NAME"].tolist()

# Fruit multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Submit order section
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

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


# New section to display smoothiefroot nutrition information
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

smoothiefroot_json = smoothiefroot_response.json()

# The API may return either "nutrition" or "nutritions"
nutrition_data = (
    smoothiefroot_json.get("nutrition")
    or smoothiefroot_json.get("nutritions")
    or {}
)

# Build the nutrition table
nutrition_rows = []

for nutrient, value in nutrition_data.items():
    nutrition_rows.append(
        {
            "": nutrient,
            "family": smoothiefroot_json.get("family"),
            "genus": smoothiefroot_json.get("genus"),
            "id": smoothiefroot_json.get("id"),
            "name": smoothiefroot_json.get("name"),
            "nutrition": value,
            "order": smoothiefroot_json.get("order"),
        }
    )

nutrition_df = pd.DataFrame(nutrition_rows)

if not nutrition_df.empty:
    nutrition_df = nutrition_df.set_index("")
    st.dataframe(nutrition_df, use_container_width=True)
else:
    st.warning("No nutrition data found from the SmoothieFroot API.")
