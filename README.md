# NHL Playoff Predictor

### The deliverable on this project is a pickled machine learning model that will predict whether or not an NHL team will make the playoffs as determined by a variety of statistics midway through the season. I was ultimately able to achieve an 88% prediction rate on the validation data. Prediction scoring will be conducted on the 2018-2019 NHL season and will be updated here after 41 games and at the end of the season.

### Presentation can be found [here](https://www.youtube.com/watch?v=ykzbCkNoTSo) An updated version using Spark can be found [here](https://www.youtube.com/watch?time_continue=1&v=HBgS6G8JHFc)

### Predictions:
<pre>
Anaheim Ducks           0 - Correct
Arizona Coyotes         0 - Correct
Boston Bruins           1 - Correct
Buffalo Sabres          1 - Incorrect
Calgary Flames          1 - Correct
Carolina Hurricanes     0 - Incorrect
Chicago Blackhawks      0 - Correct
Colorado Avalanche      1 - Correct
Columbus Blue Jackets   1 - Correct
Dallas Stars            1 - Correct
Detroit Red Wings       0 - Correct
Edmonton Oilers         0 - Correct
Florida Panthers        0 - Correct
Los Angeles Kings       0 - Correct
Minnesota Wild          1 - Incorrect
Montreal Canadiens      1 - Incorrect
Nashville Predators     1 - Correct
New Jersey Devils       0 - Correct
New York Islanders      1 - Correct
New York Rangers        0 - Correct
Ottawa Senators         0 - Correct
Philadelphia Flyers     0 - Correct
Pittsburgh Penguins     1 - Correct
San Jose Sharks         1 - Correct
St. Louis Blues         0 - Correct
Tampa Bay Lightning     1 - Correct
Toronto Maple Leafs     1 - Correct
Vancouver Canucks       0 - Correct
Vegas Golden Knights    1 - Correct
Washington Capitals     1 - Correct
Winnipeg Jets           1 - Correct

Total Accuracy:         27/31=87%
</pre>

### Details:

The goal of this project was to demonstrate a variety of data science skills. To be clear, the goal of this project
was NOT to simulate a traditional workflow but to highlight successfully querying an SQL database and ML algorithm
creation.
The workflow for this project is as follows:

1. scrape.py scrapes historical NHL data and then formats several dataframe according to the schema stored in
    database_schema
2. csv_to_sql.py connects to a mysql server, creates the tables indicated in the schema and stores the dataframe
    in the mysql database.
3. output.sql holds the sql query that created the predictors and response variables for the ML algorithm. The results
    of this query were stored in training_data.csv
4. train_model.py reads in the csv file, trains the ML algorithm, displays the results and returns a pickled version
     of the model. It also will allow for future predictions.

This process will be repeated for the 2018-2019 season data to make predictions.

<pre>
usage: train_model.py [-h] [-m MODEL] file

Train and predict whether NHL teams will make the playoffs

positional arguments:
  file        Pathway to file to predict or train with

optional arguments:
  -h, --help  show this help message and exit
  -m MODEL    Pathway to model to use if predicting, otherwise left blank
</pre>
