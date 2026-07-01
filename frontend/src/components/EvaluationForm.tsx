export default function EvaluationForm() {
  return (
    <div
      style={{
        background: "#1c2438",
        border: "1px solid #2d3748",
        borderRadius: "16px",
        padding: "30px",
        marginTop: "40px",
      }}
    >
      <h2 style={{ color: "white", marginBottom: "20px" }}>
        Threat Evaluation
      </h2>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ color: "#9ca3af" }}>Action Verb</label>
        <input
          type="text"
          placeholder="WRITE"
          style={inputStyle}
        />
      </div>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ color: "#9ca3af" }}>Target Resource</label>
        <input
          type="text"
          placeholder="database"
          style={inputStyle}
        />
      </div>

      <div style={{ marginBottom: "15px" }}>
        <label style={{ color: "#9ca3af" }}>Agent ID</label>
        <input
          type="text"
          placeholder="demo-agent"
          style={inputStyle}
        />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <label style={{ color: "#9ca3af" }}>Reasoning Context</label>
        <textarea
          placeholder="Updating customer profile..."
          rows={4}
          style={{
            ...inputStyle,
            resize: "vertical",
          }}
        />
      </div>

      <button
        style={{
          background: "#06b6d4",
          color: "white",
          border: "none",
          padding: "12px 24px",
          borderRadius: "10px",
          cursor: "pointer",
          fontSize: "16px",
          fontWeight: "bold",
        }}
      >
        Evaluate Threat
      </button>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  marginTop: "8px",
  padding: "12px",
  borderRadius: "8px",
  border: "1px solid #374151",
  background: "#111827",
  color: "white",
  boxSizing: "border-box",
};