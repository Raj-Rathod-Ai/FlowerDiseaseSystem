import React, { useState, useEffect } from "react";
import "./Comments.css";

const BASE_API_URL = process.env.REACT_APP_API_URL || "https://flowerdiseasesystem.onrender.com";

function Comments() {
    const [comments, setComments] = useState([]);
    const [improvements, setImprovements] = useState([]);
    const [activeTab, setActiveTab] = useState("comments");
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        type: "comment",
        name: "",
        email: "",
        content: ""
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    useEffect(() => {
        fetchComments();
        fetchImprovements();
    }, []);

    const fetchComments = async () => {
        try {
            const response = await fetch(`${BASE_API_URL}/comments?type=comment`);
            const data = await response.json();
            setComments(data);
        } catch (error) {
            console.error("Error fetching comments:", error);
        }
    };

    const fetchImprovements = async () => {
        try {
            const response = await fetch(`${BASE_API_URL}/comments?type=improvement`);
            const data = await response.json();
            setImprovements(data);
        } catch (error) {
            console.error("Error fetching improvements:", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage("");

        try {
            const response = await fetch(`${BASE_API_URL}/comments`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage("Thank you for your feedback!");
                setFormData({ type: "comment", name: "", email: "", content: "" });
                setShowForm(false);

                // Refresh the appropriate list
                if (formData.type === "comment") {
                    fetchComments();
                } else {
                    fetchImprovements();
                }
            } else {
                setMessage(data.error || "Error submitting feedback");
            }
        } catch (error) {
            setMessage("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    };

    return (
        <div className="comments component__space" id="Comments">
            <div className="heading">
                <h1 className="heading">Community Feedback</h1>
                <p className="heading p__color">
                    Share your thoughts and help us improve the flower disease detection experience
                </p>
            </div>

            <div className="container">
                {/* Tab Navigation */}
                <div className="comments__tabs">
                    <button
                        className={`comments__tab ${activeTab === "comments" ? "active" : ""}`}
                        onClick={() => setActiveTab("comments")}
                    >
                        💬 Comments ({comments.length})
                    </button>
                    <button
                        className={`comments__tab ${activeTab === "improvements" ? "active" : ""}`}
                        onClick={() => setActiveTab("improvements")}
                    >
                        💡 Improvement Suggestions ({improvements.length})
                    </button>
                </div>

                {/* Add Feedback Button */}
                <div className="comments__actions">
                    <button
                        className="btn__add__feedback"
                        onClick={() => setShowForm(!showForm)}
                    >
                        {showForm ? "✕ Cancel" : "➕ Share Feedback"}
                    </button>
                </div>

                {/* Feedback Form */}
                {showForm && (
                    <div className="feedback__form__container">
                        <form className="feedback__form" onSubmit={handleSubmit}>
                            <h3>Share Your Feedback</h3>

                            <div className="form__group">
                                <label>Type of Feedback:</label>
                                <select
                                    name="type"
                                    value={formData.type}
                                    onChange={handleInputChange}
                                    required
                                >
                                    <option value="comment">💬 General Comment</option>
                                    <option value="improvement">💡 Improvement Suggestion</option>
                                </select>
                            </div>

                            <div className="form__group">
                                <label>Name (optional):</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                    placeholder="Your name"
                                />
                            </div>

                            <div className="form__group">
                                <label>Email (optional):</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    placeholder="your.email@example.com"
                                />
                            </div>

                            <div className="form__group">
                                <label>Message:</label>
                                <textarea
                                    name="content"
                                    value={formData.content}
                                    onChange={handleInputChange}
                                    placeholder={formData.type === "comment"
                                        ? "Share your thoughts about the app..."
                                        : "Suggest how we can improve..."
                                    }
                                    required
                                    rows="4"
                                />
                            </div>

                            <button type="submit" className="btn__submit" disabled={loading}>
                                {loading ? "⏳ Submitting..." : "📤 Submit Feedback"}
                            </button>

                            {message && (
                                <div className={`message ${message.includes("Error") ? "error" : "success"}`}>
                                    {message}
                                </div>
                            )}
                        </form>
                    </div>
                )}

                {/* Comments/Improvements List */}
                <div className="feedback__list">
                    {(activeTab === "comments" ? comments : improvements).map((item) => (
                        <div key={item.id} className="feedback__item">
                            <div className="feedback__header">
                                <div className="feedback__author">
                                    {item.name ? (
                                        <span className="author__name">{item.name}</span>
                                    ) : (
                                        <span className="author__anonymous">Anonymous</span>
                                    )}
                                </div>
                                <div className="feedback__date">
                                    {formatDate(item.created_at)}
                                </div>
                            </div>
                            <div className="feedback__content">
                                {item.content}
                            </div>
                        </div>
                    ))}

                    {(activeTab === "comments" ? comments : improvements).length === 0 && (
                        <div className="no__feedback">
                            <div className="no__feedback__icon">
                                {activeTab === "comments" ? "💬" : "💡"}
                            </div>
                            <p>
                                {activeTab === "comments"
                                    ? "No comments yet. Be the first to share your thoughts!"
                                    : "No improvement suggestions yet. Help us make the app better!"
                                }
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Comments;