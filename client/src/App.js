import React, { useState } from "react";
import About from "./About";
import "./App.css";
import Comments from "./Comments";
import FAQ from "./FAQ";
import Footer from "./Footer";
import Gallery from "./Gallery";
import Home from "./Home";
import Layout from "./Layout";
import Services from "./Services";

function App() {
  const [activeSection, setActiveSection] = useState("Home");

  const renderActiveSection = () => {
    switch (activeSection) {
      case "Home":
        return <Home setActiveSection={setActiveSection} />;
      case "About":
        return <About />;
      case "Services":
        return <Services setActiveSection={setActiveSection} />;
      case "FAQ":
        return <FAQ />;
      case "Gallery":
        return <Gallery />;
      case "Comments":
        return <Comments />;
      default:
        return <Home setActiveSection={setActiveSection} />;
    }
  };

  return (
    <Layout setActiveSection={setActiveSection} activeSection={activeSection}>
      {renderActiveSection()}
      <Footer setActiveSection={setActiveSection} />
    </Layout>
  );
}

export default App;
