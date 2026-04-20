import React, { useState, useRef, useCallback } from "react";
import "./Services.css";

const API_URL = process.env.REACT_APP_API_URL || "https://flowerdiseasesystem.onrender.com";

const MAX_UPLOAD_ATTEMPTS = 3;

const HEALTHY_SUGGESTIONS = [
  "🌱 Keep up the great care! Your flower is thriving with proper watering and sunlight.",
  "💧 Maintain consistent watering - not too much, not too little. Your plant is happy!",
  "☀️ Continue providing adequate sunlight. Healthy plants need 6-8 hours of light daily.",
  "🌿 Your plant looks fantastic! Keep monitoring for pests and maintain good air circulation.",
  "🌸 Excellent care! Consider fertilizing lightly during the growing season to boost health.",
  "💚 Your flower is in perfect condition. Keep the soil well-draining to prevent root rot.",
  "🌞 Great job! Healthy plants respond well to regular leaf cleaning to remove dust.",
  "🌺 Your plant is flourishing! Rotate it occasionally for even growth on all sides."
];

const DISEASED_SUGGESTIONS = [
  "🩺 Isolate the plant to prevent disease spread to other flowers in your garden.",
  "✂️ Carefully remove all affected leaves and dispose of them away from your garden.",
  "💨 Improve air circulation by spacing plants apart and avoiding overcrowding.",
  "🚫 Stop watering from above - water at soil level to keep leaves dry.",
  "🧴 Consider using a fungicide appropriate for your plant type after identifying the issue.",
  "🔍 Check for pests on the undersides of leaves and treat accordingly if found.",
  "🌡️ Ensure proper temperature - most plants prefer 65-75°F (18-24°C).",
  "🦠 Clean your gardening tools between plants to prevent cross-contamination."
];

const FLOWER_EMOJIS = { rose: "🌹", lily: "🌷", sunflower: "🌻" };
const HEALTH_CONFIG = {
  healthy: { emoji: "✅", color: "#4caf50", label: "Healthy", bg: "rgba(76,175,80,0.1)", border: "rgba(76,175,80,0.25)" },
  diseased: { emoji: "⚠️", color: "#f44336", label: "Diseased", bg: "rgba(244,67,54,0.1)", border: "rgba(244,67,54,0.25)" },
};

/* ── Get random suggestion ── */
function getRandomSuggestion(isHealthy) {
  const suggestions = isHealthy ? HEALTHY_SUGGESTIONS : DISEASED_SUGGESTIONS;
  return suggestions[Math.floor(Math.random() * suggestions.length)];
}

const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  for (let attempt = 1; attempt <= MAX_UPLOAD_ATTEMPTS; attempt += 1) {
    try {
      const res = await fetch(`${API_URL}/image/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Server error (${res.status})${errorText ? `: ${errorText}` : ""}`);
      }

      return await res.json();
    } catch (err) {
      if (attempt === MAX_UPLOAD_ATTEMPTS) {
        throw err;
      }
      console.log("Retrying upload...", attempt, err.message);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }
  }

  throw new Error("Server not responding");
};

/* ── Skeleton placeholder while loading ── */
function ResultSkeleton() {
  return (
    <div className="skeleton__card">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="skeleton__line" style={{ width: i % 2 === 0 ? "60%" : "100%" }} />
      ))}
    </div>
  );
}

function Service({ setActiveSection }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageSrc, setImageSrc] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isWakingUp, setIsWakingUp] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisStep, setAnalysisStep] = useState(0);
  const [showReviewPrompt, setShowReviewPrompt] = useState(false);
  const [hasCompletedFirstAnalysis, setHasCompletedFirstAnalysis] = useState(false);
  const fileInputRef = useRef(null);

  const STEPS = [
    "Uploading image…",
    "Preprocessing & normalising…",
    "Running AI inference…",
    "Calibrating confidence scores…",
  ];

  const processFile = (file) => {
    if (!file || !file.type.startsWith("image/")) {
      setErrorMessage("Please upload a valid image file (jpg, png, webp).");
      return;
    }
    setSelectedFile(file);
    setErrorMessage("");
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setImageSrc(e.target.result);
    reader.readAsDataURL(file);
  };

  const changeHandler = (e) => processFile(e.target.files[0]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    processFile(e.dataTransfer.files[0]);
  }, []);

  const onDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = () => setIsDragging(false);

  const handleSubmission = async () => {
    if (!selectedFile) {
      setErrorMessage("Please upload an image first.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setIsWakingUp(true);
    setResult(null);
    setAnalysisStep(0);

    const stepTimer = setInterval(() =>
      setAnalysisStep((s) => (s < STEPS.length - 1 ? s + 1 : s)), 1200);

    try {
      const data = await uploadImage(selectedFile);
      if (data.error) {
        setErrorMessage(data.error);
      } else {
        setResult(data);
        if (!hasCompletedFirstAnalysis) {
          setTimeout(() => {
            setShowReviewPrompt(true);
            setHasCompletedFirstAnalysis(true);
          }, 2000);
        }
      }
    } catch (err) {
      const lower = err.message?.toLowerCase() || "";
      if (lower.includes("502") || lower.includes("server error")) {
        setErrorMessage("Server is waking up or unavailable. Please wait 30 seconds and try again.");
      } else {
        setErrorMessage("Network error. Please check your connection and try again.");
      }
    } finally {
      clearInterval(stepTimer);
      setIsLoading(false);
      setIsWakingUp(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setImageSrc("");
    setResult(null);
    setErrorMessage("");
    setAnalysisStep(0);
    setShowReviewPrompt(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleReviewResponse = (response) => {
    setShowReviewPrompt(false);
    if (response === "yes") {
      setActiveSection("Comments");
    }
  };

  const healthCfg = result
    ? (HEALTH_CONFIG[result.health] || { emoji: "❓", color: "#aaa", label: result.health, bg: "transparent", border: "#aaa" })
    : null;

  return (
    <div className="service component__space" id="Services">
      <div className="heading">
        <h1 className="heading">Flower Disease Detection</h1>
        <p className="heading p__color">
          Upload a flower image to identify species and detect disease instantly
        </p>
      </div>

      <div className="container">
        <div className="detect__grid">

          {/* ── LEFT: Upload panel ── */}
          <div className="upload__panel">
            <div
              className={`drop__zone ${isDragging ? "dragging" : ""} ${selectedFile ? "has__file" : ""}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={changeHandler}
              />
              {imageSrc ? (
                <div className="preview__wrap">
                  <img src={imageSrc} alt="Preview" className="preview__img" />
                  <div className="preview__overlay"><span>Click to change</span></div>
                </div>
              ) : (
                <div className="drop__content">
                  <div className="drop__icon">🌸</div>
                  <p className="drop__title">Drag &amp; drop your image here</p>
                  <p className="drop__sub">or click to browse</p>
                  <p className="drop__hint">Supports JPG · PNG · WEBP</p>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="btn__row">
              <button
                className="btn__detect"
                onClick={handleSubmission}
                disabled={!selectedFile || isLoading}
              >
                {isLoading
                  ? <><span className="btn__spinner" /> Analyzing…</>
                  : <><span>🔍</span> Analyze Flower</>}
              </button>
              {selectedFile && (
                <button className="btn__reset" onClick={handleReset}>✕ Reset</button>
              )}
            </div>

            {/* Loading progress */}
            {isLoading && (
              <div className="analysis__box">
                <div className="loader-ring" />
                <p className="analysis__card">{STEPS[analysisStep]}</p>
                <div className="analysis__steps">
                  {STEPS.map((_, i) => (
                    <div
                      key={i}
                      className={`analysis__dot ${i <= analysisStep ? "analysis__dot--active" : ""}`}
                    />
                  ))}
                </div>
              </div>
            )}

            {isWakingUp && !errorMessage && isLoading && (
              <div className="wakeup__message">
                <span>⏳</span> Server waking up... first request may take up to 30 seconds.
              </div>
            )}

            {errorMessage && (
              <div className="error__box">
                <span>⚠️</span> {errorMessage}
              </div>
            )}
          </div>

          {/* ── RIGHT: Results panel ── */}
          <div className="results__panel">
            {!result && !isLoading && (
              <div className="results__placeholder">
                <div className="placeholder__icon">🌿</div>
                <p>Your analysis results will appear here</p>
                <p className="placeholder__sub">Upload an image and click Analyze</p>
              </div>
            )}

            {isLoading && <ResultSkeleton />}

            {result && (
              <div className="result__card">
                <div className="result__title__row">
                  <h2 className="result__title">Analysis Complete</h2>
                  <span className="result__check">✓</span>
                </div>

                {/* Species section */}
                <div className="result__section">
                  <div className="result__header">
                    <span className="result__emoji">{FLOWER_EMOJIS[result.species] || "🌸"}</span>
                    <div>
                      <p className="result__label">Flower Species</p>
                      <p className="result__value" style={{ textTransform: "capitalize" }}>
                        {result.species}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="result__divider" />

                {/* Health section */}
                <div className="result__section">
                  <div className="result__header">
                    <span className="result__emoji">{healthCfg.emoji}</span>
                    <div>
                      <p className="result__label">Health Status</p>
                      <p className="result__value" style={{ color: healthCfg.color }}>
                        {healthCfg.label}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Special message for roses */}
                {result.message && (
                  <div className="result__section">
                    <div className="result__header">
                      <span className="result__emoji">🌹</span>
                      <div>
                        <p className="result__label">Special Note</p>
                        <p className="result__value" style={{ color: "#e91e63", fontStyle: "italic" }}>
                          {result.message}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {result.message && <div className="result__divider" />}

                {/* Advice box */}
                <div
                  className="advice__box"
                  style={{ background: healthCfg.bg, borderColor: healthCfg.border }}
                >
                  <p>{getRandomSuggestion(result.health === "healthy")}</p>
                </div>
              </div>
            )}

            {/* Review Prompt */}
            {showReviewPrompt && (
              <div className="review__prompt">
                <div className="review__prompt__content">
                  <div className="review__prompt__icon">⭐</div>
                  <h3>Help Us Improve!</h3>
                  <p>Would you like to share your feedback or suggest improvements to make FloraScan better?</p>
                  <div className="review__prompt__buttons">
                    <button
                      className="btn__review btn__review--yes"
                      onClick={() => handleReviewResponse("yes")}
                    >
                      💬 Yes, I'd like to help
                    </button>
                    <button
                      className="btn__review btn__review--no"
                      onClick={() => handleReviewResponse("no")}
                    >
                      🙏 Maybe later
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Service;
