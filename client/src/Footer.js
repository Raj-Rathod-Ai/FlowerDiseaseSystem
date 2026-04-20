import React from "react";
import "./Footer.css";

const currentYear = new Date().getFullYear();

const LINKS = {
  Explore: [
    { label: "Home", href: "#Home" },
    { label: "About", href: "#About" },
    { label: "Detect", href: "#Services" },
    { label: "Gallery", href: "#Gallery" },
  ],
  Technology: [
    { label: "Deep Learning", href: "#About" },
    { label: "Image Analysis", href: "#Services" },
    { label: "Disease Atlas", href: "#Gallery" },
    { label: "How It Works", href: "#About" },
  ],
};

const SOCIALS = [
  {
    label: "GitHub",
    href: "https://github.com/Raj-Rathod-Ai/FlowerDiseaseSystem",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
      </svg>
    ),
  },
  {
    label: "LinkedIn",
    href: "https://linkedin.com/in/raj-rathod-ai",
    icon: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
      </svg>
    ),
  },
];

function Footer() {
  return (
    <footer className="footer" id="Footer">
      {/* Top wave divider */}
      <div className="footer__wave">
        <svg viewBox="0 0 1440 80" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M0,40 C360,80 1080,0 1440,40 L1440,80 L0,80 Z"
            fill="#0a1a0d"
          />
        </svg>
      </div>

      <div className="footer__body">
        <div className="container">
          <div className="footer__grid">

            {/* Brand column */}
            <div className="footer__brand__col">
              <div className="footer__brand">
                <img src="/logo.svg" alt="FloraScan" className="footer__logo" />
                <span className="footer__brand__name">FloraScan</span>
              </div>
              <p className="footer__tagline">
                AI-powered flower health diagnostics. Detect diseases early,
                keep your garden thriving.
              </p>
              <div className="footer__socials">
                {SOCIALS.map((s) => (
                  <a
                    key={s.label}
                    href={s.href}
                    className="footer__social__link"
                    target="_blank"
                    rel="noreferrer"
                    aria-label={s.label}
                  >
                    {s.icon}
                  </a>
                ))}
              </div>
            </div>

            {/* Link columns */}
            {Object.entries(LINKS).map(([section, items]) => (
              <div key={section} className="footer__links__col">
                <h4 className="footer__col__heading">{section}</h4>
                <ul className="footer__link__list">
                  {items.map((item) => (
                    <li key={item.label}>
                      <a href={item.href} className="footer__link">
                        {item.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}

            {/* Contact / info column */}
            <div className="footer__links__col">
              <h4 className="footer__col__heading">About</h4>
              <ul className="footer__link__list">
                <li>
                  <span className="footer__info__item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
                      <circle cx="12" cy="9" r="2.5" />
                    </svg>
                    Deep Learning Model
                  </span>
                </li>
                <li>
                  <span className="footer__info__item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M12 6v6l4 2" />
                    </svg>
                    Real-time Analysis
                  </span>
                </li>
                <li>
                  <span className="footer__info__item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    3 Flower Species
                  </span>
                </li>
                <li>
                  <span className="footer__info__item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                    </svg>
                    Health Detection
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Divider */}
          <div className="footer__divider" />

          {/* Bottom bar */}
          <div className="footer__bottom">
            <p className="footer__copyright">
              © {currentYear} <strong>FloraScan</strong>. All rights reserved.
            </p>
            <div className="footer__bottom__links">
              <a href="#Home" className="footer__bottom__link">Privacy Policy</a>
              <span className="footer__dot">·</span>
              <a href="#Home" className="footer__bottom__link">Terms of Service</a>
              <span className="footer__dot">·</span>
              <a href="#Home" className="footer__bottom__link">Contact</a>
            </div>
            <p className="footer__powered">
              Powered by{" "}
              <span className="footer__powered__highlight">TensorFlow</span> &amp;{" "}
              <span className="footer__powered__highlight">React</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
