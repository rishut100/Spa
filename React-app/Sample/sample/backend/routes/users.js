const router = require("express").Router();
let User = require("../models/user.model");
const bcrypt = require("bcryptjs");

router.route("/").get((req, res) => {
  User.find()
    .then((users) => res.json(users))
    .catch((err) => res.status(400).json("Error: " + err));
});

//Register User
router.route("/add").post((req, res) => {
  const username = req.body.username;
  const password = req.body.password;
  const name = req.body.name;

  const newUser = new User({
    username: username,
    password: password,
    name: name,
  });

  newUser
    .save()
    .then(() => res.json("User added!"))
    .catch((err) => res.status(400).json("Error: " + err));
});

module.exports = router;
