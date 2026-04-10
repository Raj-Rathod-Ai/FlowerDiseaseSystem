import React, { useState } from "react";
import "./Services.css";

function Service() {
  const [selectedFile, setSelectedFile] = useState();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [predictedFlowerDisease, setPredictedFlowerDisease] = useState("");
  const [predictedFlower, setPredictedFlower] = useState("");
  const [imageSrc, setImageSrc] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const changeHandler = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setErrorMessage("");
    setIsSubmitted(false);
    setIsLoading(false);

    const reader = new FileReader();
    reader.onload = function (event) {
      setImageSrc(event.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmission = () => {
    if (!selectedFile) {
      setErrorMessage("Please upload an image before submitting.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setIsSubmitted(false);

    const formData = new FormData();
    formData.append("file", selectedFile);

    const API_URL = "https://flowerdiseasesystem.onrender.com";

    fetch(`${API_URL}/image/upload`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false);
        if (result.error) {
          setErrorMessage(result.error);
          setIsSubmitted(false);
          return;
        }

        console.log("Success:", result);
        setPredictedFlower(result.species || "Unknown flower");
        setPredictedFlowerDisease(result.health || "Unknown health status");
        setErrorMessage("");
        setIsSubmitted(true);
      })
      .catch((error) => {
        console.error("Error React:", error);
        setErrorMessage("Unable to process image. Please try again.");
        setIsSubmitted(false);
        setIsLoading(false);
      });
  };

  return (
    <>
      <div className="service component__space" id="Services">
        <div className="heading">
          <h1 className="heading">Our Service</h1>
          <p className="heading p__color">Detect the Flower and Disease it has</p>
          <p className="heading p__color"></p>
        </div>

        <div className="container">
          <div className="row">
            {imageSrc && (
              <img src={imageSrc} alt="Uploaded preview" className="flower" />
            )}
            <div className="col__3">
              <input
                type="file"
                name="File"
                id="fileUp"
                hidden
                onChange={changeHandler}
              />
              <label htmlFor="fileUp">
                <div className="service__box pointer">
                  <div className="icon">
                    <svg
                      stroke="currentColor"
                      fill="none"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      height="1em"
                      width="1em"
                      align="center"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                      <polyline points="2 17 12 22 22 17"></polyline>
                      <polyline points="2 12 12 17 22 12"></polyline>
                    </svg>
                  </div>
                  <div className="service__meta">
                    <h1 className="service__text">Upload Image</h1>
                    <p className="p service__text p__color">
                      Upload the Image of the Flower that has
                    </p>
                    <p className="p service__text p__color">
                      to be Tested for Detection.
                    </p>
                  </div>
                </div>
              </label>
              <button
                onClick={handleSubmission}
                disabled={!selectedFile || isLoading}
                style={{
                  fontSize: 20,
                  backgroundColor: selectedFile && !isLoading ? "#f9004d" : "#ccc",
                  color: selectedFile && !isLoading ? "#ffffff" : "#666",
                  padding: "15px 32px",
                  margin: 0,
                  border: "none",
                  borderRadius: "4px",
                  cursor: selectedFile && !isLoading ? "pointer" : "not-allowed",
                }}
              >
                {isLoading ? "Analyzing..." : "Submit"}
              </button>
              {isLoading && (
                <div className="analysis__box">
                  <div className="loader-ring" />
                  <p className="analysis__card">Checking the image and analyzing flower health...</p>
                </div>
              )}
              {errorMessage && (
                <p style={{ color: "#ffcccb", textAlign: "center", marginTop: 16 }}>
                  {errorMessage}
                </p>
              )}
              {isSubmitted && !errorMessage && !isLoading ? (
                <div className="prediction__card">
                  <h1
                    style={{
                      textAlign: "center",
                      paddingTop: 20,
                      fontSize: 30,
                    }}
                  >
                    Prediction
                  </h1>
                  <div
                    style={{
                      textAlign: "left",
                      padding: "20px 24px",
                      backgroundColor: "rgba(249, 0, 77, 0.12)",
                      borderRadius: "14px",
                      color: "#f3f9f1",
                      marginTop: 16,
                    }}
                  >
                    <p style={{ fontSize: 20, margin: "10px 0" }}>
                      Flower Name :- <strong>{predictedFlower}</strong>
                    </p>
                    <p style={{ fontSize: 20, margin: "10px 0" }}>
                      Disease Status :- <strong>{predictedFlowerDisease}</strong>
                    </p>
                  </div>
                </div>
              ) : null}
              {/* </div> */}
            </div>
          </div>
        </div>
      </div>
    </>

  );
}


export default Service;
