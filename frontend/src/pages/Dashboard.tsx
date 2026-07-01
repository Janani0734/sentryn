import EvaluationForm from "../components/EvaluationForm";
import { useEffect, useState } from "react";
import Header from "../components/Header";
import StatusCard from "../components/StatusCard";
import { getHealth } from "../api/health";

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getHealth()
      .then((data) => {
        console.log(data);
        setHealth(data);
      })
      .catch(console.error);
  }, []);

  if (!health) {
    return (
      <div
        style={{
          color: "white",
          padding: "50px",
          fontSize: "24px",
        }}
      >
        Connecting to Sentryn Backend...
      </div>
    );
  }

  return (
    <>
      <Header />

      <div
        style={{
          padding: "40px",
        }}
      >
        {/* Backend Status */}
        <h2
          style={{
            color: "white",
            marginBottom: "30px",
          }}
        >
          Backend Status
        </h2>

        <div
          style={{
            display: "flex",
            gap: "25px",
            flexWrap: "wrap",
            marginBottom: "40px",
          }}
        >
          <StatusCard
            title="API"
            status="ONLINE"
          />

          <StatusCard
            title="Redis"
            status={health.redis_connected ? "CONNECTED" : "OFFLINE"}
          />

          <StatusCard
            title="Qdrant"
            status={health.qdrant_connected ? "CONNECTED" : "OFFLINE"}
          />

          <StatusCard
            title="Embedding"
            status={
              health.embedding_model_loaded
                ? "READY"
                : "NOT READY"
            }
          />
        </div>

        {/* Threat Evaluation */}
        <EvaluationForm />
      </div>
    </>
  );
}