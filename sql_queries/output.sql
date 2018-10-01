CREATE TEMPORARY TABLE wins
SELECT sub.id, sub.year, SUM(CASE WHEN sub.result = 'W' THEN 1 ELSE 0 END) AS 'wins', SUM(sub.points) AS 'points'
FROM (SELECT teams.id, results.year, points.result, points.points, ROW_NUMBER() OVER (PARTITION BY teams.id, year) AS 'row_number'
        FROM teams
        INNER JOIN results on teams.id = results.team_id
        INNER JOIN points on results.points_id = points.id
        WHERE results.year <> 2013
    ) AS sub
WHERE sub.row_number <= 41
GROUP BY sub.id, sub.year;

CREATE TEMPORARY TABLE goal_diff
SELECT sub.team_id, sub.year, SUM(sub.diff) AS 'goal_diff'
FROM (SELECT r.team_id, r.year, r.goals - r2.goals AS 'diff', ROW_NUMBER() OVER (PARTITION BY r.team_id, year) AS 'row_number'
        FROM results AS r
        INNER JOIN results AS r2 ON r.game_id = r2.game_ID AND r.id <> r2.id
    ) AS sub
WHERE sub.row_number <= 41
GROUP BY sub.team_id, sub.year
ORDER BY sub.team_id, sub.year;

CREATE TEMPORARY TABLE strength
SELECT last.id, last.year, SUM(last.wins) AS 'strength'
FROM (SELECT teams.id, schedule.year, ROW_NUMBER() OVER (PARTITION BY teams.id, year) AS 'row_number', wins.wins
        FROM schedule
        INNER JOIN teams on teams.id = schedule.away_id OR teams.id = schedule.home_id
        INNER JOIN wins
            ON wins.id = schedule.away_id + schedule.home_id - teams.id AND wins.year = schedule.year
      ) AS last
WHERE last.row_number > 41
GROUP BY last.id, last.year
ORDER BY last.id, last.year;


SELECT teams.id, wins.year, wins.wins, wins.points, goal_diff.goal_diff, strength.strength, playoffs.playoffs
FROM teams
INNER JOIN wins ON teams.id = wins.id
INNER JOIN goal_diff on teams.id = goal_diff.team_id AND wins.year = goal_diff.year
INNER JOIN strength on teams.id = strength.id AND wins.year = strength.year
INNER JOIN playoffs on teams.id = playoffs.team_id AND wins.year = playoffs.year
ORDER BY wins.year, teams.id
