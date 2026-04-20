import React from "react";
import "./Gallery.css";
import roseImg from "./img/Rose.png";
import lilyImg from "./img/lily.png";
import sunflowerImg from "./img/sunflower.png";
import bg1Img from "./img/bg1.jpeg";
import bg2Img from "./img/bg2.jpg";
import bg3Img from "./img/bg3.jpg";
import bg4Img from "./img/bg4.jpg";
import bgRoseImg from "./img/bg_rose.jpeg";

function Gallery() {
  const flowers = [
    { name: "Rose", image: roseImg, description: "Beautiful and fragrant, roses can suffer from black spot and powdery mildew." },
    { name: "Lily", image: lilyImg, description: "Elegant lilies are prone to botrytis blight and lily mosaic virus." },
    { name: "Sunflower", image: sunflowerImg, description: "Cheerful sunflowers may face downy mildew and rust diseases." },
    { name: "Tulip", image: bg1Img, description: "Vibrant tulips can be affected by tulip fire disease and botrytis blight." },
    { name: "Daisy", image: bg2Img, description: "Delicate daisies are susceptible to powdery mildew and leaf spot." },
    { name: "Orchid", image: bg3Img, description: "Exotic orchids may encounter root rot and fungal infections." },
    { name: "Carnation", image: bg4Img, description: "Fragrant carnations can develop rust and bacterial wilt." },
    { name: "Garden Rose", image: bgRoseImg, description: "Classic garden roses are vulnerable to aphids and fungal diseases." },
    { name: "Healthy Bloom", image: bg1Img, description: "A healthy flower showcases vibrant colors and strong petals." }
  ];

  return (
    <div className="gallery component__space" id="Gallery">
      <div className="container">
        <div className="heading">
          <h1 className="heading">Flower Gallery</h1>
          <p className="heading p__color">Explore common flowers and their potential diseases</p>
          <p className="heading p__color">Learn to identify healthy blooms and common issues</p>
        </div>
        <div className="row">
          {flowers.map((flower, index) => (
            <div key={index} className="col__3 gallery__item">
              <div className="gallery__card">
                <img src={flower.image} alt={flower.name} className="gallery__img" />
                <h3>{flower.name}</h3>
                <p>{flower.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Gallery;