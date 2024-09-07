# import knn
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd

# Load the data
data = pd.read_csv('audio_dataset.csv')

y = data['patient_type']
X = data.drop('patient_type', axis=1)

# Create the model
model = KNeighborsClassifier(n_neighbors=3)

# Train the model
model.fit(X, y)

# Save the model
import joblib
joblib.dump(model, 'knn_model.sav')