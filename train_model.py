import pandas as pd
import pickle
import csv
import argparse
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, TransformerMixin


class ColumnSelector(BaseEstimator, TransformerMixin):

    def __init__(self, columns=[]):
        self.columns = columns

    def transform(self, X, y=None):
        return X.iloc[:, self.columns].astype(float)

    def fit(self, X, y=None):
        return self


def train_model(file):
    """Creates and saves a trained ML model used to predict whether an NHL team will make the playoffs as
    determined after 41 games played in a season.

        Args:
            file(:str:): The pathway to the training data set

        Returns:
            Nothing
    """

    data = pd.read_csv(f'{file}')

    X_train, X_test, y_train, y_test = train_test_split(
        data.iloc[:, 0:6].astype(float), data.iloc[:, 6], random_state=0, test_size=0.2)

    pipeline = make_pipeline(
        ColumnSelector(columns=[2, 3, 4, 5]),
        StandardScaler(),
        GradientBoostingClassifier()
    )

    param_grid = {
        'gradientboostingclassifier__max_depth': [1, 2, 3],
        'gradientboostingclassifier__n_estimators': [10, 50, 100, 200],
        'gradientboostingclassifier__learning_rate': [0.001, 0.001, 0.01, 0.1, 0.2, 0.3],
    }

    grid = GridSearchCV(pipeline, cv=10, param_grid=param_grid, iid=False).fit(X_train, y_train)

    print(f'Training Score: {grid.best_score_} and Params: {grid.best_params_}')
    print(f'Validation Score: {grid.score(X_test, y_test)}')

    with open('model.p', 'wb') as model_file:
        pickle.dump(grid, model_file)


def predict_model(file, model):
    """Creates, prints and saves predictions for teams making the playoffs after 41 games. Format must match
        SQL query.

        Args:
            file(:str:): The pathway to the data to predict
            model(:str:): The pathway to the pickled training model

        Returns:
            Nothing
    """

    file = pd.read_csv(file)
    model = pickle.load(open('model.p', 'rb'))

    print('Model Predictions')
    pred = model.predict(file)
    print(pred)

    with open('predict.csv', 'w') as output:
        writer = csv.writer(output)
        for ele in pred.tolist():
            writer.writerow([ele])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train and predict whether NHL teams will make the playoffs')
    parser.add_argument('file', action='store',
                        help='Pathway to file to predict or train with')
    parser.add_argument('-m', dest='model', action='store', default=None,
                        help='Pathway to model to use if predicting, otherwise left blank')
    results = parser.parse_args()

    if results.model is None:
        print("Training Model")
        train_model(results.file)
    else:
        print("Making Predictions")
        predict_model(results.file, results.model)