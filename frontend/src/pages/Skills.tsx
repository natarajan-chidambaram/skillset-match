import React from "react";
import { MethodButton } from "../components/MethodButton";

const API_BASE = "https://skillset-match-3.onrender.com";
// const API_BASE = "http://localhost:8000";

const Skills: React.FC = () => {
  return (
    <div id="skills-1773653653992">
      <nav id="ip70m4" style={{"background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "15px 30px", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "fontFamily": "Arial, sans-serif"}}>
        <p id="i6yd0k" style={{"fontSize": "24px", "fontWeight": "bold"}}>{"Skills - register skills, their corresponding ids and descriptions"}</p>
        <div id="ivmqms" style={{"display": "flex", "gap": "30px"}}>
          <a style={{"color": "white", "textDecoration": "none"}} href="/">{"Home"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/register" title="Register">{"Register"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/matching" title="Matching">{"Matching"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/sessions" title="Sessions">{"Sessions"}</a>
        </div>
      </nav>

      <div id="iywdi" style={{"display": "flex", "flexDirection": "column", "gap": "20px", "padding": "20px"}}>
        <div id="i7phz" style={{"padding": "20px", "background": "#fff3e0", "border": "2px dashed #ff9800", "minHeight": "80px"}}>
          <div id="itp99" className="card-component" style={{"display": "flex", "flexDirection": "column", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)", "overflow": "hidden", "background": "#ffffff", "minHeight": "200px"}}>
            <div className="card-header" style={{"padding": "16px", "borderBottom": "1px solid #e0e0e0", "fontWeight": "bold", "fontSize": "18px"}} />
            <div id="inkki" className="card-body" style={{"padding": "16px", "flexGrow": "1"}}>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Skill id"}</h1></section>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Skill name"}</h1></section>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Category"}</h1></section>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Description"}</h1></section>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Skill level (BEGINNER, INTERMEDIATE, ADVANCED, EXPERT, MASTERCLASS)"}</h1></section>
              <section className="bdg-sect"><h1 className="heading" style={headingStyle}>{"Estimated duration (in minutes)"}</h1></section>
            </div>
            <div className="card-footer" style={{"padding": "16px", "borderTop": "1px solid #e0e0e0", "backgroundColor": "#f5f5f5"}} />
          </div>
          <br />
          <MethodButton
            className="action-button-component"
            style={btnStyle}
            label="Register skill"
            endpoint="/skill/"
            isClassMethod={true}
            backendUrl={API_BASE}
            parameters={[
              { name: "skillId", type: "integer", required: true },
              { name: "skillName", type: "string", required: true },
              { name: "category", type: "string", required: true },
              { name: "description", type: "string", required: false },
              { name: "skillLevel", type: "string", required: true, inputKind: "enum", options: ["BEGINNER","INTERMEDIATE","ADVANCED","EXPERT","MASTERCLASS"] },
              { name: "estimatedDuration", type: "integer", required: true }
            ]}
          />
        </div>
      </div>
    </div>
  );
};

const headingStyle: React.CSSProperties = { width: "auto", height: "auto", padding: "0", margin: "0", fontSize: "large", position: "static", textAlign: "left", zIndex: 0 };
const btnStyle: React.CSSProperties = { display: "inline-flex", alignItems: "center", padding: "6px 14px", background: "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)", color: "#fff", textDecoration: "none", borderRadius: "4px", fontSize: "13px", fontWeight: "600", letterSpacing: "0.01em", cursor: "pointer", border: "none", boxShadow: "0 1px 4px rgba(37,99,235,0.10)", transition: "background 0.2s" };

export default Skills;
