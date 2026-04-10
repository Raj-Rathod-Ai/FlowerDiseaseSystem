import React from "react";
import "./About.css";
import Detect from "./img/d2.jpg";
function About() {
  //  Up To Top Btn
  window.addEventListener("scroll", function () {
    const upToTop = document.querySelector("a.bottom__to__top");
    upToTop.classList.toggle("active", window.scrollY > 0);
  });
  return (
    <div className="about component__space" id="About">
      <div className="container">
        <div className="row">
          <div className="col__2">
            <img src={Detect} alt="" className="about__img" />
          </div>
          <div className="col__2">
            <h1 className="about__heading">Detect Disease Today</h1>
            <div className="about__meta">
              <p className="about__text p__color">
                Flowers are beautiful and delicate, but they can fall victim to various diseases that threaten their health and bloom. Common flower diseases include fungal infections like powdery mildew, rust, and black spot, bacterial issues such as bacterial blight, and viral diseases that can cause discoloration and deformities. Environmental factors like humidity, poor soil quality, and inadequate watering often exacerbate these problems.
              </p>
              <p className="about__text p__color">
                Our AI-powered detection system uses deep learning to analyze flower images and identify both the species (such as roses, lilies, and sunflowers) and their health status. Early detection is crucial for effective treatment, preventing the spread of diseases and ensuring vibrant gardens.
              </p>
              <p className="about__text p__color">
                To prevent flower diseases, maintain good plant hygiene by removing infected leaves, ensuring proper spacing for air circulation, and using organic fungicides when necessary. Regular monitoring and our detection tool can help gardeners take proactive steps to keep their flowers thriving.
              </p>
              <div className="about__button d__flex align__items__center">
                <a href="#Services">
                  <button className="about btn pointer">Try Detection</button>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* UP TO TOP BTN */}
      <div className="up__to__top__btn">
        <a href="/" className="bottom__to__top">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            fill="currentColor"
            className="bi bi-chevron-up white"
            viewBox="0 0 16 16"
          >
            <path
              fillRule="evenodd"
              d="M7.646 4.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1-.708.708L8 5.707l-5.646 5.647a.5.5 0 0 1-.708-.708l6-6z"
            />
          </svg>
        </a>
      </div>
    </div>
  );
}

export default About;
