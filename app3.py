import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore

# App title
st.title("Data Analysis and Cleaning with Streamlit")

# File uploader
uploaded_file = st.file_uploader("Upload a Dataset (CSV or Excel)", type=["csv", "xlsx", "xls"])

# Initialize session state for the DataFrame
if "df" not in st.session_state:
    st.session_state.df = None
if "cleaned" not in st.session_state:
    st.session_state.cleaned = False

if uploaded_file is not None:
    try:
        # Load the dataset into session state if not already loaded
        if st.session_state.df is None:
            if uploaded_file.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                st.session_state.df = pd.read_excel(uploaded_file)

        # Sidebar options for main sections
        st.sidebar.title("Options")
        section = st.sidebar.radio(
            "Select a Section:",
            ["Data Show", "Cleaning", "Outliers Detection", "Visualization and Correlations"]
        )

        # Section 1: Data Show
        if section == "Data Show":
            st.sidebar.subheader("Data Show Options")
            with st.sidebar.expander("Choose an Option:"):
                data_option = st.radio(
                    "Select an Option:",
                    ["Preview Data", "Columns Info", "Dataset Info", "Summary Statistics", 
                     "Missing Values per Column", "Unique Values per Column", 
                     "Detailed Column Information", "Value Distribution per Column"]
                )

            if data_option == "Preview Data":
                st.header("Preview Data")
                num_rows = st.sidebar.slider("Select the number of rows to display:", 1, len(st.session_state.df), 5)
                st.dataframe(st.session_state.df.head(num_rows))

            elif data_option == "Columns Info":
                st.header("Columns and Data Types")
                st.markdown(f"### Total Columns: {len(st.session_state.df.columns)}")
                for column, dtype in zip(st.session_state.df.columns, st.session_state.df.dtypes):
                    column_type = "Numeric" if pd.api.types.is_numeric_dtype(dtype) else "Categorical"
                    st.markdown(f"- **{column}**: {column_type} ({str(dtype)})")

            elif data_option == "Dataset Info":
                st.header("Dataset Info")
                buffer = StringIO()
                st.session_state.df.info(buf=buffer)
                st.text(buffer.getvalue())

            elif data_option == "Summary Statistics":
                st.header("Summary Statistics")
                st.write(st.session_state.df.describe(include='all'))

            elif data_option == "Missing Values per Column":
                st.header("Missing Values per Column")
                missing_values = st.session_state.df.isnull().sum()
                st.write(missing_values)

            elif data_option == "Unique Values per Column":
                st.header("Unique Values per Column")
                unique_values = st.session_state.df.nunique()
                st.write(unique_values)

            elif data_option == "Detailed Column Information":
                st.header("Detailed Column Information")
                for column in st.session_state.df.columns:
                    st.subheader(f"**{column}**")
                    column_data = st.session_state.df[column]
                    st.markdown(f"- **Data Type**: {column_data.dtype}")
                    st.markdown(f"- **Number of Missing Values**: {column_data.isnull().sum()}")
                    st.markdown(f"- **Number of Unique Values**: {column_data.nunique()}")
                    st.markdown(f"- **Value Distribution**: {column_data.value_counts().head()}")
                    st.markdown(f"- **Example Values**: {column_data.head().to_list()}")
                    st.markdown("---")

            elif data_option == "Value Distribution per Column":
                st.header("Value Distribution per Column")
                column_to_plot = st.sidebar.selectbox("Select a column to visualize:", st.session_state.df.columns.tolist())
                st.header(f"Value Distribution of {column_to_plot}")
                if st.session_state.df[column_to_plot].dtype == 'object':
                    fig = plt.figure(figsize=(10, 6))
                    sns.countplot(y=st.session_state.df[column_to_plot], palette="Set2")
                    st.pyplot(fig)
                else:
                    st.warning("Please select a categorical column for this option.")

        # Section 2: Cleaning
        elif section == "Cleaning":
            st.sidebar.subheader("Cleaning Options")
            with st.sidebar.expander("Choose a Cleaning Option:"):
                cleaning_option = st.radio(
                    "Select a Cleaning Option:",
                    ["Clean Column ", "Remove Duplicates", "Handle Missing Values", 
                     "Remove Columns", "Drop Rows with Missing Values"]
                )

            if cleaning_option == "Clean Column ":
                st.header("Step 1: Cleaning Column")
                original_columns = st.session_state.df.columns.tolist()

                # Clean column names
                st.session_state.df.columns = (
                    st.session_state.df.columns
                    .str.strip()
                    .str.replace(r"\s+", "_", regex=True)
                    .str.replace(r"[^a-zA-Z0-9_]", "")
                    .str.lower()
                    .str.replace(r"^(?=\d)", "_", regex=True)
                )

                cleaned_columns = st.session_state.df.columns.tolist()
                if original_columns != cleaned_columns:
                    st.write("Column names have been cleaned:")
                    for original, cleaned in zip(original_columns, cleaned_columns):
                        if original != cleaned:
                            st.write(f"- **{original}** → **{cleaned}**")
                else:
                    st.write("Column names are already clean.")

                # Clean column values
                for column in st.session_state.df.columns:
                    if st.session_state.df[column].dtype == 'object':
                        st.session_state.df[column] = st.session_state.df[column].str.lower()

                    if pd.api.types.is_categorical_dtype(st.session_state.df[column]) or st.session_state.df[column].dtype == 'object':
                        num_numeric_values = st.session_state.df[column].apply(pd.to_numeric, errors='coerce').notna().sum()
                        total_values = len(st.session_state.df[column])
                        numeric_percentage = num_numeric_values / total_values * 100

                        if numeric_percentage > 70:
                            st.session_state.df[column] = pd.to_numeric(st.session_state.df[column], errors='coerce')

                st.success("Column names and values have been cleaned.")
                st.session_state.cleaned = True  # Mark as cleaned

                # Add option to rename a column
                st.sidebar.subheader("Rename a Column")
                column_to_rename = st.sidebar.selectbox(
                    "Select a column to rename:", st.session_state.df.columns.tolist()
                )
                new_name = st.sidebar.text_input(f"Enter the new name for column '{column_to_rename}':")
                if new_name and new_name != column_to_rename:
                    st.session_state.df = st.session_state.df.rename(columns={column_to_rename: new_name})
                    st.success(f"Column '{column_to_rename}' renamed to '{new_name}'.")

                # Add option to convert a column's data type
                st.sidebar.subheader("Convert Data Type")
                column_to_convert = st.sidebar.selectbox(
                    "Select a column to convert its data type:", st.session_state.df.columns.tolist()
                )
                new_data_type = st.sidebar.selectbox(
                    f"Select the new data type for column '{column_to_convert}':",
                    ["int", "float", "str", "bool"]
                )   
                
                if st.sidebar.button("Convert Data Type"):
                    try:
                        # Convert the column's data type
                       st.session_state.df[column_to_convert] = st.session_state.df[column_to_convert].astype(new_data_type)
                       st.success(f"Data type of column '{column_to_convert}' converted to '{new_data_type}'.")
                    except Exception as e:
                        st.error(f"Error converting data type of column '{column_to_convert}': {e}")
            
            
 
 

            elif cleaning_option == "Remove Duplicates":
                st.header("Remove Duplicate Rows")
                initial_rows = len(st.session_state.df)
                st.session_state.df = st.session_state.df.drop_duplicates()
                final_rows = len(st.session_state.df)
                st.success(f"Duplicate rows removed. Rows reduced from {initial_rows} to {final_rows}.")
                st.session_state.cleaned = True  # Mark as cleaned

            elif cleaning_option == "Handle Missing Values":
                st.header("Handle Missing Values")
                
                # Show missing values count for numeric columns only
                numeric_columns = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_columns:
                    st.subheader("Missing Values in Numeric Columns:")
                    missing_values_numeric = st.session_state.df[numeric_columns].isnull().sum()
                    st.write(missing_values_numeric)

                    # Fill missing values for numeric columns
                    column_to_fill_numeric = st.sidebar.selectbox("Select a numeric column to fill missing values:", numeric_columns)
                    if column_to_fill_numeric:
                        fill_method_numeric = st.sidebar.radio(
                            f"Select how to fill missing values for numeric column '{column_to_fill_numeric}':",
                            ["Do Nothing", "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with Specific Value"]
                        )

                        if fill_method_numeric == "Do Nothing":
                            st.info(f"No missing value filling action selected for column '{column_to_fill_numeric}'.")
                        
                        elif fill_method_numeric == "Fill with Mean":
                            mean_value = st.session_state.df[column_to_fill_numeric].mean()
                            st.session_state.df[column_to_fill_numeric] = st.session_state.df[column_to_fill_numeric].fillna(mean_value)
                            st.success(f"Missing values in column '{column_to_fill_numeric}' filled with the mean ({mean_value}).")

                        elif fill_method_numeric == "Fill with Median":
                            median_value = st.session_state.df[column_to_fill_numeric].median()
                            st.session_state.df[column_to_fill_numeric] = st.session_state.df[column_to_fill_numeric].fillna(median_value)
                            st.success(f"Missing values in column '{column_to_fill_numeric}' filled with the median ({median_value}).")

                        elif fill_method_numeric == "Fill with Mode":
                            mode_value = st.session_state.df[column_to_fill_numeric].mode()[0]
                            st.session_state.df[column_to_fill_numeric] = st.session_state.df[column_to_fill_numeric].fillna(mode_value)
                            st.success(f"Missing values in column '{column_to_fill_numeric}' filled with the mode ({mode_value}).")

                        elif fill_method_numeric == "Fill with Specific Value":
                            specific_value_numeric = st.sidebar.number_input("Enter the specific value:", value=0.0)

                            if specific_value_numeric == 0.0:
                              st.warning("Please enter a value greater than 0 to fill the missing data.")
                            else:
                                st.session_state.df[column_to_fill_numeric] = st.session_state.df[column_to_fill_numeric].fillna(specific_value_numeric)
                                st.success(f"Missing values in column '{column_to_fill_numeric}' filled with '{specific_value_numeric}'.")





                else:
                    st.warning("No numeric columns available to fill missing values.")

                # Handle missing values for text columns
                text_columns = st.session_state.df.select_dtypes(include=[object]).columns.tolist()
                if text_columns:
                    st.subheader("Missing Values in Text Columns:")
                    missing_values_text = st.session_state.df[text_columns].isnull().sum()
                    st.write(missing_values_text)

                    # Fill missing values for text columns
                    column_to_fill_text = st.sidebar.selectbox("Select a text column to fill missing values:", text_columns)
                    if column_to_fill_text:
                        fill_method_text = st.sidebar.radio(
                            f"Select how to fill missing values for text column '{column_to_fill_text}':",
                            ["Do Nothing","Fill with Most Frequent Value", "Fill with Specific Value"]
                        )

                        if fill_method_text  == "Do Nothing":
                            st.info(f"No missing value filling action selected for column '{column_to_fill_text}'.")

                        elif fill_method_text == "Fill with Most Frequent Value":
                            most_frequent_value = st.session_state.df[column_to_fill_text].mode()[0]
                            st.session_state.df[column_to_fill_text] = st.session_state.df[column_to_fill_text].fillna(most_frequent_value)
                            st.success(f"Missing values in column '{column_to_fill_text}' filled with the most frequent value ({most_frequent_value}).")

                        elif fill_method_text == "Fill with Specific Value":
                            specific_value_text = st.sidebar.text_input("Enter the specific value:", value="")
    
                            if specific_value_text.strip() != "":  # التحقق من أن القيمة المدخلة ليست فارغة
                              st.session_state.df[column_to_fill_text] = st.session_state.df[column_to_fill_text].fillna(specific_value_text)
                              st.success(f"Missing values in column '{column_to_fill_text}' filled with '{specific_value_text}'.")
                            else:
                                st.warning("Please enter a valid value to fill the missing data.")




                else:
                    st.warning("No text columns available to fill missing values.")

                # Mark as cleaned
                st.session_state.cleaned = True

            elif cleaning_option == "Remove Columns":
                st.header("Remove Columns")
                columns_to_remove = st.sidebar.multiselect(
                    "Select columns to remove:", st.session_state.df.columns.tolist()
                )
                if columns_to_remove:
                    st.session_state.df = st.session_state.df.drop(columns=columns_to_remove)
                    st.success(f"Columns removed: {', '.join(columns_to_remove)}")
                st.session_state.cleaned = True  # Mark as cleaned

            elif cleaning_option == "Drop Rows with Missing Values":
                st.header("Drop Rows with Missing Values")
                initial_rows = len(st.session_state.df)
                st.session_state.df = st.session_state.df.dropna()
                final_rows = len(st.session_state.df)
                st.success(f"Rows with missing values have been dropped. Rows reduced from {initial_rows} to {final_rows}.")
                st.session_state.cleaned = True  # Mark as cleaned

    # Section 3: Outliers Detection
        elif section == "Outliers Detection":
            st.sidebar.subheader("Outliers Detection Options")
            with st.sidebar.expander("Choose Outlier Detection Method:"):
                outlier_method = st.radio(
                    "Select Outlier Detection Method:",
                    ["IQR"]
                )

            # Define numeric_columns for outlier detection
            numeric_columns = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()

            if outlier_method == "IQR":
                st.header("Outlier Detection using IQR")
                Q1 = st.session_state.df[numeric_columns].quantile(0.25)
                Q3 = st.session_state.df[numeric_columns].quantile(0.75)
                IQR = Q3 - Q1

                # Detect outliers
                outliers = ((st.session_state.df[numeric_columns] < (Q1 - 1.5 * IQR)) | 
                             (st.session_state.df[numeric_columns] > (Q3 + 1.5 * IQR)))
                
                # Display the number of outliers for each column
                st.write("Number of outliers detected using IQR method for each column:")
                outlier_counts = outliers.sum()  # Count of True values (outliers)
                st.write(outlier_counts)

                # Add option to fill outliers with predefined methods or a custom value
                fill_method = st.sidebar.radio("Select how to fill outliers:", 
                                                ["Do Nothing","Replace with Mean", "Replace with Median", 
                                                 "Replace with Mode", "Replace with Custom Value"])
                custom_value = None
                if fill_method == "Replace with Custom Value":
                    custom_value = st.sidebar.number_input("Enter value to replace outliers:", value=0)

                column_to_fill = st.sidebar.selectbox("Select a column to replace outliers:", numeric_columns)

                # Replace outliers based on the selected method
                if st.sidebar.button("Replace Outliers"):
                    
                    if fill_method == "Do Nothing":
                            st.info(f"No OutLier Action '{column_to_fill}'.")

                    elif fill_method == "Replace with Mean":
                        mean_value = st.session_state.df[column_to_fill].mean()
                        st.session_state.df[column_to_fill] = st.session_state.df[column_to_fill].where(
                            ~outliers[column_to_fill], mean_value
                        )
                        st.success(f"Outliers in column '{column_to_fill}' replaced with the mean value ({mean_value}).")

                    elif fill_method == "Replace with Median":
                        median_value = st.session_state.df[column_to_fill].median()
                        st.session_state.df[column_to_fill] = st.session_state.df[column_to_fill].where(
                            ~outliers[column_to_fill], median_value
                        )
                        st.success(f"Outliers in column '{column_to_fill}' replaced with the median value ({median_value}).")

                    elif fill_method == "Replace with Mode":
                        mode_value = st.session_state.df[column_to_fill].mode()[0]
                        st.session_state.df[column_to_fill] = st.session_state.df[column_to_fill].where(
                            ~outliers[column_to_fill], mode_value
                        )
                        st.success(f"Outliers in column '{column_to_fill}' replaced with the mode value ({mode_value}).")

                    elif fill_method == "Replace with Custom Value" and custom_value is not None:
                        st.session_state.df[column_to_fill] = st.session_state.df[column_to_fill].where(
                            ~outliers[column_to_fill], custom_value
                        )
                        st.success(f"Outliers in column '{column_to_fill}' replaced with the custom value ({custom_value}).")

            

        # Section 4: Visualization and Correlations
        elif section == "Visualization and Correlations":
            st.sidebar.subheader("Visualization Options")
            vis_option = st.sidebar.radio(
                "Select a Visualization Option:",
                ["Histogram", "Scatter Plot", "Correlation Matrix", "Box Plot", "Pair Plot", "Violin Plot"]
            )

            numeric_columns = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()

            if vis_option in ["Histogram", "Box Plot", "Violin Plot"]:
                column_to_plot = st.sidebar.selectbox("Select a numeric column to plot:", numeric_columns)
                st.header(f"{vis_option} of {column_to_plot}")
                if vis_option == "Histogram":
                    fig = plt.figure(figsize=(10, 6))
                    sns.histplot(st.session_state.df[column_to_plot], kde=True, bins=30)
                    st.pyplot(fig)

                elif vis_option == "Box Plot":
                    fig = plt.figure(figsize=(10, 6))
                    sns.boxplot(x=st.session_state.df[column_to_plot])
                    st.pyplot(fig)

                elif vis_option == "Violin Plot":
                    fig = plt.figure(figsize=(10, 6))
                    sns.violinplot(x=st.session_state.df[column_to_plot])
                    st.pyplot(fig)

            elif vis_option == "Scatter Plot":
                x_axis = st.sidebar.selectbox("Select the column for X-axis:", numeric_columns)
                y_axis = st.sidebar.selectbox("Select the column for Y-axis:", numeric_columns)
                st.header(f"Scatter Plot between {x_axis} and {y_axis}")
                fig = plt.figure(figsize=(10, 6))
                sns.scatterplot(x=st.session_state.df[x_axis], y=st.session_state.df[y_axis])
                st.pyplot(fig)

            elif vis_option == "Correlation Matrix":
                st.header("Correlation Matrix")
                corr = st.session_state.df[numeric_columns].corr()
                fig = plt.figure(figsize=(10, 8))
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
                st.pyplot(fig)

            elif vis_option == "Pair Plot":
                st.header("Pair Plot")
                fig = px.scatter_matrix(st.session_state.df[numeric_columns])
                st.plotly_chart(fig)

        # Download button for cleaned dataset (only after cleaning)
        if st.session_state.cleaned:
            st.sidebar.subheader("Download Cleaned Dataset")
            cleaned_file = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="Download Cleaned Dataset",
                data=cleaned_file,
                file_name='cleaned_dataset.csv',
                mime='text/csv',
                key='download-csv'
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    st.info("Please upload a CSV or Excel file to start analyzing your data.")