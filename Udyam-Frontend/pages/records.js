import { useEffect, useState } from "react";
import Link from "next/link";

import Navbar from "../components/Navbar";

import { api } from "../lib/api";

export default function RecordsPage() {

  const [records, setRecords] = useState([]);

  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");

  // =========================================
  // FETCH RECORDS
  // =========================================
  const fetchRecords = async () => {

    try {

      setLoading(true);

      const res = await api.get("/records/all");

      console.log("RECORDS RESPONSE:", res.data);

      setRecords(res.data || []);

    } catch (err) {

      console.error("FETCH RECORDS ERROR:", err);

    } finally {

      setLoading(false);
    }
  };

  // =========================================
  // LOAD ON START
  // =========================================
  useEffect(() => {

    fetchRecords();

  }, []);

  // =========================================
  // DELETE RECORD
  // =========================================
  const deleteRecord = async (id) => {

    try {

      await api.delete(`/records/${id}`);

      setRecords(
        records.filter((r) => r.id !== id)
      );

    } catch (err) {

      console.error(err);

      alert("Delete failed");
    }
  };

  // =========================================
  // UPDATE STATUS
  // =========================================
  const updateStatus = async (id, status) => {

    try {

      await api.put(
        `/records/status/${id}`,
        { status }
      );

      // UPDATE UI IMMEDIATELY
      setRecords((prev) =>
        prev.map((record) =>

          record.id === id

            ? {
                ...record,
                business_status: status
              }

            : record
        )
      );

    } catch (err) {

      console.error("STATUS UPDATE ERROR:", err);

      alert("Failed to update status");
    }
  };

  // =========================================
  // FILTER RECORDS
  // =========================================
  const filteredRecords = records.filter((r) => {

    const text = search.toLowerCase();

    return (
      r.name?.toLowerCase().includes(text) ||
      r.pan?.toLowerCase().includes(text) ||
      r.ubid?.toLowerCase().includes(text)
    );
  });

  return (
    <>
      <Navbar />

      <div className="container">

        {/* HEADER */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px"
          }}
        >

          <div>

            <h1>All Business Records</h1>

            <p
              style={{
                color: "#666",
                marginTop: "-10px"
              }}
            >
              View and manage all submitted entities
            </p>

          </div>

          <Link href="/">

            <button
              style={{
                width: "180px"
              }}
            >
              + Add Record
            </button>

          </Link>

        </div>

        {/* SEARCH */}
        <div className="card">

          <input
            placeholder="Search by Name, PAN or UBID..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
          />

        </div>

        {/* TABLE */}
        <div className="card">

          {loading ? (

            <p>Loading records...</p>

          ) : (

            <div className="table-container">

              <table>

                <thead>

                  <tr>
                    <th>Name</th>
                    <th>PAN</th>
                    <th>Source</th>
                    <th>UBID</th>
                    <th>Address</th>
                    <th>Phone</th>
                    <th>Decision</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>

                </thead>

                <tbody>

                  {filteredRecords.length > 0 ? (

                    filteredRecords.map((r) => (

                      <tr key={r.id}>

                        {/* NAME */}
                        <td>{r.name}</td>

                        {/* PAN */}
                        <td>{r.pan || "-"}</td>

                        {/* SOURCE */}
                        <td>{r.source || "-"}</td>

                        {/* UBID */}
                        <td>
                          <strong>
                            {r.ubid || "-"}
                          </strong>
                        </td>

                        {/* ADDRESS */}
                        <td>{r.address}</td>

                        {/* PHONE */}
                        <td>{r.phone || "-"}</td>

                        {/* DECISION */}
                        <td>

                          <span
                            className={
                              r.decision === "auto_merge"
                                ? "status-active"
                                : r.decision === "review"
                                ? "status-dormant"
                                : "status-closed"
                            }
                          >
                            {r.decision || "-"}
                          </span>

                        </td>

                        {/* CONFIDENCE */}
                        <td>

                          {r.confidence !== undefined
                            ? Number(r.confidence).toFixed(2)
                            : "0.00"}

                        </td>

                        {/* STATUS */}
                        <td>

                          <select
                            value={
                              r.business_status || "Active"
                            }
                            onChange={(e) =>
                              updateStatus(
                                r.id,
                                e.target.value
                              )
                            }
                            style={{
                              padding: "8px",
                              borderRadius: "6px",
                              border: "1px solid #ccc",
                              fontWeight: "500",
                              backgroundColor: "white"
                            }}
                          >

                            <option value="Active">
                              Active
                            </option>

                            <option value="Dormant">
                              Dormant
                            </option>

                            <option value="Closed">
                              Closed
                            </option>

                          </select>

                        </td>

                        {/* ACTIONS */}
                        <td>

                          <button
                            className="delete-btn"
                            onClick={() =>
                              deleteRecord(r.id)
                            }
                          >
                            Delete
                          </button>

                        </td>

                      </tr>

                    ))

                  ) : (

                    <tr>

                      <td
                        colSpan="10"
                        style={{
                          textAlign: "center",
                          padding: "20px"
                        }}
                      >
                        No records found
                      </td>

                    </tr>

                  )}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>
    </>
  );
}