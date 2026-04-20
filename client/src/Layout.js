import React from "react";
import "./Layout.css";

function Layout({ children, setActiveSection, activeSection }) {
    // fixed Header
    React.useEffect(() => {
        const handleScroll = () => {
            const header = document.querySelector(".header");
            if (header) {
                header.classList.toggle("active", window.scrollY > 0);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const handleNavClick = (section) => {
        setActiveSection(section);
        // Scroll to top when changing sections
        window.scrollTo(0, 0);
    };

    return (
        <div className="layout">
            {/* Header/Navbar */}
            <header className="header d__flex align__items__center pxy__30">
                <div className="brand">
                    <img src="/logo.svg" alt="FloraScan Logo" className="brand__logo" />
                    <span className="brand__name">FloraScan</span>
                </div>
                <nav className="navigation pxy__30">
                    <ul className="navbar d__flex">
                        <li
                            className={`nav__items mx__15 ${activeSection === "Home" ? "active" : ""}`}
                            onClick={() => handleNavClick("Home")}
                        >
                            Home
                        </li>
                        <li
                            className={`nav__items mx__15 ${activeSection === "About" ? "active" : ""}`}
                            onClick={() => handleNavClick("About")}
                        >
                            About
                        </li>
                        <li
                            className={`nav__items mx__15 ${activeSection === "Services" ? "active" : ""}`}
                            onClick={() => handleNavClick("Services")}
                        >
                            Detect
                        </li>
                        <li
                            className={`nav__items mx__15 ${activeSection === "FAQ" ? "active" : ""}`}
                            onClick={() => handleNavClick("FAQ")}
                        >
                            FAQ
                        </li>
                        <li
                            className={`nav__items mx__15 ${activeSection === "Comments" ? "active" : ""}`}
                            onClick={() => handleNavClick("Comments")}
                        >
                            Comments
                        </li>
                        <li
                            className={`nav__items mx__15 ${activeSection === "Gallery" ? "active" : ""}`}
                            onClick={() => handleNavClick("Gallery")}
                        >
                            Gallery
                        </li>
                    </ul>
                </nav>
            </header>

            {/* Main Content */}
            <main className="main__content">
                {children}
            </main>
        </div>
    );
}

export default Layout;