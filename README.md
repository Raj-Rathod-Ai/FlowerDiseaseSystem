# 🌸 Flower Disease Recognition using Deep Learning

## 📌 Project Overview
This project builds an **end-to-end flower recognition and disease detection system** using deep learning.  
Given an input image, the model predicts:
- **Flower species** (lily, rose, sunflower)
- **Health status** (healthy or diseased)

The system is designed for **quick screening and early disease detection**, reducing reliance on manual inspection.


## ⚙️ Data & Preprocessing
- Image dataset organized by **species** and **health condition**
- Invalid and corrupted images removed
- Images standardized to RGB format and resized
- **Targeted data augmentation** applied only to diseased images to address class imbalance


## 🧠 Modeling Approach
- **Transfer Learning** with a pre-trained **ResNet50V2** backbone
- **Multi-task learning architecture**:
  - Shared CNN feature extractor
  - Two output heads:
    - Species classification (3 classes)
    - Disease detection (2 classes)
- Two-phase training:
  - Frozen backbone training
  - Fine-tuning top layers with a low learning rate


## 📊 Results
- **Species classification accuracy:** ~84%
- **Disease detection accuracy:** ~98%
- Strong recall for diseased class, suitable for screening use cases
- Transfer learning significantly outperformed custom CNN baselines


## 🚀 Deployment
This project is a **full-stack app** with:
- `backend/` running a Flask API and serving the trained Keras model
- `client/` running a React frontend that uploads images to the backend

### Run locally
1. Backend
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
   - `python app.py`
2. Frontend
   - `cd client`
   - `npm install`
   - `npm start`

The frontend uses the `package.json` proxy `http://localhost:5000/` and the backend defaults to port `5000`, so local requests should work without additional configuration.

If you want to point the frontend to a different backend URL, set `REACT_APP_API_URL=http://your-backend-url` before running `npm start`.

### Useful links
- GitHub: https://github.com/Raj-Rathod-Ai/FlowerDiseaseSystem
- LinkedIn: https://linkedin.com/in/raj-rathod-ai

### Recommended free deployment
For this stack, the best approach is:
- **Railway**: easiest free option for hosting the Flask backend and static React app in separate services
- **Render**: also supports a free Flask service, with the React frontend deployed separately as static sites

### Suggested deployment flow
1. Deploy `backend/` on Railway or Render as a Python app.
2. Build `client/` with `npm run build` and deploy the generated static site on Vercel, Netlify, or Render.
3. Update the frontend API URL if needed to point at the deployed backend.

### Why these platforms?
- Railway and Render support Flask apps directly on free tiers.
- Vercel/Netlify are ideal for hosting the React frontend as static files.
- This setup is the cleanest fit for your current `client` + `backend` repo structure.

## 📁 Folder Structure
```
Flower-Disease-Detection-using-Deep-Learning-main/
├── backend/          # Flask API and model serving
├── client/           # React frontend application
├── manifests/        # label map and dataset metadata files
├── models/           # trained Keras model files
└── README.md         # project documentation
```

### Folder details
- `backend/`: contains the Flask app and API endpoint for image upload and prediction.
- `client/`: houses the React app, UI components, and CSS styling for the web interface.
- `manifests/`: stores supporting JSON and CSV files used for label mapping and dataset organization.
- `models/`: holds saved model weights used by the backend for inference.

## 🛠️ Tech Stack
- **Programming Language:** Python  
- **Deep Learning Framework:** TensorFlow / Keras  
- **Image Processing:** OpenCV, Albumentations  
- **Backend / API:** Flask  
- **Frontend:** React  
- **Development & Experimentation:** Jupyter Notebook  


## 📌 Key Takeaway
This project demonstrates how **deep learning and transfer learning** can be applied to real-world image classification problems, handling **class imbalance**, enabling **multi-task predictions**, and supporting **deployable ML systems**.
