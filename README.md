# Steam Select: A Steam Game Recommendation System 🎮  

## Overview  
**Steam Select** is a cutting-edge recommendation system designed to help Steam users discover new video games based on their preferences. Users interact with a chatbot interface, providing details about games they liked or disliked. The system suggests similar games, dissimilar games, or profitable bundles tailored to the user's interests.  

This project leverages advanced recommendation techniques and an intuitive chatbot interface to deliver an engaging and personalized experience for gamers.  

---

## Features  
- **Personalized Recommendations**: Suggests games similar to user favorites or dissimilar to disliked games.  
- **Bundle Suggestions**: Recommends profitable bundles based on user preferences.  
- **Interactive Chatbot**: Provides a seamless conversational interface for game discovery.  
- **Cloud Integration**: Hosted on Google Cloud Platform (GCP) for scalability and efficiency.  

---

## Dataset  
The dataset includes user reviews, purchase data, gameplay statistics, and bundle details, sourced from Julian McAuley's **Steam Video Game and Bundle Data**.  
- **Reviews**: 7,793,069  
- **Users**: 2,567,538  
- **Items**: 15,474  
- **Bundles**: 615  

Dataset URL: [Steam Data Repository](https://cseweb.ucsd.edu/~jmcauley/datasets.html#steam_data)  

---

## Tech Stack  
### Backend:  
- **Recommendation Engine**: Scikit-learn, TensorFlow, or PyTorch  
- **Pre-trained Models**: BERT, Sentence Transformers for NLP tasks  
- **Data Processing**: Pandas, NumPy  

### Cloud Platform:  
- **Data Hosting**: Snowflake  
- **Model Deployment**: Google Cloud Vertex AI  
- **Pipeline Orchestration**: Apache Airflow  

### Frontend:  
- **API Development**: FastAPI  
- **User Interface**: Streamlit  

### DevOps:  
- **CI/CD**: GitHub Actions, Docker  
- **Monitoring & Alerting**: GCP Cloud Monitoring  

---

## Project Workflow  
1. **Data Collection & Ingestion**: Extract data from JSON, load into Snowflake, and schedule ingestion pipelines with Apache Airflow.  
2. **Data Preprocessing & Validation**: Clean and validate data using Pandas, NumPy, and Great Expectations.  
3. **Model Training**: Train collaborative filtering and content-based models. Fine-tune pre-trained models as needed.  
4. **Model Versioning**: Track experiments, hyperparameters, and metrics with MLflow.  
5. **Deployment**: Use Docker to containerize the model and deploy it on GCP Vertex AI.  
6. **Frontend Integration**: Develop an interactive chatbot using FastAPI and Streamlit.  
7. **Monitoring & Maintenance**: Implement monitoring tools to track performance and schedule periodic retraining with Airflow.  

---

## Getting Started  
### Prerequisites  
- Python 3.9+  
- GCP account with Vertex AI access  
- Snowflake account  
- GitHub repository setup with CI/CD pipelines  

### Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/your-username/steam-select.git
   cd steam-select
# Steam-Select