SELECT sub.team_id, sub.year, SUM(sub.diff) AS 'goal_diff'
FROM (SELECT r.team_id, r.year, r.goals - r2.goals AS 'diff', ROW_NUMBER() OVER (PARTITION BY r.team_id, year) AS 'row_number'
        FROM results AS r
        INNER JOIN results AS r2 ON r.game_id = r2.game_ID AND r.id <> r2.id
    ) AS sub
WHERE sub.row_number <= 41
GROUP BY sub.team_id, sub.year
ORDER BY sub.team_id, sub.year