let request = require('request');
let fs = require('fs');
let serviceRequestStatus = require('../request');
let clientIP = serviceRequestStatus.ip;
// function getProcedureName(expression) {
//   let splitArray = expression.split('(');
//
//   return splitArray[0].trim();
// }
//
// fs.readFile('../main.js', 'utf8', function(err, data) {
//   let result = data.replace('add(11,2)', 'let rpcCall = proxy.callProcedure(\'add\', \'number\', 11, 2);');
//
//   console.log(result);
//   fs.writeFile('../main.js', result, 'utf8', function (err) {
//     if (err) return console.log(err);
//   });
// });
function typeOf( obj ) {
  return ({}).toString.call( obj ).match(/\s(\w+)/)[1].toLowerCase();
}

function getArguementTypes(argValues) {
  let argTypes = [];

  for (let count = 0; count < argValues.length; count++ ) {
    if (typeOf(argValues[count]) == 'string' && argValues[count].length == 1) {
      argTypes.push('char');
    } else {
      argTypes.push(typeOf(argValues[count]));
    }
  }

  return argTypes;
}

// function getArguementValues(expression) {
//   let splitArray = expression.split('(');
//   splitArray[1].trim();
//   splitArray[1] = splitArray[1].slice(0, -1);
//
//   let values = splitArray[1].split(',');
//   for(let count in values) {
//     values[count] = values[count].trim();
//   }
//
//   return values;
// }

let idl = {
  number: 'int',
  boolean: 'boolean',
  int: 'int',
  string: 'string',
  char: 'char'
};

function getClientIP() {
  return new Promise(function (resolve, reject) {
    request.get('http://myip.dnsomatic.com/', function (err, res) {
      if(res.body != null && res.body != '' && res.body) {
        clientIP = res.body;
      }

      resolve(clientIP);
    });
  })
}

function marshall(procedure, argTypes, returnType) {
  let allParams = [];

  for(let count in argTypes) {
    let position = parseInt(count, 10) + 1;
    let param = {
      parameterPosition: position,
      parameterType: idl[argTypes[count]]
    };

    allParams.push(param);
  }

  let data = { serviceName: procedure,
    parameters: allParams
  };

  return data;
}

function marshallValue(procedure, argTypes, argValues, returnType) {
  let allParams = [];

  for(let count in argTypes) {
    let position = parseInt(count, 10) + 1;
    let param = {
      parameterPosition: position,
      parameterType: idl[argTypes[count]],
      parameterValue: argValues[count]
    };

    allParams.push(param);
    //allParams.push(argValues[count]);
  }

  let data = { serviceName: procedure,
    parameters: allParams,
    requestID: serviceRequestStatus.services[procedure],
    clientIp: clientIP
  };

  return data;
}

let rpcCall = function(xdrData, xdrDataValues) {
  return new Promise(function (resolve, reject) {
    let options = {
      url: 'https://registry-service-provider.herokuapp.com/service-provider',
      headers: {
        'data': JSON.stringify(xdrData)
      }
    };
    request.get(options, function (err, res) {
      if(err) {
        console.log(err);
      }
      //console.log(res.body)
      let data = JSON.parse(res.body);
      let serverAddress = data.serverAddress;
      //let address = serverAddress.split(':');

      //console.log(serverAddress);
      // options = {
      //   url: serverAddress + '/port',
      //   headers: {
      //     'data': JSON.stringify(xdrData)
      //   }
      // };

      // request.get(options, function (err, response) {
      //   if (err) {
      //     console.log(err);
      //   }
      //   data = JSON.parse(response.body);
      //   let port = data.PORT;
      //
      //   console.log(port);
      //   if (address.length >= 2) {
      //     serverAddress = address[0] + ':' + address[1];
      //   }
        let options = {
          method: 'post',
          body: xdrDataValues,
          json: true,
          //url: serverAddress + ':' + port
          url: serverAddress
        };
        request(options, function (err, resp) {
          if (err) {
            console.log(err);
          } else {
            let data = resp.body;
            //resolve(data.Result);
            resolve(data);
          }
        })
      });
    });
  //});
};

// async function add(a, b) {
//   let procedure = 'add';
//   let argValues = Array.prototype.slice.call(arguments);
//   let argTypes = getArguementTypes(argValues);
//   let returnType = 'int';
//   let xdrData = marshall(procedure, argTypes, returnType);
//   let xdrDataValues = marshallValue(procedure, argTypes, argValues, returnType);
//   let result = await rpcCall(xdrData, xdrDataValues);
//
//   return result;
// }

async function callProcedure(procedure, returnType,  ... arguments) {
  if(serviceRequestStatus.ip == null) {
    await getClientIP();
  }
  let argValues = Array.prototype.slice.call(arguments);
  let argTypes = getArguementTypes(argValues);
  let xdrData = marshall(procedure, argTypes, returnType);
  let xdrDataValues = marshallValue(procedure, argTypes, argValues, returnType);
  let result = rpcCall(xdrData, xdrDataValues);

  result.then(() => {
    let requestID = serviceRequestStatus.services[procedure];

    requestID+= 1;
    serviceRequestStatus.services[procedure] = requestID;
    serviceRequestStatus.ip = clientIP;

    fs.writeFileSync('../request.json', JSON.stringify(serviceRequestStatus), (err, res) => {

    });
  });

  return result;
}

module.exports = {
  callProcedure: callProcedure
};
