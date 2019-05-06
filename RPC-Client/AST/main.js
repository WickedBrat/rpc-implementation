const acorn = require('acorn');
const estraverse =require('estraverse');
const escodegen = require('escodegen');
const fs = require('fs');
const services = require('../Services/services');

fs.readFile(process.argv[2], 'utf8', function(err, data) {
  let ast = acorn.parse(data, {
    ranges: true
  });
  estraverse.traverse(ast, {
    enter: function(node, parent) {
      if(node.type == 'CallExpression' && (services.name.includes(node.callee.name))) {
        let args = [];
        let service = node.callee.name;

        node.callee.name = "proxy.callProcedure";
        args.push({
          type: 'Literal',
          value: service
        });
        args.push({
          type: 'Literal',
          value: 'number'
        });
        for(let arg of node.arguments) {
          args.push(arg);
        }
        //node.arguments = [1, 2];
        node.arguments = args;
        return node;
      }
    }
  });
  let js = escodegen.generate(ast);
  fs.writeFile('../main.js', js, 'utf8', function (err) {
    if (err) return console.log(err);
    require('../main.js');
  });
});