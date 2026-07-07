import streamlit as st
from snowflake.snowpark.functions import col

# Use Streamlit connection only
cnx = st.connection("snowflake")
session = cnx.session()

st.title("My Parents New Healthy Diner")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from Snowflake
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Convert Snowflake dataframe to pandas/list for Streamlit multiselect
fruit_df = my_dataframe.to_pandas()
fruit_options = fruit_df["FRUIT_NAME"].tolist()

st.dataframe(fruit_df, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    st.write("Selected ingredients:", ingredients_string)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
