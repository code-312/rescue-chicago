import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
import joblib

# Import necessary constants and functions from config.py
from config import AGE_DICT, SIZE_DICT, TARGET_COLS, BINARY_COLS, HEROKU_URL

class ModelAndData:
    def __init__(self):
        self.model = None
        self.preprocessor = None

    def read_data(self, uri):
        df_raw = pd.read_sql('petfinder_with_dates', uri)
        return df_raw

    def preprocess_data(self, df):
        # Drop irrelevant columns
        columns_to_drop = [
            "index", "id", "name", "organization_id", "published_at", "status_changed_at",
            "attribute_declawed", "color_tertiary", "good_with_cats", "good_with_children",
            "good_with_dogs", "breed_secondary", "color_secondary"
        ]
        df = df.drop(columns=columns_to_drop)

        # Transform "age" column
        df['age'] = df['age'].map(AGE_DICT).astype(int)

        # Transform "size" column
        df['size'] = df['size'].map(SIZE_DICT).astype(int)

        # Drop rows with unknown gender
        df.drop(df[df['gender'] == 'Unknown'].index, inplace=True)

        # Convert binary columns to binary (0/1) data type
        df[BINARY_COLS] = df[BINARY_COLS].astype(bool).astype(int)

        # Filter data for los 1+
        df = df[df['los'] >= 1]

        # Target encoding on larger categorical features
        for col in TARGET_COLS:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])

        return df

    def fill_nan_mode(self, df, reference_column, feature):
        # Calculate the mode coat for each breed_primary
        mode_by_breed = df.groupby(reference_column)[feature].apply(
            lambda x: x.mode().iloc[0] if not x.isnull().all() else None
        )

        # Create a dictionary mapping each breed to its mode coat
        mode_dict = dict(mode_by_breed)

        # Fill the NaN values in 'coat' based on the breed using the mode_dict
        df[feature] = df.apply(
            lambda row: mode_dict[row[reference_column]] if pd.isna(row[feature]) and row[reference_column] in mode_dict else row[feature],
            axis=1
        )

        return df

    def drop_null_rows(self, df, feature):
        # Drop rows with null values
        df.dropna(subset=[feature], inplace=True)
        return df

    def remove_outliers(self, df, columns, zscore_threshold=3):
        for col in columns:
            mean = df[col].mean()
            std = df[col].std()
            z_scores = np.abs((df[col] - mean) / std)
            df = df[z_scores <= zscore_threshold]
        return df

    def train_kmeans_clustering(self, df):
        # Rescale data using Standard Scaler for better clustering results
        scaler = StandardScaler()
        full_data = scaler.fit_transform(df)

        # Create a list to store the sum of squared distances for each k
        ssd = []

        # Fit KMeans clustering with different values of k
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(full_data)
            ssd.append(kmeans.inertia_)

        # Fit PCA with a specified number of components
        pca = PCA(n_components=14, random_state=42)
        df_pca = pca.fit_transform(full_data)

        # Train KMeans clustering model with the chosen number of clusters
        kmeans = KMeans(n_clusters=6, random_state=42)
        kmeans.fit(df_pca)

        # Predict clusters
        pred = kmeans.predict(df_pca)

        # Append cluster assignments to the dataframe
        df['Cluster'] = pred

        return df

    def train_random_forest_classification(self, X_train, y_train):
        # Initialize the classifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42)

        # Train the classifier
        clf.fit(X_train, y_train)

        return clf

    def main(self, uri):
        # Read data from the database
        df_raw = self.read_data(uri)

        # Preprocess data
        df_preprocessed = self.preprocess_data(df_raw)

        # Remove outliers
        outlier_columns = ['organization_name', 'los', 'breed_primary']
        df_no_outliers = self.remove_outliers(df_preprocessed, outlier_columns)
        df = self.fill_nan_mode(df_no_outliers, 'breed_primary', 'coat')
        df = self.fill_nan_mode(df_no_outliers, 'breed_primary', 'color_primary')
        df = self.drop_null_rows(df, 'coat')
        df = self.drop_null_rows(df, 'color_primary')

        # Train KMeans clustering model and append cluster assignments
        df = self.train_kmeans_clustering(df)

        # Features and target for classification
        X = df.drop('Cluster', axis=1)
        y = df['Cluster']

        # Split the data into training and testing sets
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Random Forest classification model
        self.model = self.train_random_forest_classification(X_train, y_train)

    def save_model(self, filename):
        joblib.dump(self.model, filename)


if __name__=="__main__":
    HEROKU_URL = os.getenv('HEROKU_POSTGRESQL_AMBER_URL')
    uri = HEROKU_URL
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    model_and_data = ModelAndData()
    model_and_data.main(uri)
    model_and_data.save_model('random_forest_model.pkl')
