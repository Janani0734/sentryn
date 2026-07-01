const API_URL =
  "https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io";

export async function getHealth() {
  const response = await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error("Failed to fetch backend health");
  }

  return response.json();
}