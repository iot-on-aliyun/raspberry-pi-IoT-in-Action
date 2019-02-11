-- 总人数
SELECT COUNT(id) AS total
FROM shopping_mall_visitors

-- 戴眼镜总人数
SELECT COUNT(id) AS total
FROM shopping_mall_visitors
WHERE glass ='y'

-- 男/女 人数汇总
SELECT COUNT(id) AS total, 
	CASE gender
		WHEN 'f' THEN '女性'
		ELSE '男性'
	END AS gender
FROM shopping_mall_visitors
GROUP BY gender

-- 戴眼镜/无 人数汇总
SELECT COUNT(id) AS total, 
	CASE glass
		WHEN 'y' THEN '戴眼镜'
		ELSE '无'
	END AS glass
FROM shopping_mall_visitors
GROUP BY glass

-- 年龄分布 人数汇总
SELECT age_range, COUNT(1) AS total
FROM (
	SELECT CASE 
			WHEN age < 11 THEN '0-11'
			WHEN age >= 11 AND age <= 20 THEN '11-20'
			WHEN age >= 21 AND age <= 30 THEN '21-30'
			WHEN age >= 31 AND age <= 40 THEN '31-40'
			WHEN age >= 41 AND age <= 50 THEN '41-50'
			WHEN age >= 51 AND age <= 60 THEN '51-60'
			WHEN age > 60 THEN '60-100'
		END AS age_range
	FROM shopping_mall_visitors
) a
GROUP BY age_range
ORDER BY age_range ASC

