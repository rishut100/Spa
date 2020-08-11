const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const exercisesRouter = require("./routes/exercises");
const usersRouter = require("./routes/users");

require("dotenv").config();

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// const uri = process.env.ATLAS_URI;
// mongoose.connect(uri, { useNewUrlParser: true, useCreateIndex: true });
// const connection = mongoose.connection;
// connection.once("open", () => {
//   console.log("MongoDB database connection established successfully");
// });

const url = "mongodb://localhost:27017/sample";
mongoose.connect(url, { useNewUrlParser: true });
const db = mongoose.connection;
db.once("open", (_) => {
  console.log("Database connected:", url);
});

app.use("/exercises", exercisesRouter);
app.use("/users", usersRouter);

if (process.env.NODE_ENV === "production") {
  app.use(express.static("../build"));
}

app.listen(port, () => {
  console.log(`Server running on port : ${port}`);
});
