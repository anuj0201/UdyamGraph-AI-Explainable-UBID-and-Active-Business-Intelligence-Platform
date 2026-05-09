import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import Navbar from "../components/Navbar";
import { api } from "../lib/api";

const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d"),
  { ssr: false }
);

export default function GraphPage() {

  const [graphData, setGraphData] = useState({
    nodes: [],
    links: []
  });

  useEffect(() => {
    loadGraph();
  }, []);

  // =========================================
  // LOAD GRAPH DATA
  // =========================================
  const loadGraph = async () => {

    try {

      const reviewsRes = await api.get("/reviews/");
      const recordsRes = await api.get("/records/all");

      const recordsMap = {};

      recordsRes.data.forEach((r) => {
        recordsMap[r.id] = r;
      });

      const nodesMap = new Map();
      const links = [];

      reviewsRes.data.forEach((r) => {

        const rec1 = recordsMap[r.record_id];
        const rec2 = recordsMap[r.candidate_record_id];

        if (!rec1 || !rec2) return;

        const id1 = "r-" + rec1.id;
        const id2 = "r-" + rec2.id;

        // =========================================
        // NODE 1
        // =========================================
        if (!nodesMap.has(id1)) {

          nodesMap.set(id1, {
            id: id1,
            name: rec1.name,
            pan: rec1.pan,
            address: rec1.address,
            type: "record"
          });
        }

        // =========================================
        // NODE 2
        // =========================================
        if (!nodesMap.has(id2)) {

          nodesMap.set(id2, {
            id: id2,
            name: rec2.name,
            pan: rec2.pan,
            address: rec2.address,
            type: "candidate"
          });
        }

        // =========================================
        // LINK
        // =========================================
        links.push({
          source: id1,
          target: id2,
          score: r.score
        });
      });

      setGraphData({
        nodes: Array.from(nodesMap.values()),
        links
      });

    } catch (err) {

      console.error(err);
    }
  };

  return (
    <>
      <Navbar />

      <div
        style={{
          minHeight: "100vh",
          background:
            "linear-gradient(135deg, #020617, #0f172a)",
          padding: "40px"
        }}
      >

        {/* PAGE HEADER */}
        <div
          style={{
            maxWidth: "1300px",
            margin: "0 auto"
          }}
        >

          <h1
            style={{
              color: "white",
              fontSize: "52px",
              fontWeight: "800",
              marginBottom: "10px"
            }}
          >
            Business Relationship Graph
          </h1>

          <p
            style={{
              color: "#94a3b8",
              marginBottom: "25px",
              fontSize: "18px"
            }}
          >
            Visualize business matching relationships
            and entity connections
          </p>

          {/* LEGEND */}
          <div
            style={{
              display: "flex",
              gap: "25px",
              marginBottom: "25px",
              color: "white",
              fontSize: "16px"
            }}
          >

            <div>
              🔵 Original Record
            </div>

            <div>
              🟢 Candidate Match
            </div>

          </div>

          {/* GRAPH CARD */}
          <div
            style={{
              height: "700px",
              borderRadius: "24px",
              overflow: "hidden",
              border: "1px solid #1e293b",
              background:
                "linear-gradient(145deg, #0f172a, #111827)",
              boxShadow:
                "0 20px 40px rgba(0,0,0,0.4)"
            }}
          >

            <ForceGraph2D
              graphData={graphData}

              backgroundColor="#0b1120"

              // =========================================
              // TOOLTIP
              // =========================================
              nodeLabel={(node) =>
                `
Name: ${node.name}
PAN: ${node.pan || "N/A"}
Address: ${node.address || "N/A"}
                `
              }

              // =========================================
              // NODE DESIGN
              // =========================================
              nodeCanvasObject={(node, ctx, globalScale) => {

                const label = node.name;

                const fontSize = 16 / globalScale;

                ctx.font = `600 ${fontSize}px Inter`;

                // =========================================
                // NODE COLOR
                // =========================================
                ctx.fillStyle =
                  node.type === "record"
                    ? "#3b82f6"
                    : "#22c55e";

                // NODE CIRCLE
                ctx.beginPath();

                ctx.arc(
                  node.x,
                  node.y,
                  16,
                  0,
                  2 * Math.PI
                );

                ctx.fill();

                // GLOW EFFECT
                ctx.shadowColor =
                  node.type === "record"
                    ? "#3b82f6"
                    : "#22c55e";

                ctx.shadowBlur = 18;

                ctx.fill();

                ctx.shadowBlur = 0;

                // =========================================
                // TEXT COLOR FIXED HERE
                // =========================================
                ctx.fillStyle = "#ffffff";

                ctx.textAlign = "center";
                ctx.textBaseline = "top";

                ctx.fillText(
                  label,
                  node.x,
                  node.y + 22
                );
              }}

              // =========================================
              // LINK STYLING
              // =========================================
              linkWidth={2.5}

              linkColor={() =>
                "rgba(139, 92, 246, 0.8)"
              }

              linkDirectionalArrowLength={8}

              linkDirectionalArrowRelPos={1}

              // =========================================
              // LINK LABELS
              // =========================================
              linkCanvasObject={(link, ctx) => {

                const { source, target } = link;

                if (!source || !target) return;

                const dx = target.x - source.x;
                const dy = target.y - source.y;

                const length = Math.sqrt(
                  dx * dx + dy * dy
                );

                if (length === 0) return;

                const midX = source.x + dx * 0.5;
                const midY = source.y + dy * 0.5;

                const offset = 18;

                const offsetX = -dy / length;
                const offsetY = dx / length;

                const labelX =
                  midX + offsetX * offset;

                const labelY =
                  midY + offsetY * offset;

                // =========================================
                // MATCH TEXT COLOR FIXED HERE
                // =========================================
                ctx.font = "bold 18px Inter";

                ctx.fillStyle = "#ffffff";

                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                // background glow
                ctx.shadowColor = "#8b5cf6";
                ctx.shadowBlur = 10;

                ctx.fillText(
                  `Match (${link.score.toFixed(2)})`,
                  labelX,
                  labelY
                );

                ctx.shadowBlur = 0;
              }}

              // =========================================
              // PHYSICS
              // =========================================
              d3VelocityDecay={0.18}

              cooldownTicks={300}

              nodeRelSize={8}

              linkDistance={220}

              linkStrength={0.5}

              d3Force="charge"
              d3ForceConfig={{
                strength: -500
              }}
            />

          </div>

        </div>

      </div>
    </>
  );
}