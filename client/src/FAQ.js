import React from "react";
import "./FAQ.css";

function FAQ() {
    const faqs = [
        {
            question: "How does the flower disease detection work?",
            answer: "Our AI-powered system uses a deep learning model trained on thousands of flower images to identify species and detect diseases. Simply upload a clear photo of your flower, and our algorithm will analyze it within seconds to provide species identification and health assessment."
        },
        {
            question: "What types of flowers can the app identify?",
            answer: "Currently, our system can identify roses, lilies, and sunflowers. We're continuously expanding our database to include more flower species. The app will clearly indicate when it cannot confidently identify a flower."
        },
        {
            question: "How accurate is the disease detection?",
            answer: "Our model achieves high accuracy for common diseases affecting these flowers. However, accuracy can vary based on image quality, lighting, and the specific disease. We recommend using this tool as a helpful guide rather than a definitive diagnosis."
        },
        {
            question: "What should I do if the app gives incorrect results?",
            answer: "If you believe the identification or health assessment is wrong, try taking a clearer photo with better lighting and different angles. You can also consult with a local plant specialist or extension service for professional diagnosis."
        },
        {
            question: "Is my uploaded image stored or shared?",
            answer: "No, your images are processed temporarily for analysis and are not stored on our servers or shared with third parties. We prioritize your privacy and data security."
        },
        {
            question: "What image formats are supported?",
            answer: "The app supports common image formats including JPG, JPEG, PNG, WEBP, BMP, and JFIF. Images should be clear, well-lit, and show the flower clearly for best results."
        },
        {
            question: "Why does the app show different confidence levels?",
            answer: "Confidence levels indicate how certain our AI model is about its prediction. Higher confidence means the model is more sure, while lower confidence suggests the result is less certain. We've implemented temperature scaling to provide more realistic confidence estimates."
        },
        {
            question: "Can I use this app for commercial purposes?",
            answer: "This tool is designed for educational and personal use. For commercial applications or large-scale plant health monitoring, please consult with agricultural professionals or consider our enterprise solutions."
        },
        {
            question: "What should I do if my plant shows signs of disease?",
            answer: "If disease is detected, follow the specific care suggestions provided. Common steps include isolating the plant, improving air circulation, adjusting watering practices, and consulting a plant specialist. Prevention is always better than cure!"
        },
        {
            question: "How often should I check my plants?",
            answer: "Regular monitoring is key to plant health. We recommend checking your plants weekly for any changes in appearance, and using our app whenever you notice something unusual or want to confirm plant health."
        }
    ];

    return (
        <div className="faq component__space" id="FAQ">
            <div className="heading">
                <h1 className="heading">Frequently Asked Questions</h1>
                <p className="heading p__color">
                    Everything you need to know about our flower disease detection system
                </p>
            </div>

            <div className="container">
                <div className="faq__grid">
                    {faqs.map((faq, index) => (
                        <div key={index} className="faq__item">
                            <div className="faq__question">
                                <span className="faq__icon">❓</span>
                                <h3>{faq.question}</h3>
                            </div>
                            <div className="faq__answer">
                                <p>{faq.answer}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default FAQ;