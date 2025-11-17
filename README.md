# 🎓 College Fit Predictor

A comprehensive college recommendation system that helps students find colleges that best match their preferences, financial situation, and personal circumstances. The tool uses a weighted scoring algorithm combined with AI-powered personalized summaries to provide tailored college recommendations.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data](#data)
- [Technologies](#technologies)
- [How It Works](#how-it-works)

## ✨ Features

- **Personalized College Matching**: Rank colleges based on multiple factors including:
  - Geographic preferences (desired state, home state)
  - Financial constraints (tuition, debt tolerance)
  - Demographics (gender, race, age)
  - Academic interests (field of study)
  - Special circumstances (student parent status, international student status)
  - Minority-Serving Institution (MSI) preferences

- **AI-Powered Summaries**: Generate personalized, data-backed summaries for recommended colleges using Google's Gemini AI model

- **Weighted Scoring System**: Colleges are ranked using a sophisticated scoring algorithm that considers:
  - Gender representation (10%)
  - Racial/ethnic representation (10%)
  - Major alignment (10%)
  - Affordability (20%)
  - Debt burden (20%)
  - Student parent support (10%)
  - Age demographics (5%)
  - Post-graduation earnings (15%)

- **Interactive Web Interface**: User-friendly Streamlit application with intuitive forms and visualizations

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd DSS_Datathon
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root and add your Google Gemini API key:
   ```
   GEMINI_KEY=your_api_key_here
   ```

## 💻 Usage

1. **Navigate to the source directory**:
   ```bash
   cd src
   ```

2. **Run the Streamlit application**:
   ```bash
   streamlit run frontend.py
   ```

3. **Access the application**:
   Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

4. **Use the application**:
   - Fill in your preferences (state, tuition limits, debt tolerance, MSI type)
   - Provide personal information (gender, race, age, income, major, etc.)
   - Specify the number of colleges you want to see
   - Click "Find Colleges" to get ranked recommendations
   - Click "Generate AI Summary" on any college to get a personalized analysis

## 📁 Project Structure

```
DSS_Datathon/
├── data/                          # Data files
│   ├── College_Affordability_Gap_Data_Filtered.csv
│   ├── College_Affordability_Gap_Data_Raw.csv
│   ├── College_Results_Data_Filtered.csv
│   ├── College_Results_Data_Raw.csv
│   └── Joint_Data.csv            # Combined dataset used by the application
├── src/
│   ├── frontend.py               # Main Streamlit application
│   ├── functions.py              # Core ranking and display functions
│   ├── model_utils.py            # AI model integration (Gemini RAG)
│   └── Notebooks/                # Exploratory data analysis notebooks
│       ├── EDA_Affordability.ipynb
│       └── EDA_Results.ipynb
├── experiments/                   # Experimental code
├── models/                        # Saved models (if any)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 📊 Data

The application uses a joint dataset (`Joint_Data.csv`) that combines:
- **College Affordability Gap Data**: Information about tuition costs, affordability gaps, student parent support, and financial aid
- **College Results Data**: Information about demographics, graduation rates, majors, earnings, and student outcomes

Key data fields include:
- Institution information (name, state, MSI status)
- Financial metrics (tuition, net price, debt, affordability gaps)
- Demographics (gender, race, age distributions)
- Academic information (majors, degree programs)
- Outcomes (earnings, employment statistics)

## 🛠 Technologies

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: scikit-learn, XGBoost
- **AI/LLM**: Google Generative AI (Gemini), Transformers, Sentence Transformers
- **Visualization**: Matplotlib, Plotly
- **Vector Search**: FAISS
- **Other**: python-dotenv, tqdm

## 🔍 How It Works

1. **Data Filtering**: The system first filters colleges based on hard constraints:
   - Desired state (if specified)
   - MSI type preference
   - Maximum tuition (in-state or out-of-state based on home state)
   - Maximum acceptable debt

2. **Scoring Algorithm**: For each college that passes the filters, a composite score is calculated using weighted factors:
   - Representation scores (gender, race, major alignment)
   - Financial scores (affordability ratio, debt burden)
   - Special circumstance scores (student parent support, age demographics)
   - Outcome scores (predicted earnings)

3. **Ranking**: Colleges are sorted by their composite score and the top K recommendations are displayed.

4. **AI Summaries**: When requested, the system:
   - Builds a RAG (Retrieval Augmented Generation) context from student profile and college data
   - Uses Google's Gemini model to generate personalized, data-grounded summaries
   - Provides specific insights about why each college fits the student's needs

## 📝 Notes

- The AI summaries are generated using Google's Gemini 2.5 Flash model
- All recommendations are based solely on the data provided in the dataset
- The scoring weights can be adjusted in `src/functions.py` in the `rank_colleges` function
- The system is designed to be transparent and data-driven, avoiding hallucinations by strictly using provided context

## 🤝 Contributing

This project was developed for the DSS Datathon. Contributions and improvements are welcome!

## 📄 License

[Add your license information here]

