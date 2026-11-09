SELECT
    renewal_month,
    COUNT(*)       AS offered,
    SUM(renewed)   AS renewed,
    AVG(renewed)   AS renewal_rate
FROM renewals
GROUP BY renewal_month
ORDER BY renewal_month;
