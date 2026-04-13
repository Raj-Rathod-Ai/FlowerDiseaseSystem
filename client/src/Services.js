import React, { useState, useRef, useCallback } from "react";
import "./Services.css";

const API_URL = "https://flowerdiseasesystem.onrender.com";

const FLOWER_EMOJIS = { rose: "🌹", lily: "🌷", sunflower: "🌻" };
const HEALTH_CONFIG = {
  healthy:  { emoji: "✅", color: "#4caf50", label: "Healthy" },
  diseased: { emoji: "⚠️", color: "#f44336", label: "Diseased" },
};

function ConfidenceBar({ label, value, color }) {
  return (
    <div className="conf__bar__wrap">
      <div className="conf__bar__label">
        <span>{label}</span>
        <span style={{ color }}>{value}%</span>
      </div>
      <div className="conf__bar__bg">
        <div
          className="conf__bar__fill"
          style={{ width: `${value}%`, background: color }}
        />
      </div>
    </div>
  );
}

function Service() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageSrc, setImageSrc]         = useState("");
  const [isDragging, setIsDragging]     = useState(false);
  const [isLoading, setIsLoading]       = useState(false);
  const [result, setResult]             = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const fileInputRef = useRef(null);

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
    if (!selectedFile) { setErrorMessage("Please upload an image first."); return; }
    setErrorMessage("");
    setIsLoading(true);
    setResult(null);
    const formData = new FormData();
    formData.append("file", selectedFile);
    try {
      const response = await fetch(`${API_URL}/image/upload`, { method: "POST", body: formData });
      const data = await response.json();
      if (data.error) { setErrorMessage(data.error); }
      else { setResult(data); }
    } catch (err) {
      setErrorMessage("Network error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setImageSrc("");
    setResult(null);
    setErrorMessage("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const healthCfg = result ? (HEALTH_CONFIG[result.health] || { emoji: "❓", color: "#aaa", label: result.health }) : null;

  return (
    <div className="service component__space" id="Services">
      <div className="heading">
        <h1 className="heading">Flower Disease Detection</h1>
        <p className="heading p__color">Upload a flower image to identify species and detect disease instantly</p>
      </div>

      <div className="container">
        <div className="detect__grid">

          {/* LEFT — Upload panel */}
          <div className="upload__panel">
            {/* Drop zone */}
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
                  <div className="preview__overlay">
                    <span>Click to change</span>
                  </div>
                </div>
              ) : (
                <div className="drop__content">
                  <div className="drop__icon">🌸</div>
                  <p className="drop__title">Drag & drop your image here</p>
                  <p className="drop__sub">or click to browse</p>
                  <p className="drop__hint">Supports JPG, PNG, WEBP</p>
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
                {isLoading ? (
                  <><span className="btn__spinner" /> Analyzing...</>
                ) : (
                  <><span>🔍</span> Analyze Flower</>
                )}
              </button>
              {selectedFile && (
                <button className="btn__reset" onClick={handleReset}>
                  ✕ Reset
                </button>
              )}
            </div>

            {/* Loading state */}
            {isLoading && (
              <div className="analysis__box">
                <div className="loader-ring" />
                <p className="analysis__card">Analyzing flower health with AI...</p>
                <p className="analysis__sub">This may take a few seconds</p>
              </div>
            )}

            {/* Error */}
            {errorMessage && (
              <div className="error__box">
                <span>⚠️</span> {errorMessage}
              </div>
            )}
          </div>

          {/* RIGHT — Results panel */}
          <div className="results__panel">
            {!result && !isLoading && (
              <div className="results__placeholder">
                <div className="placeholder__icon">🌿</div>
                <p>Your analysis results will appear here</p>
                <p className="placeholder__sub">Upload an image and click Analyze</p>
              </div>
            )}

            {result && (
              <div className="result__card">
                <h2 className="result__title">Analysis Complete</h2>

                {/* Species */}
                <div className="result__section">
                  <div className="result__header">
                    <span className="result__emoji">{FLOWER_EMOJIS[result.species] || "🌸"}</span>
                    <div>
                      <p className="result__label">Flower Species</p>
                      <p className="result__value" style={{ textTransform: "capitalize" }}>
                        {result.species}
                      </p>
                    </div>
                    <span className="result__conf">{result.species_confidence}%</span>
                  </div>
                  {result.species_all && Object.entries(result.species_all).map(([name, val]) => (
                    <ConfidenceBar
                      key={name}
                      label={name.charAt(0).toUpperCase() + name.slice(1)}
                      value={val}
                      color={name === result.species ? "#6ec26e" : "#4a4a4a"}
                    />
                  ))}
                </div>

                {/* Divider */}
                <div className="result__divider" />

                {/* Health */}
                <div className="result__section">
                  <div className="result__header">
                    <span className="result__emoji">{healthCfg.emoji}</span>
                    <div>
                      <p className="result__label">Health Status</p>
                      <p className="result__value" style={{ color: healthCfg.color }}>
                        {healthCfg.label}
                      </p>
                    </div>
                    <span className="result__conf" style={{ color: healthCfg.color }}>
                      {result.health_confidence}%
                    </span>
                  </div>
                  {result.health_all && Object.entries(result.health_all).map(([name, val]) => (
                    <ConfidenceBar
                      key={name}
                      label={name.charAt(0).toUpperCase() + name.slice(1)}
                      value={val}
                      color={name === "healthy" ? "#4caf50" : name === "diseased" ? "#f44336" : "#aaa"}
                    />
                  ))}
                </div>

                {/* Advice */}
                <div className={`advice__box ${result.health === "healthy" ? "advice__healthy" : "advice__diseased"}`}>
                  {result.health === "healthy" ? (
                    <p>✅ Your flower appears healthy! Keep up with regular watering and good drainage.</p>
                  ) : (
                    <p>⚠️ Disease detected. Consider removing affected leaves, improving air circulation, and consulting a plant specialist.</p>
                  )}
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
