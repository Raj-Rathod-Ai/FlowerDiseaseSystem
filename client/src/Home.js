import React from "react";
import "./Home.css";

function Home() {
  // fixed Header
  window.addEventListener("scroll", function () {
    const header = document.querySelector(".header");
    header.classList.toggle("active", window.scrollY > 0);
  });
  return (
    <div className="home" id="Home">
      <div className="hero__bg">
        <div className="header d__flex align__items__center pxy__30">
          <div className="brand">
            <img src="/logo.svg" alt="FloraGuard Logo" className="brand__logo" />
            <span className="brand__name">FloraScan</span>
          </div>
          <div className="navigation pxy__30">
            <ul className="navbar d__flex">
              <a href="#Home">
                <li className="nav__items mx__15">Home</li>
              </a>
              <a href="#About">
                <li className="nav__items mx__15">About</li>
              </a>
              <a href="#Services">
                <li className="nav__items mx__15">Detect</li>
              </a>
              <a href="#Gallery">
                <li className="nav__items mx__15">Gallery</li>
              </a>
            </ul>
          </div>
        </div>
        <div className="container">
          <div className="home__content">
            <div className="home__meta">
              <h2 className="home__text pz__10">AI-Powered Flower Disease Detection</h2>
              <h3 className="home__text sweet pz__10">
                Identify flower species and detect diseases instantly with advanced deep learning.
              </h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
