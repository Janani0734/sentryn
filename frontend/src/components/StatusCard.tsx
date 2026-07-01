type StatusCardProps = {
  title: string;
  status: string;
};

export default function StatusCard({
  title,
  status,
}: StatusCardProps) {
  return (
    <div
      style={{
        background: "#1c2438",
        border: "1px solid #2d3748",
        borderRadius: "16px",
        padding: "30px",
        width: "250px",
      }}
    >
      <h2
        style={{
          color: "white",
          marginBottom: "20px",
        }}
      >
        {title}
      </h2>

      <p
        style={{
          color: "#22c55e",
          fontWeight: "bold",
        }}
      >
        ● {status}
      </p>
    </div>
  );
}