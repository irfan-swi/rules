import pandas as pd
import plotly.graph_objects as go


#mapping 
reverse_party_mapping = {'Republican': 'r', 'Democrat': 'd'}
party_mapping = {'r': 'Republican', 'd': 'Democrat'}

#function to get congress details for tab2
def display_congress_details(congress_details):
    if not congress_details.empty:
        details = congress_details.iloc[0]  # Assuming there is always at least one row
        details_df = pd.DataFrame(details).reset_index()
        details_df.columns = ['Attribute', 'Value']
        details_df['Value'] = details_df['Value'].apply(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)
        return details_df
    else:
        return pd.DataFrame()

#function to apply filters to tab0
def apply_filters(data, congress_selection, rule_selection, title_selection, party_control_selection, speaker_selection, search_query,filter_changed_text,filter_new_rule, filter_new_title):
    query_conditions = []
    if congress_selection != 'All':
        query_conditions.append(f"Congress == {int(congress_selection)}")
    if rule_selection != 'all':
        query_conditions.append(f"Rule == '{rule_selection}'")
    if title_selection != 'all':
        query_conditions.append(f"Title == '{title_selection}'")
    if party_control_selection != 'All':
        short_form_party = reverse_party_mapping[party_control_selection]
        query_conditions.append(f"Party == '{short_form_party}'")
    if speaker_selection != 'all':
        query_conditions.append(f"Speaker == '{speaker_selection}'")
    
    if query_conditions:
        combined_query = " & ".join(query_conditions)
        data = data.query(combined_query)
    
    if search_query:
        #data = data[data['Title'].str.contains(search_query, case=False, na=False)]
        data = data[
        data['Title'].str.contains(search_query, case=False, na=False) |
        data['Rule'].str.contains(search_query, case=False, na=False) |
        data['Text'].str.contains(search_query, case=False, na=False)
    ]
    if filter_changed_text:
        data = data[data['changed_text']]
    
    if filter_new_rule:
        data = data[data['new_rule']]
    
    if filter_new_title:
        data = data[data['new_title']]

    return data

# #function to create Margin plots in tab0
# def create_plot(df):
#     fig = go.Figure()

#     # Iterate through the DataFrame to create segments
#     last_index = len(df) - 1
#     for i in range(last_index):
#         # Determine the segment color based on the sign of the current and next margin
#         if df['RMargin'][i] >= 0 and df['RMargin'][i + 1] >= 0:
#             color = 'red'  # Entire segment is positive
#         elif df['RMargin'][i] < 0 and df['RMargin'][i + 1] < 0:
#             color = 'blue'  # Entire segment is negative
#         else:
#             # Segment crosses y=0, calculate the exact intersection using linear interpolation
#             x_vals = [df['Congress'][i], df['Congress'][i + 1]]
#             y_vals = [df['RMargin'][i], df['RMargin'][i + 1]]
#             zero_crossing_x = x_vals[0] + (0 - y_vals[0]) * (x_vals[1] - x_vals[0]) / (y_vals[1] - y_vals[0])
#             zero_crossing_y = 0

#             # Plot up to the zero crossing point
#             fig.add_trace(go.Scatter(x=[x_vals[0], zero_crossing_x], y=[y_vals[0], zero_crossing_y],
#                                      mode='lines', line=dict(color='red' if y_vals[0] >= 0 else 'blue', width=2),
#                                      showlegend=False))

#             # Plot after the zero crossing point
#             fig.add_trace(go.Scatter(x=[zero_crossing_x, x_vals[1]], y=[zero_crossing_y, y_vals[1]],
#                                      mode='lines', line=dict(color='red' if y_vals[1] >= 0 else 'blue', width=2),
#                                      showlegend=False))
#             continue

#         # Add the segment to the plot
#         fig.add_trace(go.Scatter(x=[df['Congress'][i], df['Congress'][i + 1]],
#                                  y=[df['RMargin'][i], df['RMargin'][i + 1]],
#                                  mode='lines', line=dict(color=color, width=2),
#                                  showlegend=False))

#     # Highlight where changed is True
#     changed_df = df[df['Changed'] == True]
#     if not changed_df.empty:
#         fig.add_scatter(x=changed_df['Congress'], y=[0] * len(changed_df),
#                         mode='markers', marker=dict(color='brown', size=10), name='changed')

#     # Add a horizontal line at y=0
#     fig.add_shape(type="line", x0=min(df['Congress']), y0=0, x1=max(df['Congress']), y1=0,
#                   line=dict(color="black", width=2, dash='dash'))

#     # Update layout
#     fig.update_layout(
#         title="Congressional Margins with Changes to the text",
#         xaxis_title="Congress",
#         yaxis_title="Margin",
#         legend_title="Legend"
#     ) 
#     # Set the x-axis to show all Congress numbers
#     fig.update_xaxes(tickmode='array', tickvals=df['Congress'].unique())
    # return fig1, fig2, fig3, fig4

#text comaprison and rule/title computation for tab3
def compare_texts(current_data, previous_data):
    current_data = current_data[['Congress','Rule', 'Title','Text']]
    previous_data = previous_data[['Congress','Rule', 'Title','Text']]
    # Merge on 'Rule' and 'Title'
    merged_data = pd.merge(current_data, previous_data, on=['Rule', 'Title'], how='outer', suffixes=('_curr', '_prev'))

    # compute identical text, rule/title added and deleted
    merged_data['Identical_Text'] = merged_data.apply(lambda x: x['Text_curr'] == x['Text_prev'], axis=1)
    merged_data['Rule_Title_Added'] = merged_data['Text_prev'].isnull()
    merged_data['Rule_Title_Deleted'] = merged_data['Text_curr'].isnull()

    return merged_data

#tab1 details getter
def get_congress_details(df):
    details = df.iloc[0]
    details_df = pd.DataFrame(details)
    details_df.reset_index(inplace=True)
    details_df.columns = ['Attribute', 'Value']
    details_df['Value'] = details_df['Value'].apply(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)

    return details_df

def create_plot(Marging_df):

    def get_initials_with_prefix(row):
        name = row['Speaker']
        congress = row['Congress']
        initials = ''.join([word[0] for word in name.split()])
        return initials

# Apply function to create new column 'Initials'
    Marging_df['Initials'] = Marging_df.apply(get_initials_with_prefix, axis=1)
    floor = Marging_df
    Marging_df = Marging_df[['Margin','MajorityParty','Congress','Initials','Speaker','Changed']]
    Marging_df['AdjustedMargin'] = Marging_df.apply(lambda row: row['Margin'] if row['MajorityParty'] == 'R' else -row['Margin'], axis=1)
    Marging_df['Color'] = Marging_df['MajorityParty'].apply(lambda party: 'red' if party == 'R' else 'blue')
    Marging_df['HoverText'] = Marging_df.apply(lambda row: f"{row['Initials']}<br>{row['Margin']}", axis=1)

    # Define y-axis tick values and labels
    tickvals = [-100,-50,0,50]
    ticktext = [100,50,0,50]

# Create bar chart with margin
    fig1 = go.Figure()

    fig1.add_trace(go.Bar(
        x=Marging_df['Congress'],
        y=Marging_df['AdjustedMargin'],
        marker_color=Marging_df['Color'],
        text=Marging_df['HoverText'],
        hoverinfo='text', showlegend = False,opacity = 0.7,
        width = 0.8
))

    # fig1.add_shape(type="line", x0=min(Marging_df['Congress']), y0=0, x1=max(Marging_df['Congress']), y1=0,
    #               line=dict(color="black", width=2, dash='dash'))
    
    changed_df = Marging_df[Marging_df['Changed'] == True]
    if not changed_df.empty:
        fig1.add_scatter(x=changed_df['Congress'], y=[0] * len(changed_df),mode='markers', marker=dict(color='brown', size=15), name='changed text (GPT)')

# Update layout
    fig1.update_layout(
     title='House Majority Party and Margin (with Speaker Initials)',
     xaxis_title='Congress',
        yaxis_title='Margin',
        yaxis=dict( tickmode = 'array',tickvals = tickvals, ticktext = ticktext),
        plot_bgcolor='white',
        xaxis=dict(tickmode='array',tickvals=Marging_df['Congress']))
    
    #create stacked bar chart for speaker discretion
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Reported_novote'],
    name='No Floor Consideration',
    marker_color='Red',
    text=floor['Reported_novote'],
    textposition='auto',opacity = 0.7,
    width = 0.8
))

    fig2.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['BroughttoFloor'],
    name='Received Floor Consideration',
    marker_color='Green',
    text=floor['BroughttoFloor'],
    textposition='auto',opacity = 0.7,
    width = 0.8
))

# Create density plot for PercentageVotedOn
    fig2.add_trace(go.Scatter(
    x=floor['Congress'],
    y=floor['PercentageVotedOn'],
    mode='lines+markers',
    name='Percentage Voted On',
    line=dict(color='black'),
    text=[f"{val}%" for val in floor['PercentageVotedOn']],
    textposition='middle center',
    yaxis='y2'
))
    changed_df = floor[floor['Changed'] == True]
    if not changed_df.empty:
        fig2.add_scatter(x=changed_df['Congress'], y=[0] * len(changed_df),mode='markers', marker=dict(color='brown', size=15), name='changed text (GPT)')  

# Update layout
    fig2.update_layout(
    title='Speaker Discretion<br><sup>Of all bills reported out of committee, how many were brought to the floor? </sup>',
    xaxis_title='Congress',
    yaxis_title='Number of Bills',
    barmode='stack',
    yaxis2=dict(
        title='Voted On (%)',
        overlaying='y',
        side='right'
    ),
    plot_bgcolor='white',
    xaxis=dict(tickmode='array',tickvals=Marging_df['Congress'])
)
    #committee efficiency
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['NotReported'],
    name='Not Reported Out',
    marker_color='Red',
    text=floor['NotReported'],
    textposition='auto', opacity = 0.7,
    width = 0.8
))

    fig3.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['ReportedOut'],
    name='Reported Out',
    marker_color='Green',
    text=floor['ReportedOut'],
    textposition='auto', opacity = 0.7,
    width = 0.8
))

    

# Create density plot for PercentageVotedOn
    fig3.add_trace(go.Scatter(
    x=floor['Congress'],
    y=floor['Reported%'],
    mode='lines+markers',
    name='Percentage Reported Out',
    line=dict(color='black'),
    text=[f"{val}%" for val in floor['Reported%']],
    textposition='middle center',
    yaxis='y2'
))
    if not changed_df.empty:
        fig3.add_scatter(x=changed_df['Congress'], y=[0] * len(changed_df),mode='markers', marker=dict(color='brown', size=15), name='changed text (GPT)')  

# Update layout
    fig3.update_layout(
    title='Committee Efficiency<br><sup>Of all bills introduced by the House, how many were reported out of committee? </sup>',
    xaxis_title='Congress',
    yaxis_title='Number of Bills',
    barmode='stack',
    yaxis2=dict(
        title='Reported Out (%)',
        overlaying='y',
        side='right'
    ),
    plot_bgcolor='white',
    xaxis=dict(tickmode='array',tickvals=Marging_df['Congress']),
    legend=dict(
        font=dict(size=10),  # Adjust font size to make the legend smaller
        x=1.1,  # Shift the legend to the right
        y=1
    )
)
    
    fig4 = go.Figure()

    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Vetoed'],
    name='Vetoed',
    marker_color='Red',opacity = 1,
    #text=floor['Vetoed'],
    #textposition='auto',
    width = 0.7
))

    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['FailedFloor'],
    name='Failed Floor',
    marker_color='Red',opacity = 0.8,
    #text=floor['FailedFloor'],
    #textposition='auto',
    width = 0.7
))

    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['FailedCloture'],
    name='Failed Cloture',
    marker_color='Red',opacity = 0.6,
    #text=floor['FailedCloture'],
    #textposition='auto',
    width = 0.7
))

    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['FailedUnderSuspension'],
    name='Failed Under Suspension',
    marker_color='Red', opacity = 0.5,
    #text=floor['FailedUnderSuspension'],
    #textposition='auto',
    width = 0.7
))
    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Enacted'],
    name='Enacted',
    marker_color='Green',opacity = 0.5,
    #text=floor['Enacted'],
    #textposition='auto',
    width = 0.7
))
    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Agreed To (Concurrent)'],
    name='Agreed To (Concurrent)',
    marker_color='Green',opacity = 0.6,
    #text=floor['Agreed To (Concurrent)'],
    #textposition='auto',
    width = 0.7
))
    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Agreed To (Simple)'],
    name='Agreed To (Simple)',
    marker_color='Green',opacity = 0.8,
    #text=floor['Agreed To (Simple)'],
    #textposition='auto',
    width = 0.7
))
    fig4.add_trace(go.Bar(
    x=floor['Congress'],
    y=floor['Passed'],
    name='Passed House but did not become law',
    marker_color='Green', opacity = 1,
    #text=floor['Passed'],
    #textposition='auto',
    width = 0.7
))

# Create density plot for PercentageVotedOn
    fig4.add_trace(go.Scatter(
    x=floor['Congress'],
    y=floor['Reported%'],
    mode='lines+markers',
    name='Percentage Enacted',
    line=dict(color='black'),
    text=[f"{val}%" for val in floor['Enacted%']],
    textposition='middle center',
    yaxis='y2'
))
    if not changed_df.empty:
        # for congress in changed_df['Congress']:
            # fig4.add_shape(type='line',
            #            x0=congress, y0=0,
            #            x1=congress, y1=2000,
            #            line=dict(color='white', width=2),
            #            name='changed')
        fig4.add_scatter(x=changed_df['Congress'], y=[0] * len(changed_df),mode='markers', marker=dict(color='brown', size=15), name='changed text (GPT)')

# Update layout
    fig4.update_layout(
    title='Legislative Success<br><sup>Outcome of bills that were brought to the House floor </sup>',
    xaxis_title='Congress',
    yaxis_title='Number of Bills',
    barmode='stack',
    yaxis2=dict(
        title='Enacted (%)',
        overlaying='y',
        side='right'
    ),
    plot_bgcolor='white',
    xaxis=dict(tickmode='array',tickvals=Marging_df['Congress']),
    legend=dict(
        font=dict(size=10),  # Adjust font size to make the legend smaller
        x=1.1,  # Shift the legend to the right
        y=1
    )
)
    return fig1,fig2,fig3,fig4