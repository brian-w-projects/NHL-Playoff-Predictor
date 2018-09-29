import mysql.connector
import csv

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='cosmic joke',
    database='hockey'
)

mycursor = mydb.cursor()

# POINTS
mycursor.execute("CREATE TABLE IF NOT EXISTS points ("
                 "id INT NOT NULL, "
                 "result VARCHAR(255) NOT NULL, "
                 "points INT NOT NULL, "
                 "PRIMARY KEY (id)"
                 ");"
                 )

statement = "INSERT INTO points (id, result, points) VALUES (%s, %s, %s)"
vals = []
with open('data/points.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        vals.append(row)

mycursor.executemany(statement, vals)
mydb.commit()

# TEAMS
mycursor.execute("CREATE TABLE IF NOT EXISTS teams ("
                 "id INT NOT NULL, "
                 "team VARCHAR(255) NOT NULL, "
                 "PRIMARY KEY (id)"
                 ");"
                 )

statement = "INSERT INTO teams (id, team) VALUES (%s, %s)"
vals = []
with open('data/teams.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        vals.append(row)

mycursor.executemany(statement, vals)
mydb.commit()


# PLAYOFFS
mycursor.execute("CREATE TABLE IF NOT EXISTS playoffs ("
                 "id INT NOT NULL, "
                 "team_id INT NOT NULL, "
                 "year INT NOT NULL, "
                 "playoffs INT NOT NULL, "
                 "PRIMARY KEY (id), "
                 "FOREIGN KEY (team_id) REFERENCES teams(id)"
                 ");"
                 )

statement = "INSERT INTO playoffs (id, team_id, year, playoffs) VALUES (%s, %s, %s, %s)"
vals = []
with open('data/playoffs.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        vals.append(row)

mycursor.executemany(statement, vals)
mydb.commit()

# SCHEDULE
mycursor.execute("CREATE TABLE IF NOT EXISTS schedule ("
                 "id INT NOT NULL, "
                 "year INT NOT NULL, "
                 "away_id INT NOT NULL, "
                 "home_id INT NOT NULL, "
                 "PRIMARY KEY (id), "
                 "FOREIGN KEY (away_id) REFERENCES teams(id), "
                 "FOREIGN KEY (home_id) REFERENCES teams(id)"
                 ");"
                 )

statement = "INSERT INTO schedule (id, year, away_id, home_id) VALUES (%s, %s, %s, %s)"
vals = []
with open('data/schedule.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        vals.append(row)

mycursor.executemany(statement, vals)
mydb.commit()

# RESULTS
mycursor.execute("CREATE TABLE IF NOT EXISTS results ("
                 "id INT NOT NULL, "
                 "game_id INT NOT NULL, "
                 "year INT NOT NULL, "
                 "team_id INT NOT NULL, "
                 "goals INT NOT NULL, "
                 "points_id INT NOT NULL, "
                 "PRIMARY KEY (id), "
                 "FOREIGN KEY (game_id) REFERENCES schedule(id), "
                 "FOREIGN KEY (team_id) REFERENCES teams(id), "
                 "FOREIGN KEY (points_id) REFERENCES points(id) "
                 ");"
                 )

statement = "INSERT INTO results (id, game_id, year, team_id, goals, points_id) VALUES (%s, %s, %s, %s, %s, %s)"
vals = []
with open('data/results.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        vals.append(row)

mycursor.executemany(statement, vals)
mydb.commit()