import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import norm

# Load and prepare data
df_all = pd.read_csv('malkinhere.csv')
df = df_all.drop('Week', axis=1)
means = df.mean()[1:]
stds = df.std()[1:]

st.title('Odds Nico Loses')

st.markdown(f"<span style='font-size: 100px; display: flex; justify-content: center; color: black;'>38.17%</span>", unsafe_allow_html=True)

if st.checkbox("Explain"):
        
    st.title("Explanation")

    st.write("Nico gets a bye in the first round, but then has to win rounds 2 and 3 to win the ploffs. The odds he doesn't win are given by:")

    st.latex(r''' \small P(\text{Loses semifinals}) + P(\text{Loses finals}) \qquad \qquad (1)''')

    st.write("The first step in finding these is finding the odds a given team beats another.")

    st.subheader("Step 1: Find the odds that team A wins against team B", divider=True)

    st.write('To find the probability that a given team, A, wins against another team, B, we can use these point distributions:')


    box, strip = st.tabs(['Box Plot', 'Strip Plot'])
    with box:
        fig = px.box(df, title='Point Distribution by Player')
        st.plotly_chart(fig, use_container_width=True)
    with strip:
        fig2 = px.strip(df_all, orientation='v', title='Point Distribution by Player', labels={'value': 'Points', 'variable': 'Player'}, hover_data={'Week': True})
        st.plotly_chart(fig2, use_container_width=True)

    st.write('''If we assume each player's point distribution comes from an underlying normal 
    distribution (which is probably true because of the CLT), then the difference of two players' distributions is also normal.''')

    st.write('For example, player A with mean 300 and variance 40, player B with mean 250 and variance 45, then A - B is normal with mean 50 and variance 85.')

    st.write('Then, we just need to find the probability that A - B is greater than 0, which is given by (1 minus) the CDF of the normal distribution:')

    st.latex(r''' \small P(A \text{ beats } B) =  P(A - B > 0) =  1 - \Phi\left(0\right).''')

    st.write("This is implemented here:")

    def probAbeatsB(A, B):
        mean_diff = means[A] - means[B]
        std_diff = np.sqrt(stds[A]**2 + stds[B]**2)
        prob = 1 - norm(mean_diff, std_diff).cdf(0)
        return prob

    name1, name2, prob = st.columns([1, 1, 2])
    with name1:
        A = st.selectbox('Player A', df.columns[1:], index=0)
    with name2:
        B = st.selectbox('Player B', df.columns[1:], index=1)
    with prob:
        st.markdown("<div style='width: 1px; height: 35px'></div>", unsafe_allow_html=True)
        st.write(f'P({A} beats {B}) = {np.round(probAbeatsB(A, B)*100,2)}%')

    st.subheader("Step 2: Find the odds that Nico loses in semifinals", divider=True)

    st.write('The odds Nico loses semifinals are given by:') 

    st.latex(r''' \small P(\text{Loses semifinals}) = \sum_{i} P(\text{Nico plays Player } i) \times P(\text{Player } i \text{ beats Nico}). \quad (2)''')

    st.write("To find the odds Nico plays a given player in semifinals, let's assume (for all that is holy) that the standings remain as they are. Then, the odds that Nico plays, say, Sam, are given by:")

    st.latex(r''' \small P(\text{Nico plays Sam}) = P(\text{Sam makes semifinals}) \times P(\text{Bryce makes semifinals}),''')

    st.write('as reseeding permits only this scenario leading to Nico playing Sam in the semifinals. The odds for any player making the semifinals can easily be calculated using the probability that team A beats team B. They are shown here:')
            
    seeding = df.sum()
    seeding = pd.DataFrame(seeding, columns=["Points"]).sort_values("Points", ascending=False)
    seeding["Seed"] = [1,2,3,5,4,7,8,6,10,9]
    dfseed = seeding.sort_values("Seed")

    def odds2ndround(A):
        if dfseed.loc[A, "Seed"] in (1,2):
            return 1
        if dfseed.loc[A, "Seed"] == 3:
            opp = dfseed.index[dfseed['Seed'] == 6][0]
            return probAbeatsB(A, opp)
        if dfseed.loc[A, "Seed"] == 4:
            opp = dfseed.index[dfseed['Seed'] == 5][0]
            return probAbeatsB(A, opp)
        if dfseed.loc[A, "Seed"] == 5:
            opp = dfseed.index[dfseed['Seed'] == 4][0]
            return probAbeatsB(A, opp)
        if dfseed.loc[A, "Seed"] == 6:
            opp = dfseed.index[dfseed['Seed'] == 3][0]
            return probAbeatsB(A, opp)
        else:
            return 0
        
    name, prob2 = st.columns([1, 2])
    with name:
        C = st.selectbox('Player', dfseed.index[:6], index=0)
    with prob2:
        st.markdown("<div style='width: 1px; height: 35px'></div>", unsafe_allow_html=True)
        st.write(f'P({C} makes semifinals) = {np.round(odds2ndround(C)*100,2)}%')

    st.write('Putting this all into Eq. (2), we get')
        
    def oddsAplaysBin2nd(A,B):
        odds = 1
        if dfseed.loc[A, "Seed"] == 1:
            if dfseed.loc[B, "Seed"] in (1,2,3):
                return 0
            if dfseed.loc[B, "Seed"] == 4:
                for i in range(1,5):
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 5:
                for i in [1,2,3,5]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 6:
                for i in [1,2,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        if dfseed.loc[A, "Seed"] == 2:
            if dfseed.loc[B, "Seed"] in (1,2,6):
                return 0
            if dfseed.loc[B, "Seed"] == 3:
                for i in [1,2,3]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 4:
                for i in [1,2,4,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 5:
                for i in [1,2,5,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        if dfseed.loc[A, "Seed"] == 3:
            if dfseed.loc[B, "Seed"] in (1,3,4,5,6):
                return 0
            if dfseed.loc[B, "Seed"] == 2:
                for i in [1,2,3]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        if dfseed.loc[A, "Seed"] == 4:
            if dfseed.loc[B, "Seed"] in (3,4,5,6):
                return 0
            if dfseed.loc[B, "Seed"] == 1:
                for i in [1,2,3,4]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 2:
                for i in [1,2,4,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        if dfseed.loc[A, "Seed"] == 5:
            if dfseed.loc[B, "Seed"] in (3,4,5,6):
                return 0
            if dfseed.loc[B, "Seed"] == 1:
                for i in [1,2,5,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            if dfseed.loc[B, "Seed"] == 2:
                for i in [1,2,3,5]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        if dfseed.loc[A, "Seed"] == 6:
            if dfseed.loc[B, "Seed"] in (2,3,4,5,6):
                return 0
            if dfseed.loc[B, "Seed"] == 1:
                for i in [1,2,6]:
                    odds *= odds2ndround(dfseed.index[i - 1])
                return odds
            else:
                return 0
        else:
            return 0


    odds = 0
    for player in dfseed.index[1:6]:
        podds = oddsAplaysBin2nd("Nico", player) * probAbeatsB(player, "Nico")
        odds += podds
            
    st.latex(r''' \small P(\text{Loses semifinals}) =''' + f'{np.round(odds*100,2)} \%')

    st.subheader("Step 3: Find the odds that Nico loses in finals", divider=True)

    st.write("This is a much more intensive calculation, but it's quite easy to implement with the functions we have made so far. We can use the odds of someone making it to the semifinals to calculate the odds of two players meeting in the semifinals. Based on seeding, we get:")

    name11, name22, prob3 = st.columns([1, 1, 2])
    with name11:
        D = st.selectbox('Player 1', dfseed.index[:6], index=2)
    with name22:
        E = st.selectbox('Player 2', dfseed.index[:6], index=5)
    with prob3:
        st.markdown("<div style='width: 1px; height: 35px'></div>", unsafe_allow_html=True)
        st.write(f'P({D} plays {E} in semifinals) = {np.round(oddsAplaysBin2nd(D, E)*100,2)}%')

    st.write("And this is used to iterate over all possible matchups in the semifinals to find the odds of someone making it to the finals:")

    def odds3rdround(A):
        win2nd = 0
        for player in dfseed.index[1:6]:
            win2nd_player = oddsAplaysBin2nd(A, player)*probAbeatsB(A, player)
            win2nd += win2nd_player         
        return win2nd

    namefinal, prob4 = st.columns([1, 2])
    with namefinal:
        F = st.selectbox('Choose Player', dfseed.index[:6], index=2)
    with prob4:
        st.markdown("<div style='width: 1px; height: 35px'></div>", unsafe_allow_html=True)
        st.write(f'P({F} makes finals) = {np.round(odds3rdround(F)*100,2)}%')

    st.write("Finally, we can use this to find the odds Nico loses in the finals:")

    st.latex(r''' \small P(\text{Loses finals}) = P(\text{Nico makes finals}) \times \sum_{i}  P(\text{Player } i \text{ makes finals}) \times P(\text{Player } i \text{ beats Nico}).''')

    odds2 = 0
    for player in dfseed.index[1:6]:
        podds2 = odds3rdround(player) * odds3rdround("Nico") * probAbeatsB(player, "Nico")
        odds2 += podds

    st.write("This gives us:")
            
    st.latex(r''' \small P(\text{Loses finals}) = ''' + f'{np.round(odds2*100,2)} \%')

    st.subheader("Step 4: Slap it all together", divider=True)

    st.write("And finally, we can use Eq. (1) to find the odds Nico loses the ploffs:")

    st.latex(r''' \small P(\text{Nico loses}) = ''' + f'{np.round(odds*100,2)} \% + {np.round(odds2*100,2)} \% = {np.round(odds*100 + odds2*100,2)} \%')