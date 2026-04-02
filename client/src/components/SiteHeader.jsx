import { FaFacebookF, FaInstagram, FaTiktok, FaYoutube } from "react-icons/fa";

import logo from "../logo.svg";

function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a href="#" className="site-logo" aria-label="Million Miles">
          <img src={logo} alt="" className="site-logo__image" />
        </a>

        <nav className="site-nav" aria-label="Main navigation">
          <a href="#" className="site-nav__link active">
            Cars
          </a>
          <a href="#" className="site-nav__link">
            Services
          </a>
          <a href="#" className="site-nav__link">
            Ask an Expert
          </a>
          <a href="#" className="site-nav__link">
            About Us
          </a>
        </nav>

        <div className="site-actions">
          <span className="site-chip">English</span>
          <span className="site-chip">USD</span>
          <a href="#" className="site-icon" aria-label="Instagram">
            <FaInstagram />
          </a>
          <a href="#" className="site-icon" aria-label="Facebook">
            <FaFacebookF />
          </a>
          <a href="#" className="site-icon" aria-label="TikTok">
            <FaTiktok />
          </a>
          <a href="#" className="site-icon" aria-label="YouTube">
            <FaYoutube />
          </a>
        </div>
      </div>
    </header>
  );
}

export default SiteHeader;
