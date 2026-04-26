# 🔗 URL Classification using Random Forest

A machine learning web application that classifies URLs as **Benign**, **Malware**, or **Defacement** using a Random Forest model, served through a Flask web interface.

---

## 📁 Project Structure

```
project/
│
├── URL_Flask/
│   ├── randomforest.pkl       # Trained Random Forest model
│   ├── label_map.pkl          # Label encoding map
│   └── templates/
│       └── index.html         # Frontend HTML template
│
├── train_model.py             # Model training script
├── app.py                     # Flask web application
├── malicious_phish.csv        # Dataset
└── README.md
```

---

## 🧠 How It Works

The project is split into two parts: **model training** and **web deployment**.

### 1. Model Training (`train_model.py`)

**Step 1 — Load & Filter Dataset**

The dataset (`malicious_phish.csv`) contains URLs labeled with their type. Only three classes are kept for classification: `benign`, `malware`, and `defacement`. Phishing URLs are excluded from this version.

```python
allowed_types = ['benign', 'malware', 'defacement']
df = df[df['type'].isin(allowed_types)]
```

**Step 2 — Label Encoding**

URL types (strings) are converted into numeric codes using pandas' categorical encoding. A `label_map` dictionary is saved to reverse the prediction back to a human-readable label.

```python
df['label'] = df['type'].astype('category').cat.codes
label_map = dict(enumerate(df['type'].astype('category').cat.categories))
# Example: {0: 'benign', 1: 'defacement', 2: 'malware'}
```

**Step 3 — Feature Engineering**

Each URL is parsed and converted into 12 numerical features using the `extract_features()` function:

| Feature | Description |
|---|---|
| `url_length` | Total character count of the URL |
| `hostname_length` | Length of the domain/hostname |
| `count_dots` | Number of `.` in the URL |
| `count_hyphens` | Number of `-` in the URL |
| `count_at` | Number of `@` symbols (common in phishing) |
| `count_question` | Number of `?` (query parameters) |
| `count_percent` | Number of `%` (URL encoding) |
| `count_equals` | Number of `=` (key-value pairs) |
| `count_http` | Occurrences of the word `http` |
| `count_https` | Occurrences of the word `https` |
| `has_ip` | `1` if the hostname is a raw IP address, else `0` |
| `is_https` | `1` if the URL uses HTTPS, else `0` |

**Step 4 — Model Training**

A `RandomForestClassifier` is trained on an 80/20 train-test split with `class_weight="balanced"` to handle any class imbalance in the dataset.

```python
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)
```

**Step 5 — Evaluation**

The model is evaluated using:
- **Classification Report** — Precision, Recall, and F1-score per class
- **Confusion Matrix** — Visualized using Seaborn heatmap
- **Feature Importance Chart** — Bar chart showing which features matter most

**Step 6 — Save Model**

The trained model and label map are saved using `joblib` for later use in the Flask app.

```python
joblib.dump(model, "URL_Flask/randomforest.pkl")
joblib.dump(label_map, "URL_Flask/label_map.pkl")
```

---

### 2. Flask Web Application (`app.py`)

**Startup**

When the app launches, it loads the pre-trained model and label map from disk:

```python
model = joblib.load("URL_Flask/randomforest.pkl")
label_map = joblib.load("URL_Flask/label_map.pkl")
```

**Routes**

| Route | Method | Description |
|---|---|---|
| `/` | GET | Renders the home page (`index.html`) |
| `/check` | POST | Accepts a URL from a form and returns the prediction |

**URL Prediction Flow (`/check`)**

When a URL is submitted via the form, the following steps happen:

1. **Input Validation** — If the input contains only digits, it's rejected as invalid.

2. **Whitelist Check** — The URL is checked against a hardcoded list of trusted domains (Google, GitHub, YouTube, etc.). If matched, it is immediately classified as `benign` without running the model.

   ```python
   if any(domain in url for domain in whitelist):
       result = "benign"
   ```

3. **Model Prediction** — If the URL is not on the whitelist, features are extracted and fed into the Random Forest model. The numeric prediction is mapped back to a label.

   ```python
   feat = pd.DataFrame([extract_features(url)])
   pred = model.predict(feat)[0]
   result = label_map[pred]
   ```

4. **Result Display** — The result (`benign`, `malware`, or `defacement`) is passed back to the HTML template for display.

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install flask pandas scikit-learn joblib matplotlib seaborn
```

### Train the Model

Run this first to generate the `.pkl` files:

```bash
python train_model.py
```

### Start the Flask App

```bash
python app.py
```

Then open your browser and go to `http://127.0.0.1:5000`.

---

## 🗂️ Dataset

The model is trained on the [`malicious_phish.csv`](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset) dataset from Kaggle, which contains URLs labeled across four categories. This project uses three of them: `benign`, `malware`, and `defacement`.

---

## 📊 Sample Output

```
URL: http://malicious-phish.fakeupdate.com/index
Prediction: malware
```

---

## 🛠️ Tech Stack

- **Python** — Core language
- **Flask** — Web framework
- **scikit-learn** — Random Forest model
- **pandas / numpy** — Data processing
- **joblib** — Model serialization
- **matplotlib / seaborn** — Evaluation visualizations
