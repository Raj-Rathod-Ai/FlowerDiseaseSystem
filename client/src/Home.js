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
              <button className="home__btn" onClick={handleGetStarted}>
                Start Detection
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
