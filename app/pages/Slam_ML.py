# SlamApp - Streamlit app for SlamModel outputs
import pandas as pd, streamlit as st
from utils.preprocessor import data_processor, create_merged_data
from utils.images import get_header

#############################################
################ APP Set-Up #################
#############################################

def GrandSlam():

    # Wide Mode 
    def auto_wide_mode():
        st.set_page_config(layout="wide")

    auto_wide_mode()

    # Dataset
    @st.cache(show_spinner=False)
    def update_data():
        return data_processor()

    data = update_data()
 
    #############################################
    ################ App Sidebar ################
    #############################################

    st.sidebar.header('🎮 App Filters 🎮')

    # players
    players = pd.concat([data['Player 1'], data['Player 2'] ], axis = 0).sort_values().unique()
    selected_player = st.sidebar.multiselect(label='Select Players', options=players)

    # slams
    slams = data['Grand Slam'].unique()
    selected_slam = st.sidebar.multiselect(label='Select Slams', options=slams)

    # years
    years = data['Year'].unique()
    selected_year = st.sidebar.multiselect(label='Select Years', options=years)

    # round
    rounds = data['Round'].unique()
    selected_round = st.sidebar.multiselect(label='Select Round', options=rounds)

    #######################
    #### Apply Filters ####
    #######################

    # players
    if len(selected_player) != 0:
        data = data[(data['Player 1'].isin(selected_player)) | (data['Player 2'].isin(selected_player))]

    # slams
    if len(selected_slam) > 0:
        data = data[data['Grand Slam'].isin(selected_slam)]

    # years
    if len(selected_year) > 0:
        data = data[data['Year'].isin(selected_year)]
    else:
        data = data.drop(columns=['Year'])

    # rounds
    if len(selected_round) > 0:
        data = data[data['Round'].isin(selected_round)]


    ############################################
    ################ APP Build #################
    ############################################
    st.header('Grand Slam Predictions')

    st.markdown ('''
        This app is used for sharing the output from my SlamModel project I run throughout the year.
        ''')

    # Header Image & Source
    st.image(get_header())
    st.markdown('Image: [Josh Calabrese](https://images.unsplash.com/photo-1482614312710-79c1d29bda2a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80)')


    # Model Accuracy Chart
    st.subheader('Model Performance...')
    accuracy_round = data.groupby(by=['Round']).mean()['Predicted']*100
    accuracy_overall = round(accuracy_round.sum() / 7, 1)

    st.markdown(f'### Mean model accuracy: {accuracy_overall} %')
    st.bar_chart(accuracy_round)

    # Player Results
    st.subheader('Player Results...')
    data_merge = create_merged_data(dataset=data)
    df_players = pd.DataFrame(index = data_merge.mean().index)

    df_players['Matches Played'] = df_players.index.map(data_merge.count()['Predicted'].to_dict())
    df_players['Predicted'] = df_players.index.map(data_merge.sum()['Predicted'].to_dict()).astype(int)

    df_players['% Accuracy'] = 100 * df_players['Predicted'] / df_players['Matches Played']
    df_players['% Accuracy'] = [int(i) for i in df_players['% Accuracy']]

    df_players['Mean Model Win %'] = df_players.index.map(data_merge.mean()['P1 Win %'].to_dict()).astype(int)
    df_players['Mean Model Lose %'] = df_players.index.map(data_merge.mean()['P2 Win %'].to_dict()).astype(int)

    df_players['Last Round Played'] = df_players.index.map(data_merge.max()['Round'].to_dict())

    # filter 
    if len(selected_player) > 0:
        df_players = df_players[df_players.index.isin(selected_player)]

    st.dataframe(df_players.sort_values(by = ['Predicted', '% Accuracy'], ascending=False))

    # Filtered Data
    st.subheader('Filtered Results...')
    st.dataframe(data)

if __name__ == '__main__':
    GrandSlam()
