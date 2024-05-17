from utils import *
import streamlit as st
import pandas as pd
from openai import OpenAI
import plotly.express as px
import plotly.graph_objects as go
import base64

# page layout and image
st.set_page_config(layout="wide") 
# st.sidebar.image('SWi.png', use_column_width=True)

#css
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Get the base64 string of the image
logo_base64 = get_base64_image("SWi.png")

# Custom CSS to place the logo in the top left corner
st.markdown(f"""
    <style>
    .top-left-logo {{
        position: absolute;
        top: -30px;
        left: 400px;
        width: 300px;        
    }}
    </style>
    <img src="data:image/png;base64,{logo_base64}" class="top-left-logo">
    """, unsafe_allow_html=True)


#st.image("SWi.png", use_column_width= 'auto', output_format="PNG")
#st.markdown('<img src="SWi.png" class="top-left-logo">', unsafe_allow_html=True)

# initialize the session state for the summary DataFrame if it doesn't already exist (I don't use this anywhere but good to have it incase we add features in the future)
if 'summary_df' not in st.session_state:
    st.session_state.summary_df = pd.DataFrame(columns=['Old Congress', 'New Congress', 'Summary of Changes'])

# Load your CSV data
@st.cache_data
def load_data():
    #data cleanup
    data = pd.read_csv("output_comparison.csv")
    data['new_rule'] = data['new_rule'].astype(bool)
    data['new_title'] = data['new_title'].astype(bool)
    data['changed_text'] = data['changed_text'].astype(bool)
    data['Text'] = data.Text.str.lower()
    data['prior_text'] = data.Text.str.lower()

    congress = pd.read_csv('congress_test.csv')
    floor = pd.read_csv('floor.csv')
    return data,congress, floor

try:
    data, congress_data,floor_data = load_data()
    #data, congress_data = load_data()
except FileNotFoundError:
    st.error('Data file not found. Please check the file path and file name.')

def visualize_and_summarize_changes(rule, title):
    relevant_data = data[(data['Rule'] == rule) & (data['Title'] == title)].sort_values('Congress')
    congresses = []
    word_counts = []
    
    # # Gather data for plotting
    # for i in range(len(relevant_data)):
    #     text = relevant_data.iloc[i]['Text']
    #     congress = relevant_data.iloc[i]['Congress']
    #     word_count = len(text.split())
        
    #     congresses.append(congress)
    #     word_counts.append(word_count)

    
    rows_list = [] 
    change_list = []
    # Generate summaries using GPT
    for i in range(len(relevant_data) - 1):
        old_text = relevant_data.iloc[i]['Text']
        new_text = relevant_data.iloc[i + 1]['Text']

        congress_1 = relevant_data.iloc[i]['Congress']
        congress_2 = relevant_data.iloc[i + 1]['Congress']

        client = OpenAI(api_key='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')
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            max_tokens=4000,
            messages=[
                {"role": "system", "content": f"Explain the differences between the two following sets of rules for {title} from the {congress_1} to the {congress_2} Congress. Do not note changes in formatting. List the changes succinctly. Only output the word unchanged and nothing else if there are no changes."},
                {"role": "system", "content": old_text},
                {"role": "system", "content": new_text},
            ]
        )
        summary = response.choices[0].message.content.strip()

        # Determine if there was a change
        has_changed = summary.lower() != "unchanged"

        # Construct row data
        row_data = {
            'Congress' : congress_2,
            'Changed': has_changed
        }
        rows_list.append(row_data)

        # only show rows that have changes.
        if summary.lower() != "unchanged":
            new_row = pd.DataFrame({
            'Previous Congress': [congress_1],
            'This Congress': [congress_2],
            'Summary of Changes': [summary],
            'Previous Congress Text':[old_text],
            'This Congress text':[new_text]
            }   )

            change_list.append(new_row)  
        #new_row = pd.DataFrame({'Old Congress': [congress_1], 'New Congress': [congress_2], 'Summary of Changes': [summary]})
            st.session_state.summary_df = pd.concat([st.session_state.summary_df, new_row], ignore_index=True)

    if change_list:
        change_df = pd.concat(change_list, ignore_index=True)
    else:
        change_df = pd.DataFrame()
    
    st.dataframe(change_df)
    
    summary_df = pd.DataFrame(rows_list)
    # margin = pd.read_csv('margin.csv')
    try:
        merged_df = summary_df.merge(floor_data, on = 'Congress', how = 'right')
    
    # fig1,fig2,fig3,fig4 = create_plot(merged_df)
        fig1, fig2, fig3, fig4 = create_plot(merged_df)
        st.plotly_chart(fig1,use_container_width=True)
        st.plotly_chart(fig2,use_container_width=True)
        st.plotly_chart(fig3,use_container_width=True)
        st.plotly_chart(fig4,use_container_width=True)
    except KeyError:
        st.warning('Not enough congresses')
    # Plot the word counts as a line chart
    
    # if congresses:
    #     fig1 = px.line(x=congresses, y=word_counts, markers=True, title="Word Count Across Congresses")
    #     fig1.update_traces(line=dict(width=2, color='blue'), marker=dict(size=10, color='red'))
    #     fig1.update_layout(
    #     xaxis_title="Congress",
    #     yaxis_title="Word Count",
    #     xaxis=dict(tickmode='linear', dtick=1),  # Setting tick mode for x-axis
    #     plot_bgcolor='white'  # Set background color to white for better visibility
    #         )
    #     st.plotly_chart(fig1, use_container_width=True)
    
# Tabs
tabs = st.tabs(["Rule Comparison"])


# Rule Comparison Tab
with tabs[0]:
    # reset functionality.
    def reset():
       st.session_state.congress = 'All'
       st.session_state.title = 'All'
       st.session_state.rule = 'All'
       st.session_state.party = 'All'
       st.session_state.speaker = 'All'
       st.session_state.search = ''

    col1, col2, col3, col4, col5, col6, col_reset = st.columns(7)
    with col1:
        congress_selection = st.selectbox("Congress Selection", ['All'] + sorted(data['Congress'].unique().tolist(), reverse=True),key = 'congress')
    with col2:
        rule_selection = st.selectbox("Rule Selection", ['All'] + sorted(data['Rule'].unique().tolist()),key = 'rule')
        filter_new_rule = st.checkbox("New Rule", value=False)
    with col3:
        title_options = ['All'] + sorted(data[data['Rule'] == rule_selection]['Title'].unique().tolist()) if rule_selection != 'All' else ['All'] + sorted(data['Title'].unique().tolist())
        title_selection = st.selectbox("Rule Title", title_options, key='title', index=0)
        filter_new_title = st.checkbox("New Title Only", value=False)
        #title_selection = st.selectbox("Select Title", ['All'] + sorted(data[data['Rule'] == rule_selection]['Title'].unique()) if rule_selection != 'All' else sorted(data['Title'].unique().tolist()))
    with col4:
        
        party_control_selection = st.selectbox('Majority party', ['All'] + ['Republican', 'Democrat'],key = 'party')
    with col5:
        speaker_selection = st.selectbox('Speaker', ['All'] + sorted(data['Speaker'].unique().tolist()), key = 'speaker')
    with col6:
        search_query = st.text_input("Search", key = 'search')
        filter_changed_text = st.checkbox("Changed Text", value=False)
    with col_reset:
        st.write('')
        st.write('')
        st.button("Reset", on_click = reset)
            

    # Apply filtering and button for summaries in Rule Comparison
    filtered_data = apply_filters(data, congress_selection, rule_selection, title_selection, party_control_selection, speaker_selection, search_query,filter_changed_text,filter_new_rule, filter_new_title)

    #now transform the filtered data to look more presentable
    filtered_data['Party'] = filtered_data['Party'].replace({'R': 'Republican', 'D': 'Democrat'})
    filtered_data['Start.Year'] = filtered_data['Start.Year'].astype(str).str.replace(',','')
    filtered_data['End.Year'] = filtered_data['End.Year'].astype(str).str.replace(',','')

    #display the data
    #st.dataframe(filtered_data.merge(congress_data,on = 'Congress',how = 'left').drop(columns = ['Margin_y','Start Year_y','End Year_y','Speaker_y']),hide_index = True)
    final_data = filtered_data.merge(congress_data,on = 'Congress',how = 'left')
    final_data.rename(columns = {'prior_congress':'Prior Congress',
                       'prior_rule':'Prior Rule',
                       'prior_title':'Prior Title',
                       'prior_text':'Prior Text',
                       'new_rule':'New Rule Added',
                       'new_title':'New Title Added',
                       'changed_text':'Changed Text',
                       'Margin_x':'Margin',
                       'Speaker_x':'speaker'}, inplace = True)
    final_data.drop(columns = ['Start Year','End Year','Majority Party','Margin_y','Speaker_y'],inplace = True)
    st.dataframe(data)
    st.write(f'(Observation Count: {final_data.shape[0]})')

    # if visualize... button is pressed
    if st.button('Visualize and Summarize Changes'):
        if rule_selection != 'All' and title_selection != 'All':
            with st.spinner('Loading'):
                visualize_and_summarize_changes(rule_selection, title_selection)
            st.success('Completed')    
        else:
            st.warning("Please select specific Rule and Title to visualize and summarize changes.")