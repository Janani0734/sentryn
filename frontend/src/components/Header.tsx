export default function Header() {
  return (
    <header
      style={{
        background: "#111827",
        color: "white",
        padding: "25px 40px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        borderBottom: "1px solid #2b3445",
      }}
    >
      <div>
        <h1
          style={{
            color: "#22d3ee",
            margin: 0,
            fontSize: "42px",
          }}
        >
          Sentryn
        </h1>

        <p
          style={{
            marginTop: "10px",
            color: "#9ca3af",
            fontSize: "20px",
          }}
        >
          Enterprise AI Agent Guardrail Platform
        </p>
      </div>

      <div style={{ textAlign: "right" }}>
        <h2
          style={{
            color: "#22c55e",
            margin: 0,
          }}
        >
          ● LIVE
        </h2>

        <p style={{ color: "#9ca3af" }}>
          Azure Container Apps
        </p>
      </div>
    </header>
  );
}