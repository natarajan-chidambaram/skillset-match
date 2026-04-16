import React from "react";
import { MethodButton } from "../components/MethodButton";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Matching: React.FC = () => {
  return (
    <div id="matching-1773653664188">
      <nav id="ixqu6k" style={{"background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "15px 30px", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "fontFamily": "Arial, sans-serif"}}>
        <p id="igvj2e" style={{"fontSize": "24px", "fontWeight": "bold"}}>{"Matching - find learners and teachers"}</p>
        <div id="i799uv" style={{"display": "flex", "gap": "30px"}}>
          <a style={{"color": "white", "textDecoration": "none"}} href="/">{"Home"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/register" title="Register">{"Register"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/skills" title="Skills">{"Skills"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/sessions" title="Sessions">{"Sessions"}</a>
        </div>
      </nav>

      <div id="iu0d6e" style={{"display": "flex", "flexDirection": "column", "gap": "20px", "padding": "20px"}}>

        {/* Card - Skill Request */}
        <div id="ilj9t9" style={{"padding": "20px", "background": "#fff3e0", "border": "2px dashed #ff9800", "minHeight": "80px"}}>
          <p id="iahtey">{"Enter your user id and the skill id that you want to learn"}</p>
          <section id="container_section_7" className="bdg-sect">
            <h1 id="h1_7" className="heading" style={headingStyle}>{"Your user id"}</h1>
          </section>
          <section id="container_section_8" className="bdg-sect">
            <h1 id="h1_8" className="heading" style={headingStyle}>{"Skill id to learn"}</h1>
          </section>
          <section id="container_section_9" className="bdg-sect">
            <h1 id="h1_9" className="heading" style={headingStyle}>{"Deadline"}</h1>
          </section>
          <p style={{"fontSize": "13px", "color": "#666", "marginBottom": "8px"}}>
            📝 Click below to submit a skill request
          </p>
          <MethodButton
            className="action-button-component"
            style={btnStyle}
            label="Request teacher"
            endpoint="/skillrequest/"
            isClassMethod={true}
            backendUrl={API_BASE}
            parameters={[
              { name: "user_1", type: "string", required: true, inputKind: "lookup", entity: "user", lookupField: "userName" },
              { name: "skill_1", type: "string", required: true, inputKind: "lookup", entity: "skill", lookupField: "skillName" },
              { name: "deadlineDate", type: "date", required: true },
              { name: "createdDate", type: "date", required: true },
              { name: "status", type: "string", required: true, inputKind: "enum", options: ["OPEN"] }
            ]}
          />
        </div>

        {/* Run Matching */}
        <div style={{"padding": "20px", "background": "#e8f5e9", "border": "2px dashed #4caf50", "minHeight": "80px"}}>
          <p style={{"fontSize": "18px", "fontWeight": "bold", "marginBottom": "8px"}}>{"Find Matches"}</p>
          <p style={{"fontSize": "13px", "color": "#666", "marginBottom": "8px"}}>
            📝 Click below to automatically match learners with teachers
          </p>
          <MethodButton
            className="action-button-component"
            style={{...btnStyle, background: "linear-gradient(90deg, #2e7d32 0%, #1b5e20 100%)"}}
            label="Run Matching"
            endpoint="/run-matching/"
            isClassMethod={true}
            backendUrl={API_BASE}
            parameters={[]}
          />
        </div>

        {/* Moderate Sessions Card */}
        <div style={{ padding: "20px", background: "#e3f2fd", border: "2px dashed #1976d2", minHeight: "80px" }}>
          <p style={{ fontSize: "18px", fontWeight: "bold", marginBottom: "8px" }}>{"Moderate Sessions"}</p>
          <p style={{ fontSize: "13px", color: "#666", marginBottom: "8px" }}>
            📝 Review pending matches and approve or reject them
          </p>
          <MethodButton
            className="action-button-component"
            style={btnStyle}
            label="Moderate Sessions"
            endpoint="/skillmatch/{id}"
            isClassMethod={false}
            backendUrl={API_BASE}
            parameters={[
              {
                name: "id", type: "number", required: true,
                inputKind: "lookup", entity: "skillmatch", lookupField: "id",
                cascade: {
                  fetchUrl: "/skillmatch/{value}",
                  display: [
                    { label: "Learner",        field: "skillmatch.user_3_id" },
                    { label: "Teacher",       field: "skillmatch.user_2_id" },
                    { label: "Current Status", field: "skillmatch.status" }
                  ],
                  prefill: [
                    { paramName: "startDate",   field: "skillmatch.startDate" },
                    { paramName: "createdDate", field: "skillmatch.createdDate" },
                    { paramName: "user_2",      field: "skillmatch.user_2_id" },
                    { paramName: "user_3",      field: "skillmatch.user_3_id" }
                  ]
                }
              },
              { name: "status", type: "string", required: true,
                inputKind: "enum", options: ["PENDING", "ACTIVE", "REJECTED", "COMPLETED"] }
            ]}
          />
        </div>


      </div>
    </div>
  );
};

const headingStyle: React.CSSProperties = { width: "auto", height: "auto", padding: "0", margin: "0", fontSize: "large", position: "static", textAlign: "left", zIndex: 0 };
const btnStyle: React.CSSProperties = { display: "inline-flex", alignItems: "center", padding: "6px 14px", background: "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)", color: "#fff", textDecoration: "none", borderRadius: "4px", fontSize: "13px", fontWeight: "600", letterSpacing: "0.01em", cursor: "pointer", border: "none", boxShadow: "0 1px 4px rgba(37,99,235,0.10)", transition: "background 0.2s" };

export default Matching;
