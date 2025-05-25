import streamlit as st
import pandas as pd
from pathlib import Path
import random
from streamlit_extras.stylable_container import stylable_container

# Set page config
st.set_page_config(
    page_title="Description Comparison",
    layout="wide"
)

# Initialize session state if not exists
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
    st.session_state.data = None
    st.session_state.grades = []
    st.session_state.total_items = 0
    st.session_state.random_switch = random.randint(0, 1)

def reset_state():
    st.session_state.current_index = 0
    st.session_state.grades = []
    st.session_state.random_switch = random.randint(0, 1)

def handle_key_press():
    if st.session_state.key_pressed in ["1", "2"]:
        grade_and_next(0 if st.session_state.key_pressed == "1" else 1)
        st.session_state.key_pressed = ""  # Reset the input
        st.rerun()

def grade_and_next(selected_description):
    if st.session_state.data is not None and st.session_state.current_index < st.session_state.total_items:
        current_row = st.session_state.data.iloc[st.session_state.current_index]
        
        # If random_switch is 1, we need to flip the selected_description value
        # because the true and generated descriptions were swapped in display
        actual_selection = selected_description if st.session_state.random_switch == 0 else (1 - selected_description)
        
        # Store the grade (0 if first description was selected, 1 if second was selected)
        st.session_state.grades.append({
            'title': current_row['title'],
            'selected_desc': 'generated' if actual_selection == 0 else 'true',
            'first_shown': 'generated' if st.session_state.random_switch == 0 else 'true',
            'second_shown': 'true' if st.session_state.random_switch == 0 else 'generated',
            'true_desc': current_row['true_desc'],
            'gen_desc': current_row['gen_desc']
        })
        
        # Move to next item and randomize description order
        st.session_state.current_index += 1
        st.session_state.random_switch = random.randint(0, 1)
        
        # If we've graded all items, create and save the output file
        if st.session_state.current_index >= st.session_state.total_items:
            output_df = pd.DataFrame(st.session_state.grades)
            output_path = Path('output/comparison_results.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_df.to_csv(output_path, index=False)

def main():
    st.title("Сравнение описаний")
    
    # File upload
    uploaded_file = st.file_uploader("Загрузка csv с колонками 'title', 'gen_desc', 'true_desc':", type=['csv'], on_change=reset_state)
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            required_columns = ['title', 'gen_desc', 'true_desc']
            
            # Verify required columns
            if not all(col in df.columns for col in required_columns):
                st.error("CSV должен содержать колонки: 'title', 'gen_desc', и 'true_desc'")
                return
                
            # Store data in session state
            if st.session_state.data is None:
                st.session_state.data = df
                st.session_state.total_items = len(df)
        
        except Exception as e:
            st.error(f"Ошибка чтения файла: {str(e)}")
            return
        
        # Display current item if not all items are graded
        if st.session_state.current_index < st.session_state.total_items:
            current_item = st.session_state.data.iloc[st.session_state.current_index]
            
            # Display the title
            st.markdown(f"### Название:\n {current_item['title']}")
            
            # Create two columns for descriptions
            desc_col1, desc_col2 = st.columns(2)
            
            with desc_col1:
                st.markdown("### Описание 1:")
                first_desc = current_item['gen_desc' if st.session_state.random_switch == 0 else 'true_desc']
                st.write(first_desc)
            
            with desc_col2:
                st.markdown("### Описание 2:")
                second_desc = current_item['true_desc' if st.session_state.random_switch == 0 else 'gen_desc']
                st.write(second_desc)
            
            # Create two columns for buttons
            col1, col2 = st.columns(2)
            
            # Add buttons with custom styling
            with col1:
                with stylable_container(
                    "first",
                    css_styles="""
                    button {
                        background-color: #4a90e2;
                        color: white;
                        -moz-user-select: none;
                        -khtml-user-select: none;
                        -webkit-user-select: none;
                        -ms-user-select: none;
                        user-select: none;
                    }
                    button:hover {
                        background-color: #357abd;
                        color: white;
                    }
                    """,
                ):
                    if st.button("Предпочитаю первое описание (1)", key="first", use_container_width=True):
                        grade_and_next(0)
                        st.rerun()
            
            with col2:
                with stylable_container(
                    "second",
                    css_styles="""
                    button {
                        background-color: #4a90e2;
                        color: white;
                        -moz-user-select: none;
                        -khtml-user-select: none;
                        -webkit-user-select: none;
                        -ms-user-select: none;
                        user-select: none;
                    }
                    button:hover {
                        background-color: #357abd;
                        color: white;
                    }
                    """,
                ):
                    if st.button("Предпочитаю второе описание (2)", key="second", use_container_width=True):
                        grade_and_next(1)
                        st.rerun()
            
            # Add a visible input field that spans both columns
            st.text_input(
                "1 или 2 + Enter для выбора описания:",
                key="key_pressed",
                max_chars=1,
                on_change=handle_key_press
            )
            
            # Display progress
            st.progress(st.session_state.current_index / st.session_state.total_items)
            st.write(f"Прогресс: {st.session_state.current_index}/{st.session_state.total_items}")
        
        elif len(st.session_state.grades) > 0:
            st.success("Результаты сохранены в 'output/comparison_results.csv'")
            
            # Display the results table
            results_df = pd.DataFrame(st.session_state.grades)
            st.write("### Результаты")
            st.dataframe(results_df)

if __name__ == "__main__":
    main() 