import React from "react";
import "./Home.css";

function Home({ setActiveSection }) {
  const handleGetStarted = () => {
    setActiveSection("Services");
  };

  return (
    <div className="home" id="Home">
      <div className="hero__bg">
        <div className="container">
          <div className="home__content">
            <div className="home__meta">
              <h2 className="home__text pz__10">AI-Powered Flower Disease Detection</h2>
              <h3 className="home__text sweet pz__10">
                Identify flower species and detect diseases instantly with advanced deep learning.
              </h3>
              <p className="home__subtext">
                FloraScan helps gardeners and florists keep blooms healthy with fast image analysis, species recognition, and expert recovery guidance.
              </p>
              <div className="home__actions">
                <button className="home__btn" onClick={handleGetStarted}>
                  Start Detection
                </button>
                <button className="home__btn home__btn--ghost" onClick={() => setActiveSection("Comments")}>Share Feedback</button>
              </div>
              <div className="home__features">
                <div className="feature__card">
                  <span>🌿</span>
                  <strong>Fast results</strong>
                  <p>Upload a photo and get species + health status in seconds.</p>
                </div>
                <div className="feature__card">
                  <span>🔍</span>
                  <strong>Smart diagnosis</strong>
                  <p>AI inspects leaf patterns, discoloration and disease markers automatically.</p>
                </div>
                <div className="feature__card">
                  <span>💡</span>
                  <strong>Actionable tips</strong>
                  <p>Receive practical care advice to keep your flowers strong and vibrant.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
