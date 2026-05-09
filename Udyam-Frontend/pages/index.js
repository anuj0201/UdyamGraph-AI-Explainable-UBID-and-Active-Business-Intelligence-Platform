import { useState } from "react";
import Navbar from "../components/Navbar";
import { api } from "../lib/api";

export default function Home() {
  const [form, setForm] = useState({
    source: "",
    pan: "",
    gstin: "",
    name: "",
    address: "",
    pincode: "",
    phone: ""
  });

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {

    if (!form.name || !form.address || !form.pincode) {

      alert("Name, Address and Pincode are required");

      return;
    }

    const cleanData = {
      source: form.source || "UNKNOWN",
      pan: form.pan || null,
      gstin: form.gstin || null,
      name: form.name,
      address: form.address,
      pincode: form.pincode,
      phone: form.phone || null
    };

    try {

      setLoading(true);

      console.log("SENDING DATA:", cleanData);

      const response = await api.post(
        "/records/",
        cleanData
      );

      console.log(
        "API RESPONSE:",
        response.data
      );

      setResult({
        decision:
          response.data.decision,

        confidence:
          response.data.confidence_score ??
          response.data.confidence,

        reasons:
          Array.isArray(response.data.reasons)
            ? response.data.reasons
            : response.data.reasons
            ? [response.data.reasons]
            : [],

        ubid:
          response.data.ubid
      });

    } catch (err) {

      console.error("FULL ERROR:", err);

      console.error(
        "ERROR RESPONSE:",
        err.response?.data
      );

      alert(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        "Server error"
      );

    } finally {

      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <div className="container">

        <h1>Business Record Entry</h1>

        {/* FORM CARD */}
        <div className="card">

          <h2>Add Business Record</h2>

          {Object.keys(form).map((key) => (

            <div
              key={key}
              style={{ marginBottom: "10px" }}
            >

              <label
                style={{
                  fontSize: "14px",
                  fontWeight: "500"
                }}
              >
                {key.toUpperCase()}
              </label>

              <input
                placeholder={`Enter ${key}`}
                value={form[key]}
                onChange={(e) =>
                  setForm({
                    ...form,
                    [key]: e.target.value
                  })
                }
              />

            </div>
          ))}

          <button
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading
              ? "Processing..."
              : "Submit Record"}
          </button>

        </div>

        {/* RESULT CARD */}
        {result && (

          <div className="card">

            <h2>Matching Result</h2>

            <p style={{ marginTop: "10px" }}>
              <strong>Status:</strong>{" "}
              <span
                style={{
                  color:
                    result.business_status === "Active"
                      ? "green"
                      : result.business_status === "Dormant"
                      ? "orange"
                      : "red",
                  fontWeight: "bold"
              }}
            >
              {result.business_status}
            </span>
          </p>

            <p>
              <strong>Decision:</strong>{" "}

              <span
                style={{
                  color:
                    result.decision === "auto_merge"
                      ? "green"
                      : result.decision === "review"
                      ? "orange"
                      : result.decision === "new_entity"
                      ? "red"
                      : "black",

                  fontWeight: "bold"
                }}
              >
                {result.decision ?? "N/A"}
              </span>

            </p>

            <p>

              <strong>Confidence:</strong>{" "}

              {result.confidence !== undefined &&
              result.confidence !== null
                ? Number(
                    result.confidence
                  ).toFixed(2)
                : "N/A"}

            </p>

            <div style={{ marginTop: "10px" }}>

              <strong>Reasons:</strong>

              <ul style={{ marginTop: "5px" }}>

                {Array.isArray(result.reasons) &&
                result.reasons.length > 0 ? (

                  result.reasons.map(
                    (reason, index) => (

                      <li key={index}>
                        {reason}
                      </li>
                    )
                  )

                ) : (

                  <li>
                    No reasons available
                  </li>

                )}

              </ul>

            </div>

            {result.ubid && (

              <p style={{ marginTop: "10px" }}>

                <strong>UBID:</strong>{" "}

                {result.ubid}

              </p>
            )}

          </div>
        )}

      </div>
    </>
  );
}