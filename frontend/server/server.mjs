import express from "express";
import fetch from "node-fetch";
import path from "path";
import dotenv from "dotenv";

dotenv.config();
const app = express();

// ✅ Proxy Direct Line token
app.get("/api/directline/token", async (req, res) => {
  try {
    console.log(`Direct line secret: ${process.env.DIRECT_LINE_SECRET}`);
    const response = await fetch(
      "https://directline.botframework.com/v3/directline/tokens/generate",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${process.env.DIRECT_LINE_SECRET}`,
          "Content-Type": "application/json",
        },
      }
    );

    const data = await response.json();
    if ('error' in data) {
        res.send(500);
    }
    res.json({ token: data.token });
  } catch (err) {
    console.error("Error generating token:", err);
    res.status(500).send("Error generating token");
  }
});

// ✅ Serve React build
const __dirname = path.resolve();
app.use(express.static(path.join(__dirname, "eers_demo/build")));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "eers_demo/build", "index.html"));
});

const PORT = process.env.PORT || 3978;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
