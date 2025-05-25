import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_extras.stylable_container import stylable_container


# Set page config
st.set_page_config(
    page_title="validator",
    layout="wide"
)

# Initialize session state if not exists
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
    st.session_state.data = None
    st.session_state.grades = []
    st.session_state.total_items = 0

def reset_state():
    st.session_state.current_index = 0
    st.session_state.grades = []

def grade_and_next(grade):
    if st.session_state.data is not None and st.session_state.current_index < st.session_state.total_items:
        # Store the grade
        current_row = st.session_state.data.iloc[st.session_state.current_index]
        st.session_state.grades.append({
            'title': current_row['title'],
            'true_desc': current_row['true_desc'],
            'gen_desc': current_row['gen_desc'],
            'grade': grade
        })
        
        # Move to next item
        st.session_state.current_index += 1
        
        # If we've graded all items, create and save the output file
        if st.session_state.current_index >= st.session_state.total_items:
            output_df = pd.DataFrame(st.session_state.grades)
            output_path = Path('output/graded_descriptions.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_df.to_csv(output_path, index=False)
            st.success(f"Результаты разметки сохранены в '{output_path}'")

def main():
    # File upload
    uploaded_file = st.file_uploader("Загрзука csv с колонками 'title', 'gen_desc', 'true_desc':", type=['csv'], on_change=reset_state)
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            required_columns = ['title', 'gen_desc', 'true_desc']
            
            # Verify required columns
            if not all(col in df.columns for col in required_columns):
                st.error("CSV file must contain columns: 'title', 'gen_desc', and 'true_desc'")
                return
                
            # Store data in session state
            if st.session_state.data is None:
                st.session_state.data = df
                st.session_state.total_items = len(df)
        
        except Exception as e:
            st.error(f"Error reading the CSV file: {str(e)}")
            return
        
        # Display current item if not all items are graded
        if st.session_state.current_index < st.session_state.total_items:
            current_item = st.session_state.data.iloc[st.session_state.current_index]
            
            # Display the title
            st.markdown(f"### Название:\n {current_item['title']}")
            # Create three columns for the buttons
            col1, col2, col3 = st.columns(3)
            
            # Add buttons with custom styling
            with col1:
                with stylable_container(
                    "red",
                    css_styles="""
                    button {
                        background-color: #963d36;
                        color: black;
                    }""",
                ):
                    if st.button("Хуже", key="worse", 
                                # help="Generated description is worse than the true description",
                                use_container_width=True):
                        grade_and_next(-1)
                        st.rerun()
            with col2:
                with stylable_container(
                    "yellow",
                    css_styles="""
                    button {
                        background-color: #f5cb42;
                        color: black;
                    }""",
                ):
                    if st.button("Одинаково", key="same",
                                # help="Generated description is similar to the true description",
                                use_container_width=True):
                        grade_and_next(0)
                        st.rerun()
            
            with col3:
                with stylable_container(
                    "green",
                    css_styles="""
                    button {
                        background-color: #4aba56;
                        color: black;
                    }""",
                ):
                    if st.button("Лучше", key="better",
                                # help="Generated description is better than the true description",
                                use_container_width=True):
                        grade_and_next(1)
                        st.rerun()
                
            # Create two columns for descriptions
            desc_col1, desc_col2 = st.columns(2)
            
            with desc_col1:
                st.markdown("### Сгенерированное описание:")
                st.write(current_item['gen_desc'])
            
            with desc_col2:
                st.markdown("### Реальное описание:")
                st.write(current_item['true_desc'])
            
            # Display progress
            st.progress(st.session_state.current_index / st.session_state.total_items)
            st.write(f"Прогресс: {st.session_state.current_index}/{st.session_state.total_items}")
        
        elif len(st.session_state.grades) > 0:
            st.success("Результаты сохранены в 'output/graded_descriptions.csv'")
            
            # Display the results table
            results_df = pd.DataFrame(st.session_state.grades)
            st.write("### Результаты")
            st.dataframe(results_df)

if __name__ == "__main__":
    main() 