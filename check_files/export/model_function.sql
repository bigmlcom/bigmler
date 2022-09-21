CREATE FUNCTION predict_species (`sepal length` NUMERIC, `sepal width` NUMERIC, `petal length` NUMERIC, `petal width` NUMERIC)
RETURNS VARCHAR(250) DETERMINISTIC
RETURN IF ( (ISNULL(`petal length`)), 'Iris-setosa',
    IF ( (`petal length`>2.45),
        IF ( (ISNULL(`petal width`)), 'Iris-versicolor',
            IF ( (`petal width`>1.75),
                IF ( (`petal length`>4.85), 'Iris-virginica',
                    IF ( (`petal length`<=4.85),
                        IF ( (ISNULL(`sepal width`)), 'Iris-virginica',
                            IF ( (`sepal width`>3.1), 'Iris-versicolor',
                                IF ( (`sepal width`<=3.1), 'Iris-virginica', NULL))), NULL)),
                IF ( (`petal width`<=1.75),
                    IF ( (`petal length`>4.95),
                        IF ( (`petal width`>1.55),
                            IF ( (`petal length`>5.45), 'Iris-virginica',
                                IF ( (`petal length`<=5.45), 'Iris-versicolor', NULL)),
                            IF ( (`petal width`<=1.55), 'Iris-virginica', NULL)),
                        IF ( (`petal length`<=4.95),
                            IF ( (`petal width`>1.65), 'Iris-virginica',
                                IF ( (`petal width`<=1.65), 'Iris-versicolor', NULL)), NULL)), NULL))),
        IF ( (`petal length`<=2.45), 'Iris-setosa', NULL)))

