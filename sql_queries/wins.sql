SELECT sub.id, sub.year, SUM(CASE WHEN sub.result = 'W' THEN 1 ELSE 0 END) AS 'wins', SUM(sub.points) AS 'points'
FROM (SELECT teams.id, results.year, points.result, points.points, ROW_NUMBER() OVER (PARTITION BY teams.id, year) AS 'row_number'
        FROM teams
        INNER JOIN results on teams.id = results.team_id
        INNER JOIN points on results.points_id = points.id
        WHERE results.year <> 2013
    ) AS sub
WHERE sub.row_number <= 41
GROUP BY sub.id, sub.year
ORDER BY sub.id, sub.year

