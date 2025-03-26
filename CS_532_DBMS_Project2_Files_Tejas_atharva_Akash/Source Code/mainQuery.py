from flask import Flask, render_template, redirect, url_for     #This import is used for UI development only
import pymongo      #This import is used for Python and MongoDB connectivity to write Queries
import matplotlib.pyplot as plt     #This import is used for UI development only
import mpld3    #This import is used for UI development only
import plotly.graph_objects as go   #This import is used for UI development only

# Initialize Flask App
app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["IPL"]


def task4_analysis():
   
    collection = db["all_season_summary"]

    # Our group has written this NoSQL Query to data analysis on an unstructured data
    
    analysis_query = [
        {"$match": {"match_details_text": {"$exists": True}}},
        {"$project": {
            "_id": 0,
            "total_matches": {"$literal": 1},
            "advantageous_wins": {
                "$cond": {
                    "if": {"$eq": ["$match_details_text.toss_won", "$match_details_text.winner"]},
                    "then": {"$literal": 1},
                    "else": {"$literal": 0}
                }
            }
        }},
        {"$group": {
            "_id": None,
            "total_matches": {"$sum": "$total_matches"},
            "advantageous_wins": {"$sum": "$advantageous_wins"}
        }},
        {"$project": {
            "_id": 0,
            "total_matches": "$total_matches",
            "advantageous_wins": "$advantageous_wins",
            "percentage_advantageous_wins": {
                "$multiply": [
                    {"$divide": ["$advantageous_wins", "$total_matches"]},
                    100
                ]
            }
        }}
    ]

    #We are doing this for Executing query
    result = list(collection.aggregate(analysis_query))

    #We are doing this for Extracting results
    total_matches = result[0]["total_matches"] if result else 0
    advantageous_wins = result[0]["advantageous_wins"] if result else 0
    percentage_advantageous_wins = result[0]["percentage_advantageous_wins"] if result else 0

    #We are doing this to Create a pie chart
    labels = ['Advantageous Wins', 'Toss loser Wins']
    sizes = [advantageous_wins, total_matches - advantageous_wins]
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3)])

    fig.update_layout(
        title_text='Task 4 Analysis',
        showlegend=True,
        legend=dict(orientation='h', y=1.2),
    )

    html_content = fig.to_html(full_html=False)

    return html_content


def task3_analysis():

    collection = db["matches"]

    matches_data = list(collection.find())

    # We are doing counter initialization
    total_matches = len(matches_data)
    field_decision_matches = sum(1 for match in matches_data if match["toss_details_text"]["toss_decision"] == "field")
    bat_decision_matches = sum(1 for match in matches_data if match["toss_details_text"]["toss_decision"] == "bat")


    field_winner_matches = sum(1 for match in matches_data if match.get("toss_details_text") and match.get("toss_details_text").get("toss_decision") == "field" and match.get("toss_details_text").get("toss_winner") == match.get("winner"))
    bat_winner_matches = sum(1 for match in matches_data if match.get("toss_details_text") and match.get("toss_details_text").get("toss_decision") == "bat" and match.get("toss_details_text").get("toss_winner") == match.get("winner"))

    labels_1 = ['Field', 'Bat']
    sizes_1 = [field_decision_matches, bat_decision_matches]

    labels_2 = ['Field Win', 'Field Lose']
    sizes_2 = [field_winner_matches, field_decision_matches - field_winner_matches]

    labels_3 = ['Bat Win', 'Bat Lose']
    sizes_3 = [bat_winner_matches, bat_decision_matches - bat_winner_matches]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 30))

    colors = ['#66b3ff', '#99ff99']
    explode = (0.1, 0)  


    ax1.pie(sizes_1, autopct='%1.2f%%', startangle=90, colors=colors, explode=explode)
    ax1.set_title('Toss Decision Distribution')


    ax2.pie(sizes_2, autopct='%1.2f%%', startangle=90, colors=colors, explode=explode)
    ax2.set_title('Field Decision and Match Result')

    ax3.pie(sizes_3, autopct='%1.2f%%', startangle=90, colors=colors, explode=explode)
    ax3.set_title('Bat Decision and Match Result')

    plt.suptitle("IPL Toss Analysis", fontsize=16, weight='bold')

    ax1.legend(labels_1, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='large')
    ax2.legend(labels_2, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='large')
    ax3.legend(labels_3, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='large')

    # Saving the combined Pie Charts as HTML
    html_content = mpld3.fig_to_html(fig)
    return html_content


def task1_analysis():

    collection = db["powerplay_Details"]

    # Our group has written this NoSQL Query to data analysis on an unstructured data
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"powerplay_details_text.team1": {"$exists": True}},
                    {"powerplay_details_text.team2": {"$exists": True}},
                    {"result": {"$exists": True}},
                ]
            }
        },
        {
            "$project": {
                "_id": 0,
                "PowerplayWickets": {
                    "$cond": [
                        {"$eq": ["$winner", "winner"]},
                        "$powerplay_details_text.pplay twick1",
                        "$powerplay_details_text.pplay twick2",
                    ]
                },
            }
        },
        {
            "$match": {"PowerplayWickets": {"$exists": True}}
        },
        {
            "$group": {
                "_id": "$PowerplayWickets",
                "TotalWins": {"$sum": 1},
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    result = list(collection.aggregate(pipeline))

    powerplay_wickets = [entry["_id"] for entry in result]
    total_wins = [entry["TotalWins"] for entry in result]

    # Plotting the graph
    plt.figure(figsize=(10, 6))
    plt.bar(powerplay_wickets, total_wins, color='skyblue')

    plt.title('Number of Wickets in Powerplay vs. Total Wins')
    plt.xlabel('Number of Wickets in Powerplay')
    plt.ylabel('Total Wins')
    plt.grid(True)

    html_content = mpld3.fig_to_html(plt.gcf())
    return html_content
    
def task2p1_analysis():

    collection = db["all_season_bowling_card"]
    team_colors = {
        "CSK": "saddlebrown",
        "MI": "blue",
        "LSG": "aqua",
        "RCB": "red",
        "KKR": "purple",
        "SRH": "darkorange",
        "KXIP": "limegreen",
        "GT": "darkblue",
        "RR": "magenta",
        "DC": "black"
    }

    all_seasons = list(range(2008, 2024))

    # Our group has written this NoSQL Query to data analysis on an unstructured data
    traces = []
    for team, color in team_colors.items():
        pipeline = [
            {
                "$match": {"bowl_details_text.bowling_team": team}
            },
            {
                "$group": {
                    "_id": "$bowl_details_text.season",
                    "average_economy_rate": {"$avg": "$bowl_details_text.economyRate"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        result = list(collection.aggregate(pipeline))

        economy_rate_values = [next((entry["average_economy_rate"] for entry in result if entry["_id"] == season), None) for season in all_seasons]

        trace = go.Scatter(
            x=all_seasons,
            y=economy_rate_values,
            mode='lines+markers',
            name=team,
            marker=dict(color=color),
        )
        traces.append(trace)

    layout = go.Layout(
        title='IPL Team Bowling Economy Rate Trend Over the Years (2008-2023)',
        xaxis=dict(title='Season', tickvals=all_seasons, ticktext=[str(year) for year in all_seasons]),
        yaxis=dict(title='Economy Rate'),
        legend=dict(orientation='h', y=1.2),
        updatemenus=[{'type': 'buttons',
                      'showactive': False,
                      'buttons': [{'label': 'All',
                                   'method': 'update',
                                   'args': [{'visible': [True] * len(traces)},
                                            {'title': 'All'}]},
                                  {'label': 'None',
                                   'method': 'update',
                                   'args': [{'visible': [False] * len(traces)},
                                            {'title': 'None'}]}]}],
    )

    fig = go.Figure(data=traces, layout=layout)

    html_content = fig.to_html(full_html=False)

    return html_content
    
def task2p2_analysis():

    collection = db["all_season_points_table"]
    team_colors = {
        "CSK": "saddlebrown",
        "MI": "blue",
        "LSG": "aqua",
        "RCB": "red",
        "KKR": "purple",
        "SRH": "darkorange",
        "KXIP": "limegreen",
        "GT": "darkblue",
        "RR": "magenta",
        "DC": "black"
    }

    all_seasons = list(range(2008, 2024))

    # Our group has written this NoSQL Query to data analysis on an unstructured data
    traces = []
    for team, color in team_colors.items():
        pipeline = [
            {
                "$match": {"short_name": team}
            },
            {
                "$group": {
                    "_id": "$performance_details_text.season",
                    "total_runs_scored": {"$sum": "$performance_details_text.runs_scored"},
                    "total_wickets_taken": {"$sum": "$performance_details_text.wickets_taken"},
                    "average_nrr": {"$avg": "$performance_details_text.nrr"},
                }
            },
            {
                "$addFields": {
                    "runs_per_wicket": {
                        "$cond": {
                            "if": {"$ne": ["$total_wickets_taken", 0]},
                            "then": {"$divide": ["$total_runs_scored", "$total_wickets_taken"]},
                            "else": None
                        }
                    },
                    "nrr_squared": {"$pow": ["$average_nrr", 2]}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        result = list(collection.aggregate(pipeline))


        nrr_values = [next((entry["average_nrr"] for entry in result if entry["_id"] == season), None) for season in all_seasons]

        trace = go.Scatter(
            x=all_seasons,
            y=nrr_values,
            mode='lines+markers',
            name=team,
            legendgroup=team,
            marker=dict(color=color),
        )
        traces.append(trace)

    layout = go.Layout(
        title='IPL Team NRR Trend Over the Years (2008-2023)',
        xaxis=dict(title='Season', tickvals=all_seasons, ticktext=[str(year) for year in all_seasons]),
        yaxis=dict(title='Average NRR'),
        legend=dict(orientation='h', y=1.2),
        updatemenus=[
            {
                'buttons': [
                    {
                        'args': [{'visible': [True] * len(traces)}],
                        'label': 'All',
                        'method': 'restyle'
                    },
                    {
                        'args': [{'visible': [False] * len(traces)}],
                        'label': 'None',
                        'method': 'restyle'
                    },
                ],
                'showactive': False,
                'x': 1.05,
                'y': 1.15,
                'type': 'buttons',
            },
        ],
    )

    fig = go.Figure(data=traces, layout=layout)
    html_content = fig.to_html(full_html=False)
    return html_content
    

# Pre-computing the results
results = {
    "Task4": task4_analysis(),
    "Task3": task3_analysis(),
    "Task1": task1_analysis(),
    "Task2P1": task2p1_analysis(),
    "Task2P2": task2p2_analysis(),
}

# Homepage Route
@app.route('/')
def homepage():
    return render_template('index.html', tasks=results.keys())

# Task Route
@app.route('/task/<task_name>')
def show_task(task_name):
    return results.get(task_name, redirect(url_for('homepage')))

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
