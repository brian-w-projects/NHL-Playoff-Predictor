SELECT last.id, last.year, SUM(last.wins) AS 'strength'
FROM (SELECT teams.id, schedule.year, ROW_NUMBER() OVER (PARTITION BY teams.id, year) AS 'row_number', tot.wins
        FROM schedule
        INNER JOIN teams on teams.id = schedule.away_id OR teams.id = schedule.home_id
        INNER JOIN (SELECT sub.id, sub.year, COUNT(sub.result) AS 'wins'
                        FROM (SELECT teams.id, results.year, points.result, ROW_NUMBER() OVER (PARTITION BY teams.id, year) AS 'row_number'
                                FROM teams
                                INNER JOIN results on teams.id = results.team_id
                                INNER JOIN points on results.points_id = points.id
                                WHERE results.year <> 2013
                             ) AS sub
                        WHERE sub.row_number <= 41
                        AND sub.result = 'W'
                        GROUP BY sub.id, sub.year
                    ) as tot
            ON tot.id = schedule.away_id + schedule.home_id - teams.id AND tot.year = schedule.year
      ) AS last
WHERE last.row_number > 41
GROUP BY last.id, last.year
ORDER BY last.id, last.year
        
        
        
        
        
        
        