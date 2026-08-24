EduSaaS AI/ML
Production README & AI/ML System Overview
AI-Powered Personalized Learning Platform
Production Technical Reference • Version 1.0
1. Overview
EduSaaS is an AI-powered personalized learning platform. The AI/ML layer provides recommendation, learner-risk prediction, fraud/anomaly detection, predictive hiring, sentiment analysis, and toxicity detection capabilities.
This README is a repository-level technical reference. Detailed implementation and model documentation should be maintained in the dedicated module documentation.
2. Architecture
Frontend
   |
   v
Node.js / Express Backend
   |
   +-------------------------------+
   |               |               |
   v               v               v
Recommendation  Sentiment       Hiring
Python API      Python API      Python API
   |               |               |
   v               v               v
ML Artifacts    DistilBERT      Random Forest
   |               |               |
   +---------------+---------------+
                   |
                   v
              PostgreSQL
The Node.js backend provides the application-facing integration layer. Python services expose AI/ML inference APIs. Model artifacts are loaded at inference time and are not retrained during API requests.
3. AI/ML Model Inventory
Module	Model / Architecture	Persistence
Recommendation	SVD Collaborative Filtering + Content-Based Recommendation	.pkl artifacts
Dropout Prediction	Random Forest Classifier	.pkl artifacts
Fraud & Anomaly Detection	Random Forest + Isolation Forest	.pkl artifacts
Predictive Hiring	Random Forest	.pkl artifacts
Sentiment Analysis	DistilBERT sequence classification	Hugging Face / SafeTensors
Toxicity Detection	DistilBERT sequence classification	Hugging Face / SafeTensors
4. Repository Structure
C:\Edusaas
├── backend/
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   └── config/
├── src/
│   ├── api/
│   ├── recommendation/
│   ├── dropout/
│   ├── fraud/
│   ├── hiring/
│   ├── sentiment/
│   └── toxicity/
├── models/
│   ├── fraud/
│   ├── hiring/
│   ├── sentiment/
│   └── toxicity/
├── tests/
├── docs/
├── requirements.txt
└── README.md
5. Model Artifacts
Traditional machine-learning models are persisted with Joblib and use .pkl files. Transformer models are persisted using the Hugging Face model directory format and use model.safetensors plus tokenizer/configuration files.
models/
├── svd_recommendation_model.pkl
├── content_vectorizer.pkl
├── content_similarity.pkl
├── dropout_random_forest.pkl
├── dropout_feature_columns.pkl
├── fraud/
│   ├── fraud_random_forest.pkl
│   ├── fraud_isolation_forest.pkl
│   └── fraud_feature_columns.pkl
├── hiring/
│   ├── hiring_random_forest.pkl
│   └── hiring_feature_columns.pkl
├── sentiment/
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── tokenizer_config.json
└── toxicity/
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    ├── tokenizer_config.json
    └── training_args.bin
6. Recommendation System
Provides personalized course recommendations using collaborative filtering and content similarity. The current artifact set contains the SVD model, content vectorizer, and content similarity matrix.
src/recommendation/
├── collaborative_filter.py
├── content_based.py
├── hybrid_recommendation.py
├── learning_pathway.py
├── prerequisite_validator.py
├── confidence_calculator.py
├── explanation_engine.py
├── model_loader.py
└── recommend.py
7. Dropout Prediction
Predicts learner dropout risk using engagement, activity, learning progress, login, and inactivity signals.
Model: Random Forest Classifier.
src/dropout/
├── data_cleaning.py
├── feature_engineering.py
├── train_model.py
└── predict_dropout.py
8. Fraud & Anomaly Detection
Combines supervised fraud classification with unsupervised anomaly detection.
Random Forest Classifier
Isolation Forest
Feature-column artifact for inference consistency
src/fraud/
├── preprocessing.py
├── feature_engineering.py
├── fraud_dataset.py
├── train_model.py
├── evaluate_model.py
├── fraud_feature_calculator.py
├── model_loader.py
├── predict_fraud.py
├── fraud_service.py
└── fraud_repository.py
9. Predictive Hiring
Evaluates candidate-job compatibility using experience, skill matching, domain alignment, and profile score signals.
Confirmed model inputs:
user_id
job_id
experience_years
required_experience_years
skill_match_score
experience_match_score
domain_match
profile_score
Frontend
   |
   v
Node.js /api/hiring/predict
   |
   v
Python /hiring/predict
   |
   v
Hiring Random Forest
The current documented Python integration service is configured around port 8004. Exact training metrics, dataset details, and additional model internals should be taken from the hiring model documentation rather than inferred here.
10. Sentiment Analysis
Classifies educational/community text into NEGATIVE, NEUTRAL, or POSITIVE using a DistilBERT sequence-classification model.
models/sentiment/
├── config.json
├── model.safetensors
├── tokenizer.json
└── tokenizer_config.json
Inference loads the tokenizer and model from the saved Hugging Face directory and runs the model in evaluation mode.
11. Toxicity Detection
Identifies potentially toxic or abusive community content using a DistilBERT sequence-classification model.
models/toxicity/
├── config.json
├── model.safetensors
├── tokenizer.json
├── tokenizer_config.json
├── training_args.bin
└── checkpoint-100/
The model loader loads the tokenizer and sequence-classification model from the saved directory and switches the model to evaluation mode.
12. Backend Integration
The standard application integration pattern is:
Client
  |
  v
Node.js Controller
  |
  v
Node.js Service
  |
  v
Axios / HTTP
  |
  v
Python FastAPI
  |
  v
Model Loader
  |
  v
ML Inference
  |
  v
Prediction
  |
  v
Node.js Response
  |
  v
Client
Connection failures, timeouts, validation errors, and model-service errors should be surfaced through the backend's documented error-handling path.
13. Technology Stack
Layer	Technology
Backend	Node.js, Express.js, Axios
AI APIs	Python, FastAPI
Machine Learning	Scikit-learn, Surprise
Deep Learning / NLP	PyTorch, Hugging Face Transformers
Data Processing	Pandas, NumPy
Persistence	Joblib, SafeTensors, Hugging Face save_pretrained
Database	PostgreSQL
ORM / DB access	SQLAlchemy and PostgreSQL drivers where applicable
14. Model Lifecycle
Data
  ↓
Preprocessing
  ↓
Feature Engineering
  ↓
Training
  ↓
Evaluation
  ↓
Model Artifact
  ↓
Model Loader
  ↓
FastAPI Inference
  ↓
Node.js Integration
  ↓
Application UI
Training and inference are separate concerns. A production API should load a persisted artifact rather than retraining a model for each request.
15. Local Development
15.1 Activate Environment
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& C:\Edusaas\venv\Scripts\Activate.ps1
15.2 Start Backend
cd C:\Edusaas\backend
npm start
15.3 Start Python API
uvicorn <module>:app --reload --port <port>
Use the actual module and configured port for the individual AI service. Do not assume a common port for all services.
16. Artifact Verification
Get-ChildItem C:\Edusaas\models -Recurse |
Select-Object FullName, Length, LastWriteTime
Get-ChildItem C:\Edusaas\src -Recurse -Include *.py |
Select-String -Pattern "joblib.dump|pickle.dump|torch.save|save_pretrained|model.save" 
These checks help verify that training code creates artifacts and that the artifacts exist locally.
17. Production Engineering Rules
Never train a model inside a prediction request.
Load model artifacts once and reuse them where appropriate.
Keep training and inference feature ordering identical.
Version model artifacts and associate predictions with a model version where supported.
Validate API inputs before inference.
Handle AI-service timeouts and connection failures explicitly.
Never commit database passwords, API keys, or other secrets.
Keep model artifacts synchronized with the code version that loads them.
Test model loading as part of deployment validation.
Monitor model quality and data drift after deployment.
Document known limitations rather than hiding gaps with assumptions.
18. Security and Data Governance
The repository should treat learner, candidate, discussion, and prediction data as application data requiring appropriate access controls. Secrets must be supplied through environment configuration rather than committed to source control. Security controls that are not explicitly implemented in the current source should be treated as production requirements, not as completed features.
19. Testing and Validation
Validate model artifacts before service startup.
Test Python API endpoints independently.
Test Node.js-to-Python integration.
Test invalid UUIDs and missing required fields.
Test model-service timeout and connection-refused behavior.
Validate prediction output schema.
Evaluate trained models with documented metrics before release.
20. Deployment Checklist
☐ Confirm the correct Git branch and commit.
☐ Confirm required model artifacts are present.
☐ Confirm model loaders point to the intended artifacts.
☐ Confirm environment variables are configured.
☐ Confirm PostgreSQL connectivity.
☐ Start each required Python AI service.
☐ Start the Node.js backend.
☐ Run health checks.
☐ Run representative API smoke tests.
☐ Review application and AI-service logs.
☐ Verify that no secrets or unintended local files are committed.
21. Documentation Map
Document	Purpose
README.md	Repository-level architecture, setup, model inventory, and operational overview.
Recommendation documentation	Detailed recommendation architecture, hybrid logic, artifacts, and inference.
Dropout documentation	Detailed dropout features, Random Forest training/evaluation, and inference.
Fraud documentation	Detailed fraud classification and anomaly-detection pipeline.
Sentiment documentation	Detailed DistilBERT training, inference, tokenizer, and persistence.
Toxicity documentation	Detailed toxicity training, inference, tokenizer, and persistence.
Predictive Hiring documentation	Detailed candidate-job prediction architecture and integration.
22. Important Artifact Note
Not every AI model is expected to be a .pkl file. Scikit-learn/Surprise artifacts use Joblib serialization, while Transformer models use the Hugging Face directory format with SafeTensors and tokenizer/configuration files. Therefore, the absence of a .pkl file for Sentiment or Toxicity does not indicate that the model was not saved.
23. Current Scope
The repository-level AI/ML scope documented here covers Recommendation, Dropout Prediction, Fraud & Anomaly Detection, Predictive Hiring, Sentiment Analysis, and Toxicity Detection. Exact implementation details should always be verified against the corresponding source code and module documentation.
24. Engineering Principle
Source of truth: The running code, model artifacts, database schema, and service configuration are authoritative. This README provides the system-level map and should be updated whenever architecture, APIs, model artifacts, or operational procedures change.
