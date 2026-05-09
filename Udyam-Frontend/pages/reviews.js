import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../lib/api";

export default function ReviewsPage() {

  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReviews();
  }, []);

  // =========================================
  // LOAD REVIEWS
  // =========================================
  const loadReviews = async () => {

    try {

      const res = await api.get("/reviews/");

      setReviews(res.data);

    } catch (err) {

      console.error(err);

      alert("Failed to load reviews");

    } finally {

      setLoading(false);
    }
  };

  // =========================================
  // APPROVE REVIEW
  // =========================================
  const approveReview = async (id) => {

    try {

      await api.post(`/reviews/${id}/approve`);

      setReviews((prev) =>
        prev.filter((r) => r.id !== id)
      );

      alert("Review approved successfully");

    } catch (err) {

      console.error(err);

      alert(
        JSON.stringify(
          err.response?.data || err.message
        )
      );
    }
  };

  // =========================================
  // REJECT REVIEW
  // =========================================
  const rejectReview = async (id) => {

    try {

      await api.post(`/reviews/${id}/reject`);

      setReviews((prev) =>
        prev.filter((r) => r.id !== id)
      );

      alert("Review rejected successfully");

    } catch (err) {

      console.error(err);

      alert(
        JSON.stringify(
          err.response?.data || err.message
        )
      );
    }
  };

  return (

    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, #020617, #0f172a)",
        padding: "50px 30px",
        fontFamily: "Inter, Arial, sans-serif",
        color: "white"
      }}
    >

      {/* PAGE CONTAINER */}
      <div
        style={{
          maxWidth: "1000px",
          margin: "0 auto"
        }}
      >

        {/* HEADER */}
        <div
          style={{
            marginBottom: "30px"
          }}
        >

          <h1
            style={{
              fontSize: "58px",
              fontWeight: "800",
              marginBottom: "12px",
              color: "white",
              letterSpacing: "-1px"
            }}
          >
            Review Queue
          </h1>

          <Link
            href="/"
            style={{
              color: "#8b5cf6",
              textDecoration: "none",
              fontWeight: "600",
              fontSize: "16px"
            }}
          >
            ← Back to Home
          </Link>

        </div>

        {/* LOADING */}
        {loading ? (

          <div
            style={{
              background: "#111827",
              borderRadius: "20px",
              padding: "40px",
              border: "1px solid #1e293b"
            }}
          >
            <p
              style={{
                color: "#cbd5e1",
                fontSize: "18px"
              }}
            >
              Loading reviews...
            </p>
          </div>

        ) : reviews.length === 0 ? (

          <div
            style={{
              background: "#111827",
              borderRadius: "20px",
              padding: "40px",
              border: "1px solid #1e293b",
              boxShadow:
                "0 10px 30px rgba(0,0,0,0.35)"
            }}
          >

            <h2
              style={{
                color: "white",
                marginBottom: "10px"
              }}
            >
              No Pending Reviews
            </h2>

            <p
              style={{
                color: "#94a3b8"
              }}
            >
              All business matches are processed.
            </p>

          </div>

        ) : (

          <div>

            {reviews.map((review) => (

              <div
                key={review.id}
                style={{
                  background:
                    "linear-gradient(145deg, #0f172a, #111827)",
                  border: "1px solid #1e293b",
                  borderRadius: "22px",
                  padding: "28px",
                  marginBottom: "28px",
                  boxShadow:
                    "0 12px 35px rgba(0,0,0,0.35)"
                }}
              >

                {/* TOP ROW */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "22px",
                    flexWrap: "wrap",
                    gap: "10px"
                  }}
                >

                  <div>

                    <div
                      style={{
                        color: "#94a3b8",
                        fontSize: "14px",
                        marginBottom: "6px"
                      }}
                    >
                      Match Score
                    </div>

                    <div
                      style={{
                        fontSize: "34px",
                        fontWeight: "800",
                        color: "#22c55e"
                      }}
                    >
                      {review.score?.toFixed(2)}
                    </div>

                  </div>

                  <div
                    style={{
                      background:
                        "rgba(139,92,246,0.15)",
                      color: "#c4b5fd",
                      padding: "10px 18px",
                      borderRadius: "999px",
                      fontWeight: "700",
                      border:
                        "1px solid rgba(139,92,246,0.25)"
                    }}
                  >
                    Review Required
                  </div>

                </div>

                {/* REASONS */}
                <div
                  style={{
                    marginBottom: "28px"
                  }}
                >

                  <h3
                    style={{
                      marginBottom: "14px",
                      color: "white",
                      fontSize: "20px"
                    }}
                  >
                    Matching Reasons
                  </h3>

                  <ul
                    style={{
                      paddingLeft: "22px",
                      color: "#cbd5e1",
                      lineHeight: "1.9"
                    }}
                  >

                    {review.reasons?.map((reason, index) => (

                      <li
                        key={index}
                        style={{
                          marginBottom: "8px",
                          fontSize: "16px"
                        }}
                      >
                        {reason}
                      </li>

                    ))}

                  </ul>

                </div>

                {/* BUTTONS */}
                <div
                  style={{
                    display: "flex",
                    gap: "16px"
                  }}
                >

                  {/* APPROVE */}
                  <button
                    onClick={() =>
                      approveReview(review.id)
                    }
                    style={{
                      flex: 1,
                      padding: "15px",
                      border: "none",
                      borderRadius: "14px",
                      background:
                        "linear-gradient(135deg, #22c55e, #15803d)",
                      color: "white",
                      fontWeight: "700",
                      fontSize: "16px",
                      cursor: "pointer",
                      transition: "0.3s"
                    }}
                  >
                    Approve Match
                  </button>

                  {/* REJECT */}
                  <button
                    onClick={() =>
                      rejectReview(review.id)
                    }
                    style={{
                      flex: 1,
                      padding: "15px",
                      border: "none",
                      borderRadius: "14px",
                      background:
                        "linear-gradient(135deg, #ef4444, #b91c1c)",
                      color: "white",
                      fontWeight: "700",
                      fontSize: "16px",
                      cursor: "pointer",
                      transition: "0.3s"
                    }}
                  >
                    Reject Match
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>
  );
}