import React from "react";
import { MethodButton } from "../components/MethodButton";

const API_BASE = "https://skillset-match-3.onrender.com";
// const API_BASE = "http://localhost:8000";

const Sessions: React.FC = () => {
  return (
    <div id="sessions-1773653670779">

      {/* Navbar */}
      <nav id="ikqhco" style={{"background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "15px 30px", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "fontFamily": "Arial, sans-serif"}}>
        <p id="imsvnf" style={{"fontSize": "24px", "fontWeight": "bold"}}>{"Session review"}</p>
        <div id="igew7e" style={{"display": "flex", "gap": "30px"}}>
          <a style={{"color": "white", "textDecoration": "none"}} href="/">{"Home"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/register" title="Register">{"Register"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/skills" title="Skills">{"Skills"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/matching" title="Matching">{"Matching"}</a>
        </div>
      </nav>

      {/* Main Content */}
      <div id="iimyo1" style={{"display": "flex", "flexWrap": "wrap", "padding": "10px", "gap": "20px"}}>
        <div id="ibl3tj" style={{"flex": "1 1 calc(33.333% - 20px)", "minWidth": "250px"}}>

          {/* Session Info Labels */}
          <section id="container_section_12" className="bdg-sect">
            <h1 className="heading" style={headingStyle}>{"Active Sessions"}</h1>
          </section>
          <section id="container_section_13" className="bdg-sect">
            <h1 className="heading" style={headingStyle}>{"Submit your review below"}</h1>
          </section>

          {/* Review Card */}
          <div id="iq2rcg" style={{"padding": "20px", "background": "#fff3e0", "border": "2px dashed #ff9800", "minHeight": "80px"}}>
            <p id="i40683">{"Enter review for sessions"}</p>

            <div id="i7kvmq" className="card-component" style={{"display": "flex", "flexDirection": "column", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)", "overflow": "hidden", "background": "#ffffff", "minHeight": "200px"}}>

              <div className="card-header" style={{"padding": "16px", "borderBottom": "1px solid #e0e0e0", "fontWeight": "bold", "fontSize": "18px"}}>
                {"Session Review Form"}
              </div>

              <div id="ipjpmb" className="card-body" style={{"padding": "16px", "flexGrow": "1"}}>
                <h1 className="heading" style={headingStyle}>{"Session id"}</h1>
                <p style={{"color": "#888", "fontSize": "13px", "marginBottom": "8px"}}>{"The session ID will be entered in the form below."}</p>

                <span id="izop1g" style={{"fontWeight": "600"}}>{"Rating"}</span>
                <p style={{"color": "#555", "fontSize": "13px", "marginBottom": "8px"}}>
                  {"1 - very bad, 2 - bad, 3 - neutral, 4 - good, 5 - very good, 0 - cancelled or not applicable"}
                </p>

                <span id="izop1g-2" style={{"fontWeight": "600"}}>{"Comments"}</span>
                <p style={{"color": "#888", "fontSize": "13px", "marginBottom": "8px"}}>{"Optional feedback about the session."}</p>
              </div>

              <div className="card-footer" style={{"padding": "16px", "borderTop": "1px solid #e0e0e0", "backgroundColor": "#f5f5f5"}}>
                <p style={{"fontSize": "13px", "color": "#666", "marginBottom": "8px"}}>
                  📝 Click below to submit your session review
                </p>
                <MethodButton
                  className="action-button-component"
                  style={btnStyle}
                  label="Submit review"
                  endpoint="/sessionreview/"
                  isClassMethod={true}
                  backendUrl={API_BASE}
                  parameters={[
                    { name: "session_1", type: "string", required: true, inputKind: "lookup", entity: "session", lookupField: "sessionId" },
                    { name: "rating", type: "number", required: true, inputKind: "enum", options: ["0", "1", "2", "3", "4", "5"] },
                    { name: "comments", type: "string", required: false },
                    { name: "reviewDate", type: "date", required: true }
                  ]}
                />
              </div>

            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

const headingStyle: React.CSSProperties = {
  width: "auto", height: "auto", padding: "0", margin: "0",
  fontSize: "large", position: "static", textAlign: "left", zIndex: 0
};

const btnStyle: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", padding: "6px 14px",
  background: "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)",
  color: "#fff", textDecoration: "none", borderRadius: "4px",
  fontSize: "13px", fontWeight: "600", letterSpacing: "0.01em",
  cursor: "pointer", border: "none",
  boxShadow: "0 1px 4px rgba(37,99,235,0.10)", transition: "background 0.2s"
};

export default Sessions;
