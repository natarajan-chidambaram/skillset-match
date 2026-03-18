import React, { useState, useEffect } from "react";
import { MethodButton } from "../components/MethodButton";
import { fetchUsers, fetchSkills } from "../api";

const API_BASE = "https://skillset-match-3.onrender.com";
// const API_BASE = "http://localhost:8000";

const Register: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);

  useEffect(() => {
    fetchUsers().then(setUsers);
    fetchSkills().then(setSkills);
  }, []);

  return (
    <div id="register-1773653756266">
      <nav id="ih2ctk" style={{"background": "linear-gradient(135deg, #4b3c82 0%, #5a3d91 100%)", "color": "white", "padding": "15px 30px", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "fontFamily": "Arial, sans-serif"}}>
        <p id="ivg67r" style={{"fontSize": "24px", "fontWeight": "bold"}}>{"Register - register user and add or update user skills"}</p>
        <div id="ikw66k" style={{"display": "flex", "gap": "30px"}}>
          <a style={{"color": "white", "textDecoration": "none"}} href="/">{"Home"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/skills" title="Skills">{"Skills"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/matching" title="Matching">{"Matching"}</a>
          <a style={{"color": "white", "textDecoration": "none"}} href="/sessions" title="Sessions">{"Sessions"}</a>
        </div>
      </nav>

      <div id="iyy6i" style={{"display": "flex", "flexDirection": "column", "gap": "20px", "padding": "20px"}}>

        {/* Card 1 - User Details */}
        <div id="ioc0l" style={{"padding": "20px", "background": "#fff3e0", "border": "2px dashed #ff9800", "minHeight": "80px"}}>
          <p id="igcfey" style={{"fontSize": "30px"}}>{"User details"}</p>
          <div id="iaoj6" className="card-component" style={{"display": "flex", "flexDirection": "column", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)", "overflow": "hidden", "background": "#ffffff", "minHeight": "200px"}}>
            <div className="card-header" style={{"padding": "16px", "borderBottom": "1px solid #e0e0e0", "fontWeight": "bold", "fontSize": "18px"}} />
            <div className="card-body" style={{"padding": "16px", "flexGrow": "1"}}>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Name"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"User Id"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Email id"}</h1>
              </section>
            </div>
            <div className="card-footer" style={{"padding": "16px", "borderTop": "1px solid #e0e0e0", "backgroundColor": "#f5f5f5"}} />
          </div>
          <br />
          <MethodButton
            className="action-button-component"
            style={btnStyle}
            label="Create User"
            endpoint="/user/"
            isClassMethod={true}
            backendUrl={API_BASE}
            onSuccess={() => fetchUsers().then(setUsers)}
            parameters={[
              { name: "userName", type: "string", required: true },
              { name: "userId", type: "number", required: true },
              { name: "emailId", type: "string", required: true }
            ]}
          />
        </div>

        {/* Card 2 - UserSkill */}
        <div id="iwiig" style={{"padding": "20px", "background": "#fff3e0", "border": "2px dashed #ff9800", "minHeight": "80px"}}>
          <p id="i5pacm" style={{"fontSize": "30px"}}>{"Add user skills"}</p>
          <div id="ic89pb" className="card-component" style={{"display": "flex", "flexDirection": "column", "borderRadius": "8px", "boxShadow": "0 2px 8px rgba(0,0,0,0.1)", "overflow": "hidden", "background": "#ffffff", "minHeight": "200px"}}>
            <div className="card-header" style={{"padding": "16px", "borderBottom": "1px solid #e0e0e0", "fontWeight": "bold", "fontSize": "18px"}} />
            <div className="card-body" style={{"padding": "16px", "flexGrow": "1"}}>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"User id (select from existing users)"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Skill id (select from existing skills)"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Skill level (NOVICE, COMPETENT, PROFICIENT, EXPERT, AUTHORITY)"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Years of experience"}</h1>
              </section>
              <section className="bdg-sect">
                <h1 className="heading" style={headingStyle}>{"Certification (true/false)"}</h1>
              </section>
            </div>
            <div className="card-footer" style={{"padding": "16px", "borderTop": "1px solid #e0e0e0", "backgroundColor": "#f5f5f5"}} />
          </div>
          <br />
          <MethodButton
            className="action-button-component"
            style={btnStyle}
            label="Add User Skill"
            endpoint="/userskill/"
            isClassMethod={true}
            backendUrl={API_BASE}
            parameters={[
              { name: "user", type: "number", required: true, inputKind: "lookup", entity: "user", lookupField: "userId" },
              { name: "skill", type: "number", required: true, inputKind: "lookup", entity: "skill", lookupField: "skillId" },
              { name: "skillLevel", type: "string", required: true, inputKind: "enum", options: ["NOVICE","COMPETENT","PROFICIENT","EXPERT","AUTHORITY"] },
              { name: "yearsOfExperience", type: "float", required: true },
              { name: "certification", type: "boolean", required: true }
            ]}
          />
        </div>

      </div>
    </div>
  );
};

const headingStyle: React.CSSProperties = { width: "auto", height: "auto", padding: "0", margin: "0", fontSize: "large", position: "static", textAlign: "left", zIndex: 0 };
const btnStyle: React.CSSProperties = { display: "inline-flex", alignItems: "center", padding: "6px 14px", background: "linear-gradient(90deg, #2563eb 0%, #1e40af 100%)", color: "#fff", textDecoration: "none", borderRadius: "4px", fontSize: "13px", fontWeight: "600", letterSpacing: "0.01em", cursor: "pointer", border: "none", boxShadow: "0 1px 4px rgba(37,99,235,0.10)", transition: "background 0.2s" };

export default Register;
