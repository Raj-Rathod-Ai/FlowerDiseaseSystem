import React from "react";
import "./Gallery.css";
import roseImg from "./img/Rose.png";
import lilyImg from "./img/lily.png";
import sunflowerImg from "./img/sunflower.png";

function Gallery() {
  const flowers = [
    { name: "Rose", image: roseImg, description: "Beautiful and fragrant, roses can suffer from black spot and powdery mildew." },
    { name: "Lily", image: lilyImg, description: "Elegant lilies are prone to botrytis blight and lily mosaic virus." },
    { name: "Sunflower", image: sunflowerImg, description: "Cheerful sunflowers may face downy mildew and rust diseases." }
  ];

  return (
    <div className="gallery component__space" id="Gallery">
      <div className="container">
        <div className="heading">
          <h1 className="heading">Flower Gallery</h1>
          <p className="heading p__color">Explore common flowers and their potential diseases</p>
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