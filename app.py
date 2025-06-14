import streamlit as st
import pandas as pd
from pathlib import Path
import random
from streamlit_extras.stylable_container import stylable_container

# Set page config
st.set_page_config(
    page_title="Pairwise Completion Comparison",
    layout="wide"
)

# Initialize session state if not exists
if 'current_comparison_index' not in st.session_state:
    st.session_state.current_comparison_index = 0
    st.session_state.data = None
    st.session_state.grades = []
    st.session_state.total_items = 0
    st.session_state.all_comparisons = []  # List of all comparisons to be made

def reset_state():
    st.session_state.current_comparison_index = 0
    st.session_state.grades = []
    st.session_state.all_comparisons = []

def generate_all_comparisons(df):
    """Generate all comparisons for all publications and randomize their order"""
    all_comparisons = []
    
    for idx, row in df.iterrows():
        # Create both comparison types for this publication
        comparison_types = [
            {
                'type': 'finetuned_vs_baseline',
                'options': ['generated_finetuned', 'generated_baseline'],
                'name': "Сравнение: Дообученная модель vs Базовая модель"
            },
            {
                'type': 'finetuned_vs_continuation', 
                'options': ['generated_finetuned', 'continuation'],
                'name': "Сравнение: Дообученная модель vs Истинное продолжение"
            }
        ]
        
        for comp_type in comparison_types:
            # Randomize option order for this comparison
            options = comp_type['options'].copy()
            if random.randint(0, 1):
                options = options[::-1]  # Reverse order randomly
            
            comparison = {
                'publication_index': idx,
                'comparison_type': comp_type['type'],
                'comparison_name': comp_type['name'],
                'option1_type': options[0],
                'option2_type': options[1],
                'title': row['title'],
                'desc': row['desc'],
                'beginning': row['beginning'],
                'continuation': row['continuation'],
                'generated_baseline': row['generated_baseline'],
                'generated_finetuned': row['generated_finetuned']
            }
            all_comparisons.append(comparison)
    
    # Randomize the order of all comparisons
    random.shuffle(all_comparisons)
    return all_comparisons

def handle_key_press():
    if st.session_state.key_pressed in ["1", "2"]:
        make_comparison(0 if st.session_state.key_pressed == "1" else 1)
        st.session_state.key_pressed = ""  # Reset the input
        st.rerun()

def make_comparison(selected_option):
    if st.session_state.current_comparison_index < len(st.session_state.all_comparisons):
        current_comparison = st.session_state.all_comparisons[st.session_state.current_comparison_index]
        
        # Store the comparison result
        selected_completion_type = (current_comparison['option1_type'] if selected_option == 0 
                                   else current_comparison['option2_type'])
        
        grade_entry = {
            'comparison_order': st.session_state.current_comparison_index + 1,
            'publication_index': current_comparison['publication_index'] + 1,
            'title': current_comparison['title'],
            'desc': current_comparison['desc'],
            'beginning': current_comparison['beginning'],
            'comparison_type': current_comparison['comparison_type'],
            'selected_completion': selected_completion_type,
            'option1_type': current_comparison['option1_type'],
            'option2_type': current_comparison['option2_type'],
            'selected_position': selected_option + 1,
            'continuation': current_comparison['continuation'],
            'generated_baseline': current_comparison['generated_baseline'],
            'generated_finetuned': current_comparison['generated_finetuned']
        }
        
        st.session_state.grades.append(grade_entry)
        
        # Move to next comparison
        st.session_state.current_comparison_index += 1
        
        # If we've completed all comparisons, create and save the output file
        if st.session_state.current_comparison_index >= len(st.session_state.all_comparisons):
            output_df = pd.DataFrame(st.session_state.grades)
            output_path = Path('output/pairwise_comparison_results.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_df.to_csv(output_path, index=False)

def main():
    st.title("Парное сравнение завершений описаний")
    
    # File upload
    uploaded_file = st.file_uploader("Загрузка csv с колонками 'title', 'desc', 'beginning', 'continuation', 'generated_baseline', 'generated_finetuned':", type=['csv'], on_change=reset_state)
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            required_columns = ['title', 'desc', 'beginning', 'continuation', 'generated_baseline', 'generated_finetuned']
            
            # Verify required columns
            if not all(col in df.columns for col in required_columns):
                st.error("CSV должен содержать колонки: 'title', 'desc', 'beginning', 'continuation', 'generated_baseline', 'generated_finetuned'")
                return
                
            # Store data in session state
            if st.session_state.data is None:
                st.session_state.data = df
                st.session_state.total_items = len(df)
                # Generate all comparisons in random order
                st.session_state.all_comparisons = generate_all_comparisons(df)
        
        except Exception as e:
            st.error(f"Ошибка чтения файла: {str(e)}")
            return
        
        # Display current comparison if not all comparisons are completed
        if st.session_state.current_comparison_index < len(st.session_state.all_comparisons):
            current_comparison = st.session_state.all_comparisons[st.session_state.current_comparison_index]
            
            # Display the context
            st.markdown(f"### Название:\n{current_comparison['title']}")
            
            st.markdown("---")
            st.markdown(f"### Начало:\n{current_comparison['beginning']}")
            
            # Create two columns for options
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Продолжение 1:")
                option1_text = current_comparison[current_comparison['option1_type']]
                st.write(option1_text)
            
            with col2:
                st.markdown("#### Продолжение 2:")
                option2_text = current_comparison[current_comparison['option2_type']]
                st.write(option2_text)
            
            # Create two columns for buttons
            btn_col1, btn_col2 = st.columns(2)
            
            # Add buttons with custom styling
            with btn_col1:
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
                    if st.button("Вариант 1 (клавиша 1)", key="first", use_container_width=True):
                        make_comparison(0)
                        st.rerun()
            
            with btn_col2:
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
                    if st.button("Вариант 2 (клавиша 2)", key="second", use_container_width=True):
                        make_comparison(1)
                        st.rerun()
            
            # Add a visible input field for keyboard shortcuts
            st.text_input(
                "1 или 2 + Enter для выбора варианта:",
                key="key_pressed",
                max_chars=1,
                on_change=handle_key_press
            )
            
            # Display progress
            total_comparisons = len(st.session_state.all_comparisons)
            completed_comparisons = st.session_state.current_comparison_index
            
            st.progress(completed_comparisons / total_comparisons)
            st.write(f"Прогресс: {completed_comparisons}/{total_comparisons} сравнений")
            st.write(f"Всего айтемов: {st.session_state.total_items}")
        
        elif len(st.session_state.grades) > 0:
            st.success("Результаты сохранены в 'output/pairwise_comparison_results.csv'")
            
            # Display the results table
            results_df = pd.DataFrame(st.session_state.grades)
            st.write("### Результаты парных сравнений")
            st.dataframe(results_df)
            
            # Show summary statistics
            st.write("### Статистика выбора")
            
            # Overall selection statistics
            comptype_2name = {
                'generated_baseline': 'Базовая',
                'generated_finetuned': 'Дообученная',
                'continuation': 'Истина'
            }
            selection_counts = results_df['selected_completion']\
                .map(lambda x: comptype_2name[x]).value_counts()
            st.write("#### Общая статистика выбора:")
            st.bar_chart(selection_counts)
            
            # Statistics by comparison type
            st.write("#### Статистика по типам сравнений:")
            for comp_type in results_df['comparison_type'].unique():
                comp_data = results_df[results_df['comparison_type'] == comp_type]
                comp_counts = comp_data['selected_completion']\
                    .map(lambda x: comptype_2name[x]).value_counts()
                st.write(f"**{comp_type}:**")
                st.bar_chart(comp_counts)

if __name__ == "__main__":
    main() 