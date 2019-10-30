var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn

/* GET crossing csv files */
router.get('/', function(req, res, next) {
  res.render('crossing', { title: 'data cross' });
});

module.exports = router;
